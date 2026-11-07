from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QPointF, QRect, QRectF, Signal

from src.worldbuilder.domain.layer import RasterLayer


MIN_SCALE = 0.1
MAX_SCALE = 10.0
ZOOM_STEP = 1.15
BACKGROUND = QColor("#434B4D")
PAPER = QColor(255, 255, 255)
PAN_BUTTONS = (Qt.MouseButton.RightButton)


class CanvasWidget(QWidget):
  brushSizeSignal = Signal(int)
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setMinimumSize(400, 400)
    self.setMouseTracking(True)
    self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    self.setCursor(Qt.CursorShape.CrossCursor)
    self.document = None
    self.tool = None
    self._scale = 1.0
    self._offset = QPointF(0, 0)
    self._panning = False
    self._last_mouse_pos = QPointF()
    self._tool_link = None

  def set_document(self, document):
    self.document = document
    self.reset_view()

  def set_tool(self, tool):
    self._disconnect_tool()
    self.tool = tool
    if tool is not None:
      if hasattr(tool, "dirty"):
        signal, slot = tool.dirty, self._on_dirty
      else:
        signal, slot = tool.changed, self.update
      signal.connect(slot)
      self._tool_link = (signal, slot)
    self.update()

  def _disconnect_tool(self):
    if self._tool_link is None:
      return
    signal, slot = self._tool_link
    self._tool_link = None
    try:
      signal.disconnect(slot)
    except (RuntimeError, TypeError):
      pass  # инструмент уже удалён


  def _screen_to_canvas(self, screen_pos):
    return (screen_pos - self._offset) / self._scale

  def _canvas_to_screen_rect(self, rect):
    s, o = self._scale, self._offset
    return QRectF(
      rect.x() * s + o.x(),
      rect.y() * s + o.y(),
      rect.width() * s,
      rect.height() * s,
    )

  def zoom_by(self, factor, anchor=None):
    if anchor is None:
      anchor = QPointF(self.rect().center())
    old_pos = self._screen_to_canvas(anchor)
    self._scale = max(MIN_SCALE, min(self._scale * factor, MAX_SCALE))
    new_pos = self._screen_to_canvas(anchor)
    self._offset += (new_pos - old_pos) * self._scale
    self.update()

  def reset_view(self):
    self._scale = 1.0
    rect = self._canvas_rect()
    self._offset = QPointF(
      (self.width() - rect.width()) / 2,
      (self.height() - rect.height()) / 2,
    )
    self.update()

  def _canvas_rect(self):
    if self.document is None:
      return QRect()
    for layer in self.document.layers:
      if isinstance(layer, RasterLayer) and layer.image is not None:
        return QRect(0, 0, layer.image.width(), layer.image.height())
    return QRect()


  def _on_dirty(self, rect):
    screen = self._canvas_to_screen_rect(rect)
    self.update(screen.adjusted(-2, -2, 2, 2).toAlignedRect())

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.fillRect(event.rect(), BACKGROUND)

    canvas_rect = self._canvas_rect()
    if canvas_rect.isEmpty():
      return

    # Сглаживание только при уменьшении
    painter.setRenderHint(
      QPainter.RenderHint.SmoothPixmapTransform,
      self._scale < 1.0,
    )
    painter.translate(self._offset)
    painter.scale(self._scale, self._scale)

    painter.fillRect(canvas_rect, PAPER)
    for layer in self.document.layers:  # первый слой снизу
      if layer.visible and isinstance(layer, RasterLayer) and layer.image is not None:
        painter.setOpacity(layer.opacity)
        painter.drawImage(0, 0, layer.image)
    painter.setOpacity(1.0)


  def mousePressEvent(self, event):
    if event.button() in PAN_BUTTONS:
      self._panning = True
      self._last_mouse_pos = event.position()
      self.setCursor(Qt.CursorShape.ClosedHandCursor)
      return

    if self.tool and event.button() == Qt.MouseButton.LeftButton:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_press(pos, event.button())

  def mouseMoveEvent(self, event):
    if self._panning:
      delta = event.position() - self._last_mouse_pos
      self._offset += delta
      self._last_mouse_pos = event.position()
      self.update()
      return

    if self.tool:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_move(pos, event.buttons())

  def mouseReleaseEvent(self, event):
    if self._panning and event.button() in PAN_BUTTONS:
      self._panning = False
      self.setCursor(Qt.CursorShape.CrossCursor)
      return

    if self.tool and event.button() == Qt.MouseButton.LeftButton:
      pos = self._screen_to_canvas(event.position())
      self.tool.on_release(pos, event.button())

  def wheelEvent(self, event):
    if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
      dy = event.angleDelta().y()
      if dy == 0:
        return
      factor = ZOOM_STEP if dy > 0 else 1 / ZOOM_STEP
      self.zoom_by(factor, event.position())
    else:
      delta = event.angleDelta().y()
      if delta:
          step = 1 if delta > 0 else -1
          self.brushSizeSignal.emit(step)
      event.accept()

    