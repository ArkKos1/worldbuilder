from pathlib import Path

from PySide6.QtGui import QAction, QColor
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


class MainWindow:
  def __init__(self,parents=None):
    loader = QUiLoader()
    ui_file = QFile("ui/main_window.ui")
    self.window = loader.load(ui_file,parents)
    ui_file.close()
    self.color = (0,0,0)
    # Дети
    self.new_planet_action = self.window.findChild(
      QAction, "actionPlanet"
    )
    
    self.canvas_container = self.window.findChild(
      QWidget, "canvasContainer"
    )

    self.tool_options = self.window.findChild(
      QStackedWidget, "toolOptionStacked"
    )

    self.brush_button = self.window.findChild(
      QToolButton, "brushButton"
    )

    # Параметры инструментов

    self.brush_button.clicked.connect(
      self.press_brush_button
    )


    self.new_planet_action.triggered.connect(self.open_new_planet_dialog)
    layout = self.canvas_container.layout()
    if layout is None:
      layout = QVBoxLayout(self.canvas_container)
      layout.setContentsMargins(0, 0, 0, 0)
      layout.setSpacing(0)
    self.canvas = CanvasWidget(self.canvas_container)
    layout.addWidget(self.canvas)
    

    self.window.show()

    
  def open_new_planet_dialog(self):
    dialog = NewPlanetDialog(self.window)
    result = dialog.exec()
    if result != QDialog.DialogCode.Accepted:
      return
    planet = dialog.planet
    print(f"planet created: {planet.name}")
    print(f"Equator length: {planet.equator_length}")
    print(f"Resolution:{planet.resolution}")

  def load_widget(self,ui_path,parent=None):
    loader = QUiLoader()
    file = QFile(ui_path)
    try:
      widget = loader.load(file,parent)
    finally:
      file.close()
    return widget

#Press Functions

  def press_brush_button(self):
    self.brush_options_class = BrushOptionsWidget()
    brush_options_widget = self.brush_options_class.widget
    brush_index = self.tool_options.addWidget(brush_options_widget)
    self.brush_options_class.settingsApplied.connect(self.apply_brush_settings)
    
    self.tool_options.setCurrentIndex(brush_index)

  def apply_brush_settings(self,size,color):
    self.canvas.set_brush_color(color)
    self.canvas.set_brush_size(size)


class MainWindow2:


  def __init__(self,parents=None):
    self._load_ui(parents) # Loader
    self._init_state() # State
    self._find_widgets() # All of the widgets
    self._setup_canvas() # Canvas
    self._connect_signal() # All actions (connects)
    self.window.show()


  def _load_ui(self,parents=None):
    loader = QUiLoader()
    ui_file = QFile("ui/main_window.ui")
    self.window = loader.load(ui_file, parents)
    ui_file.close()


  def _init_state(self):
    self.document = 14
    self.undo_stack = None # History of changes
    self.renderer = None 
    self.tools = {}
    self.current_file_path = None
    self.active_tool_name = None

    # LAZY WIDGETS
    self._options_widgets = {
      "brush": {"class": BrushOptionsWidget, "instance": None}
    }


  def _find_widgets(self):

    # TOOLS BUTTONS
    self.choose_button = self._find(QToolButton,"chooseButton")
    self.select_button = self._find(QToolButton,"selectButton")
    self.pan_button = self._find(QToolButton,"panButton")
    self.brush_button = self._find(QToolButton,"brushButton")
    self.eraser_button = self._find(QToolButton,"eraserButton")
    self.fill_button = self._find(QToolButton,"fillButton")
    self.polygon_button = self._find(QToolButton,"polygonButton")
    self.edit_vertices_button = self._find(QToolButton,"editVerticesButton")
    self.measure_button = self._find(QToolButton,"measureButton")
    self.pipette_button = self._find(QToolButton,"pipetteButton")
    self.magic_wand_button = self._find(QToolButton,"magicWandButton")
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
    self.planet_action = self._find(QAction,"planetAction")
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
    #TOOLS
    self.brush_button.clicked.connect(lambda: self._on_tool_selected("brush"))
    self.eraser_button.clicked.connect(lambda: self._on_tool_selected("eraser"))
    self.fill_button.clicked.connect(lambda: self._on_tool_selected("fill"))
    self.magic_wand_button.clicked.connect(lambda: self._on_tool_selected("magic_wand"))
    self.select_button.clicked.connect(lambda: self._on_tool_selected("select"))
    self.choose_button.clicked.connect(lambda: self._on_tool_selected("choose"))
    self.pan_button.clicked.connect(lambda: self._on_tool_selected("pan"))
    self.polygon_button.clicked.connect(lambda: self._on_tool_selected("polygon"))
    self.edit_vertices_button.clicked.connect(lambda: self._on_tool_selected("edit_vertices"))
    self.measure_button.clicked.connect(lambda: self._on_tool_selected("measure"))
    self.pipette_button.clicked.connect(lambda: self._on_tool_selected("pipette"))

  
  def _on_tool_selected(self,name):
    if self.document is None:
      return
    tool = self.tools.get(name)
    # if tool is None:
    #   return
    self.canvas.set_tool(tool)
    self.active_tool_name = name
    self._show_tool_options(name)

  def _show_tool_options(self,name):
    entry = self._options_widgets.get(name)
    if entry is None:
      self.tool_options.setCurrentIndex(-1)
      return
    if entry["instance"] is None:
      widget = entry["class"]()
      self.tool_options.addWidget(widget.widget)
      entry["instance"] = widget
      slot_name = f"_on_{name}_settings"
      if hasattr(self,slot_name):
        widget.settingsApplied.connect(getattr(self,slot_name))
    self.tool_options.setCurrentWidget(entry["instance"].widget)


  def _on_new_planet(self):
    pass

  
  def _on_undo(self):
    pass

  
  def _on_redo(self):
    pass

  

