import tkinter as tk
import os
from PIL import Image, ImageTk
from picamera2 import Picamera2
import cv2
import numpy as np

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

        # --- Camera Frame and Label for Video ---
        camera_frame = tk.Frame(
            self,
            width=200,
            height=170,
            bg="#000000",
            relief="ridge",
            bd=3
        )
        camera_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        self.camera_label = tk.Label(camera_frame)
        self.camera_label.pack(fill="both", expand=True)

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

        # --- Camera and Tracking Setup ---
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": (320, 240), "format": "BGR888"})

        self.picam2.configure(config)
        self.picam2.start()

        self.lower_ball = np.array([108, 36, 179], dtype=np.uint8)
        self.upper_ball = np.array([140, 92, 118], dtype=np.uint8)
        self.kernel = np.ones((3, 3), np.uint8)

        self.update_camera()

    def update_camera(self):
        frame = self.picam2.capture_array()
        hsv   = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(hsv, self.lower_ball, self.upper_ball)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)

        dist  = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        sure_bg = cv2.dilate(mask, self.kernel, iterations=3)
        unknown = cv2.subtract(sure_bg, sure_fg)

        num_markers, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0

        ws_input = frame.copy()
        cv2.watershed(ws_input, markers)

        for marker_id in range(2, num_markers + 1):
            mask_obj = np.uint8(markers == marker_id)
            area = cv2.countNonZero(mask_obj)
            if area < 600:
                continue

            cnts, _ = cv2.findContours(mask_obj, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                continue
            c = max(cnts, key=cv2.contourArea)

            (x_f, y_f), radius = cv2.minEnclosingCircle(c)
            center = (int(x_f), int(y_f))
            radius = int(radius)

            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.circle(frame, center, 3, (0, 0, 255), -1)

        # Resize for display in the small square
        frame = cv2.resize(frame, (200, 170))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.config(image=imgtk)

        self.after(30, self.update_camera)

    def ball_scored(self):
        self.score += 10
        self.successful_guesses += 1
        self.score_label.configure(text=f"SCORE: {self.score}")
        self.guesses_label.configure(text=f"SUCCESSFUL GUESSES: {self.successful_guesses}")
        print(f"[Simulated] Sensor detected ball in tunnel! Successful guesses: {self.successful_guesses}")
        self.controller.show_frame("FinalScreen")