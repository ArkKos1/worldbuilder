from pathlib import Path

from PySide6.QtCore import QFile, QObject, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QSpinBox, QPushButton


UI_FILE = Path(__file__).resolve().parents[5] / "ui" / "widgets" / "parameters" / "brush.ui"


class BrushOptionsWidget(QObject):

  settingsApplied = Signal(int, QColor)

  def __init__(self, size=5, color=QColor(0, 0, 0), parent=None):
    super().__init__(parent)

    loader = QUiLoader()
    file = QFile(str(UI_FILE))
    self.widget = loader.load(file)
    file.close()
    if self.widget is None:
      raise RuntimeError(f"Can't load UI: {UI_FILE}")

    self.size = size
    self.color = QColor(color)


    self.size_spin = self.widget.findChild(QSpinBox, "sizeSpinBox")
    self.red_spin = self.widget.findChild(QSpinBox, "redSpinBox")
    self.green_spin = self.widget.findChild(QSpinBox, "greenSpinBox")
    self.blue_spin = self.widget.findChild(QSpinBox, "blueSpinBox")


    for name in ("applyButton", "cancelButton"):
      button = self.widget.findChild(QPushButton, name)
      if button is not None:
        button.hide()


    self.size_spin.setValue(self.size)
    self.red_spin.setValue(self.color.red())
    self.green_spin.setValue(self.color.green())
    self.blue_spin.setValue(self.color.blue())


    for spin in (self.size_spin, self.red_spin, self.green_spin, self.blue_spin):
      spin.valueChanged.connect(self._apply)

  def _apply(self, _value=None):
    self.size = self.size_spin.value()
    self.color = QColor(
      self.red_spin.value(),
      self.green_spin.value(),
      self.blue_spin.value(),
    )
    self.settingsApplied.emit(self.size, self.color)