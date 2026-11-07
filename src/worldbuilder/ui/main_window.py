from pathlib import Path

from PySide6.QtGui import QAction, QColor, QUndoStack
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (
  QMainWindow,
  QDialog,
  QWidget,
  QVBoxLayout,
  QStackedWidget,
  QToolButton
)
from src.worldbuilder.ui.new_planet_dialog import NewPlanetDialog
from src.worldbuilder.ui.canvas_widget import CanvasWidget
from src.worldbuilder.ui.widgets.parameters.brush import BrushOptionsWidget
from src.worldbuilder.ui.widgets.parameters.eraser import EraserOptionsWidget

from src.worldbuilder.tools.painter.eraser import EraserTool
from src.worldbuilder.tools.painter.brush import BrushTool
from src.worldbuilder.domain.document import Document


UI_DIR = Path(__file__).resolve().parents[3] / "ui"


TOOL_BUTTONS = {
  "choose": "chooseButton",
  "select": "selectButton",
  "pan": "panButton",
  "brush": "brushButton",
  "eraser": "eraserButton",
  "fill": "fillButton",
  "polygon": "polygonButton",
  "edit_vertices": "editVerticesButton",
  "measure": "measureButton",
  "pipette": "pipetteButton",
  "magic_wand": "magicWandButton",
}

TOOL_FACTORIES = {
  "brush": lambda doc: BrushTool(doc, color=QColor(0, 0, 0), size=5),
  "eraser": lambda doc: EraserTool(doc,size=5)
}

OPTIONS_CLASSES = {
  "brush": BrushOptionsWidget,
  "eraser": EraserOptionsWidget,
}


