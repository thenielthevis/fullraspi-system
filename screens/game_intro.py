import tkinter as tk
from PIL import Image, ImageTk
import os
import tkinter.messagebox as messagebox

class GameIntroScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_tunnels = []
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        title = tk.Label(
            self,
            text="CHOOSE 3 TUNNELS",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.15, anchor="center")
        subtitle = tk.Label(
            self,
            text="TOUCH TO SELECT 3/5 TUNNELS",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.25, anchor="center")
        self.tunnels = ["Tunnel A", "Tunnel B", "Tunnel C", "Tunnel D", "Tunnel E"]
        self.buttons = {}
        # Grid-like layout: 2 rows, 3 columns, centered
        for i, tunnel in enumerate(self.tunnels):
            row = i // 3  # 0 for first row, 1 for second row
            col = i % 3   # 0, 1, 2 for columns
            relx = 0.3 + col * 0.25  # Spread buttons horizontally
            rely = 0.4 + row * 0.15  # Spread buttons vertically
            button = tk.Button(
                self,
                text=tunnel,
                font=("Press Start 2P", 12),
                bg="#000000",
                fg="#00ffff",
                activebackground="#000000",
                activeforeground="#ff66cc",
                relief="flat",
                padx=20,
                pady=8,
                command=lambda t=tunnel: self.select_tunnel(t)
            )
            button.place(relx=relx, rely=rely, anchor="center")
            self.buttons[tunnel] = button
        confirm_button = tk.Button(
            self,
            text="CONFIRM",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.confirm_selection
        )
        confirm_button.place(relx=0.5, rely=0.75, anchor="center")
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
            command=lambda: self.controller.show_frame("InstructionScreen")
        )
        back_button.place(relx=0.5, rely=0.85, anchor="center")

    def select_tunnel(self, tunnel):
        if tunnel in self.selected_tunnels:
            self.selected_tunnels.remove(tunnel)
            self.buttons[tunnel].configure(bg="#000000")
        elif len(self.selected_tunnels) < 3:
            self.selected_tunnels.append(tunnel)
            self.buttons[tunnel].configure(bg="#1e1e1e")
        print(f"[Simulated] Selected tunnels: {self.selected_tunnels}")

    def confirm_selection(self):
        if len(self.selected_tunnels) == 3:
            print(f"[Simulated] Confirmed tunnels: {self.selected_tunnels}")
            self.controller.show_frame("GameplayScreen")
        else:
            messagebox.showwarning("Selection Error", "Please select exactly 3 tunnels!")