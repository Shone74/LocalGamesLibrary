from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QFormLayout
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)

        self.settings = settings or {}

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 300)

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(
            self.settings.get("theme", "Dark")
        )

        appearance_layout.addRow(
            "Theme: ",
            self.theme_combo
        )

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # Library settings
        library_group = QGroupBox("Library")
        library_layout = QFormLayout()

        self.default_view_combo = QComboBox()
        self.default_view_combo.addItems(
            ["All Games", "Favorites", "Genres"]
        )

        self.default_view_combo.setCurrentText(
            self.settings.get(
                "default_view",
                "All Games"
            )
        )

        library_layout.addRow(
            "Default View: ",
            self.default_view_combo
        )

        library_group.setLayout(library_layout)
        layout.addWidget(library_group)

        # Behavior settings
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.confirm_delete_checkbox = QCheckBox(
            "Confirm game deletion"
        )

        self.confirm_delete_checkbox.setChecked(
            self.settings.get(
                "confirm_delete",
                True
            )
        )

        behavior_layout.addWidget(
            self.confirm_delete_checkbox
        )

        self.launch_behavior_combo = QComboBox()
        self.launch_behavior_combo.addItems(
            [
                "Minimize library",
                "Keep library open"
            ]
        )

        self.launch_behavior_combo.setCurrentText(
            self.settings.get(
                "launch_behavior",
                "Keep library open"
            )
        )

        behavior_layout.addWidget(
            QLabel("Launch behavior: ")
        )

        behavior_layout.addWidget(
            self.launch_behavior_combo
        )

        behavior_group.setLayout(
            behavior_layout
        )

        layout.addWidget(
            behavior_group
        )

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(
            self.reject
        )

        buttons_layout.addWidget(
            cancel_btn
        )

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(
            self.accept
        )

        buttons_layout.addWidget(
            save_btn
        )

        layout.addLayout(
            buttons_layout
        )

        self.apply_dialog_theme()

    def apply_dialog_theme(self):
        """Apply a readable theme to the settings dialog."""
        theme = self.settings.get(
            "theme",
            "Dark"
        )

        if theme == "Dark":
            self.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                    color: white;
                }

                QLabel {
                    color: white;
                }

                QGroupBox {
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }

                QGroupBox::title {
                    color: white;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }

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

                QCheckBox {
                    color: white;
                }

                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: 1px solid #555555;
                    padding: 6px 12px;
                    border-radius: 4px;
                }

                QPushButton:hover {
                    background-color: #444444;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    color: #222222;
                }

                QLabel {
                    color: #222222;
                }

                QGroupBox {
                    color: #222222;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }

                QGroupBox::title {
                    color: #222222;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }

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

                QCheckBox {
                    color: #222222;
                }

                QPushButton {
                    background-color: #e8e8e8;
                    color: #222222;
                    border: 1px solid #bbbbbb;
                    padding: 6px 12px;
                    border-radius: 4px;
                }

                QPushButton:hover {
                    background-color: #d8d8d8;
                }
            """)

    def get_settings(self):
        """Return the selected preferences in the storage format."""
        return {
            "theme": self.theme_combo.currentText(),
            "default_view": self.default_view_combo.currentText(),
            "confirm_delete": self.confirm_delete_checkbox.isChecked(),
            "launch_behavior": self.launch_behavior_combo.currentText(),
        }