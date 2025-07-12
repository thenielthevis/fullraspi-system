import tkinter as tk
from PIL import Image, ImageTk
import os

class EndScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="GAME OVER",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")
        subtitle = tk.Label(
            self,
            text="SCAN RFID TO SAVE POINTS",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.35, anchor="center")
        score_label = tk.Label(
            self,
            text="TOTAL SCORE: [SIMULATED SCORE]",
            font=("Press Start 2P", 14),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        score_label.place(relx=0.5, rely=0.45, anchor="center")
        save_button = tk.Button(
            self,
            text="SAVE POINTS",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.save_points
        )
        save_button.place(relx=0.5, rely=0.55, anchor="center")
        claim_button = tk.Button(
            self,
            text="CLAIM REWARDS",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=lambda: self.controller.show_frame("RewardsScreen")
        )
        claim_button.place(relx=0.5, rely=0.65, anchor="center")
        back_button = tk.Button(
            self,
            text="BACK",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=lambda: self.controller.show_frame("WelcomeScreen")
        )
        back_button.place(relx=0.5, rely=0.75, anchor="center")

    def save_points(self):
        print("[Simulated] Points saved to RFID.")