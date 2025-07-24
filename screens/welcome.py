import tkinter as tk
from PIL import Image, ImageTk
import os
from TESTCONTROLLER import send_status_cmd, main
import threading

class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Get screen dimensions for responsive background
        self.update_idletasks()
        screen_width = controller.winfo_screenwidth()
        screen_height = controller.winfo_screenheight()
        
        img_path = os.path.join("assets", "space.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="WELCOME TO ARPI",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.4, anchor="center")
        subtitle = tk.Label(
            self,
            text="SCAN RFID TO BEGIN!",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.55, anchor="center")
        self.start_button = tk.Button(
            self,
            text="SCAN RFID",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.start_rfid
        )
        self.start_button.place(relx=0.5, rely=0.7, anchor="center")
        
        # Exit button (positioned in bottom right corner)
        self.exit_button = tk.Button(
            self,
            text="EXIT",
            font=("Press Start 2P", 10),
            bg="#660000",
            fg="#ffffff",
            activebackground="#990000",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=8,
            command=self.exit_application
        )
        self.exit_button.place(relx=0.95, rely=0.95, anchor="se")
        
        self.loading = False

    def start_rfid(self):
        if self.loading:
            return
        self.loading = True
        self.start_button.config(text="WAITING FOR RFID...", state="disabled")
        if hasattr(self.controller, 'start_rfid'):
            self.controller.start_rfid()
        else:
            print("RFID start method not available!")

    def reset_loading(self):
        self.loading = False
        self.start_button.config(text="SCAN RFID", state="normal")

    def exit_application(self):
        """Exit the application completely"""
        print("[WELCOME] Exiting application...")
        if hasattr(self.controller, 'stop_bgmusic'):
            self.controller.stop_bgmusic()
        
        # Clean shutdown of MQTT client
        if hasattr(self.controller, 'mqtt_client') and self.controller.mqtt_client:
            self.controller.mqtt_client.loop_stop()
            self.controller.mqtt_client.disconnect()
        
        # Destroy the main window
        self.controller.quit()
        self.controller.destroy()