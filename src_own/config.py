"""Quản lý cấu hình game (đọc/ghi từ JSON) và giao diện cài đặt (GUI) bằng Tkinter.

Last Modified: 2026-05-13
"""

import json
import os
from res_path import writable_path

CONFIG_FILE = writable_path('config.json')

DEFAULT_CONFIG = {
    "ship_acceleration": 0.27,
    "ship_max_velocity": 10.0,
    "ship_turn_angle": 6.5,
    "ship_bullet_velocity": 18.0,
    "ship_max_bullets": 100,
    "start_lives": 5,
    "start_rocks": 15,
    "saucer_max_count": 4,
    "saucer_fire_delay_large": 30,
    "saucer_fire_delay_medium": 25,
    "saucer_fire_delay_hard": 25,
    "saucer_velocity_large": 3.5,
    "saucer_velocity_medium": 4.0,
    "saucer_velocity_hard": 4.5,
    "rock_vel_large": 3.5,
    "rock_vel_medium": 4.0,
    "rock_vel_small": 5.0,
    "rock_vel_tiny": 6.0,
    "rock_scale_large": 1.8,
    "rock_scale_medium": 1.2,
    "rock_scale_small": 0.6,
    "rock_scale_tiny": 0.3
}

def load_config():
    """Đọc cấu hình từ file JSON. Nếu không có hoặc lỗi, trả về mặc định.
    
    Returns:
        Dict cấu hình đang sử dụng.

    Last Modified: 2026-05-13
    """
    if not os.path.exists(CONFIG_FILE):
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(data)
            return cfg
    except (json.JSONDecodeError, KeyError, TypeError):
        return dict(DEFAULT_CONFIG)

def save_config(cfg):
    """Ghi cấu hình ra file JSON.
    
    Args:
        cfg: Dict chứa cấu hình cần lưu.

    Last Modified: 2026-05-13
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

def show_settings_gui(on_close_callback=None):
    """Mở cửa sổ Tkinter để chỉnh sửa cấu hình trực quan.
    
    Args:
        on_close_callback: Hàm gọi lại khi cửa sổ đóng.

    Last Modified: 2026-05-13
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    cfg = load_config()
    
    root = tk.Tk()
    root.title("Asteroids Settings")
    root.geometry("450x450")
    root.resizable(False, False)
    root.configure(bg="black")
    
    root.attributes('-topmost', True)
    root.focus_force()

    style = ttk.Style()
    style.theme_use('default')
    
    bg_color = "black"
    fg_color = "#33FF33"
    
    style.configure(".", background=bg_color, foreground=fg_color, font=("Courier", 11, "bold"))
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.configure("TFrame", background=bg_color)
    style.configure("TButton", background="#111111", foreground=fg_color, borderwidth=2, font=("Courier", 10, "bold"))
    style.map("TButton", background=[("active", "#225522")])
    style.configure("TNotebook", background=bg_color, borderwidth=0)
    style.configure("TNotebook.Tab", background="#111111", foreground=fg_color, padding=[10, 5], borderwidth=1)
    style.map("TNotebook.Tab", background=[("selected", "#225522")])
    style.configure("TEntry", fieldbackground="#111111", foreground=fg_color, insertcolor=fg_color, borderwidth=1)

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="GAME SETTINGS", font=("Courier", 18, "bold"), foreground="#FFFFFF").pack(pady=(0, 10))

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    f_ship = ttk.Frame(notebook, padding="10")
    f_saucer = ttk.Frame(notebook, padding="10")
    f_rock = ttk.Frame(notebook, padding="10")

    notebook.add(f_ship, text="Ship & General")
    notebook.add(f_saucer, text="Saucers")
    notebook.add(f_rock, text="Asteroids")

    entries = {}

    def add_fields(parent, config_dict):
        """Thêm các trường nhập liệu vào giao diện cài đặt.
        
        Args:
            parent: Giao diện cha chứa trường nhập.
            config_dict: Cấu hình mặc định.

        Last Modified: 2026-05-13
        """
        row = 0
        for key, label_text in config_dict.items():
            ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(cfg[key]))
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.E, padx=10, pady=5)
            entries[key] = var
            row += 1

    add_fields(f_ship, {
        "ship_acceleration": "Ship Acceleration (0.27):",
        "ship_max_velocity": "Ship Max Speed (10.0):",
        "ship_turn_angle": "Ship Turn Angle (6.5):",
        "ship_bullet_velocity": "Bullet Speed (18.0):",
        "ship_max_bullets": "Max Bullets (100):",
        "start_lives": "Starting Lives (5):",
        "start_rocks": "Starting Asteroids (15):"
    })

    add_fields(f_saucer, {
        "saucer_max_count": "Max Saucers on Screen (4):",
        "saucer_fire_delay_large": "Large Saucer Fire Delay (30):",
        "saucer_fire_delay_medium": "Medium Saucer Fire Delay (25):",
        "saucer_fire_delay_hard": "Hard Saucer Fire Delay (25):",
        "saucer_velocity_large": "Large Saucer Speed (3.5):",
        "saucer_velocity_medium": "Medium Saucer Speed (4.0):",
        "saucer_velocity_hard": "Hard Saucer Speed (4.5):"
    })

    add_fields(f_rock, {
        "rock_vel_large": "Large Asteroid Speed (3.5):",
        "rock_vel_medium": "Medium Asteroid Speed (4.0):",
        "rock_vel_small": "Small Asteroid Speed (5.0):",
        "rock_vel_tiny": "Tiny Asteroid Speed (6.0):",
        "rock_scale_large": "Large Asteroid Size (1.8):",
        "rock_scale_medium": "Medium Asteroid Size (1.2):",
        "rock_scale_small": "Small Asteroid Size (0.6):",
        "rock_scale_tiny": "Tiny Asteroid Size (0.3):"
    })

    def save_and_close():
        """Lưu lại thay đổi cấu hình và đóng cửa sổ giao diện.

        Last Modified: 2026-05-13
        """
        new_cfg = {}
        try:
            for k in ["ship_max_bullets", "start_lives", "start_rocks", "saucer_max_count", 
                      "saucer_fire_delay_large", "saucer_fire_delay_medium", "saucer_fire_delay_hard"]:
                new_cfg[k] = int(entries[k].get())
            
            for k in ["ship_acceleration", "ship_max_velocity", "ship_turn_angle", "ship_bullet_velocity",
                      "saucer_velocity_large", "saucer_velocity_medium", "saucer_velocity_hard",
                      "rock_vel_large", "rock_vel_medium", "rock_vel_small", "rock_vel_tiny",
                      "rock_scale_large", "rock_scale_medium", "rock_scale_small", "rock_scale_tiny"]:
                new_cfg[k] = float(entries[k].get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return

        save_config(new_cfg)
        root.destroy()
        if on_close_callback:
            on_close_callback()

    def reset_defaults():
        """Khôi phục lại các giá trị cấu hình mặc định.

        Last Modified: 2026-05-13
        """
        for key, val in DEFAULT_CONFIG.items():
            entries[key].set(str(val))

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(15, 0))

    ttk.Button(btn_frame, text="Reset Defaults", command=reset_defaults).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Save & Close", command=save_and_close).pack(side=tk.RIGHT, padx=5)

    def on_closing():
        """Xử lý sự kiện khi đóng cửa sổ cài đặt.

        Last Modified: 2026-05-13
        """
        root.destroy()
        if on_close_callback:
            on_close_callback()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    show_settings_gui()
