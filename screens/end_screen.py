import tkinter as tk
from PIL import Image, ImageTk
import os
from DbSetup import add_points_to_user, get_user_info

class EndScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Get screen dimensions for responsive background
        self.update_idletasks()
        screen_width = controller.winfo_screenwidth()
        screen_height = controller.winfo_screenheight()
        
        # Load background image
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized_img)
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)
        
        # Title
        title = tk.Label(
            self,
            text="GAME COMPLETE!",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.15, anchor="center")
        
        # Player name label (will be updated when screen is shown)
        self.player_label = tk.Label(
            self,
            text="Player: Loading...",
            font=("Press Start 2P", 14),
            fg="#ffff00",
            bg="#000000",
            pady=5
        )
        self.player_label.place(relx=0.5, rely=0.3, anchor="center")
        
        # Round points label
        self.round_points_label = tk.Label(
            self,
            text="Round Points: 0",
            font=("Press Start 2P", 16),
            fg="#00ff00",
            bg="#000000",
            pady=5
        )
        self.round_points_label.place(relx=0.5, rely=0.35, anchor="center")
        
        # Points breakdown section
        breakdown_title = tk.Label(
            self,
            text="POINTS BREAKDOWN:",
            font=("Press Start 2P", 12),
            fg="#ffaa00",
            bg="#000000",
            pady=5
        )
        breakdown_title.place(relx=0.5, rely=0.42, anchor="center")
        
        # Detailed breakdown labels
        self.base_points_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 9),
            fg="#ffffff",
            bg="#000000",
            pady=2
        )
        self.base_points_label.place(relx=0.5, rely=0.47, anchor="center")
        
        self.tunnel_bonus_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 9),
            fg="#00ffff",
            bg="#000000",
            pady=2
        )
        self.tunnel_bonus_label.place(relx=0.5, rely=0.51, anchor="center")
        
        self.led_bonus_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 9),
            fg="#ff6600",
            bg="#000000",
            pady=2
        )
        self.led_bonus_label.place(relx=0.5, rely=0.55, anchor="center")
        
        self.beacon_status_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 8),
            fg="#ff0000",
            bg="#000000",
            pady=2
        )
        self.beacon_status_label.place(relx=0.5, rely=0.59, anchor="center")
        
        # Total points label (will be updated when screen is shown)
        self.total_points_label = tk.Label(
            self,
            text="Total Points: Loading...",
            font=("Press Start 2P", 18),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        self.total_points_label.place(relx=0.5, rely=0.67, anchor="center")
        
        # Status message
        self.status_label = tk.Label(
            self,
            text="Points automatically saved to your account!",
            font=("Press Start 2P", 10),
            fg="#00ffff",
            bg="#000000",
            pady=10
        )
        self.status_label.place(relx=0.5, rely=0.75, anchor="center")
        
        # Play Again button
        play_again_button = tk.Button(
            self,
            text="PLAY AGAIN",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ff00",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.play_again
        )
        play_again_button.place(relx=0.5, rely=0.85, anchor="center")
        
        # Store reference to the detect/back button
        self.detect_back_button = tk.Button(
            self,
            text="DETECTING 3 BALLS...",
            font=("Press Start 2P", 12),
            bg="#000000",
            fg="#ffff00",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=20,
            pady=8,
            command=self.ultra_scan_command
        )
        self.detect_back_button.place(relx=0.5, rely=0.93, anchor="center")
        
        # Exit button (positioned in bottom right corner)
        exit_button = tk.Button(
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
        exit_button.place(relx=0.95, rely=0.95, anchor="se")

        self.ultra_scan_running = False  # Track if scan has been started

    def tkraise(self, aboveThis=None):
        """Override tkraise to update display when screen is shown"""
        super().tkraise(aboveThis)
        self.update_display()
        self.ultra_scan_running = False  # Reset scan state on show
        self.start_ultra_scan_and_monitor()

    def update_display(self):
        """Update the display with current player info and points"""
        # Get current player info
        player_name = getattr(self.controller, 'current_user_name', 'Unknown Player')
        player_uid = getattr(self.controller, 'current_user_uid', None)
        round_points = getattr(self.controller, 'final_total_points', 0)
        
        # Update player name
        self.player_label.config(text=f"Player: {player_name}")
        
        # Update round points
        self.round_points_label.config(text=f"Round Points: {round_points}")
        
        # Get detailed points breakdown
        points_breakdown = getattr(self.controller, 'points_breakdown', {})
        
        # Display base points
        base_points = points_breakdown.get('base_points', 0)
        self.base_points_label.config(text=f"🎮 Base Game Points: +{base_points}")
        
        # Display tunnel bonus
        tunnel_bonus = points_breakdown.get('tunnel_bonus', 0)
        if tunnel_bonus > 0:
            tunnel_matches = points_breakdown.get('tunnel_matches', 0)
            self.tunnel_bonus_label.config(text=f"🎯 Tunnel Predictions: +{tunnel_bonus}")
        else:
            self.tunnel_bonus_label.config(text="🎯 Tunnel Predictions: +0 (No matches)")
        
        # Display LED multiplier bonus
        led_bonus = points_breakdown.get('led_multiplier_bonus', 0)
        if led_bonus > 0:
            led_matches = points_breakdown.get('led_matches', 0)
            matched_colors = points_breakdown.get('matched_colors', [])
            colors_text = ', '.join(matched_colors) if matched_colors else 'None'
            self.led_bonus_label.config(text=f"🎆 LED Multiplier ({led_matches}x): +{led_bonus}")
            
            # Show beacon status
            beacon_activated = points_breakdown.get('beacon_activated', False)
            if beacon_activated:
                self.beacon_status_label.config(text="🚨 BEACON ACTIVATED! 🚨")
            else:
                self.beacon_status_label.config(text="")
        else:
            self.led_bonus_label.config(text="🎆 LED Multiplier: +0 (No matches)")
            self.beacon_status_label.config(text="")
        
        # Save points to database and get updated total
        if player_uid and round_points > 0:
            try:
                # Add points to database
                add_points_to_user(player_uid, round_points)
                
                # Get updated user info
                user_info = get_user_info(player_uid)
                if user_info:
                    total_points = user_info[1]  # points column
                    self.total_points_label.config(text=f"Total Points: {total_points}")
                    self.status_label.config(
                        text=f"✅ {round_points} points added successfully!",
                        fg="#00ff00"
                    )
                    print(f"[END SCREEN] Points saved: {player_name} earned {round_points} points (Total: {total_points})")
                    print(f"[END SCREEN] Breakdown: Base({base_points}) + Tunnel({tunnel_bonus}) + LED({led_bonus}) = {round_points}")
                else:
                    self.total_points_label.config(text="Total Points: Error")
                    self.status_label.config(
                        text="❌ Error retrieving total points",
                        fg="#ff0000"
                    )
            except Exception as e:
                print(f"[END SCREEN ERROR] Failed to save points: {e}")
                self.total_points_label.config(text="Total Points: Error")
                self.status_label.config(
                    text="❌ Error saving points to database",
                    fg="#ff0000"
                )
        else:
            # No points to save or no user logged in
            self.total_points_label.config(text="Total Points: 0")
            if not player_uid:
                self.status_label.config(
                    text="No player logged in",
                    fg="#ff6600"
                )
            else:
                self.status_label.config(
                    text="No points earned this round",
                    fg="#ff6600"
                )

    def update_detect_back_button(self):
        """Update the detect/back button based on number of detected balls"""
        num_balls = len(getattr(self.controller, 'tunnel_passages', []))
        if num_balls >= 3:
            self.detect_back_button.config(
                text="BACK TO WELCOME",
                state="normal",
                command=lambda: self.controller.show_frame("WelcomeScreen")
            )
        else:
            self.detect_back_button.config(
                text="DETECTING 3 BALLS",
                state="disabled",
                command=self.ultra_scan_command
            )

    def ultra_scan_command(self):
        """Send ULTRA_SCAN command to esp32"""
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("ULTRA_SCAN")
        else:
            print("[END SCREEN] send_esp2_command not available")
        self.detect_back_button.config(state="disabled", text="DETECTING 3 BALLS")
        self.after(1000, self.update_detect_back_button)

    def start_ultra_scan_and_monitor(self):
        """Start ULTRA_SCAN and monitor for 3 balls detected"""
        if not self.ultra_scan_running:
            self.ultra_scan_command()
            self.ultra_scan_running = True
        self.update_detect_back_button()
        # Continue checking until 3 balls detected
        if len(getattr(self.controller, 'tunnel_passages', [])) < 3:
            self.after(500, self.start_ultra_scan_and_monitor)
        else:
            self.ultra_scan_running = False  # Stop scan loop

    def play_again(self):
        """Reset game state and go back to game intro"""
        # Reset game state
        if hasattr(self.controller, 'final_ball_sectors'):
            delattr(self.controller, 'final_ball_sectors')
        if hasattr(self.controller, 'final_sectors_string'):
            delattr(self.controller, 'final_sectors_string')
        if hasattr(self.controller, 'final_total_points'):
            delattr(self.controller, 'final_total_points')
        if hasattr(self.controller, 'points_breakdown'):
            delattr(self.controller, 'points_breakdown')
        if hasattr(self.controller, 'prediction_bonus'):
            delattr(self.controller, 'prediction_bonus')
        if hasattr(self.controller, 'correct_predictions'):
            delattr(self.controller, 'correct_predictions')
        if hasattr(self.controller, 'has_led_multiplier'):
            delattr(self.controller, 'has_led_multiplier')
        
        # Reset LED colors and tunnel predictions for new game
        self.controller.led_colors = []
        self.controller.tunnel_predictions = []
        self.controller.tunnel_passages = []  # Reset actual tunnel passage tracking
        
        print("[END SCREEN] Starting new game...")
        self.controller.show_frame("GameIntroScreen")
        if hasattr(self.controller, 'play_bgmusic'):
            self.controller.play_bgmusic()

    def exit_application(self):
        """Exit the application completely"""
        print("[END SCREEN] Exiting application...")
        if hasattr(self.controller, 'stop_bgmusic'):
            self.controller.stop_bgmusic()
        
        # Clean shutdown of MQTT client
        if hasattr(self.controller, 'mqtt_client') and self.controller.mqtt_client:
            self.controller.mqtt_client.loop_stop()
            self.controller.mqtt_client.disconnect()
        
        # Destroy the main window
        self.controller.quit()
        self.controller.destroy()