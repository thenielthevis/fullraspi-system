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
        # Store reference to play button
        self.play_button = tk.Button(
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
        self.play_button.place(relx=0.5, rely=0.58, anchor="center")
        self.coin_status_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 14),
            fg="#ffff00",
            bg="#000000",
            pady=10
        )
        self.coin_status_label.place(relx=0.5, rely=0.46, anchor="center")
        self.ultra_scan_running = False  # Track if scan has been started

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.ultra_scan_running = False  # Reset scan state on show
        self.start_ultra_scan_and_monitor()

    def start_ultra_scan_and_monitor(self):
        """Start ULTRA_SCAN and monitor for 3 balls detected"""
        if not self.ultra_scan_running:
            self.ultra_scan_command()
            self.ultra_scan_running = True
        self.check_ball_detection_and_update_play_button()
        # Continue checking until 3 balls detected
        if not self.is_three_balls_detected():
            self.after(500, self.start_ultra_scan_and_monitor)
        else:
            self.ultra_scan_running = False  # Stop scan loop

    def is_three_balls_detected(self):
        """Check if 3 balls detected from tunnel_passages or log"""
        # Check tunnel_passages first
        if len(getattr(self.controller, 'tunnel_passages', [])) >= 3:
            return True
        # Check logs if available
        logs = getattr(self.controller, 'esp32_logs', [])
        for log in logs:
            if ("3 balls detected" in log and "20-35cm" in log) or \
               ("Ball detected in range" in log and "(3/3)" in log):
                return True
        return False

    def check_ball_detection_and_update_play_button(self):
        """Update PLAY button state based on ball detection"""
        if self.is_three_balls_detected():
            self.play_button.config(state="normal", text="PLAY")
        else:
            self.play_button.config(state="disabled", text="DETECTING 3 BALLS")

    def update_play_button_state(self):
        """Enable PLAY button only if 3 balls detected, update text accordingly"""
        self.check_ball_detection_and_update_play_button()

    def set_uid(self, uid):
        self.current_uid = uid
        # Fetch credit and name from DB
        conn = sqlite3.connect('arpi.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT credit, name FROM users WHERE uid = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.credit_label.config(text=f"CREDIT: {row[0]}")
            # Store user info in controller for later use
            self.controller.current_user_uid = uid
            self.controller.current_user_name = row[1]
            print(f"[User] Logged in: {row[1]} (UID: {uid})")
        else:
            self.credit_label.config(text="CREDIT: -")
        self.update_play_button_state()

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
        self.update_play_button_state()

    def play_game(self):
        # Check if user has sufficient credits before allowing gameplay
        if not self.current_uid:
            from tkinter import messagebox
            messagebox.showwarning("No User", "Please scan RFID first!")
            return
            
        # Get current credit from database
        conn = sqlite3.connect('arpi.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT credit FROM users WHERE uid = ?", (self.current_uid,))
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[0] <= 0:
            # No credits available - show options
            from tkinter import messagebox
            result = messagebox.askyesno(
                "No Credits", 
                "You have 0 credits!\n\nWould you like to insert coins to play?\n\nYes = Insert Coins\nNo = Return to Welcome"
            )
            if result:
                # User wants to insert coins
                self.start_coin_mode()
                return
            else:
                # User wants to exit
                self.controller.show_frame("WelcomeScreen")
                return
        
        # Deduct 1 credit for gameplay
        from DbSetup import add_credit
        add_credit(self.current_uid, -1)  # Subtract 1 credit
        self.set_uid(self.current_uid)  # Refresh display
        print(f"[CREDIT] 1 credit deducted for gameplay. Player: {self.current_uid}")
        
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

    def ultra_scan_command(self):
        """Send ULTRA_SCAN command to esp32"""
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("ULTRA_SCAN")
        else:
            print("[ADD CREDIT] send_esp2_command not available")
        self.play_button.config(state="disabled", text="DETECTING 3 BALLS")
        # No need to re-enable here; update_play_button_state will handle it

    def on_new_ultrasonic_log(self):
        """Call this when a new ultrasonic log is received to update play button state."""
        self.update_play_button_state()

    def enable_play_button(self):
        """Enable the PLAY button and set its text to 'PLAY'."""
        self.play_button.config(state="normal", text="PLAY")