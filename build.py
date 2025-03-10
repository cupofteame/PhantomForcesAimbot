import PyInstaller.__main__
import os
import shutil

def build_exe():
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("PhantomForcesAssist.spec"):
        os.remove("PhantomForcesAssist.spec")
    
    # PyInstaller configuration
    PyInstaller.__main__.run([
        'src/phantomforcesaim.py',  # Your main script
        '--onefile',  # Create a single executable
        '--noconsole',  # Don't show console window
        '--name=PhantomForcesAssist',  # Name of the executable
        '--hidden-import=tkinter',
        '--hidden-import=json',
        '--hidden-import=numpy',
        '--hidden-import=cv2',
        '--hidden-import=mss',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32gui',
        '--hidden-import=requests',
        '--clean',  # Clean PyInstaller cache
        '--uac-admin',  # Request admin privileges
    ])
    
    print("Build completed! Executable is in the dist folder.")
    print("\nNOTE: When distributing the executable:")
    print("1. The config file will be created automatically on first run")
    print("2. The template image will be downloaded automatically on first run")
    print("3. Run the executable as administrator for proper functionality")

if __name__ == "__main__":
    print("Starting build process...")
    build_exe() 