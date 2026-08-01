from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QGridLayout,
    QPushButton,
    QMessageBox,
    QLineEdit,
    QDialog,
    QComboBox
)
from PySide6.QtCore import Qt, QObject, QThread, Signal, QTimer
from models.game import Game
from storage.json_storage import JsonStorage
from services.game_library import GameLibrary
from services.game_launcher import GameLauncher
from services.metadata_service import GameMetadataService
from ui.game_card import GameCard
from ui.add_game_dialog import AddGameDialog
from ui.detailed_view_widget import DetailedViewWidget
from ui.settings_dialog import SettingsDialog


class MetadataRefreshWorker(QObject):
    """Fetch missing metadata without ever delaying the user interface."""

    metadata_found = Signal(str, dict)
    finished = Signal()

    def __init__(self, games):
        super().__init__()
        self.games = games

    def refresh(self):
        try:
            if not GameMetadataService.is_online():
                return

            for game in self.games:
                if not self._needs_metadata(game):
                    continue

                metadata = GameMetadataService.fetch_metadata(game.title)

                if metadata:
                    self.metadata_found.emit(game.id, metadata.to_dict())
        finally:
            self.finished.emit()

    @staticmethod
    def _needs_metadata(game):
        return any(
            not getattr(game, field).strip()
            for field in (
                "genre",
                "description",
                "developer",
                "publisher",
                "release_date",
                "cover_path"
            )
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Local Game Library")
        self.setGeometry(100, 100, 1200, 800)

        self.storage = JsonStorage()
        self.game_library = GameLibrary(self.storage)
        self.game_launcher = GameLauncher(self.game_library)
        self.settings = self.storage.load_settings()

        self.current_view = self.view_name_to_key(
            self.settings["default_view"]
        )
        self.search_term = ""
        self.metadata_refresh_thread = None
        self.metadata_refresh_worker = None

        self.setup_ui()
        self.apply_theme()

        self.load_games()
        QTimer.singleShot(0, self.refresh_missing_metadata)

    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")

        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        header_layout = QHBoxLayout()

        title_label = QLabel("Local Game Library")
        title_label.setObjectName("headerTitle")
        header_layout.addWidget(title_label)

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search games...")
        self.search_bar.textChanged.connect(self.on_search_changed)
        header_layout.addWidget(self.search_bar)

        self.genre_filter = QComboBox()
        self.genre_filter.setObjectName("genreFilter")
        self.genre_filter.currentTextChanged.connect(self.load_games)
        header_layout.addWidget(self.genre_filter)

        self.add_game_btn = QPushButton("+ Add Game")
        self.add_game_btn.setObjectName("addGameButton")
        self.add_game_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.add_game_btn.clicked.connect(
            self.show_add_game_dialog
        )
        header_layout.addWidget(self.add_game_btn)

        content_layout.addLayout(header_layout)

        self.games_grid = QGridLayout()
        self.games_grid.setSpacing(20)

        self.empty_state_widget = self.create_empty_state()

        scroll_area = QScrollArea()
        scroll_area.setObjectName("gamesScrollArea")

        scroll_widget = QWidget()
        scroll_widget.setObjectName("gamesScrollWidget")
        scroll_widget.setLayout(self.games_grid)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        content_layout.addWidget(scroll_area)

    def create_sidebar(self):
        """Create the sidebar"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout()
        sidebar.setLayout(layout)

        sidebar_buttons = [
            ("Home", self.show_home),
            ("All Games", self.show_all_games),
            ("Favorites", self.show_favorites),
            ("Genres", self.show_genres),
            ("Settings", self.show_settings)
        ]

        for text, handler in sidebar_buttons:
            btn = QPushButton(text)
            btn.setObjectName("sidebarButton")
            btn.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()

        return sidebar

    def show_home(self):
        """Show home view"""
        self.current_view = "all"
        self.load_games()

    def show_all_games(self):
        """Show all games view"""
        self.current_view = "all"
        self.load_games()

    def show_favorites(self):
        """Show favorites view"""
        self.current_view = "favorites"
        self.load_games()

    def show_genres(self):
        """Show games by genre, using the genre selector in the header."""
        self.current_view = "genres"
        self.load_games()

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(
            self.settings,
            self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()

            if not self.storage.save_settings(
                self.settings
            ):
                QMessageBox.warning(
                    self,
                    "Settings Error",
                    self.storage.last_error
                )

            self.apply_theme()

            self.current_view = self.view_name_to_key(
                self.settings["default_view"]
            )

            self.load_games()

    def show_add_game_dialog(self):
        """Show the add game dialog"""
        dialog = AddGameDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            game = dialog.get_game_data()

            if self.game_library.add_game(game):
                self.load_games()
                self.refresh_missing_metadata()

                QMessageBox.information(
                    self,
                    "Success",
                    f"Game '{game.title}' added successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "A game with this executable already exists!"
                )

    def on_search_changed(self, text):
        """Handle search text change"""
        self.search_term = text.lower()
        self.load_games()

    def load_games(self):
        """Load and display games"""
        for i in reversed(
            range(self.games_grid.count())
        ):
            item = self.games_grid.itemAt(i)

            if item is not None:
                widget = item.widget()

                if widget is not None:
                    widget.setParent(None)

        all_games = self.game_library.get_all_games()

        self.update_genre_filter(
            all_games
        )

        if self.current_view == "favorites":
            games = self.game_library.get_favorite_games()
        else:
            games = all_games

        selected_genre = self.genre_filter.currentText()

        if (
            self.current_view == "genres"
            and selected_genre == "All Genres"
        ):
            games = sorted(
                games,
                key=lambda game: (
                    game.genre.lower(),
                    game.title.lower()
                )
            )
        elif selected_genre != "All Genres":
            games = [
                game
                for game in games
                if game.genre == selected_genre
            ]

        if self.search_term:
            games = [
                game
                for game in games
                if self.search_term
                in game.title.lower()
            ]

        if not games:
            (
                title,
                description,
                show_add_button
            ) = self.get_empty_state_content(
                all_games
            )

            self.empty_state_title.setText(
                title
            )

            self.empty_state_description.setText(
                description
            )

            self.empty_state_add_button.setVisible(
                show_add_button
            )

            self.games_grid.addWidget(
                self.empty_state_widget,
                0,
                0,
                1,
                4,
                Qt.AlignmentFlag.AlignCenter
            )

            return

        for i, game in enumerate(games):
            row = i // 4
            col = i % 4

            game_card = GameCard(game)

            game_card.apply_theme(
                self.settings.get(
                    "theme",
                    "Dark"
                )
            )

            game_card.play_clicked.connect(
                self.on_play_game
            )

            game_card.details_clicked.connect(
                self.on_show_details
            )

            game_card.favorite_clicked.connect(
                self.on_toggle_favorite
            )

            self.games_grid.addWidget(
                game_card,
                row,
                col
            )

    def get_empty_state_content(
        self,
        all_games
    ):
        """Return contextual empty-state content."""
        if not all_games:
            return (
                "Your library is empty",
                "Add your first game to get started.",
                True
            )

        if self.search_term:
            return (
                "No games found",
                "Try a different game name or clear the search.",
                False
            )

        if (
            self.genre_filter.currentText()
            != "All Genres"
        ):
            return (
                "No games in this genre",
                "Choose another genre or add a game with this genre.",
                False
            )

        if self.current_view == "favorites":
            return (
                "No favorite games yet",
                "Use the star on a game card to add it to Favorites.",
                False
            )

        return (
            "No games found",
            "Adjust the current filters and try again.",
            False
        )

    def on_play_game(
        self,
        game: Game
    ):
        """Handle play game request"""
        print(
            f"Playing game: {game.title}"
        )

        success = self.game_launcher.launch_game(
            game
        )

        if not success:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to launch game: {game.title}"
            )
        else:
            self.load_games()

    def on_show_details(
        self,
        game: Game
    ):
        """Handle show details request"""
        dialog = DetailedViewWidget(
            game,
            self.game_library,
            self.game_launcher,
            confirm_delete=self.settings[
                "confirm_delete"
            ],
            minimize_on_launch=(
                self.settings[
                    "launch_behavior"
                ]
                == "Minimize library"
            ),
            parent=self
        )

        dialog.exec()
        self.load_games()

    def on_toggle_favorite(
        self,
        game: Game
    ):
        """Handle toggle favorite request"""
        if not self.game_library.update_game(
            game.id,
            game
        ):
            QMessageBox.warning(
                self,
                "Save Error",
                self.storage.last_error
                or "Could not save favorite status."
            )

        self.load_games()

    def refresh_missing_metadata(self):
        """Enrich incomplete games in background."""
        if (
            self.metadata_refresh_thread
            and self.metadata_refresh_thread.isRunning()
        ):
            return

        self.metadata_refresh_thread = QThread(
            self
        )

        self.metadata_refresh_worker = MetadataRefreshWorker(
            list(
                self.game_library.get_all_games()
            )
        )

        self.metadata_refresh_worker.moveToThread(
            self.metadata_refresh_thread
        )

        self.metadata_refresh_thread.started.connect(
            self.metadata_refresh_worker.refresh
        )

        self.metadata_refresh_worker.metadata_found.connect(
            self.apply_metadata
        )

        self.metadata_refresh_worker.finished.connect(
            self.metadata_refresh_thread.quit
        )

        self.metadata_refresh_worker.finished.connect(
            self.metadata_refresh_worker.deleteLater
        )

        self.metadata_refresh_thread.finished.connect(
            self.metadata_refresh_thread.deleteLater
        )

        self.metadata_refresh_thread.finished.connect(
            self.clear_metadata_refresh
        )

        self.metadata_refresh_thread.start()

    def apply_metadata(
        self,
        game_id,
        metadata
    ):
        """Save only previously missing fields."""
        game = self.game_library.get_game_by_id(
            game_id
        )

        if not game:
            return

        changed = False

        for field in (
            "genre",
            "description",
            "developer",
            "publisher",
            "release_date",
            "cover_path"
        ):
            value = metadata.get(
                field,
                ""
            )

            if (
                value
                and not getattr(
                    game,
                    field
                ).strip()
            ):
                setattr(
                    game,
                    field,
                    value
                )

                changed = True

        if (
            changed
            and self.game_library.update_game(
                game.id,
                game
            )
        ):
            self.load_games()

    def clear_metadata_refresh(self):
        self.metadata_refresh_thread = None
        self.metadata_refresh_worker = None

    def create_empty_state(self):
        """Create reusable empty-state panel."""
        widget = QWidget()
        widget.setObjectName(
            "emptyStateWidget"
        )

        widget.setMinimumHeight(
            260
        )

        layout = QVBoxLayout(
            widget
        )

        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.setSpacing(
            8
        )

        self.empty_state_title = QLabel()
        self.empty_state_title.setObjectName(
            "emptyStateTitle"
        )

        self.empty_state_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.empty_state_title
        )

        self.empty_state_description = QLabel()
        self.empty_state_description.setObjectName(
            "emptyStateDescription"
        )

        self.empty_state_description.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.empty_state_description.setWordWrap(
            True
        )

        layout.addWidget(
            self.empty_state_description
        )

        self.empty_state_add_button = QPushButton(
            "+ Add Game"
        )

        self.empty_state_add_button.setObjectName(
            "emptyStateAddButton"
        )

        self.empty_state_add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.empty_state_add_button.clicked.connect(
            self.show_add_game_dialog
        )

        layout.addWidget(
            self.empty_state_add_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        return widget

    @staticmethod
    def view_name_to_key(
        view_name
    ):
        return {
            "All Games": "all",
            "Favorites": "favorites",
            "Genres": "genres"
        }.get(
            view_name,
            "all"
        )

    def update_genre_filter(
        self,
        games
    ):
        """Keep genre selector synchronized."""
        selected = (
            self.genre_filter.currentText()
            or "All Genres"
        )

        genres = sorted(
            {
                game.genre.strip()
                for game in games
                if game.genre.strip()
            }
        )

        self.genre_filter.blockSignals(
            True
        )

        self.genre_filter.clear()

        self.genre_filter.addItem(
            "All Genres"
        )

        self.genre_filter.addItems(
            genres
        )

        self.genre_filter.setCurrentText(
            selected
            if selected in genres
            else "All Genres"
        )

        self.genre_filter.blockSignals(
            False
        )

    def apply_theme(self):
        """Apply the selected theme to the complete main window."""
        current_theme = self.settings.get(
            "theme",
            "Dark"
        )

        if current_theme == "Dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: white;
                }

                QWidget#centralWidget,
                QWidget#contentWidget,
                QWidget#gamesScrollWidget {
                    background-color: #1e1e1e;
                    color: white;
                }

                QWidget#sidebar {
                    background-color: #2d2d2d;
                }

                QPushButton#sidebarButton {
                    background-color: #383838;
                    color: white;
                    border: 1px solid #4a4a4a;
                    border-radius: 5px;
                    text-align: left;
                    padding: 10px;
                    font-size: 14px;
                }

                QPushButton#sidebarButton:hover {
                    background-color: #4a4a4a;
                    color: white;
                    border: 1px solid #666666;
                }

                QLineEdit,
                QComboBox {
                    background-color: #333333;
                    color: white;
                    border: 1px solid #555555;
                    padding: 4px;
                }

                QComboBox QAbstractItemView {
                    background-color: #333333;
                    color: white;
                    selection-background-color: #555555;
                    selection-color: white;
                }

                QScrollArea {
                    background-color: #1e1e1e;
                    border: none;
                }

                QWidget#emptyStateWidget {
                    background-color: transparent;
                }

                QLabel#headerTitle {
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }

                QLabel#emptyStateTitle {
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }

                QLabel#emptyStateDescription {
                    color: #aaaaaa;
                    font-size: 14px;
                }

                QPushButton#addGameButton,
                QPushButton#emptyStateAddButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }

                QPushButton#addGameButton:hover,
                QPushButton#emptyStateAddButton:hover {
                    background-color: #45a049;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                    color: #222222;
                }

                QWidget#centralWidget,
                QWidget#contentWidget,
                QWidget#gamesScrollWidget {
                    background-color: #f5f5f5;
                    color: #222222;
                }

                QWidget#sidebar {
                    background-color: #e8e8e8;
                }

                QPushButton#sidebarButton {
                    background-color: #ffffff;
                    color: #222222;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    text-align: left;
                    padding: 10px;
                    font-size: 14px;
                }

                QPushButton#sidebarButton:hover {
                    background-color: #dcdcdc;
                    color: #111111;
                    border: 1px solid #aaaaaa;
                }

                QLineEdit,
                QComboBox {
                    background-color: white;
                    color: #222222;
                    border: 1px solid #bbbbbb;
                    padding: 4px;
                }

                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #222222;
                    selection-background-color: #dcdcdc;
                    selection-color: #222222;
                }

                QScrollArea {
                    background-color: #f5f5f5;
                    border: none;
                }

                QWidget#emptyStateWidget {
                    background-color: transparent;
                }

                QLabel#headerTitle {
                    color: #222222;
                    font-size: 18px;
                    font-weight: bold;
                }

                QLabel#emptyStateTitle {
                    color: #222222;
                    font-size: 20px;
                    font-weight: bold;
                }

                QLabel#emptyStateDescription {
                    color: #666666;
                    font-size: 14px;
                }

                QPushButton#addGameButton,
                QPushButton#emptyStateAddButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }

                QPushButton#addGameButton:hover,
                QPushButton#emptyStateAddButton:hover {
                    background-color: #45a049;
                    color: white;
                }
            """)

        for i in range(
            self.games_grid.count()
        ):
            item = self.games_grid.itemAt(
                i
            )

            if item is not None:
                widget = item.widget()

                if isinstance(
                    widget,
                    GameCard
                ):
                    widget.apply_theme(
                        current_theme
                    )