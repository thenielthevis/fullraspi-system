import tkinter as tk
from screens.welcome import WelcomeScreen
from screens.add_credit import AddCreditScreen
from screens.instructions import InstructionScreen
from screens.game_intro import GameIntroScreen
from screens.gameplay import GameplayScreen
from screens.final_screen import FinalScreen
from screens.end_screen import EndScreen
from screens.rewards import RewardsScreen
from TESTCONTROLLER import send_status_cmd, set_rfid_callback, set_coin_callback, set_touch_callback, set_proximity_callback, set_led_callback
import paho.mqtt.client as mqtt
from DbSetup import user_exists
import uuid
import pygame  # For playing sound

class ArcadeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arcade Game")
        
        # Make app fullscreen and always on top
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.configure(bg='#000000')
        
        # Hide cursor for kiosk mode (uncomment for production)
        # self.configure(cursor="none")
        
        # Bind Escape key to exit fullscreen (for development)
        self.bind('<Escape>', self.toggle_fullscreen)
        self.bind('<F11>', self.toggle_fullscreen)
        
        # Bind mouse click and keyboard events to ensure focus
        self.bind_all('<Button-1>', lambda e: self.focus_force())
        self.bind_all('<Key>', lambda e: self.focus_force())
        self.bind_all('<Motion>', lambda e: self.focus_force())
        
        # Force focus and bring to front
        self.focus_force()
        self.lift()
        self.grab_set()  # Make window modal to ensure focus

        # Initialize pygame mixer
        pygame.mixer.init()
        self.bgmusic_playing = False

        # Initialize LED colors storage
        self.led_colors = []  # Will store the 3 LED colors for matching bonus
        
        # Initialize current user info
        self.current_user_uid = None
        self.current_user_name = None
        
        # Initialize tunnel predictions for scoring
        self.tunnel_predictions = []
        self.tunnel_passages = []  # Track actual tunnel passages from proximity sensors

        # Set up MQTT client with a unique client_id to avoid disconnect loops
        unique_id = f"PiControlClient-{uuid.uuid4()}"
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=unique_id)
        from TESTCONTROLLER import on_connect, on_message
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect("192.168.76.34", 1883, keepalive=60)
        self.mqtt_client.loop_start()

        # Register callback for RFID
        def on_rfid(uid):
            print(f"RFID UID received: {uid}")
            welcome_screen = self.frames.get("WelcomeScreen")
            if welcome_screen:
                welcome_screen.reset_loading()

            if user_exists(uid):
                self.play_bgmusic()
                add_credit_screen = self.frames.get("AddCreditScreen")
                if add_credit_screen:
                    add_credit_screen.set_uid(uid)
                if hasattr(self, 'mqtt_client') and self.mqtt_client:
                    self.send_esp1_command("STOP_RFID")
                self.after(0, lambda: self.show_frame("AddCreditScreen"))
            else:
                self.play_register_first_sound()
                def show_unregistered():
                    from tkinter import messagebox
                    messagebox.showwarning("Unregistered", f"RFID {uid} not registered!")
                self.after(0, show_unregistered)

        set_rfid_callback(on_rfid)

        # --- COIN EVENT HANDLING ---
        def on_coin():
            self.play_coin_insert_sound()
            add_credit_screen = self.frames.get("AddCreditScreen")
            if add_credit_screen:
                self.after(0, add_credit_screen.on_coin_inserted)

        from TESTCONTROLLER import set_coin_callback, set_touch_callback, set_proximity_callback
        set_coin_callback(on_coin)

        # --- TOUCH EVENT HANDLING ---
        def on_touch(sensor_idx):
            game_intro_screen = self.frames.get("GameIntroScreen")
            if game_intro_screen:
                self.after(0, lambda: game_intro_screen.on_mqtt_touch_event(sensor_idx))
        set_touch_callback(on_touch)

        # --- PROXIMITY EVENT HANDLING ---
        # Tunnels are pathways that balls pass through BEFORE landing on color discs
        # Each tunnel has a proximity sensor that detects when a ball passes through
        self.proximity_count = 0
        self.proximity_last_state = {}
        self.tunnel_passages = []  # Track which tunnels balls actually passed through
        
        # Map proximity sensors to tunnel names
        # These sensors detect balls passing through tunnels BEFORE they hit the color disc
        self.sensor_to_tunnel = {
            "sensor1": "Tunnel A",
            "sensor2": "Tunnel B", 
            "sensor3": "Tunnel C",
            "sensor4": "Tunnel D",
            "sensor5": "Tunnel E"
        }
        
        def on_proximity(data):
            try:
                sensor, state = data.split(":")
                if sensor not in self.proximity_last_state:
                    self.proximity_last_state[sensor] = state
                    return
                last = self.proximity_last_state[sensor]
                self.proximity_last_state[sensor] = state
                
                # Ball passed through tunnel (falling edge: 1 -> 0)
                if last == "1" and state == "0":
                    self.proximity_count += 1
                    
                    # Record which tunnel the ball passed through
                    if sensor in self.sensor_to_tunnel:
                        tunnel_name = self.sensor_to_tunnel[sensor]
                        self.tunnel_passages.append(tunnel_name)
                        print(f"🎯 BALL PASSED THROUGH: {tunnel_name} (sensor: {sensor})")
                        print(f"🎯 TUNNEL PASSAGES SO FAR: {self.tunnel_passages}")
                        
                        # Check if this was a correct prediction and show popup
                        tunnel_predictions = getattr(self, 'tunnel_predictions', [])
                        if tunnel_name in tunnel_predictions:
                            self.show_tunnel_success_popup(tunnel_name)
                    
                    if self.proximity_count == 3:
                        if hasattr(self, 'send_esp2_command'):
                            self.send_esp2_command("NEON_ON")
                        else:
                            send_status_cmd(self.mqtt_client, "NEON_ON", topic_override="esp32/control/esp2")
                    if self.proximity_count >= 3:
                        if hasattr(self, 'send_esp1_command'):
                            self.send_esp1_command("STOP_PROXIMITY")
                        else:
                            send_status_cmd(self.mqtt_client, "STOP_PROXIMITY", topic_override="esp32/control/esp1")
                        self.after(10000, lambda: (
                            self.send_esp2_command("NEON_OFF") if hasattr(self, 'send_esp2_command')
                            else send_status_cmd(self.mqtt_client, "NEON_OFF", topic_override="esp32/control/esp2")
                        ))
            except Exception as e:
                print(f"[Proximity Parse Error] {e}")
        set_proximity_callback(on_proximity)

        # Register callback for LED colors
        def on_led_colors(led_data):
            try:
                # Parse LED colors from the message
                # Example: "Color 1: Blue, Color 2: Black, Color 3: Orange"
                if "Color 1:" in led_data and "Color 2:" in led_data and "Color 3:" in led_data:
                    # Extract the 3 colors
                    parts = led_data.split(", ")
                    color1 = parts[0].split("Color 1: ")[1].strip()
                    color2 = parts[1].split("Color 2: ")[1].strip() 
                    color3 = parts[2].split("Color 3: ")[1].strip()
                    
                    self.led_colors = [color1, color2, color3]
                    print(f"🎆 LED Colors stored for matching: {self.led_colors}")
                else:
                    print(f"🎆 Running LED animation")
            except Exception as e:
                print(f"[LED Color Parse Error] {e}")
        set_led_callback(on_led_colors)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for ScreenClass in (WelcomeScreen, AddCreditScreen, InstructionScreen, GameIntroScreen,
                            GameplayScreen, FinalScreen, EndScreen, RewardsScreen):
            frame = ScreenClass(container, self)
            self.frames[ScreenClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeScreen")

    def get_screen_size(self):
        """Get current screen dimensions"""
        return self.winfo_screenwidth(), self.winfo_screenheight()

    def play_bgmusic(self):
        if not self.bgmusic_playing:
            try:
                pygame.mixer.music.load("assets/sounds/bgmusic.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.bgmusic_playing = True
            except Exception as e:
                print(f"[Music Error] {e}")

    def play_register_first_sound(self):
        try:
            pygame.mixer.music.stop()
            self.bgmusic_playing = False
            sound = pygame.mixer.Sound("assets/sounds/RegisterFirst.mp3")
            sound.set_volume(0.8)
            sound.play()
        except Exception as e:
            print(f"[Register Sound Error] {e}")

    def play_coin_insert_sound(self):
        try:
            sound = pygame.mixer.Sound("assets/sounds/CoinInsert.mp3")
            sound.set_volume(0.9)
            sound.play()
        except Exception as e:
            print(f"[Coin Insert Sound Error] {e}")

    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()

        # 🔊 Screen-specific audio cues
        try:
            if screen_name == "InstructionScreen":
                pygame.mixer.music.stop()
                self.bgmusic_playing = False
                sound = pygame.mixer.Sound("assets/sounds/howtoplay.mp3")
                sound.set_volume(0.9)
                sound.play()
            elif screen_name == "GameIntroScreen":
                pygame.mixer.music.stop()
                self.bgmusic_playing = False
                sound = pygame.mixer.Sound("assets/sounds/CHOOSETHREE.mp3")
                sound.set_volume(0.9)
                sound.play()
        except Exception as e:
            print(f"[Screen Sound Error] {e}")

    def send_esp2_command(self, cmd):
        send_status_cmd(self.mqtt_client, cmd, topic_override="esp32/control/esp2")

    def send_esp1_command(self, cmd):
        send_status_cmd(self.mqtt_client, cmd, topic_override="esp32/control/esp1")

    def start_rfid(self):
        self.send_esp1_command("START_RFID")

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode (for development)"""
        current_state = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not current_state)
        
    def ensure_focus(self):
        """Ensure the app maintains focus"""
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        # Schedule periodic focus check (less frequent to avoid interference)
        self.after(5000, self.ensure_focus)

    def show_tunnel_success_popup(self, tunnel_name):
        """Show a popup when a ball passes through a correctly predicted tunnel"""
        import tkinter as tk
        
        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("Correct Prediction!")
        popup.geometry("400x200")
        popup.configure(bg="#000000")
        popup.attributes('-topmost', True)
        popup.resizable(False, False)
        
        # Center the popup on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (popup.winfo_screenheight() // 2) - (200 // 2)
        popup.geometry(f"400x200+{x}+{y}")
        
        # Success message
        success_label = tk.Label(
            popup,
            text="🎯 CORRECT PREDICTION! 🎯",
            font=("Press Start 2P", 14),
            fg="#00ff00",
            bg="#000000"
        )
        success_label.pack(pady=20)
        
        # Tunnel name
        tunnel_label = tk.Label(
            popup,
            text=f"Ball passed through {tunnel_name}!",
            font=("Press Start 2P", 12),
            fg="#00ffff",
            bg="#000000"
        )
        tunnel_label.pack(pady=10)
        
        # Bonus points
        bonus_label = tk.Label(
            popup,
            text="+50 BONUS POINTS!",
            font=("Press Start 2P", 16),
            fg="#ffff00",
            bg="#000000"
        )
        bonus_label.pack(pady=15)
        
        # Auto-close after 2 seconds
        popup.after(2000, popup.destroy)
        
        print(f"[TUNNEL SUCCESS POPUP] Showing popup for {tunnel_name}")

if __name__ == "__main__":
    app = ArcadeApp()
    
    # Ensure proper fullscreen initialization
    app.update_idletasks()  # Process all pending events
    app.attributes('-fullscreen', True)
    app.attributes('-topmost', True)
    app.focus_set()
    
    # Start focus maintenance after a delay
    app.after(1000, app.ensure_focus)
    
    # Additional window management for better interaction
    def on_focus_in(event):
        app.attributes('-topmost', True)
    
    def on_focus_out(event):
        # Gently regain focus if lost (less aggressive)
        app.after(500, lambda: app.focus_force())
    
    app.bind('<FocusIn>', on_focus_in)
    app.bind('<FocusOut>', on_focus_out)
    
    # Force window to front and start
    app.lift()
    app.focus_force()
    app.mainloop()
