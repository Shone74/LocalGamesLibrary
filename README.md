# Local Game Library

A Windows desktop application for managing and launching your locally installed PC games.

## Features

- Add any PC game via .exe file
- Automatically remembers game locations
- Automatically identify basic game details from an executable
- Enrich title, genre, description, developer, publisher, release date, and cover through Steam when available
- Add games immediately while offline; incomplete metadata is retried on a later application start
- Edit game details or add cover images manually at any time
- Modern game library display
- Search and filter games
- Mark favorite games
- Launch games directly from the application
- Track play count and last played time
- Edit game details
- Remove games from library
- Detailed game view
- Settings for customization
- Modern dark theme UI
- Packaged as .exe for easy distribution

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   pip install -r requirements.txt

## Usage

1. Run the application:
   python main.py

2. Click "+ Add Game" to add your first game
3. Browse to select the game's .exe file
4. Review the automatically detected details, or enter them manually
5. Click "Add Game"
6. Your game will appear in the library
7. Click "PLAY" to launch the game
8. Use the sidebar to navigate between views
9. Use the search bar to find specific games

## Project Structure

- main.py: Application entry point
- models/: Data models
- storage/: Data storage implementations
- services/: Business logic services
- ui/: User interface components
- data/: Application data files
- assets/: Images and other assets

## Requirements

- Python 3.8+
- PySide6

## Building Executable

To create a standalone executable:

1. Install PyInstaller:
   pip install pyinstaller

2. Create executable:
   pyinstaller --onefile --windowed main.py

The executable will be created in the dist/ directory.
