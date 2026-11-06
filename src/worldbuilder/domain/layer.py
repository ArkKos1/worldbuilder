from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


@dataclass(eq=False)
class Layer(ABC):
  name: str
  id: UUID = field(default_factory=uuid4)
  visible: bool = True
  opacity: float = 1.0
  locked: bool = False

  @abstractmethod
  def paint(self, painter, rect=None):
    """Рисует слой в painter (rect в координатах холста, None = весь слой)."""

  @abstractmethod
  def clone(self):
    pass


@dataclass(eq=False)
class RasterLayer(Layer):
  width: int = 0
  height: int = 0
  image: QImage = None

  def __post_init__(self):
    if self.image is None:
      if self.width > 0 and self.height > 0:
        self.image = QImage(self.width, self.height, QImage.Format.Format_ARGB32_Premultiplied)
        self.image.fill(Qt.GlobalColor.transparent)
    else:
      if self.image.format() != QImage.Format.Format_ARGB32_Premultiplied:
        self.image = self.image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
      self.width = self.image.width()
      self.height = self.image.height()
    self.opacity = max(0.0, min(1.0, self.opacity))

  def paint(self, painter, rect=None):
    if not self.visible or self.image is None:
      return
    painter.save()
    painter.setOpacity(painter.opacity() * self.opacity)
    if rect is None:
      painter.drawImage(0, 0, self.image)
    else:
      painter.drawImage(rect, self.image, rect)
    painter.restore()

  def clone(self):
    return RasterLayer(
      name=f"{self.name} (copy)",
      image=self.image.copy() if self.image else None,
      width=self.width,
      height=self.height,
      visible=self.visible,
      opacity=self.opacity,
      locked=self.locked,
    )