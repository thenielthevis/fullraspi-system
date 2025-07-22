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
        # Tunnel shape and touch sensor logic
        self.tunnels = ["Tunnel A", "Tunnel B", "Tunnel C", "Tunnel D", "Tunnel E"]
        self.tunnel_canvas = tk.Canvas(self, width=800, height=250, bg="black", highlightthickness=0)
        self.tunnel_canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.tunnel_shapes = []  # Store canvas shape IDs
        self.tunnel_labels = []
        self.tunnel_states = [False] * 5  # Track which tunnels are lit
        # Draw 5 tunnel shapes (rounded rectangles or arcs)
        tunnel_width = 110
        tunnel_height = 180
        spacing = 30
        start_x = 60
        y = 30
        for i, tunnel in enumerate(self.tunnels):
            x = start_x + i * (tunnel_width + spacing)
            # Draw tunnel as a rounded rectangle (simulate tunnel look)
            shape = self.tunnel_canvas.create_arc(
                x, y, x + tunnel_width, y + tunnel_height,
                start=0, extent=180, style=tk.ARC, width=8, outline="#00ffff"
            )
            rect = self.tunnel_canvas.create_rectangle(
                x, y + tunnel_height // 2, x + tunnel_width, y + tunnel_height,
                outline="#00ffff", width=8
            )
            self.tunnel_shapes.append((shape, rect))
            # Add tunnel label
            label = self.tunnel_canvas.create_text(
                x + tunnel_width // 2, y + tunnel_height + 20,
                text=tunnel, fill="#ffffff", font=("Press Start 2P", 10)
            )
            self.tunnel_labels.append(label)
        # For demo: simulate touch sensor event with keypress (remove in production)
        self.bind_all("<KeyPress-1>", lambda e: self.handle_touch_event(0))
        self.bind_all("<KeyPress-2>", lambda e: self.handle_touch_event(1))
        self.bind_all("<KeyPress-3>", lambda e: self.handle_touch_event(2))
        self.bind_all("<KeyPress-4>", lambda e: self.handle_touch_event(3))
        self.bind_all("<KeyPress-5>", lambda e: self.handle_touch_event(4))

    def handle_touch_event(self, tunnel_idx):
        # Ensure tunnel_idx is int
        try:
            tunnel_idx = int(tunnel_idx)
        except Exception:
            return
        # Called when a touch sensor event is received (tunnel_idx: 0-4)
        # Toggle tunnel state (simulate touch sensor input)
        if tunnel_idx < 0 or tunnel_idx >= len(self.tunnel_states):
            return
        # Only allow up to 3 tunnels to be lit at once
        lit_count = sum(self.tunnel_states)
        if not self.tunnel_states[tunnel_idx] and lit_count >= 3:
            return
        self.tunnel_states[tunnel_idx] = not self.tunnel_states[tunnel_idx]
        self.update_tunnel_graphics()

    def update_tunnel_graphics(self):
        # Update the color of tunnel shapes based on self.tunnel_states
        for i, (arc_id, rect_id) in enumerate(self.tunnel_shapes):
            if self.tunnel_states[i]:
                color = "#ff66cc"  # Lit color
            else:
                color = "#00ffff"  # Default color
            self.tunnel_canvas.itemconfig(arc_id, outline=color)
            self.tunnel_canvas.itemconfig(rect_id, outline=color)

    def on_mqtt_touch_event(self, tunnel_idx):
        # Ensure tunnel_idx is int
        try:
            tunnel_idx = int(tunnel_idx)
        except Exception:
            return
        self.handle_touch_event(tunnel_idx)
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


    def reset_tunnel_selection(self):
        self.tunnel_states = [False] * 5
        self.update_tunnel_graphics()

    # Remove select_tunnel, selection is now based on touch sensor events

    def confirm_selection(self):
        # Confirm only if exactly 3 tunnels are lit
        selected = [self.tunnels[i] for i, lit in enumerate(self.tunnel_states) if lit]
        if len(selected) == 3:
            print(f"[Simulated] Confirmed tunnels: {selected}")
            # Prompt user to pick up the ball
            from tkinter import messagebox
            messagebox.showinfo("Get Ready!", "Please pick up the ball from the container.")
            # Send solenoid ON command to ESP2
            if hasattr(self.controller, 'send_esp2_command'):
                self.controller.send_esp2_command("SOLENOID_ON")
            else:
                from TESTCONTROLLER import send_status_cmd
                send_status_cmd(self.controller.mqtt_client, "SOLENOID_ON", topic_override="esp32/control/esp2")
            # Show 'Drop Balls' button
            self.show_drop_balls_button()
        else:
            messagebox.showwarning("Selection Error", "Please select exactly 3 tunnels!")

    def show_drop_balls_button(self):
        # Disable confirm button to prevent double action
        # (Assume confirm button is at relx=0.5, rely=0.75)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "CONFIRM":
                widget.config(state="disabled")
        self.drop_balls_button = tk.Button(
            self,
            text="DROP BALLS",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#ffcc00",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.drop_balls_action
        )
        self.drop_balls_button.place(relx=0.5, rely=0.80, anchor="center")

    def drop_balls_action(self):
        # Send solenoid OFF command to ESP2
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("SOLENOID_OFF")
        else:
            from TESTCONTROLLER import send_status_cmd
            send_status_cmd(self.controller.mqtt_client, "SOLENOID_OFF", topic_override="esp32/control/esp2")
        # Enable servo on ESP1 (use SERVO_RUN)
        if hasattr(self.controller, 'send_esp1_command'):
            self.controller.send_esp1_command("SERVO_RUN")
            self.controller.send_esp1_command("START_PROXIMITY")
        else:
            from TESTCONTROLLER import send_status_cmd
            send_status_cmd(self.controller.mqtt_client, "SERVO_RUN", topic_override="esp32/control/esp1")
            send_status_cmd(self.controller.mqtt_client, "START_PROXIMITY", topic_override="esp32/control/esp1")
        # Remove the button
        if hasattr(self, 'drop_balls_button'):
            self.drop_balls_button.destroy()
        # Reset tunnel selection after gameplay starts
        self.reset_tunnel_selection()
        self.controller.show_frame("GameplayScreen")

    def tkraise(self, *args, **kwargs):
        # Override to reset tunnel selection whenever this screen is shown
        self.reset_tunnel_selection()
        super().tkraise(*args, **kwargs)

    def back_to_instruction(self):
        self.reset_tunnel_selection()
        self.controller.show_frame("InstructionScreen")