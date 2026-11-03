from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtCore import Qt

class CanvasWidget(QWidget):
  def __init__(self,parent=None,color=(0,0,0),width=1):
    super().__init__(parent)
    self.setMinimumSize(400,300)
    self.setMouseTracking(True)
    self.strokes = []
    self.current_stroke = None
    r,g,b = color
    self.width = width
    self.color = QColor(r,g,b)

  def paintEvent(self,event):
    painter = QPainter(self)

    painter.fillRect(
      self.rect(),
      QColor(255,255,255)
    )

    for stroke in self.strokes:
      self.draw_stroke(painter,stroke)

    if self.current_stroke is not None:
      self.draw_stroke(painter,self.current_stroke)


  def set_tool(self,name):
    pass

  def mousePressEvent(self,event):
    if event.button() == Qt.MouseButton.LeftButton:
      self.current_stroke = {
        "color": self.color,
        "width": self.width,
        "points": [event.position()]
      }
      self.update()

  def mouseMoveEvent(self, event):
    if self.current_stroke is not None:
      self.current_stroke["points"].append(event.position())
      self.update()

  def mouseReleaseEvent(self,event):
    if (
      event.button() == Qt.MouseButton.LeftButton
      and self.current_stroke is not None 
    ):
      self.strokes.append(self.current_stroke)
      self.current_stroke = None
      self.update()

  def draw_stroke(self,painter,stroke):
    points = stroke["points"]

    if not points:
      return
    
    pen = QPen(stroke["color"])
    pen.setWidthF(float(stroke["width"]))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    if len(points) == 1:
      painter.drawPoint(points[0])
      return
    
    for index in range(len(points)-1):
      painter.drawLine(
        points[index],
        points[index+1]
      )
      
  def set_brush_color(self, color:QColor):
    self.color = QColor(color)

  def set_brush_size(self,size:int):
    self.width = size