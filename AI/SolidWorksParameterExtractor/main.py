from PySide6.QtWidgets import QApplication, QMainWindow
import sys

from ui.extractor_ui import MainWindow
from sw_api.solidworks_connector import SolidWorksConnector


def main():
    app = QApplication(sys.argv)
    
    # Initialize SolidWorks connector
    sw_connector = SolidWorksConnector()
    
    window = MainWindow(sw_connector)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()