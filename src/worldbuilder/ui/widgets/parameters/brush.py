from pathlib import Path

from PySide6.QtCore import QFile, QObject, Signal, QSignalBlocker, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QSpinBox, QPushButton,QComboBox, QSlider, QColorDialog


UI_FILE = Path(__file__).resolve().parents[5] / "ui" / "widgets" / "parameters" / "brush.ui"
PALETTES = {
    "Basic": ["#000000", "#FFFFFF", "#808080", "#C0C0C0", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#800080", "#8B4513", "#FFC0CB", "#00FFFF", "#FF00FF"],
    "Map": ["#8B4513", "#A0522D", "#D2B48C", "#F5DEB3", "#556B2F", "#228B22", "#006400", "#98FB98", "#808080", "#696969", "#BC8F8F", "#CD853F", "#2F4F4F", "#A9A9A9"],
    "Water": ["#E0FFFF", "#AFEEEE", "#48D1CC", "#00CED1", "#1E90FF", "#00BFFF", "#4169E1", "#0000CD", "#00008B", "#191970", "#008B8B", "#5F9EA0", "#2F4F4F", "#000080"],
    "Flora": ["#ADFF2F", "#7CFC00", "#32CD32", "#00FA9A", "#00FF7F", "#3CB371", "#2E8B57", "#008000", "#006400", "#6B8E23", "#9ACD32", "#8FBC8F", "#20B2AA", "#2F4F4F"],
    "Fire": ["#FFD700", "#FFA500", "#FF8C00", "#FF7F50", "#FF6347", "#FF4500", "#FF0000", "#DC143C", "#B22222", "#8B0000", "#A52A2A", "#D2691E", "#CD853F", "#000000"],
    "Magic": ["#4B0082", "#8A2BE2", "#9400D3", "#DA70D6", "#FF00FF", "#FF1493", "#C71585", "#483D8B", "#6A5ACD", "#7B68EE", "#191970", "#000000", "#2F4F4F", "#E6E6FA"],
}

class BrushOptionsWidget(QObject):

  settingsApplied = Signal(int, QColor,QColor)

  def __init__(self, size=5, color=QColor(0, 0, 0, 255), parent=None):
    super().__init__(parent)

    loader = QUiLoader()
    file = QFile(str(UI_FILE))
    self.widget = loader.load(file)
    file.close()
    if self.widget is None:
      raise RuntimeError(f"Can't load UI: {UI_FILE}")

    self.size = size
    self.prime_color = QColor(color)
    self.secondary_color = QColor(255,255,255,255)

    #COLORS MAIN
    self.size_spin = self.widget.findChild(QSpinBox, "sizeSpinBox")
    self.red_spin = self.widget.findChild(QSpinBox, "redSpinBox")
    self.green_spin = self.widget.findChild(QSpinBox, "greenSpinBox")
    self.blue_spin = self.widget.findChild(QSpinBox, "blueSpinBox")
    self.red_slider = self.widget.findChild(QSlider,"redSlider")
    self.green_slider = self.widget.findChild(QSlider,"greenSlider")
    self.blue_slider = self.widget.findChild(QSlider,"blueSlider")
    self.alpha_slider = self.widget.findChild(QSlider,"alphaSlider")
    self.alpha_spin = self.widget.findChild(QSpinBox, "alphaSpinBox")
    self.prime_color_button = self.widget.findChild(QPushButton, "primeColorButton")
    self.secondary_color_button = self.widget.findChild(QPushButton, "secondaryColorButton")
    self.change_colors_button = self.widget.findChild(QPushButton,"changeColorButton")

    self.size_spin.setValue(self.size)
    self.red_spin.setValue(self.prime_color.red())
    self.green_spin.setValue(self.prime_color.green())
    self.blue_spin.setValue(self.prime_color.blue())
    self.alpha_spin.setValue(self.prime_color.alpha())

    self.change_colors_button.clicked.connect(self._change_colors)
    self.prime_color_button.clicked.connect(self._new_prime_color)
    self.secondary_color_button.clicked.connect(self._new_secondary_color)

    #COLOR PALETTE 
    self.paletteButtons = {}
    self.chooseColorButtons = {}
    for id in range(14):
      widget_base = self.widget.findChild(QPushButton,f"baseColorButton_{id}")
      widget_choose = self.widget.findChild(QPushButton,f"chooseColorButton_{id}")
      self.paletteButtons[id] = {"widget": widget_base,"color":PALETTES["Basic"][id]}
      self.chooseColorButtons[id] = {"widget": widget_choose,"color":"#FFFFFF"}
      if widget_base:
        widget_base.clicked.connect(lambda checked=False,b=id: self._on_base_color_clicked(b))
      if widget_choose:
        widget_choose.clicked.connect(lambda checked=False,b=id: self._on_choose_color_clicked(b))
      
    self.palette_combo = self.widget.findChild(QComboBox,"paletteComboBox")
    self.add_color_button = self.widget.findChild(QPushButton,"addColorButton")
    self.delete_color_button = self.widget.findChild(QPushButton,"deleteColorButton")
    self.palette_combo.addItems(["Basic","Map","Water","Flora","Fire","Magic"])
    self.palette_combo.currentTextChanged.connect(self._on_palette_changed)
    self._on_palette_changed()
    self.current_base_color_button = None
    self.current_choose_color_button = None
    # NEW COLOR ADD
    self.free_buttons = [i for i in range(14)]
    self.place_of_new_color = 0
    self.add_color_button.clicked.connect(self._add_new_color)
    self.delete_color_button.clicked.connect(self._delete_color)
    #SPINS
    for spin in (self.size_spin, self.red_spin, self.green_spin, self.blue_spin, self.alpha_spin):
      spin.valueChanged.connect(self._apply)

    self._update_swatch()


  def _apply(self, _value=None):
    self.size = self.size_spin.value()
    self.prime_color = QColor(
      self.red_spin.value(),
      self.green_spin.value(),
      self.blue_spin.value(),
      self.alpha_spin.value(),
    )
    self._update_swatch()
    self.settingsApplied.emit(self.size, QColor(self.prime_color),QColor(self.secondary_color))


  def _change_colors(self):
    self.prime_color, self.secondary_color = self.secondary_color, self.prime_color
    self.color_to_prime()
    
    self._update_swatch()
    self._apply()


  def _update_swatch(self):
    self.prime_color_button.setStyleSheet(f"background-color: {self.prime_color.name()};")
    self.secondary_color_button.setStyleSheet(f"background-color: {self.secondary_color.name()};")


  def _on_palette_changed(self):
    self.current_palette = self.palette_combo.currentText()
    for id in range(14):
      self.paletteButtons[id]["widget"].setStyleSheet(f"background-color: {PALETTES[self.current_palette][id]}; border: 1px solid black;")
      self.paletteButtons[id]["color"] = PALETTES[self.current_palette][id]


  def color_to_prime(self):
    color = self.prime_color

    controls = [
        self.red_spin,
        self.green_spin,
        self.blue_spin,
        self.alpha_spin,
        self.red_slider,
        self.green_slider,
        self.blue_slider,
        self.alpha_slider
    ]

    blockers = [QSignalBlocker(control) for control in controls if control]

    self.red_spin.setValue(color.red())
    self.green_spin.setValue(color.green())
    self.blue_spin.setValue(color.blue())
    self.alpha_spin.setValue(color.alpha())

    self.red_slider.setValue(color.red())
    self.green_slider.setValue(color.green())
    self.blue_slider.setValue(color.blue())
    self.alpha_slider.setValue(color.alpha())


  def _on_base_color_clicked(self, button_id):
    if self.current_base_color_button is not None:
        old_id = self.current_base_color_button
        color = self.paletteButtons[old_id]["color"]
        widget = self.paletteButtons[old_id]["widget"]

        widget.setStyleSheet(
            f"background-color: {color}; border: 1px solid black;"
        )

    if self.current_choose_color_button is not None:
        old_id = self.current_choose_color_button
        color = self.chooseColorButtons[old_id]["color"]
        widget = self.chooseColorButtons[old_id]["widget"]

        widget.setStyleSheet(
            f"background-color: {color}; border: 1px solid black;"
        )

    self.current_base_color_button = button_id
    self.current_choose_color_button = None
    color = self.paletteButtons[button_id]["color"]
    widget = self.paletteButtons[button_id]["widget"]
    widget.setStyleSheet(
        f"background-color: {color}; border: 3px solid black;"
    )

    self.prime_color = QColor(color)
    self.color_to_prime()
    self._apply()
  

  def _on_choose_color_clicked(self, button_id):
    if self.current_base_color_button is not None:
        old_id = self.current_base_color_button
        color = self.paletteButtons[old_id]["color"]
        widget = self.paletteButtons[old_id]["widget"]

        widget.setStyleSheet(
            f"background-color: {color}; border: 1px solid black;"
        )

    if self.current_choose_color_button is not None:
        old_id = self.current_choose_color_button
        color = self.chooseColorButtons[old_id]["color"]
        widget = self.chooseColorButtons[old_id]["widget"]

        widget.setStyleSheet(
            f"background-color: {color}; border: 1px solid black;"
        )

    self.current_choose_color_button = button_id
    self.current_base_color_button = None
    color = self.chooseColorButtons[button_id]["color"]
    widget = self.chooseColorButtons[button_id]["widget"]

    widget.setStyleSheet(
        f"background-color: {color}; border: 3px solid black;"
    )

    self.prime_color = QColor(color)
    self.color_to_prime()
    self._apply()


  def _add_new_color(self):
    color_place = self.free_buttons.pop(0)
    self.chooseColorButtons[color_place]["color"] = self.prime_color.name()
    self.chooseColorButtons[color_place]["widget"].setStyleSheet(f"background-color: {self.prime_color.name()}; border: 1px solid black;")


  def _delete_color(self):
    if self.current_choose_color_button is not None:
      self.chooseColorButtons[self.current_choose_color_button]["color"] = "#FFFFFF"
      self.chooseColorButtons[self.current_choose_color_button]["widget"].setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
      self.free_buttons.append(self.current_choose_color_button)
      self.free_buttons.sort()


  def _new_prime_color(self):
    color = QColorDialog.getColor(
      self.prime_color,
      self.widget,
      "Choose brush color",
      QColorDialog.ColorDialogOption.ShowAlphaChannel
    )

    if color.isValid():
      self.prime_color = color
      self.color_to_prime()
      self._apply()


  def _new_secondary_color(self):
    color = QColorDialog.getColor(
      self.secondary_color,
      self.widget,
      "Choose brush color",
      QColorDialog.ColorDialogOption.ShowAlphaChannel
    )

    if color.isValid():
      self.secondary_color = color
      self._apply()


  def change_brush_size(self,step):
    self.size_spin.setValue(self.size_spin.value()+step)