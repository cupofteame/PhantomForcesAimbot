# Phantom Forces Vision Assistant

A computer vision-based assistance tool for Phantom Forces with a configurable GUI interface.

## Features

- Real-time screen analysis using OpenCV
- Customizable sensitivity settings
- Prediction system for moving targets
- User-friendly GUI for configuration
- Dark/Light theme support
- Configurable keybinds
- Performance optimization settings

## Requirements

- Python 3.8 or higher
- Windows 10 (uses Win32 API)
- 1920x1080 resolution (default, configurable)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Building Executable

You can build a standalone executable using one of these methods:

### Method 1: Using build script
1. Run the build script:
```bash
python build.py
```
2. Find the executable in the `dist` folder

### Method 2: Manual PyInstaller command
```bash
pyinstaller --onefile --noconsole --name=PhantomForcesAssist --add-data "src/enemyIndic3.png;." src/phantomforcesaim.py
```

The executable will be created in the `dist` folder.

## Configuration

The tool includes a GUI configuration panel with the following sections:

### Sensitivity Settings
- Roblox Sensitivity
- PF Mouse Sensitivity
- PF Aim Sensitivity
- Movement Compensation

### Screen Settings
- Screen Resolution
- Capture Size
- Performance Options

### Keybinds
Default keybinds:
- Exit: '6' key (configurable)
- Aim: Right Mouse Button (configurable)

## File Structure

```
├── src/
│   ├── phantomforcesaim.py  # Main logic
│   ├── config.py            # Configuration management
│   └── ui.py               # GUI interface
├── build.py                # Build script for executable
├── requirements.txt
└── README.md
```

## Usage

### Running from Source
```bash
python src/phantomforcesaim.py
```

### Running Executable
1. Double-click the executable in the `dist` folder
2. Use the GUI to configure settings
3. Use configured keybinds to control the tool

## Configuration File

Settings are stored in `aimbot_config.json` and can be modified through the GUI or manually.

## Notes

- Ensure you have the correct screen resolution set
- Adjust sensitivity settings to match your in-game configuration
- The tool requires template images for vision processing
- When running the executable, make sure to run it as administrator

## Dependencies

- numpy: Numerical computations
- opencv-python: Computer vision processing
- mss: Screen capture
- pywin32: Windows API interface
- keyboard: Key event handling
- tkinter: GUI framework (included with Python)
- pyinstaller: For creating executable

## Development

The project uses:
- Python's built-in threading for performance
- JSON for configuration storage
- Win32 API for system interaction
- OpenCV for image processing
