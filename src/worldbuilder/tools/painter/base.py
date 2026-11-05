from PySide6.QtCore import QObject, Signal

class BaseTool(QObject):
  changed = Signal()

  def __init__(self, document):
    super().__init__()
    self.doc = document
    # self.undo = undo_stack

  def can_apply(self,layer):
    return True
  
  def on_press(self,pos,button):
    pass

  def on_move(self,pos,button):
    pass

  def on_release(self,pos,button):
    pass