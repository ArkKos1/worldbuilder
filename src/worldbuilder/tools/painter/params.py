from dataclasses import dataclass
from typing import Any

@dataclass
class Param:
  key: str
  label: str
  kind: str
  default: Any
  min: float = 0
  max: float = 100
  choices:tuple = ()