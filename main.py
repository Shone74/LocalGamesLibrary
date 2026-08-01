import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def create_directories(): 
    """Create necessary directories"""
    directories = ["data", "assets", "assets/icons", "assets/backgrounds"]
    for directory in directories: 
        os.makedirs(directory, exist_ok=True)

def create_default_files(): 
    """Create default files if they don't exist"""
    # Create default games.json if it doesn't exist
    if not os.path.exists("data/games.json"): 
        with open("data/games.json", "w") as f:
            f.write("[]")
    
    # Create default cover if it doesn't exist
    if not os.path.exists("assets/default_cover.png"): 
        from PySide6.QtGui import QPixmap, QPainter, QColor
        from PySide6.QtCore import Qt
        
        pixmap = QPixmap(200, 300)
        pixmap.fill(QColor("#333333"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.setFont(painter.font())
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "No Cover")
        painter.end()
        
        pixmap.save("assets/default_cover.png")

def main(): 
    # Create required directories before starting Qt.
    create_directories()
    
    # QPixmap creation in create_default_files requires a QApplication.
    app = QApplication(sys.argv)

    # Create data and image assets after Qt has been initialized.
    create_default_files()
    
    # Set application properties
    app.setApplicationName("Local Game Library")
    app.setApplicationVersion("0.1")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()
