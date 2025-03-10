import os
import sys
import requests
import hashlib

def get_executable_dir():
    """Get the directory where the executable/script is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def download_template():
    """Download the template image if it doesn't exist or is corrupted"""
    template_url = "https://raw.githubusercontent.com/cupofteame/PhantomForcesAimbot/refs/heads/master/src/enemyIndic3.png"
    template_path = os.path.join(get_executable_dir(), "enemyIndic3.png")
    
    try:
        # Check if file exists and is valid
        if os.path.exists(template_path):
            print("Template image found, verifying...")
            return True
            
        print("Downloading template image...")
        response = requests.get(template_url)
        
        if response.status_code == 200:
            with open(template_path, 'wb') as f:
                f.write(response.content)
            print("Template image downloaded successfully!")
            return True
        else:
            print(f"Error downloading template: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading template: {str(e)}")
        return False

if __name__ == "__main__":
    download_template() 