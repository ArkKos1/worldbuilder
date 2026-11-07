from pathlib import Path

from PySide6.QtCore import QFile, QObject, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QSpinBox

UI_FILE = Path(__file__).resolve().parents[5] / "ui" / "widgets" / "parameters" / "eraser.ui"

class EraserOptionsWidget(QObject):

  settingsApplied = Signal(int)

  def __init__(self, size=5,parent=None):
    super().__init__(parent)

    loader = QUiLoader()
    file = QFile(str(UI_FILE))
    self.widget = loader.load(file)
    file.close()
    if self.widget is None:
      raise RuntimeError(f"Can't load UI: {UI_FILE}")
    
    self.size = size

    self.size_spin = self.widget.findChild(QSpinBox,"sizeSpinBox")
    self.size_spin.setValue(self.size)

    self.size_spin.valueChanged.connect(self._apply)
  
  def _apply(self,_value=None):
    self.size = self.size_spin.value()
    self.settingsApplied.emit(self.size)

  def change_brush_size(self,step):
    self.size_spin.setValue(self.size_spin.value()+step)