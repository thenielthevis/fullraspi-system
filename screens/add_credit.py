import tkinter as tk
from PIL import Image, ImageTk
import os
from DbSetup import user_exists
import sqlite3
from TESTCONTROLLER import send_status_cmd
from DbSetup import add_credit

class AddCreditScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_uid = None
        self.coin_mode = False
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="ADD CREDIT",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.2, anchor="center")
        subtitle = tk.Label(
            self,
            text="INSERT COIN OR Proceed",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.35, anchor="center")
        credit_button = tk.Button(
            self,
            text="INSERT COIN",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.start_coin_mode
        )
        credit_button.place(relx=0.5, rely=0.5, anchor="center")
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
        back_button.place(relx=0.5, rely=0.65, anchor="center")
        self.credit_label = tk.Label(
            self,
            text="CREDIT: -",
            font=("Press Start 2P", 18),
            fg="#00ff00",
            bg="#000000",
            pady=10
        )
        self.credit_label.place(relx=0.5, rely=0.42, anchor="center")
        play_button = tk.Button(
            self,
            text="PLAY",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ff00",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.play_game
        )
        play_button.place(relx=0.5, rely=0.58, anchor="center")
        self.coin_status_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 14),
            fg="#ffff00",
            bg="#000000",
            pady=10
        )
        self.coin_status_label.place(relx=0.5, rely=0.46, anchor="center")

    def set_uid(self, uid):
        self.current_uid = uid
        # Fetch credit from DB
        conn = sqlite3.connect('arpi.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT credit FROM users WHERE uid = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.credit_label.config(text=f"CREDIT: {row[0]}")
        else:
            self.credit_label.config(text="CREDIT: -")

    def add_credit(self):
        print("[Simulated] Credit added.")
        self.controller.show_frame("InstructionScreen")

    def start_coin_mode(self):
        if not self.current_uid:
            self.coin_status_label.config(text="Scan RFID first!")
            return
        self.coin_mode = True
        self.coin_status_label.config(text="Insert coins now!")
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("START_COIN")
        else:
            send_status_cmd(self.controller.mqtt_client, "START_COIN")
        # Optionally, subscribe to coin events here

    def on_coin_inserted(self):
        if self.current_uid:
            add_credit(self.current_uid, 1)
            self.set_uid(self.current_uid)
            self.coin_status_label.config(text="Coin inserted! Credit updated.")

    def play_game(self):
        if self.coin_mode:
            if hasattr(self.controller, 'send_esp2_command'):
                self.controller.send_esp2_command("STOP_COIN")
            else:
                send_status_cmd(self.controller.mqtt_client, "STOP_COIN")
            self.coin_mode = False
            self.coin_status_label.config(text="Coin acceptor stopped.")
        # Send START_TOUCH to ESP1 (corrected)
        if hasattr(self.controller, 'send_esp1_command'):
            self.controller.send_esp1_command("START_TOUCH")
        else:
            send_status_cmd(self.controller.mqtt_client, "START_TOUCH", topic_override="esp32/control/esp1")
        print("[Simulated] Play button pressed.")
        self.controller.show_frame("InstructionScreen")