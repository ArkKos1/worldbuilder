from PySide6.QtGui import QPainter

from src.worldbuilder.tools.painter.brush import BrushTool

class EraserTool(BrushTool):
  def _setup_painter(self,painter):
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)

