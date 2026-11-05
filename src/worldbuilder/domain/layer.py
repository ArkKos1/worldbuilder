from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from PySide6.QtGui import QImage, QColor

@dataclass
class Layer(ABC):
  name: str
  id: UUID = field(default_factory=uuid4)
  visible: bool = True
  opacity: float = 1.0
  locked: bool = False

  @abstractmethod
  def clone(self):
    pass

@dataclass
class RasterLayer(Layer):
  width: int = 0
  height: int = 0
  image: QImage = None

  def __post_init__(self):
    if self.image is None and self.width > 0 and self.height > 0:
      self.image = QImage(self.width,self.height, QImage.Format.Format_ARGB32)
      self.image.fill(QColor(0,0,0,0))

  def clone(self):
    return RasterLayer(
      name=f"{self.name} (copy)",
      width=self.width,
      height=self.height,
      image=self.image.copy() if self.image else None,
      visible = self.visible,
      opacity=self.opacity,
      locked=self.locked,
    )