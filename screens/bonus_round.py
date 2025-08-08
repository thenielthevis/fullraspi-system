import tkinter as tk
from PIL import Image, ImageTk
import os

class BonusRoundScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Get screen dimensions for responsive background
        self.update_idletasks()
        screen_width = controller.winfo_screenwidth()
        screen_height = controller.winfo_screenheight()
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="BONUS ROUND",
            font=("Press Start 2P", 32),  # Increased from 25
            fg="#00ffff",
            bg="#000000",
            pady=30  # Increased from 20
        )
        title.place(relx=0.5, rely=0.15, anchor="center")  # Moved up
        subtitle = tk.Label(
            self,
            text="USE JOYSTICK TO SPIN!",
            font=("Press Start 2P", 16),  # Increased from 12
            fg="#ffffff",
            bg="#000000",
            pady=15  # Increased from 10
        )
        subtitle.place(relx=0.5, rely=0.35, anchor="center")
        spin_button = tk.Button(
            self,
            text="SPIN LEDS",
            font=("Press Start 2P", 20),  # Increased from 15
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=40,  # Increased from 30
            pady=15,  # Increased from 10
            command=self.spin_leds
        )
        spin_button.place(relx=0.5, rely=0.6, anchor="center")  # Adjusted from 0.5
        complete_button = tk.Button(
            self,
            text="COMPLETE BONUS",
            font=("Press Start 2P", 20),  # Increased from 15
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=40,  # Increased from 30
            pady=15,  # Increased from 10
            command=self.complete_bonus
        )
        complete_button.place(relx=0.5, rely=0.75, anchor="center")  # Adjusted from 0.6
        footer = tk.Label(
            self,
            text="POINTS SAVED TO RFID",
            font=("Press Start 2P", 14),  # Increased from 10
            fg="#ffffff",
            bg="#000000",
            pady=8  # Increased from 5
        )
        footer.place(relx=0.5, rely=0.95, anchor="center")  # Adjusted from 0.9

    def spin_leds(self):
        print("[Simulated] LEDs spinning!")

    def complete_bonus(self):
        print("[Simulated] Bonus round complete.")
        self.controller.show_frame("EndScreen")