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
            pady=10
        )
        self.round_points_label.place(relx=0.5, rely=0.4, anchor="center")
        
        # Bonus breakdown label
        self.bonus_breakdown_label = tk.Label(
            self,
            text="",
            font=("Press Start 2P", 10),
            fg="#FFAA00",
            bg="#000000",
            pady=5
        )
        self.bonus_breakdown_label.place(relx=0.5, rely=0.48, anchor="center")
        
        # Total points label (will be updated when screen is shown)
        self.total_points_label = tk.Label(
            self,
            text="Total Points: Loading...",
            font=("Press Start 2P", 18),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        self.total_points_label.place(relx=0.5, rely=0.55, anchor="center")
        
        # Status message
        self.status_label = tk.Label(
            self,
            text="Points automatically saved to your account!",
            font=("Press Start 2P", 10),
            fg="#00ffff",
            bg="#000000",
            pady=15
        )
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")
        
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
        play_again_button.place(relx=0.5, rely=0.8, anchor="center")
        
        # Back to Welcome button
        back_button = tk.Button(
            self,
            text="BACK TO WELCOME",
            font=("Press Start 2P", 12),
            bg="#000000",
            fg="#ffff00",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=20,
            pady=8,
            command=lambda: self.controller.show_frame("WelcomeScreen")
        )
        back_button.place(relx=0.5, rely=0.9, anchor="center")

    def tkraise(self, aboveThis=None):
        """Override tkraise to update display when screen is shown"""
        super().tkraise(aboveThis)
        self.update_display()

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
        
        # Show bonus breakdown if available
        prediction_bonus = getattr(self.controller, 'prediction_bonus', 0)
        correct_predictions = getattr(self.controller, 'correct_predictions', 0)
        
        bonus_breakdown = ""
        if prediction_bonus > 0:
            bonus_breakdown += f"🎯 Tunnel Bonus: {correct_predictions}/3 (+{prediction_bonus})\n"
        if hasattr(self.controller, 'has_led_multiplier') and self.controller.has_led_multiplier:
            bonus_breakdown += f"🎆 LED Multiplier Bonus Applied\n"
        
        if bonus_breakdown:
            self.bonus_breakdown_label.config(text=bonus_breakdown.strip())
        else:
            self.bonus_breakdown_label.config(text="No bonus points this round")
        
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

    def play_again(self):
        """Reset game state and go back to game intro"""
        # Reset game state
        if hasattr(self.controller, 'final_ball_sectors'):
            delattr(self.controller, 'final_ball_sectors')
        if hasattr(self.controller, 'final_sectors_string'):
            delattr(self.controller, 'final_sectors_string')
        if hasattr(self.controller, 'final_total_points'):
            delattr(self.controller, 'final_total_points')
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