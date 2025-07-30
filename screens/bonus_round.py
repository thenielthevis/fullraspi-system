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
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")
        subtitle = tk.Label(
            self,
            text="USE JOYSTICK TO SPIN!",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.35, anchor="center")
        spin_button = tk.Button(
            self,
            text="SPIN LEDS",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.spin_leds
        )
        spin_button.place(relx=0.5, rely=0.5, anchor="center")
        complete_button = tk.Button(
            self,
            text="COMPLETE BONUS",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.complete_bonus
        )
        complete_button.place(relx=0.5, rely=0.6, anchor="center")
        footer = tk.Label(
            self,
            text="POINTS SAVED TO RFID",
            font=("Press Start 2P", 10),
            fg="#ffffff",
            bg="#000000",
            pady=5
        )
        footer.place(relx=0.5, rely=0.9, anchor="center")

    def spin_leds(self):
        print("[Simulated] LEDs spinning!")

    def complete_bonus(self):
        print("[Simulated] Bonus round complete.")
        self.controller.show_frame("EndScreen")