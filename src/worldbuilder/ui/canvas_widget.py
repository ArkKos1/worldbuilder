from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtCore import Qt

class CanvasWidget(QWidget):
  def __init__(self,parent=None):
    super().__init__(parent)
    self.setMinimumSize(400,300)
    self.setMouseTracking(True)

  def paintEvent(self,event):
    painter = QPainter(self)

    painter.fillRect(
      self.rect(),
      QColor(30,33,40)
    )

    painter.setPen(QPen(QColor(200,200,200)))

    font = QFont()
    font.setPointSize(14)
    painter.setFont(font)

    painter.drawText(
      self.rect(),
      Qt.AlignmentFlag.AlignCenter,
      "Worldbuilder Canvas",
    )

    painter.end()