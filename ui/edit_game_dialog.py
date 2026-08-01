from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QTextEdit, QPushButton, QFileDialog, 
                               QLabel, QMessageBox)
from PySide6.QtCore import Qt
import os
from models.game import Game

class EditGameDialog(QDialog): 
    def __init__(self, game: Game, parent=None): 
        super().__init__(parent)
        self.game = game
        self.setWindowTitle("Edit Game")
        self.setModal(True)
        self.resize(500, 400)
        
        self.cover_path = game.cover_path
        
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self): 
        """Setup the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Executable path (read-only)
        self.exe_path_label = QLabel()
        self.exe_path_label.setWordWrap(True)
        form_layout.addRow("Executable: ", self.exe_path_label)
        
        # Install directory (read-only)
        self.install_dir_label = QLabel()
        self.install_dir_label.setWordWrap(True)
        form_layout.addRow("Install Directory: ", self.install_dir_label)
        
        # Game details
        self.title_edit = QLineEdit()
        form_layout.addRow("Title: ", self.title_edit)
        
        self.genre_edit = QLineEdit()
        form_layout.addRow("Genre: ", self.genre_edit)
        
        self.developer_edit = QLineEdit()
        form_layout.addRow("Developer: ", self.developer_edit)
        
        self.publisher_edit = QLineEdit()
        form_layout.addRow("Publisher: ", self.publisher_edit)
        
        self.release_date_edit = QLineEdit()
        form_layout.addRow("Release Date: ", self.release_date_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description: ", self.description_edit)
        
        # Cover image
        cover_layout = QHBoxLayout()
        self.cover_path_edit = QLineEdit()
        self.cover_path_edit.setReadOnly(True)
        cover_browse_btn = QPushButton("Browse...")
        cover_browse_btn.clicked.connect(self.browse_cover)
        cover_layout.addWidget(self.cover_path_edit)
        cover_layout.addWidget(cover_browse_btn)
        form_layout.addRow("Cover Image: ", cover_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def populate_fields(self): 
        """Populate form fields with game data"""
        self.exe_path_label.setText(self.game.executable_path)
        self.install_dir_label.setText(self.game.install_dir)
        self.title_edit.setText(self.game.title)
        self.genre_edit.setText(self.game.genre)
        self.developer_edit.setText(self.game.developer)
        self.publisher_edit.setText(self.game.publisher)
        self.release_date_edit.setText(self.game.release_date)
        self.description_edit.setPlainText(self.game.description)
        self.cover_path_edit.setText(self.game.cover_path)
    
    def browse_cover(self): 
        """Browse for cover image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path: 
            self.cover_path = file_path
            self.cover_path_edit.setText(file_path)
    
    def get_game_data(self) -> Game: 
        """Get the updated game data from the form"""
        return Game(
            id=self.game.id,
            title=self.title_edit.text(), 
            executable_path=self.game.executable_path,
            install_dir=self.game.install_dir,
            genre=self.genre_edit.text(), 
            description=self.description_edit.toPlainText(), 
            developer=self.developer_edit.text(), 
            publisher=self.publisher_edit.text(), 
            release_date=self.release_date_edit.text(), 
            cover_path=self.cover_path,
            is_favorite=self.game.is_favorite,
            play_count=self.game.play_count,
            last_played=self.game.last_played
        )
    
    def accept(self): 
        """Override accept to validate input"""
        if not self.title_edit.text().strip(): 
            QMessageBox.warning(self, "Validation Error", "Please enter a game title.")
            return
        
        super().accept()