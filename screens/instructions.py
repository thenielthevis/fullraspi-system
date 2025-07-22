import tkinter as tk
from PIL import Image, ImageTk
import os

class InstructionScreen(tk.Frame):
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
            text="HOW TO PLAY",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")
        instructions = (
            "Scan RFID card to load credits.\n\n"
            "Select 3 out of 5 tunnels via touch.\n\n"
            "Watch the ball roll through a tunnel.\n\n"
            "Ball enters a wheel with colored segments.\n\n"
            "Each color awards points or a bonus round.\n\n"
            "Score points for correct tunnel guesses!\n\n"
            "Final round: Spinning lights with multipliers."
        )
        instruction_label = tk.Label(
            self,
            text=instructions,
            font=("Press Start 2P", 10),
            fg="#ffffff",
            bg="#000000",
            justify="center",
            padx=20
        )
        instruction_label.place(relx=0.5, rely=0.5, anchor="center")
        def on_continue():
            if hasattr(self.controller, 'send_esp1_command'):
                self.controller.send_esp1_command("START_TOUCH")
            else:
                from TESTCONTROLLER import send_status_cmd
                send_status_cmd(self.controller.mqtt_client, "START_TOUCH", topic_override="esp32/control/esp1")
            self.controller.show_frame("GameIntroScreen")
        continue_button = tk.Button(
            self,
            text="CONTINUE",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=on_continue
        )
        continue_button.place(relx=0.5, rely=0.8, anchor="center")