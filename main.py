import sys

from src.worldbuilder.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import resources_rc

def main():
  app = QApplication(sys.argv)

  main_window = MainWindow()
  sys.exit(app.exec())

if __name__ == "__main__":
  main()