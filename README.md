# Phantom Forces CV

A computer vision-based tool for Phantom Forces with a GUI interface. Credit to [manuroger112](https://github.com/manuroger112) for the idea and base! Check out their video on it [here!](https://www.youtube.com/watch?v=L2Mgs4MtA0k) Feel free to fork, open issues, and open pull requests.

## Notes

- When running the executable, make sure to run it as administrator
- Ensure you have the correct screen resolution set
- Adjust sensitivity settings to match your in-game configuration

## Requirements

- Python 3.8 or higher
- Windows 10 (uses Win32 API)
- 1920x1080 resolution (default, configurable)

## Keybinds
Default keybinds:
- Aim: Right Mouse Button (configurable) with hex codes

You can ignore the below information if you download files from the downloads and are a regular user!

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Building Executable

You can build a standalone executable this method:

### Method 1: Using build script
1. Run the build script:
```bash
python build.py
```

The executable will be created in the `dist` folder.

## Dependencies

- numpy: Numerical computations
- opencv-python: Computer vision processing
- mss: Screen capture
- pywin32: Windows API interface
- keyboard: Key event handling
- tkinter: GUI framework (included with Python)
- pyinstaller: For creating executable
