from PySide6.QtCore import QFile
from PySide6.QtWidgets import (
  QDialog,
  QLineEdit,
  QDoubleSpinBox,
  QSpinBox,
  QPushButton,
  QMessageBox,
)
from PySide6.QtUiTools import QUiLoader
from src.worldbuilder.domain.planet import Planet

class NewPlanetDialog:
  def __init__(self,parent=None):
    loader = QUiLoader()
    ui_file = QFile("ui/dialogs/CreateNewPlanet.ui")
    self.dialog = loader.load(ui_file,parent)
    ui_file.close()

    self.name_edit = self.dialog.findChild(
      QLineEdit, "planetNameEdit"
    )

    self.equator_spinbox = self.dialog.findChild(
      QDoubleSpinBox, "equatorLengthSpinBox"
    )
    
    self.resolution_spinbox = self.dialog.findChild(
      QSpinBox, "resolutionSpinBox"
    )

    self.create_button = self.dialog.findChild(
      QPushButton, "createButton"
    )

    self.cancel_button = self.dialog.findChild(
      QPushButton, "cancelButton"
    )

    self.create_button.clicked.connect(self.on_create_click)
    self.cancel_button.clicked.connect(self.dialog.reject)

    self.planet = None


  def on_create_click(self):
    name = self.name_edit.text().strip()
    equator_length = self.equator_spinbox.value()
    resolution = self.resolution_spinbox.value()

    self.planet = Planet(
      name=name,
      equator_length=equator_length,
      resolution=resolution,
    )

    self.dialog.accept()

  def exec(self):
    return self.dialog.exec()
  