from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter,QColor, QPen
from PySide6.QtCore import Qt, QPointF


class CanvasWidget(QWidget):
  def __init__(self,parent=None):
    super().__init__(parent)
    self.setMinimumSize(400,400)
    self.setMouseTracking(True)
    self.setFocusPolicy(Qt.StrongFocus)
    self.renderer = None
    self.tool = None
    # Camera
    self._scale = 1.0
    self._offset = QPointF(0,0)
    self._panning = False
    self._last_mouse_pos = QPointF()


  def set_tool(self,tool):
    self.tool = tool
    if tool:
      tool.changed.connect(self.update)

  def set_renderer(self,renderer):
    self.renderer = renderer
    self.update()

  
  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
    painter.setRenderHint(
      QPainter.RenderHint.SmoothPixmapTransform,
      self._scale < 5.0,
    )

    painter.fillRect(self.rect(), QColor("#434B4D"))
    painter.translate(self._offset)
    painter.scale(self._scale,self._scale)

    if self.tool and hasattr(self.tool, "doc") and self.tool.doc:
      layer = self.tool.doc.layers[0]
      if layer.image:
        painter.drawImage(0,0,layer.image)
    else:
      painter.fillRect(0,0,1400,800,QColor(255,255,255))
    # if self.renderer:
    #   self.renderer.paint(painter)
    # else:
    #   painter.fillRect(0,0,1400,800,QColor(255,255,255))

  def _screen_to_canvas(self,screen_pos):
    return (screen_pos - self._offset)/self._scale
    

  def mousePressEvent(self,event):
    if event.button() == Qt.MouseButton.RightButton:
      self._panning = True
      self._last_mouse_pos = event.position()
      self.setCursor(Qt.CursorShape.ClosedHandCursor)
      return
    
    if self.tool and event.button() == Qt.MouseButton.LeftButton:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_press(pos,event.button())
  

  def mouseMoveEvent(self, event):
    if self._panning:
      delta = event.position() - self._last_mouse_pos
      self._offset += delta
      self._last_mouse_pos = event.position()
      self.update()
      return
    
    if self.tool:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_move(pos,event.buttons())

  
  def mouseReleaseEvent(self, event):
    if event.button() == Qt.MouseButton.RightButton:
      self._panning = False
      self.setCursor(Qt.CursorShape.CrossCursor)
      return
    
    if self.tool and event.button() == Qt.MouseButton.LeftButton:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_release(pos,event.button())
  

  def wheelEvent(self, event):
    zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
    old_pos = self._screen_to_canvas(event.position())
    self._scale *= zoom_factor
    self._scale = max(0.1, min(self._scale,10.0))
    new_pos = self._screen_to_canvas(event.position())
    self._offset += (new_pos-old_pos) * self._scale
    self.update()
    