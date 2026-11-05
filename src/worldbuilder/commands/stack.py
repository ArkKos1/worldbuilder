from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage


class Command:
  def execute(self):
    pass

  def undo(self):
    pass



class PaintCommand(Command):
  def __init__(self,layer,before,after):
    self.layer = layer
    self.before = before
    self.after = after

  def execute(self):
    self.layer.image = self.after

  def undo(self):
    self.layer.image = self.before


class SetAttrCommand(Command):
  def __init__(self,target,attr_name,old_value,new_value):
    self.target = target
    self.attr_name = attr_name
    self.old_value = old_value
    self.new_value = new_value

  def execute(self):
    setattr(self.target,self.attr_name,self.new_value)

  def undo(self):
    setattr(self.target,self.attr_name,self.old_value)
