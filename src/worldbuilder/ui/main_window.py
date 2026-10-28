from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (
  QMainWindow,
  QDialog,
  QWidget,
  QVBoxLayout
)
from src.worldbuilder.ui.new_planet_dialog import NewPlanetDialog
from src.worldbuilder.ui.canvas_widget import CanvasWidget


class MainWindow:
  def __init__(self,parents=None):
    loader = QUiLoader()
    ui_file = QFile("ui/main_window.ui")
    self.window = loader.load(ui_file,parents)
    ui_file.close()

    self.new_planet_action = self.window.findChild(
      QAction, "actionPlanet"
    )
    self.new_planet_action.triggered.connect(self.open_new_planet_dialog)
    self.canvas_container = self.window.findChild(
      QWidget, "canvasContainer"
    )
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
