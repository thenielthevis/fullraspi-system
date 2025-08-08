import tkinter as tk
from PIL import Image, ImageTk
import os

class RewardsScreen(tk.Frame):
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
            text="REDEEM YOUR REWARDS",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")
        points_label = tk.Label(
            self,
            text="YOU HAVE [SIMULATED POINTS] POINTS",
            font=("Press Start 2P", 14),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        points_label.place(relx=0.5, rely=0.35, anchor="center")
        prizes = ["Prize A", "Prize B"]
        for i, prize in enumerate(prizes):
            button = tk.Button(
                self,
                text=f"EXCHANGE FOR {prize.upper()}",
                font=("Press Start 2P", 15),
                bg="#0f0f0f",
                fg="#00ffff",
                activebackground="#1e1e1e",
                activeforeground="#ff66cc",
                relief="flat",
                padx=30,
                pady=10,
                command=lambda p=prize: self.redeem(p)
            )
            button.place(relx=0.5, rely=0.5 + i * 0.1, anchor="center")
        back_button = tk.Button(
            self,
            text="BACK TO START",
            font=("Press Start 2P", 15),
            bg="#0f0f0f",
            fg="#00ffff",
            activebackground="#1e1e1e",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=lambda: self.controller.show_frame("WelcomeScreen")
        )
        back_button.place(relx=0.5, rely=0.8, anchor="center")

    def redeem(self, prize):
        print(f"[Simulated] Redeemed: {prize}")
        self.controller.show_frame("WelcomeScreen")