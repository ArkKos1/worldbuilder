from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QPainter,QUndoCommand


class Command:
  def execute(self):
    pass

  def undo(self):
    pass



class PaintCommand(QUndoCommand):
  def __init__(self,layer,rect: QRect, before_patch: QImage, after_patch: QImage, text="Paint"):
    super().__init__(text)
    self.layer = layer
    self.rect = QRect(rect)
    self.before_patch = before_patch
    self.after_patch = after_patch
  
  def redo(self):
    self._apply(self.after_patch)

  def undo(self):
    self._apply(self.before_patch)

  def _apply(self,patch: QImage):
    painter = QPainter(self.layer.image)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    painter.drawImage(self.rect,patch)
    painter.end()


class SetAttrCommand(QUndoCommand):
  def __init__(self,target,attr_name,old_value,new_value, text=None):
    super().__init__(text or f"Change {attr_name}")
    self.target = target
    self.attr_name = attr_name
    self.old_value = old_value
    self.new_value = new_value

  def redo(self):
    setattr(self.target,self.attr_name,self.new_value)

  def undo(self):
    setattr(self.target,self.attr_name,self.old_value)
