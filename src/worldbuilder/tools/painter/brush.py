from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen

from src.worldbuilder.domain.layer import RasterLayer
from src.worldbuilder.tools.painter.base import BaseTool


class BrushTool(BaseTool):
  dirty = Signal(QRectF)

  def __init__(self, document, color=QColor(0, 0, 0), size=4):
    super().__init__(document)
    self.color = QColor(color)
    self.size = size
    self._painter = None
    self._last_pos = None

  def can_apply(self, layer):
    return (
      isinstance(layer, RasterLayer)
      and layer.image is not None
      and not layer.locked
    )

  def on_press(self, pos, button):
    if self.doc is None:
      return
    layer = self.doc.active_layer
    if not self.can_apply(layer):
      return

    self._end_stroke()
    self._painter = QPainter(layer.image)
    self._painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    self._setup_painter(self._painter)
    self._painter.setPen(self._make_pen())
    self._last_pos = pos
    self._painter.drawPoint(pos)
    self._emit_dirty(pos, pos)

  def on_move(self, pos, buttons):
    if self._painter is None:
      return
    self._painter.drawLine(self._last_pos, pos)
    self._emit_dirty(self._last_pos, pos)
    self._last_pos = pos

  def on_release(self, pos, button):
    self._end_stroke()

  def _make_pen(self):
    return QPen(
      self.color,
      self.size,
      Qt.PenStyle.SolidLine,
      Qt.PenCapStyle.RoundCap,
      Qt.PenJoinStyle.RoundJoin,
    )

  def _end_stroke(self):
    if self._painter is not None:
      self._painter.end()
      self._painter = None
    self._last_pos = None

  def _emit_dirty(self, a, b):
    margin = self.size / 2 + 2
    rect = QRectF(a, b).normalized().adjusted(-margin, -margin, margin, margin)
    self.dirty.emit(rect)

  def _setup_painter(self,painter):
    pass
