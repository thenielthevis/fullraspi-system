import tkinter as tk
from PIL import Image, ImageTk
import os

class GameplayScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.score = 0
        self.successful_guesses = 0
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="GAMEPLAY",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.3, anchor="center")
        self.score_label = tk.Label(
            self,
            text=f"SCORE: {self.score}",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=5
        )
        self.score_label.place(relx=0.0, rely=0.0, anchor="nw", x=10, y=10)
        self.guesses_label = tk.Label(
            self,
            text=f"SUCCESSFUL GUESSES: {self.successful_guesses}",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=5
        )
        self.guesses_label.place(relx=0.0, rely=0.05, anchor="nw", x=10, y=40)
        instruction_label = tk.Label(
            self,
            text="Watch the ball enter a tunnel\nand spin the wheel for points!",
            font=("Press Start 2P", 15),
            fg="#ffffff",
            bg="#000000",
            justify="center",
            padx=15
        )
        instruction_label.place(relx=0.5, rely=0.45, anchor="center")
        camera_frame = tk.Frame(
            self,
            width=200,
            height=170,
            bg="#000000",
            relief="ridge",
            bd=3
        )
        camera_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        scored_button = tk.Button(
            self,
            text="SENSOR DETECTED BALL",
            font=("Press Start 2P", 15),
            bg="#0f0f0f",
            fg="#00ffff",
            activebackground="#1e1e1e",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.ball_scored
        )
        scored_button.place(relx=0.5, rely=0.6, anchor="center")

    def ball_scored(self):
        self.score += 10  # Simulated points for sensor-detected correct guess
        self.successful_guesses += 1  # Increment successful guesses
        self.score_label.configure(text=f"SCORE: {self.score}")
        self.guesses_label.configure(text=f"SUCCESSFUL GUESSES: {self.successful_guesses}")
        print(f"[Simulated] Sensor detected ball in tunnel! Successful guesses: {self.successful_guesses}")
        self.controller.show_frame("FinalScreen")