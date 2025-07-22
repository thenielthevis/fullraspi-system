import tkinter as tk
from PIL import Image, ImageTk
import os

class FinalScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Send the LED control command to ESP32
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("LED_RUN")

        # Load background image
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)

        # Background
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)

        # Camera Frame (placeholder)
        camera_frame = tk.Frame(
            self,
            width=200,
            height=170,
            bg="#000000",
            relief="ridge",
            bd=3
        )
        camera_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Title
        title = tk.Label(
            self,
            text="FINAL ROUND",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")

        # Subtitle
        subtitle = tk.Label(
            self,
            text="LIGHTS SPINNING AUTOMATICALLY!",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.35, anchor="center")

        # Result label
        self.result_label = tk.Label(
            self,
            text="[SIMULATED] LANDED ON COLOR: XX POINTS",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        self.result_label.place(relx=0.5, rely=0.5, anchor="center")

        # Complete button
        complete_button = tk.Button(
            self,
            text="COMPLETE ROUND",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.complete_round
        )
        complete_button.place(relx=0.5, rely=0.65, anchor="center")

        # Footer
        footer = tk.Label(
            self,
            text="COLOR DETERMINES POINTS AWARDED",
            font=("Press Start 2P", 10),
            fg="#ffffff",
            bg="#000000",
            pady=5
        )
        footer.place(relx=0.5, rely=0.9, anchor="center")

    def complete_round(self):
        print("[Simulated] Final round complete. Points awarded for color.")
        self.controller.show_frame("EndScreen")
