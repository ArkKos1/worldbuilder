from pathlib import Path

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
  QLineEdit,
  QDoubleSpinBox,
  QSpinBox,
  QPushButton,
  QMessageBox,
)

from src.worldbuilder.domain.planet import Planet

UI_FILE = Path(__file__).resolve().parents[3] / "ui" / "dialogs" / "CreateNewPlanet.ui"


class NewPlanetDialog:
  def __init__(self, parent=None):
    self.planet = None

    loader = QUiLoader()
    ui_file = QFile(str(UI_FILE))
    self.dialog = loader.load(ui_file, parent)
    ui_file.close()
    if self.dialog is None:
      raise RuntimeError(f"Can't load UI: {UI_FILE}")

    self.name_edit = self.dialog.findChild(QLineEdit, "planetNameEdit")
    self.equator_spinbox = self.dialog.findChild(QDoubleSpinBox, "equatorLengthSpinBox")
    self.resolution_spinbox = self.dialog.findChild(QSpinBox, "resolutionSpinBox")
    self.create_button = self.dialog.findChild(QPushButton, "createButton")
    self.cancel_button = self.dialog.findChild(QPushButton, "cancelButton")

    self.create_button.clicked.connect(self._on_create_click)
    self.cancel_button.clicked.connect(self.dialog.reject)

  def _on_create_click(self):
    name = self.name_edit.text().strip()
    if not name:
      QMessageBox.warning(self.dialog, "Error", "Planet name can't be empty")
      self.name_edit.setFocus()
      return

    equator_length = self.equator_spinbox.value()
    if equator_length <= 0:
      QMessageBox.warning(self.dialog, "Error", "Equator length must be greater than zero")
      self.equator_spinbox.setFocus()
      return

    self.planet = Planet(
      name=name,
      equator_length=equator_length,
      resolution=self.resolution_spinbox.value(),
    )
    self.dialog.accept()

  def exec(self):
    return self.dialog.exec()