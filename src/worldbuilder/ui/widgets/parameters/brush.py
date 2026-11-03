from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
  QWidget,
  QSpinBox,
  QPushButton
)

class BrushOptionsWidget(QWidget):
  settingsApplied = Signal(int, QColor)
  def __init__(self,parent=None):
    super().__init__(parent)
    loader = QUiLoader()
    file = QFile("ui/widgets/parameters/brush.ui")
    self.widget = loader.load(file)
    file.close()
    self.size = 1
    self.color = QColor(0,0,0)
    
    #Виджеты
    self.width = self.widget.findChild(
      QSpinBox, "sizeSpinBox"
    )
    self.red = self.widget.findChild(
      QSpinBox, "redSpinBox"
    )
    self.green = self.widget.findChild(
      QSpinBox, "greenSpinBox"
    )
    self.blue = self.widget.findChild(
      QSpinBox, "blueSpinBox"
    )
    self.apply_button = self.widget.findChild(
      QPushButton, "applyButton"
    )
    self.cancel_button = self.widget.findChild(
      QPushButton, "cancelButton"
    )

    self.apply_button.clicked.connect(self.apply_press)
    self.cancel_button.clicked.connect(self.cancel_press)

  def apply_press(self):
    r = self.red.value()
    g = self.green.value()
    b = self.blue.value()
    size = self.width.value()

    self.color = QColor(r,g,b)
    self.size = size
    self.settingsApplied.emit(
      self.size,self.color
    )

  def cancel_press(self):
    pass


    