from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QTextEdit, QPushButton, QFileDialog, 
                               QLabel, QMessageBox)
from PySide6.QtCore import Qt, QObject, QThread, Signal
import os
from models.game import Game
from services.metadata_service import GameMetadataService
import uuid
from datetime import datetime


class MetadataLookupWorker(QObject):
    """Run optional online metadata lookup off the GUI thread."""

    metadata_found = Signal(dict)
    metadata_not_found = Signal()
    finished = Signal()

    def __init__(self, title: str):
        super().__init__()
        self.title = title

    def search(self):
        try:
            metadata = GameMetadataService.fetch_metadata(self.title)
            if metadata:
                self.metadata_found.emit(metadata.to_dict())
            else:
                self.metadata_not_found.emit()
        except Exception:
            self.metadata_not_found.emit()
        finally:
            self.finished.emit()

class AddGameDialog(QDialog): 
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.setWindowTitle("Add Game")
        self.setModal(True)
        self.resize(500, 400)
        
        self.executable_path = ""
        self.install_dir = ""
        self.cover_path = ""
        self.detected_title = ""
        self.cover_search_thread = None
        self.cover_search_worker = None
        
        self.setup_ui()
    
    def setup_ui(self): 
        """Setup the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Executable selection
        exe_layout = QHBoxLayout()
        self.exe_path_edit = QLineEdit()
        self.exe_path_edit.setReadOnly(True)
        exe_browse_btn = QPushButton("Browse...")
        exe_browse_btn.clicked.connect(self.browse_executable)
        exe_layout.addWidget(self.exe_path_edit)
        exe_layout.addWidget(exe_browse_btn)
        form_layout.addRow("Executable: ", exe_layout)
        
        # Install directory (auto-filled)
        self.install_dir_label = QLabel()
        self.install_dir_label.setStyleSheet("color: #888888;")
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

        self.cover_status_label = QLabel()
        self.cover_status_label.setStyleSheet("color: #888888;")
        self.cover_status_label.setWordWrap(True)
        form_layout.addRow("Cover Search: ", self.cover_status_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        self.add_btn = QPushButton("Add Game")
        self.add_btn.clicked.connect(self.accept)
        self.add_btn.setEnabled(False)  # Disabled until executable is selected
        buttons_layout.addWidget(self.add_btn)
        
        layout.addLayout(buttons_layout)
    
    def browse_executable(self): 
        """Browse for game executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Executable", "", "Executable Files (*.exe)"
        )
        
        if file_path: 
            self.executable_path = file_path
            self.exe_path_edit.setText(file_path)
            
            # Identify the game locally first; this always works offline.
            local_metadata = GameMetadataService.identify_executable(file_path)
            self.install_dir = local_metadata["install_dir"]
            self.install_dir_label.setText(self.install_dir)

            title = local_metadata["title"]
            self.detected_title = title
            self.title_edit.setText(title)

            self.find_metadata(title)
            
            # Enable add button
            self.add_btn.setEnabled(True)
    
    def browse_cover(self): 
        """Browse for cover image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path: 
            self.cover_path = file_path
            self.cover_path_edit.setText(file_path)
            self.cover_status_label.setText("Cover image selected manually.")

    def find_metadata(self, title: str):
        """Try to enrich the locally identified game without blocking Add Game."""
        self.cover_status_label.setText("Looking up game metadata in the background...")
        if self.cover_search_thread and self.cover_search_thread.isRunning():
            return

        self.cover_search_thread = QThread(self)
        self.cover_search_worker = MetadataLookupWorker(title)
        self.cover_search_worker.moveToThread(self.cover_search_thread)
        self.cover_search_thread.started.connect(self.cover_search_worker.search)
        self.cover_search_worker.metadata_found.connect(self.on_metadata_found)
        self.cover_search_worker.metadata_not_found.connect(self.on_metadata_not_found)
        self.cover_search_worker.finished.connect(self.cover_search_thread.quit)
        self.cover_search_worker.finished.connect(self.cover_search_worker.deleteLater)
        self.cover_search_thread.finished.connect(self.cover_search_thread.deleteLater)
        self.cover_search_thread.finished.connect(self.clear_cover_search)
        self.cover_search_thread.start()

    def on_metadata_found(self, metadata: dict):
        """Fill empty fields only, preserving anything the user has entered."""
        provider_title = metadata.get("title", "")
        if provider_title and self.title_edit.text().strip() == self.detected_title:
            self.title_edit.setText(provider_title)
        fields = {
            "genre": self.genre_edit,
            "description": self.description_edit,
            "developer": self.developer_edit,
            "publisher": self.publisher_edit,
            "release_date": self.release_date_edit,
        }
        for field_name, widget in fields.items():
            value = metadata.get(field_name, "")
            current = widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text()
            if value and not current.strip():
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)

        cover_path = metadata.get("cover_path", "")
        if cover_path and not self.cover_path:
            self.set_automatic_cover(cover_path, "Game metadata and cover found automatically.")
        else:
            self.cover_status_label.setText("Game metadata found automatically.")

    def on_metadata_not_found(self):
        self.cover_status_label.setText(
            "No internet or metadata match found. The game can still be added now."
        )

    def set_automatic_cover(self, cover_path: str, status: str):
        """Show an automatically selected local cover path in the form."""
        self.cover_path = cover_path
        self.cover_path_edit.setText(cover_path)
        self.cover_status_label.setText(status)

    def clear_cover_search(self):
        """Release references after a background cover search has completed."""
        self.cover_search_thread = None
        self.cover_search_worker = None
    
    def get_game_data(self) -> Game: 
        """Get the game data from the form"""
        return Game(
            id=str(uuid.uuid4()), 
            title=self.title_edit.text(), 
            executable_path=self.executable_path, 
            install_dir=self.install_dir, 
            genre=self.genre_edit.text(), 
            description=self.description_edit.toPlainText(), 
            developer=self.developer_edit.text(), 
            publisher=self.publisher_edit.text(), 
            release_date=self.release_date_edit.text(), 
            cover_path=self.cover_path, 
            is_favorite=False, 
            play_count=0, 
            last_played=""
        )
    
    def accept(self): 
        """Override accept to validate input"""
        if not self.title_edit.text().strip(): 
            QMessageBox.warning(self, "Validation Error", "Please enter a game title.")
            return
        
        if not self.executable_path: 
            QMessageBox.warning(self, "Validation Error", "Please select a game executable.")
            return
        
        super().accept()
