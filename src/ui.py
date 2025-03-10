import tkinter as tk
from tkinter import ttk, messagebox
import json
from config import CONFIG
import win32api
import threading
import time
import sys

class ConfigUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aimbot Configuration")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        
        # Add close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Flag to signal program termination
        self.should_exit = False
        
        # Apply theme
        self.style = ttk.Style()
        self.apply_theme()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.create_sensitivity_tab()
        self.create_aimbot_tab()
        self.create_screen_tab()
        self.create_keybinds_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.pack(side='bottom', fill='x', padx=5, pady=5)
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_status)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def apply_theme(self):
        if CONFIG.config["theme"] == "dark":
            # Configure dark theme colors
            bg_color = '#2b2b2b'
            fg_color = 'white'
            entry_bg = '#333333'
            button_bg = '#404040'
            
            self.root.configure(bg=bg_color)
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("Dark.TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=button_bg, foreground=fg_color)
            self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook.Tab", background=button_bg, foreground=fg_color)
            
            # Configure Entry widget colors
            self.root.option_add("*Entry.Background", entry_bg)
            self.root.option_add("*Entry.Foreground", fg_color)
            
            # Configure Canvas default background
            self.root.option_add("*Canvas.Background", bg_color)
            
        else:
            # Configure light theme colors
            bg_color = '#f0f0f0'
            fg_color = 'black'
            entry_bg = 'white'
            button_bg = '#e0e0e0'
            
            self.root.configure(bg=bg_color)
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("Light.TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=button_bg, foreground=fg_color)
            self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook.Tab", background=button_bg, foreground=fg_color)
            
            # Configure Entry widget colors
            self.root.option_add("*Entry.Background", entry_bg)
            self.root.option_add("*Entry.Foreground", fg_color)
            
            # Configure Canvas default background
            self.root.option_add("*Canvas.Background", bg_color)
    
    def create_sensitivity_tab(self):
        sens_frame = ttk.Frame(self.notebook)
        self.notebook.add(sens_frame, text='Sensitivity')
        
        # Roblox Sensitivity
        ttk.Label(sens_frame, text="Roblox Sensitivity:").pack(pady=5)
        roblox_sens = ttk.Entry(sens_frame)
        roblox_sens.insert(0, str(CONFIG.config["roblox_sensitivity"]))
        roblox_sens.pack(pady=5)
        
        # PF Mouse Sensitivity
        ttk.Label(sens_frame, text="PF Mouse Sensitivity:").pack(pady=5)
        pf_mouse_sens = ttk.Entry(sens_frame)
        pf_mouse_sens.insert(0, str(CONFIG.config["pf_mouse_sensitivity"]))
        pf_mouse_sens.pack(pady=5)
        
        # PF Aim Sensitivity
        ttk.Label(sens_frame, text="PF Aim Sensitivity:").pack(pady=5)
        pf_aim_sens = ttk.Entry(sens_frame)
        pf_aim_sens.insert(0, str(CONFIG.config["pf_aim_sensitivity"]))
        pf_aim_sens.pack(pady=5)
        
        # Movement Compensation
        ttk.Label(sens_frame, text="Movement Compensation:").pack(pady=5)
        move_comp = ttk.Entry(sens_frame)
        move_comp.insert(0, str(CONFIG.config["movement_compensation"]))
        move_comp.pack(pady=5)
        
        # Apply Button
        def apply_sensitivity():
            try:
                roblox = float(roblox_sens.get())
                mouse = float(pf_mouse_sens.get())
                aim = float(pf_aim_sens.get())
                comp = float(move_comp.get())
                
                self.update_config("roblox_sensitivity", roblox)
                self.update_config("pf_mouse_sensitivity", mouse)
                self.update_config("pf_aim_sensitivity", aim)
                self.update_config("movement_compensation", comp)
                
                self.status_var.set("Sensitivity settings updated successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for sensitivity values")
        
        ttk.Button(sens_frame, text="Apply", command=apply_sensitivity).pack(pady=20)
    
    def create_aimbot_tab(self):
        aim_frame = ttk.Frame(self.notebook)
        self.notebook.add(aim_frame, text='Aimbot')
        
        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(aim_frame, bg='#2b2b2b' if CONFIG.config["theme"] == "dark" else '#f0f0f0')
        scrollbar = ttk.Scrollbar(aim_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame' if CONFIG.config["theme"] == "dark" else 'Light.TFrame')

        # Configure canvas background
        if CONFIG.config["theme"] == "dark":
            canvas.configure(bg='#2b2b2b')
        else:
            canvas.configure(bg='#f0f0f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create the scrolled window with proper width
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)  # Fixed width slightly less than window width

        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to update inner frame width
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_frame, width=e.width - 20)  # Leave space for scrollbar
        canvas.bind('<Configure>', on_canvas_configure)

        # Create a container frame for content with padding
        content_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame' if CONFIG.config["theme"] == "dark" else 'Light.TFrame')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Auto Shoot
        auto_shoot_var = tk.BooleanVar(value=CONFIG.config["auto_shoot_enabled"])
        auto_shoot = ttk.Checkbutton(content_frame, text="Auto Shoot Enabled",
                                   variable=auto_shoot_var,
                                   command=lambda: self.update_config("auto_shoot_enabled", auto_shoot_var.get()))
        auto_shoot.pack(pady=10)
        
        # Match Threshold
        ttk.Label(content_frame, text="Match Threshold:").pack(pady=5)
        match_threshold = ttk.Entry(content_frame)
        match_threshold.insert(0, str(CONFIG.config["match_threshold"]))
        match_threshold.pack(pady=5)

        # Smoothing Settings Section
        ttk.Label(content_frame, text="Smoothing Settings", font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Smoothing Factor
        ttk.Label(content_frame, text="Smoothing Factor (0.0-1.0):").pack(pady=5)
        smoothing_factor = ttk.Entry(content_frame)
        smoothing_factor.insert(0, str(CONFIG.config["smoothing_factor"]))
        smoothing_factor.pack(pady=5)
        
        # Acceleration Cap
        ttk.Label(content_frame, text="Acceleration Cap:").pack(pady=5)
        acceleration_cap = ttk.Entry(content_frame)
        acceleration_cap.insert(0, str(CONFIG.config["acceleration_cap"]))
        acceleration_cap.pack(pady=5)
        
        # Min Movement Threshold
        ttk.Label(content_frame, text="Minimum Movement Threshold:").pack(pady=5)
        min_movement = ttk.Entry(content_frame)
        min_movement.insert(0, str(CONFIG.config["min_movement_threshold"]))
        min_movement.pack(pady=5)
        
        # Prediction Settings Section
        ttk.Label(content_frame, text="Prediction Settings", font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        pred_var = tk.BooleanVar(value=CONFIG.config["prediction_enabled"])
        prediction = ttk.Checkbutton(content_frame, text="Prediction Enabled",
                                   variable=pred_var,
                                   command=lambda: self.update_config("prediction_enabled", pred_var.get()))
        prediction.pack(pady=10)
        
        ttk.Label(content_frame, text="Prediction Strength:").pack(pady=5)
        pred_strength = ttk.Entry(content_frame)
        pred_strength.insert(0, str(CONFIG.config["prediction_strength"]))
        pred_strength.pack(pady=5)
        
        # Apply Button
        def apply_aimbot():
            try:
                threshold = float(match_threshold.get())
                strength = float(pred_strength.get())
                smooth = float(smoothing_factor.get())
                accel = float(acceleration_cap.get())
                min_move = float(min_movement.get())
                
                if not (0 <= threshold <= 1):
                    raise ValueError("Match threshold must be between 0 and 1")
                if not (0 <= strength <= 1):
                    raise ValueError("Prediction strength must be between 0 and 1")
                if not (0 <= smooth <= 1):
                    raise ValueError("Smoothing factor must be between 0 and 1")
                if accel <= 0:
                    raise ValueError("Acceleration cap must be positive")
                if min_move < 0:
                    raise ValueError("Minimum movement threshold cannot be negative")
                
                self.update_config("match_threshold", threshold)
                self.update_config("prediction_strength", strength)
                self.update_config("smoothing_factor", smooth)
                self.update_config("acceleration_cap", accel)
                self.update_config("min_movement_threshold", min_move)
                
                self.status_var.set("Aimbot settings updated successfully")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(content_frame, text="Apply", command=apply_aimbot).pack(pady=20)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
    
    def create_screen_tab(self):
        screen_frame = ttk.Frame(self.notebook)
        self.notebook.add(screen_frame, text='Screen')
        
        # Screen Width
        ttk.Label(screen_frame, text="Screen Width:").pack(pady=5)
        width_entry = ttk.Entry(screen_frame)
        width_entry.insert(0, str(CONFIG.config["screen_width"]))
        width_entry.pack(pady=5)
        
        # Screen Height
        ttk.Label(screen_frame, text="Screen Height:").pack(pady=5)
        height_entry = ttk.Entry(screen_frame)
        height_entry.insert(0, str(CONFIG.config["screen_height"]))
        height_entry.pack(pady=5)
        
        # Capture Size
        ttk.Label(screen_frame, text="Capture Size:").pack(pady=5)
        capture_entry = ttk.Entry(screen_frame)
        capture_entry.insert(0, str(CONFIG.config["capture_size"]))
        capture_entry.pack(pady=5)
        
        # Apply Button
        def apply_screen():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                capture = int(capture_entry.get())
                
                if width <= 0 or height <= 0 or capture <= 0:
                    raise ValueError("All values must be positive")
                
                self.update_config("screen_width", width)
                self.update_config("screen_height", height)
                self.update_config("capture_size", capture)
                
                self.status_var.set("Screen settings updated successfully")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(screen_frame, text="Apply", command=apply_screen).pack(pady=20)
    
    def create_keybinds_tab(self):
        key_frame = ttk.Frame(self.notebook)
        self.notebook.add(key_frame, text='Keybinds')
        
        # Aim Key
        ttk.Label(key_frame, text="Aim Key (hex):").pack(pady=5)
        aim_key = ttk.Entry(key_frame)
        aim_key.insert(0, CONFIG.config["aim_key"])
        aim_key.pack(pady=5)
        
        # Help text
        help_text = """
        Common key codes:
        - Left Mouse: 0x01
        - Right Mouse: 0x02
        - Middle Mouse: 0x04
        - 1-9 Keys: 0x31-0x39
        - A-Z Keys: 0x41-0x5A
        """
        ttk.Label(key_frame, text=help_text, justify=tk.LEFT).pack(pady=10)
        
        # Apply Button
        def apply_keys():
            try:
                aim_val = aim_key.get()
                
                # Validate hex value
                int(aim_val, 16)
                
                self.update_config("aim_key", aim_val)
                self.status_var.set("Keybind updated successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid hexadecimal value (e.g., 0x02)")
        
        ttk.Button(key_frame, text="Apply", command=apply_keys).pack(pady=20)
    
    def update_config(self, key, value):
        if CONFIG.update_setting(key, value):
            self.status_var.set(f"Updated {key} to {value}")
        else:
            self.status_var.set(f"Error updating {key}")
    
    def monitor_status(self):
        while self.running:
            try:
                if win32api.GetAsyncKeyState(int(CONFIG.config["aim_key"], 16)) & 0x8000:
                    self.status_var.set("Aiming...")
                else:
                    self.status_var.set("Ready")
                time.sleep(0.1)
            except Exception as e:
                self.status_var.set(f"Error monitoring keys: {str(e)}")
                time.sleep(1)
    
    def on_closing(self):
        """Handle window closing event"""
        self.running = False
        self.should_exit = True
        self.root.quit()  # Use quit() instead of destroy()
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.running = False
            self.should_exit = True

if __name__ == "__main__":
    app = ConfigUI()
    app.run() 