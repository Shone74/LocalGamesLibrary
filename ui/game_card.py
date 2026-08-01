from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from models.game import Game
import os


class GameCard(QWidget):
    play_clicked = Signal(Game)
    details_clicked = Signal(Game)
    favorite_clicked = Signal(Game)

    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.current_theme = "Dark"

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        self.setFixedWidth(200)
        self.setFixedHeight(250)

        self.setObjectName(
            "gameCard"
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.setLayout(
            layout
        )

        # Cover image
        self.cover_label = QLabel()

        self.cover_label.setObjectName(
            "coverLabel"
        )

        self.cover_label.setFixedHeight(
            120
        )

        self.cover_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.update_cover_image()

        layout.addWidget(
            self.cover_label
        )

        # Game title
        self.title_label = QLabel(
            self.game.title
        )

        self.title_label.setObjectName(
            "titleLabel"
        )

        self.title_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.title_label
        )

        # Genre
        self.genre_label = QLabel(
            self.game.genre
        )

        self.genre_label.setObjectName(
            "genreLabel"
        )

        layout.addWidget(
            self.genre_label
        )

        # Favorite and action buttons layout
        bottom_layout = QHBoxLayout()

        # Favorite button
        self.favorite_button = QPushButton()

        self.favorite_button.setObjectName(
            "favoriteButton"
        )

        self.favorite_button.setFixedSize(
            30,
            30
        )

        self.favorite_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.favorite_button.clicked.connect(
            self.on_favorite_clicked
        )

        self.update_favorite_button()

        bottom_layout.addWidget(
            self.favorite_button
        )

        # Spacer
        bottom_layout.addStretch()

        # Play button
        self.play_button = QPushButton(
            "PLAY"
        )

        self.play_button.setObjectName(
            "playButton"
        )

        self.play_button.setFixedSize(
            60,
            30
        )

        self.play_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.play_button.clicked.connect(
            self.on_play_clicked
        )

        bottom_layout.addWidget(
            self.play_button
        )

        # Details button
        self.details_button = QPushButton(
            "Details"
        )

        self.details_button.setObjectName(
            "detailsButton"
        )

        self.details_button.setFixedSize(
            60,
            30
        )

        self.details_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.details_button.clicked.connect(
            self.on_details_clicked
        )

        bottom_layout.addWidget(
            self.details_button
        )

        layout.addLayout(
            bottom_layout
        )

        self.apply_theme(
            self.current_theme
        )

    def apply_theme(
        self,
        theme
    ):
        """Apply the selected theme to the game card."""
        self.current_theme = theme

        if theme == "Dark":
            self.setStyleSheet("""
                QWidget#gameCard {
                    background-color: #2d2d2d;
                    border: 1px solid #444444;
                    border-radius: 10px;
                }

                QLabel#titleLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }

                QLabel#genreLabel {
                    color: #cccccc;
                    font-size: 12px;
                }

                QPushButton#favoriteButton {
                    background-color: transparent;
                    border: none;
                    color: #FFD700;
                    font-size: 18px;
                }

                QPushButton#favoriteButton:hover {
                    background-color: #444444;
                    color: #FFA500;
                    border-radius: 4px;
                }

                QPushButton#playButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }

                QPushButton#playButton:hover {
                    background-color: #45a049;
                    color: white;
                }

                QPushButton#detailsButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                }

                QPushButton#detailsButton:hover {
                    background-color: #1976D2;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget#gameCard {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }

                QLabel#titleLabel {
                    color: #222222;
                    font-weight: bold;
                    font-size: 14px;
                }

                QLabel#genreLabel {
                    color: #666666;
                    font-size: 12px;
                }

                QPushButton#favoriteButton {
                    background-color: transparent;
                    border: none;
                    color: #D4A000;
                    font-size: 18px;
                }

                QPushButton#favoriteButton:hover {
                    background-color: #eeeeee;
                    color: #B88600;
                    border-radius: 4px;
                }

                QPushButton#playButton {
                    background-color: #2E8B57;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }

                QPushButton#playButton:hover {
                    background-color: #246B45;
                    color: white;
                }

                QPushButton#detailsButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                }

                QPushButton#detailsButton:hover {
                    background-color: #125AA0;
                    color: white;
                }
            """)

    def update_cover_image(self):
        """Update the cover image."""
        pixmap = QPixmap()

        if (
            self.game.cover_path
            and os.path.exists(
                self.game.cover_path
            )
        ):
            pixmap.load(
                self.game.cover_path
            )
        else:
            default_cover_path = (
                "assets/default_cover.png"
            )

            if os.path.exists(
                default_cover_path
            ):
                pixmap.load(
                    default_cover_path
                )
            else:
                pixmap = QPixmap(
                    120,
                    120
                )

                pixmap.fill(
                    Qt.GlobalColor.gray
                )

        pixmap = pixmap.scaled(
            180,
            120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.cover_label.setPixmap(
            pixmap
        )

    def on_play_clicked(self):
        """Handle play button click."""
        self.play_clicked.emit(
            self.game
        )

    def on_details_clicked(self):
        """Handle details button click."""
        self.details_clicked.emit(
            self.game
        )

    def on_favorite_clicked(self):
        """Handle favorite button click."""
        self.game.is_favorite = (
            not self.game.is_favorite
        )

        self.update_favorite_button()

        self.favorite_clicked.emit(
            self.game
        )

    def update_favorite_button(self):
        """Show the current favorite state."""
        self.favorite_button.setText(
            "★"
            if self.game.is_favorite
            else "☆"
        )

        action = (
            "Remove from favorites"
            if self.game.is_favorite
            else "Add to favorites"
        )

        self.favorite_button.setToolTip(
            action
        )

        self.favorite_button.setAccessibleName(
            action
        )