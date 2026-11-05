from dataclasses import dataclass,field
from uuid import UUID
from PySide6.QtGui import QPainterPath
from src.worldbuilder.domain.layer import RasterLayer

@dataclass
class Document:
  planet: object
  layers: list = field(default_factory=list)
  active_layer_id: UUID = None
  selection: QPainterPath = field(default_factory=QPainterPath)

  @classmethod
  def from_planet(cls,planet,width,height):
    bg_layer = RasterLayer(name="BG",width=width,height=height)
    return cls(planet=planet,layers=[bg_layer],active_layer_id=bg_layer.id)
  
  @property
  def active_layer(self):
    for layer in self.layers:
      if layer.id == self.active_layer_id:
        return layer
    return None
  
  def has_selection(self):
    return not self.selection.isEmpty()