from PySide6.QtGui import QColor,QImage,QPainter,QPen
from PySide6.QtCore import Qt
from src.worldbuilder.domain.layer import RasterLayer
from src.worldbuilder.domain.document import Document
from src.worldbuilder.tools.painter.base import BaseTool


class BrushTool(BaseTool):
  def __init__(self, document, color=QColor(0, 0, 0), size=4):
    super().__init__(document)
    self.color = QColor(color)
    self.size = size
    self._image = None
    self._last_pos = None

  def on_press(self, pos, button):
    if self.doc is None:
      return
    layer = self.doc.active_layer
    if not isinstance(layer, RasterLayer) or layer.locked:
      return
        
    self._image = layer.image
    self._last_pos = pos
    self._draw_segment(pos, pos)

  def on_move(self, pos, buttons):
    if self._image is None:
      return
    self._draw_segment(self._last_pos, pos)
    self._last_pos = pos


  def on_release(self, pos, button):
    self._image = None
    self._last_pos = None


  def _draw_segment(self, a, b):
    painter = QPainter(self._image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(self.color, self.size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(a, b)
    painter.end()
    self.changed.emit()