class MainWindow:


  def __init__(self,parents=None):
    self._load_ui(parents) # Loader
    self._init_state() # State
    self._find_widgets() # All of the widgets
    self._setup_canvas() # Canvas
    self._connect_signal() # All actions (connects)
    self.window.show()


  def _load_ui(self,parents=None):
    loader = QUiLoader()
    ui_file = QFile(str(UI_DIR / "main_window.ui"))
    self.window = loader.load(ui_file, parents)
    ui_file.close()
    if self.window is None:
      raise RuntimeError(f"Can't load UI: {UI_DIR / 'main_window.ui'}")


  def _init_state(self):
    self.document = None
    self.undo_stack = QUndoStack(self.window) # History of changes
    self.tools = {} 
    self.current_file_path = None
    self.active_tool_name = None

    # LAZY WIDGETS 
    self._options_widgets = {}


  def _find_widgets(self):

    # TOOLS BUTTONS
    self.tool_buttons = {
      name: self._find(QToolButton, object_name)
      for name, object_name in TOOL_BUTTONS.items()
    }
    # ACTIONS
    self.new_planet_action = self._find(QAction,"planetAction")
    self.open_project_action = self._find(QAction,"openProjectAction")
    self.save_action = self._find(QAction,"saveAction")
    self.save_as_action = self._find(QAction,"saveAsAction")
    self.export_action = self._find(QAction,"exportAction")
    self.exit_action = self._find(QAction,"exitAction")
    self.undo_action = self._find(QAction,"undoAction")
    self.redo_action = self._find(QAction,"redoAction")
    self.cut_action = self._find(QAction,"cutAction")
    self.copy_action = self._find(QAction,"copyAction")
    self.paste_action = self._find(QAction,"pasteAction")
    self.preferences_action = self._find(QAction,"preferencesAction")
    self.zoom_in_action = self._find(QAction,"zoomInAction")
    self.zoom_out_action = self._find(QAction,"zoomOutAction")
    self.zoom_reset_action = self._find(QAction,"zoomResetAction")
    self.grid_toggle_action = self._find(QAction,"gridToggleAction")
    self.properties_panel_action = self._find(QAction,"propertiesPanelAction")
    self.layers_panel_action = self._find(QAction,"layersPanelAction")
    self.world_props_action = self._find(QAction,"worldPropsAction")
    self.new_layer_action = self._find(QAction,"newLayerAction")
    self.duplicate_layer_action = self._find(QAction,"duplicateLayerAction")
    self.delete_layer_action = self._find(QAction,"deleteLayerAction")
    self.rename_layer_action = self._find(QAction,"renameLayerAction")
    # TOOLS ACTIONS
    self.select_action = self._find(QAction,"selectAction")
    self.brush_action = self._find(QAction,"brushAction")
    self.line_action = self._find(QAction,"lineAction")
    self.polygon_action = self._find(QAction,"polygonAction")
    self.pan_action = self._find(QAction,"panAction")
    self.edit_vertices_action = self._find(QAction,"editVerticesAction")
    self.measure_action = self._find(QAction,"measureAction")
    self.magic_wand_action = self._find(QAction,"magicWandAction")
    # MISC
    self.canvas_container = self._find(QWidget,"canvasContainer")
    self.tool_options = self._find(QStackedWidget,"toolOptionStacked")


  def _find(self, cls ,name):
    widget = self.window.findChild(cls,name)
    if widget is None:
      raise RuntimeError(f"Widget '{name}' ({cls.__name__}) not found")
    return widget


  def _setup_canvas(self):
    layout = self.canvas_container.layout()
    if layout is None:
      layout = QVBoxLayout(self.canvas_container)
      layout.setContentsMargins(0,0,0,0)
      layout.setSpacing(0)
    self.canvas = CanvasWidget(self.canvas_container)
    layout.addWidget(self.canvas)


  def _connect_signal(self):
    # MENU
    self.new_planet_action.triggered.connect(self._on_new_planet)
    self.undo_action.triggered.connect(self._on_undo)
    self.redo_action.triggered.connect(self._on_redo)
    self.exit_action.triggered.connect(self.window.close)
    # UNDO STACK 
    self.undo_stack.indexChanged.connect(lambda _: self.canvas.update())
    self.undo_stack.canUndoChanged.connect(self.undo_action.setEnabled)
    self.undo_stack.canRedoChanged.connect(self.redo_action.setEnabled)
    self.undo_action.setEnabled(False)
    self.redo_action.setEnabled(False)
    # TOOLS 
    for name, button in self.tool_buttons.items():
      button.clicked.connect(lambda checked=False, n=name: self._on_tool_selected(n))
    


  def _get_tool(self, name):
    tool = self.tools.get(name)
    if tool is None:
      factory = TOOL_FACTORIES.get(name)
      if factory is None:
        return None
      tool = factory(self.document)
      self.tools[name] = tool
    return tool


  def _on_tool_selected(self,name):
    if self.document is None:
      return
    tool = self._get_tool(name)
    if tool is None:
      self.window.statusBar().showMessage(f"Tool '{name}' is not implemented yet", 3000)
      return
    self.canvas.set_tool(tool)
    self.active_tool_name = name
    self._show_tool_options(name)


  def _show_tool_options(self,name):
    cls = OPTIONS_CLASSES.get(name)
    if cls is None:
      self.tool_options.setCurrentIndex(-1)
      return
    widget = self._get_options_widget(name,cls)
    self.tool_options.setCurrentWidget(widget.widget)


  def _on_brush_settings(self, size, color, secondary_color):
    tool = self.tools.get("brush")
    if tool is None:
      return
    tool.size = size
    tool.color = QColor(color)
    tool.secondary_color = QColor(secondary_color)

  def _on_eraser_settings(self,size):
    tool = self.tools.get("eraser")
    if tool is None:
      return
    tool.size = size


  def _get_options_widget(self,name,cls):
    widget = self._options_widgets.get(name)
    if widget is None:
      widget = cls()
      self.tool_options.addWidget(widget.widget)
      slot = getattr(self,f"_on_{name}_settings", None)
      if slot is not None:
        widget.settingsApplied.connect(slot)
        
      if name == "brush" or name == "eraser":
        self.canvas.brushSizeSignal.connect(widget.change_brush_size)

      self._options_widgets[name] = widget
    return widget

  def _on_new_planet(self):
    dialog = NewPlanetDialog(self.window)
    result = dialog.exec()
    if result != QDialog.DialogCode.Accepted:
      return
    planet = dialog.planet
    self.document = Document.from_planet(planet,1400,800)
    self.canvas.set_document(self.document)
    self.undo_stack.clear()
    self.tools = {} 
    self._on_tool_selected("brush")
    self.window.setWindowTitle(f"Worldbuilder - {planet.name}")
    self.canvas.update()


  def _on_undo(self):
    self.undo_stack.undo()


  def _on_redo(self):
    self.undo_stack.redo()