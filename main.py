import tkinter as tk
from screens.welcome import WelcomeScreen
from screens.add_credit import AddCreditScreen
from screens.instructions import InstructionScreen
from screens.game_intro import GameIntroScreen
from screens.gameplay import GameplayScreen
from screens.final_screen import FinalScreen
from screens.end_screen import EndScreen
from screens.rewards import RewardsScreen
from TESTCONTROLLER import send_status_cmd, set_rfid_callback
import paho.mqtt.client as mqtt
from DbSetup import user_exists
import uuid
import pygame  # For playing sound

class ArcadeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arcade Game")
        self.geometry("800x600")
        self.resizable(False, False)

        # Initialize pygame mixer
        pygame.mixer.init()
        self.bgmusic_playing = False

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
        self.proximity_count = 0
        self.proximity_last_state = {}
        def on_proximity(data):
            try:
                sensor, state = data.split(":")
                if sensor not in self.proximity_last_state:
                    self.proximity_last_state[sensor] = state
                    return
                last = self.proximity_last_state[sensor]
                self.proximity_last_state[sensor] = state
                if last == "1" and state == "0":
                    self.proximity_count += 1
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

if __name__ == "__main__":
    app = ArcadeApp()
    app.after(0, lambda: (app.deiconify(), app.lift(), app.focus_force()))
    app.mainloop()
