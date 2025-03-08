import json
import os

DEFAULT_CONFIG = {
    # Screen settings
    "screen_width": 1920,
    "screen_height": 1080,
    "capture_size": 240,
    
    # Sensitivity settings
    "roblox_sensitivity": 0.84,
    "pf_mouse_sensitivity": 0.456,
    "pf_aim_sensitivity": 0.648,
    "movement_compensation": 0.2,
    
    # Aimbot settings
    "auto_shoot_enabled": False,
    "match_threshold": 0.85,
    "min_consecutive_matches": 2,
    
    # Prediction settings
    "prediction_enabled": True,
    "prediction_strength": 0.5,
    
    # Performance settings
    "target_fps": 60,
    
    # Keybinds
    "aim_key": "0x02",  # Default: Right mouse button
    
    # UI Theme
    "theme": "dark"  # or "light"
}

class Configuration:
    def __init__(self):
        self.config_file = "aimbot_config.json"
        self.load_config()
        self._calculate_derived_values()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update default config with loaded values
                    self.config = DEFAULT_CONFIG.copy()
                    self.config.update(loaded_config)
            else:
                self.config = DEFAULT_CONFIG.copy()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = DEFAULT_CONFIG.copy()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _calculate_derived_values(self):
        # Screen calculations
        self.center_x = self.config["screen_width"] // 2
        self.center_y = self.config["screen_height"] // 2
        self.crosshair_uniform = self.config["capture_size"] // 2
        self.capture_left = self.center_x - self.crosshair_uniform
        self.capture_top = self.center_y - self.crosshair_uniform
        
        # Region for capture
        self.region = {
            "top": self.capture_top,
            "left": self.capture_left,
            "width": self.config["capture_size"],
            "height": self.config["capture_size"]
        }
        
        # Sensitivity calculations
        pf_sensitivity = (self.config["pf_mouse_sensitivity"] * 
                        self.config["pf_aim_sensitivity"])
        self.final_sensitivity = ((self.config["roblox_sensitivity"] * 
                                 pf_sensitivity) / 0.55) + self.config["movement_compensation"]
    
    def update_setting(self, key, value):
        if key in self.config:
            self.config[key] = value
            self._calculate_derived_values()
            self.save_config()
            return True
        return False

# Create global config instance
CONFIG = Configuration() 