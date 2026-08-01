from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from models.game import Game
from services.game_library import GameLibrary
from services.game_launcher import GameLauncher
from ui.edit_game_dialog import EditGameDialog
import os

class DetailedViewWidget(QDialog): 
    def __init__(self, game: Game, game_library: GameLibrary, game_launcher: GameLauncher,
                 confirm_delete=True, minimize_on_launch=False, parent=None): 
        super().__init__(parent)
        self.game = game
        self.game_library = game_library
        self.game_launcher = game_launcher
        self.confirm_delete = confirm_delete
        self.minimize_on_launch = minimize_on_launch
        self.setWindowTitle(f"Game Details - {game.title}")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
    
    def setup_ui(self): 
        """Setup the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with cover and basic info
        header_layout = QHBoxLayout()
        
        # Cover image
        cover_label = QLabel()
        cover_label.setFixedWidth(200)
        cover_label.setFixedHeight(300)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap()
        if self.game.cover_path and os.path.exists(self.game.cover_path): 
            pixmap.load(self.game.cover_path)
        else: 
            # Load default cover
            default_cover_path = "assets/default_cover.png"
            if os.path.exists(default_cover_path): 
                pixmap.load(default_cover_path)
            else: 
                # Create a simple placeholder
                pixmap = QPixmap(200, 300)
                pixmap.fill(Qt.GlobalColor.gray)
        
        # Scale pixmap to fit label
        pixmap = pixmap.scaled(
            200, 300, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        cover_label.setPixmap(pixmap)
        header_layout.addWidget(cover_label)
        
        # Game info
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_label = QLabel(self.game.title)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(title_label)
        
        genre_label = QLabel(self.game.genre)
        genre_label.setStyleSheet("font-size: 16px; color: #cccccc;")
        info_layout.addWidget(genre_label)
        
        developer_label = QLabel(self.game.developer)
        info_layout.addWidget(developer_label)
        
        publisher_label = QLabel(self.game.publisher)
        info_layout.addWidget(publisher_label)
        
        release_label = QLabel(f"Released: {self.game.release_date}")
        info_layout.addWidget(release_label)
        
        # Favorite button
        favorite_btn = QPushButton("Remove from Favorites" if self.game.is_favorite else "Add to Favorites")
        favorite_btn.clicked.connect(self.toggle_favorite)
        info_layout.addWidget(favorite_btn)
        
        # Play button
        play_btn = QPushButton("PLAY")
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        play_btn.clicked.connect(self.play_game)
        info_layout.addWidget(play_btn)
        
        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(desc_label)
        
        description_text = QTextEdit()
        description_text.setPlainText(self.game.description)
        description_text.setReadOnly(True)
        description_text.setMaximumHeight(150)
        layout.addWidget(description_text)
        
        # Statistics
        stats_label = QLabel("Statistics")
        stats_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(stats_label)
        
        stats_layout = QFormLayout()
        stats_layout.addRow("Times Played: ", QLabel(str(self.game.play_count)))
        stats_layout.addRow("Last Played: ", QLabel(self.game.last_played or "Never"))
        layout.addLayout(stats_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        edit_btn = QPushButton("Edit Game")
        edit_btn.clicked.connect(self.edit_game)
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Game")
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(self.delete_game)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
    
    def toggle_favorite(self): 
        """Toggle favorite status"""
        self.game.is_favorite = not self.game.is_favorite
        self.game_library.update_game(self.game.id, self.game)
        self.accept()  # Close dialog to refresh
    
    def play_game(self): 
        """Play the game"""
        if self.game_launcher.launch_game(self.game):
            if self.minimize_on_launch and self.parent():
                self.parent().showMinimized()
            self.accept()
        else:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch game: {self.game.title}")
    
    def edit_game(self): 
        """Edit game details"""
        dialog = EditGameDialog(self.game, self)
        if dialog.exec() == QDialog.Accepted: 
            updated_game = dialog.get_game_data()
            if self.game_library.update_game(self.game.id, updated_game): 
                QMessageBox.information(self, "Success", "Game updated successfully!")
                self.accept()  # Close dialog to refresh
            else: 
                QMessageBox.warning(self, "Error", "Failed to update game!")
    
    def delete_game(self): 
        """Delete the game"""
        reply = QMessageBox.Yes
        if self.confirm_delete:
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to remove '{self.game.title}' from your library?\n\n"
                "This will only remove the game from Local Game Library.\n"
                "The actual game files will not be deleted.",
                QMessageBox.Yes | QMessageBox.No
            )
        
        if reply == QMessageBox.Yes: 
            if self.game_library.remove_game(self.game.id): 
                QMessageBox.information(self, "Success", "Game removed from library!")
                self.accept()  # Close dialog
            else: 
                QMessageBox.warning(self, "Error", "Failed to remove game!")
