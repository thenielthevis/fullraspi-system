import tkinter as tk
from PIL import Image, ImageTk
import os

class FinalScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Don't send LED command here - wait for screen to be shown

        # Load background image
        img_path = os.path.join("assets", "sp.png")
        original_img = Image.open(img_path)
        resized_img = original_img.resize((800, 600))
        self.bg_image = ImageTk.PhotoImage(resized_img)

        # Background
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)

        # Title
        title = tk.Label(
            self,
            text="FINAL ROUND",
            font=("Press Start 2P", 25),
            fg="#00ffff",
            bg="#000000",
            pady=20
        )
        title.place(relx=0.5, rely=0.15, anchor="center")

        # Ball Results Section
        results_frame = tk.Frame(
            self,
            bg="#000000",
            relief="ridge",
            bd=3
        )
        results_frame.place(relx=0.5, rely=0.35, anchor="center", relwidth=0.8, relheight=0.25)

        # Results title
        results_title = tk.Label(
            results_frame,
            text="BALL LANDING RESULTS:",
            font=("Press Start 2P", 14),
            fg="#00ffff",
            bg="#000000",
            pady=10
        )
        results_title.pack(pady=(10, 5))

        # Ball sectors display (will be updated when screen is shown)
        self.sectors_display = tk.Label(
            results_frame,
            text="Loading ball positions...",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            justify="center"
        )
        self.sectors_display.pack(pady=5)

        # Individual ball colors (will be created dynamically)
        self.ball_colors_frame = tk.Frame(results_frame, bg="#000000")
        self.ball_colors_frame.pack(pady=10)

        # Points calculation
        self.points_label = tk.Label(
            results_frame,
            text="Calculating points...",
            font=("Press Start 2P", 10),
            fg="#00ff00",
            bg="#000000"
        )
        self.points_label.pack(pady=5)
        
        # Prediction bonus display
        self.prediction_label = tk.Label(
            results_frame,
            text="",
            font=("Press Start 2P", 8),
            fg="#00AAFF",
            bg="#000000"
        )
        self.prediction_label.pack(pady=2)
        # Subtitle
        subtitle = tk.Label(
            self,
            text="LIGHTS SPINNING AUTOMATICALLY!",
            font=("Press Start 2P", 12),
            fg="#ffffff",
            bg="#000000",
            pady=10
        )
        subtitle.place(relx=0.5, rely=0.6, anchor="center")

        # Complete button
        complete_button = tk.Button(
            self,
            text="COMPLETE ROUND",
            font=("Press Start 2P", 15),
            bg="#000000",
            fg="#00ffff",
            activebackground="#000000",
            activeforeground="#ff66cc",
            relief="flat",
            padx=30,
            pady=10,
            command=self.complete_round
        )
        complete_button.place(relx=0.5, rely=0.75, anchor="center")

        # Footer
        footer = tk.Label(
            self,
            text="BALL COLORS DETERMINE POINTS AWARDED",
            font=("Press Start 2P", 10),
            fg="#ffffff",
            bg="#000000",
            pady=5
        )
        footer.place(relx=0.5, rely=0.9, anchor="center")

        # Color mapping for points (same as objectTest.py sectors)
        self.color_points = {
            'Red': 100,
            'Yellow': 50,
            'Blue': 75,
            'Green': 25,
            'Orange': 150,
            'Black': 200,
            'Unknown': 0
        }

        # Color mapping for display colors (RGB hex values)
        self.display_colors = {
            'Red': '#FF0000',
            'Yellow': '#FFFF00',
            'Blue': '#0080FF',
            'Green': '#00FF00',
            'Orange': '#FFA500',
            'Black': '#808080',
            'Unknown': '#FFFFFF'
        }
        
        # Animation state for LED bonus celebration
        self.animation_active = False
        self.animation_count = 0
        
        # LED Bonus Popup
        self.bonus_popup = None
        self.popup_active = False

    def celebration_animation(self):
        """Animate the points label for LED bonus celebration"""
        if not self.animation_active:
            self.animation_active = True
            self.animation_count = 0
            self.flash_points_label()

    def flash_points_label(self):
        """Flash the points label between gold and white for celebration effect"""
        if self.animation_count < 6:  # Flash 3 times (6 color changes)
            if self.animation_count % 2 == 0:
                self.points_label.configure(fg="#FFFFFF", font=("Press Start 2P", 12))  # White and bigger
            else:
                self.points_label.configure(fg="#FFD700", font=("Press Start 2P", 10))  # Gold and normal
            
            self.animation_count += 1
            self.after(300, self.flash_points_label)  # Flash every 300ms
        else:
            # End animation with final gold color
            self.points_label.configure(fg="#FFD700", font=("Press Start 2P", 10))
            self.animation_active = False

    def create_bonus_popup(self, matched_balls, bonus_points):
        """Create a fun animated popup for LED bonus notification"""
        if self.popup_active:
            return
            
        self.popup_active = True
        
        # Create popup frame with exciting styling
        self.bonus_popup = tk.Frame(
            self,
            bg="#FFD700",  # Gold background
            relief="raised",
            bd=5
        )
        
        # Calculate popup size and position
        popup_width = 600
        popup_height = 400
        screen_width = self.winfo_width() or 800
        screen_height = self.winfo_height() or 600
        
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.bonus_popup.place(x=x, y=y, width=popup_width, height=popup_height)
        
        # Animated title with emoji
        title_text = "🎆 LED MULTIPLIER BONUS! 🎆"
        self.popup_title = tk.Label(
            self.bonus_popup,
            text=title_text,
            font=("Press Start 2P", 20),
            fg="#FF0000",  # Red text
            bg="#FFD700",  # Gold background
            pady=20
        )
        self.popup_title.pack(pady=10)
        
        # Matched balls info
        matched_text = f"🎯 MATCHED BALLS: {len(matched_balls)}"
        matched_label = tk.Label(
            self.bonus_popup,
            text=matched_text,
            font=("Press Start 2P", 12),
            fg="#000000",
            bg="#FFD700"
        )
        matched_label.pack(pady=5)
        
        # List matched balls
        for ball in matched_balls:
            ball_label = tk.Label(
                self.bonus_popup,
                text=f"⚡ {ball}",
                font=("Press Start 2P", 10),
                fg="#0000FF",  # Blue text
                bg="#FFD700"
            )
            ball_label.pack(pady=2)
        
        # Bonus points display
        bonus_text = f"💰 BONUS POINTS: +{bonus_points}"
        bonus_label = tk.Label(
            self.bonus_popup,
            text=bonus_text,
            font=("Press Start 2P", 14),
            fg="#00AA00",  # Green text
            bg="#FFD700"
        )
        bonus_label.pack(pady=10)
        
        # Fun message
        fun_message = tk.Label(
            self.bonus_popup,
            text="🚀 INCREDIBLE! 🚀",
            font=("Press Start 2P", 16),
            fg="#FF6600",  # Orange text
            bg="#FFD700"
        )
        fun_message.pack(pady=5)
        
        # Auto-close countdown
        self.countdown_label = tk.Label(
            self.bonus_popup,
            text="Auto-closing in 2...",
            font=("Press Start 2P", 8),
            fg="#666666",
            bg="#FFD700"
        )
        self.countdown_label.pack(pady=5)
        
        # Optional: Add click to close functionality
        close_hint = tk.Label(
            self.bonus_popup,
            text="(Click anywhere to close)",
            font=("Press Start 2P", 6),
            fg="#999999",
            bg="#FFD700"
        )
        close_hint.pack(pady=2)
        
        # Bind click to close
        self.bonus_popup.bind("<Button-1>", lambda e: self.close_bonus_popup())
        for widget in self.bonus_popup.winfo_children():
            widget.bind("<Button-1>", lambda e: self.close_bonus_popup())
        
        # Bring popup to front
        self.bonus_popup.lift()
        
        # Start pulsing animation and countdown
        self.popup_pulse_count = 0
        self.popup_countdown = 2
        self.pulse_popup()
        self.countdown_popup()
        
        print(f"🎉 LED BONUS POPUP CREATED: {matched_balls} earned {bonus_points} bonus points!")

    def pulse_popup(self):
        """Create pulsing animation effect for the popup"""
        if not self.popup_active or not self.bonus_popup:
            return
            
        # Pulse the title between different colors
        colors = ["#FF0000", "#FF6600", "#FFFF00", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF"]
        color = colors[self.popup_pulse_count % len(colors)]
        
        if hasattr(self, 'popup_title'):
            self.popup_title.configure(fg=color)
        
        self.popup_pulse_count += 1
        
        # Continue pulsing for 2 seconds
        if self.popup_pulse_count < 20:  # 20 pulses over 2 seconds
            self.after(100, self.pulse_popup)

    def countdown_popup(self):
        """Countdown and auto-close the popup"""
        if not self.popup_active or not self.bonus_popup:
            return
            
        if self.popup_countdown > 0:
            self.countdown_label.configure(text=f"Auto-closing in {self.popup_countdown}...")
            self.popup_countdown -= 1
            self.after(1000, self.countdown_popup)  # Update every second
        else:
            self.close_bonus_popup()

    def close_bonus_popup(self):
        """Close the bonus popup"""
        if self.bonus_popup:
            self.bonus_popup.destroy()
            self.bonus_popup = None
        self.popup_active = False
        print(f"🎉 LED BONUS POPUP CLOSED")

    def tkraise(self, aboveThis=None):
        """Override tkraise to start LEDs when screen is shown"""
        super().tkraise(aboveThis)
        # Send the LED control command to ESP32 when screen is actually shown
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("LED_RUN")
        self.update_ball_display()

    def update_ball_display(self):
        """Update the display with actual ball sector information"""
        # Clear previous ball color displays
        for widget in self.ball_colors_frame.winfo_children():
            widget.destroy()

        # Get ball sectors from controller
        if hasattr(self.controller, 'final_ball_sectors') and self.controller.final_ball_sectors:
            sectors = self.controller.final_ball_sectors
            sectors_string = getattr(self.controller, 'final_sectors_string', 'Unknown positions')
            
            # Debug: Log what we received
            print(f"🎯 FINAL SCREEN RECEIVED:")
            print(f"   - Sectors: {sectors}")
            print(f"   - Sectors type: {type(sectors)}")
            print(f"   - Sectors length: {len(sectors)}")
            print(f"   - Sectors string: {sectors_string}")
            
            # Update main sectors display
            self.sectors_display.configure(text=f"Ball positions: {sectors_string}")
            
            # Create individual ball color displays
            total_points = 0
            base_points = 0  # Track base points for bonus calculation
            led_colors = getattr(self.controller, 'led_colors', [])
            
            print(f"🎆 LED Colors for matching: {led_colors}")
            print(f"🎯 Ball sectors detected: {sectors}")
            
            # Check for LED color matches (any ball color that appears in LED colors gets 2x bonus)
            led_colors_set = set(led_colors) if led_colors else set()
            matched_balls = []
            bonus_points = 0
            regular_points = 0
            
            for i, sector in enumerate(sectors):
                print(f"   - Processing ball {i+1}: {sector}")
                ball_frame = tk.Frame(self.ball_colors_frame, bg="#000000")
                ball_frame.pack(side=tk.LEFT, padx=10, pady=5)
                
                # Ball number label
                ball_label = tk.Label(
                    ball_frame,
                    text=f"Ball {i+1}:",
                    font=("Press Start 2P", 8),
                    fg="#ffffff",
                    bg="#000000"
                )
                ball_label.pack()
                
                # Color indicator
                color_display = self.display_colors.get(sector, '#FFFFFF')
                
                # Check if this ball color matches any LED color
                is_led_match = sector in led_colors_set
                if is_led_match:
                    matched_balls.append(f"Ball {i+1} ({sector})")
                
                # Add border effect for matched balls
                border_color = "#FFD700" if is_led_match else color_display  # Gold border for matches
                color_label = tk.Label(
                    ball_frame,
                    text=f"  {sector}  ",
                    font=("Press Start 2P", 10),
                    fg="#000000",
                    bg=color_display,
                    relief="raised",
                    bd=4 if is_led_match else 2,
                    highlightbackground=border_color,
                    highlightthickness=2 if is_led_match else 0
                )
                color_label.pack(pady=2)
                
                # Points for this ball
                base_ball_points = self.color_points.get(sector, 0)
                if is_led_match:
                    actual_ball_points = base_ball_points * 2  # 2x bonus for LED match
                    bonus_points += actual_ball_points
                    points_text = f"{base_ball_points}×2 = {actual_ball_points}"
                    points_color = "#FFD700"  # Gold for bonus points
                    print(f"     🎆 LED MATCH! {sector} in LED colors - {base_ball_points} × 2 = {actual_ball_points}")
                else:
                    actual_ball_points = base_ball_points
                    regular_points += actual_ball_points
                    points_text = f"{actual_ball_points} pts"
                    points_color = "#00ff00"
                
                base_points += base_ball_points
                total_points += actual_ball_points
                
                points_label = tk.Label(
                    ball_frame,
                    text=points_text,
                    font=("Press Start 2P", 7),
                    fg=points_color,
                    bg="#000000"
                )
                points_label.pack()
            
            # Check for tunnel prediction bonus
            tunnel_predictions = getattr(self.controller, 'tunnel_predictions', [])
            tunnel_passages = getattr(self.controller, 'tunnel_passages', [])
            prediction_bonus = 0
            correct_predictions = 0
            
            if tunnel_predictions:
                print(f"🎯 Checking tunnel predictions: {tunnel_predictions} vs actual passages: {tunnel_passages}")
                
                # Count how many predictions were correct
                for predicted_tunnel in tunnel_predictions:
                    if predicted_tunnel in tunnel_passages:
                        correct_predictions += 1
                        prediction_bonus += 50
                        print(f"✅ CORRECT PREDICTION: {predicted_tunnel}")
                    else:
                        print(f"❌ WRONG PREDICTION: {predicted_tunnel} (not in {tunnel_passages})")
                
                # Update prediction display
                if correct_predictions > 0:
                    prediction_text = f"🎯 Tunnel Bonus: {correct_predictions}/3 correct (+{prediction_bonus} pts)"
                    self.prediction_label.configure(text=prediction_text, fg="#00AAFF")
                else:
                    self.prediction_label.configure(text="🎯 Tunnel Bonus: 0/3 correct (no bonus)", fg="#666666")
            else:
                self.prediction_label.configure(text="🎯 No tunnel predictions", fg="#666666")
            
            # Add prediction bonus to total
            total_points += prediction_bonus
            
            # Create bonus summary text
            if matched_balls or prediction_bonus > 0:
                bonus_text = ""
                if matched_balls:
                    bonus_text += f"🎆 LED MATCH! {', '.join(matched_balls)}\n"
                    if regular_points > 0:
                        bonus_text += f"Regular: {regular_points}, LED Bonus: {bonus_points}\n"
                    else:
                        bonus_text += f"All balls LED matched! LED Bonus: {bonus_points}\n"
                
                if prediction_bonus > 0:
                    bonus_text += f"🎯 Tunnel Bonus: +{prediction_bonus}\n"
                
                bonus_text += f"TOTAL POINTS: {total_points}"
                points_color = "#FFD700"  # Gold for any bonus
                
                print(f"💰 BONUS SUMMARY:")
                print(f"   - Matched balls: {matched_balls}")
                print(f"   - Regular points: {regular_points}")
                print(f"   - LED bonus points: {bonus_points}")
                print(f"   - Prediction bonus: {prediction_bonus}")
                print(f"   - Total points: {total_points}")
                
                # 🚨 TRIGGER BEACON AND VISUAL CELEBRATION FOR LED BONUS! 🚨
                if matched_balls:  # Only trigger beacon for LED bonus, not prediction bonus
                    print(f"🎆 TRIGGERING LED BONUS CELEBRATION!")
                    if hasattr(self.controller, 'send_esp2_command'):
                        self.controller.send_esp2_command("BEACON_ON")
                        print(f"🚨 BEACON_ON sent to ESP2")
                    
                    # Store that we have a multiplier bonus for the complete_round function
                    self.controller.has_led_multiplier = True
                    self.controller.led_bonus_balls = matched_balls
                    
                    # 🎉 CREATE EXCITING POPUP NOTIFICATION! 🎉
                    self.create_bonus_popup(matched_balls, bonus_points)
                    
                    # Update points label to flash/animate for bonus
                    self.celebration_animation()
            else:
                bonus_text = f"Total Points Earned: {total_points}"
                if prediction_bonus == 0 and tunnel_predictions:
                    bonus_text += "\n(No bonuses earned)"
                points_color = "#00ff00"
                print(f"   - No bonuses earned")
                self.controller.has_led_multiplier = False
            
            # Update total points display
            self.points_label.configure(
                text=bonus_text,
                fg=points_color
            )
            
        else:
            # No ball data available
            self.sectors_display.configure(text="No ball position data available")
            self.points_label.configure(text="Points: 0")

    def complete_round(self):
        # Calculate and display final points with individual ball LED matching bonus + tunnel prediction bonus
        if hasattr(self.controller, 'final_ball_sectors') and self.controller.final_ball_sectors:
            sectors = self.controller.final_ball_sectors
            led_colors = getattr(self.controller, 'led_colors', [])
            led_colors_set = set(led_colors) if led_colors else set()
            tunnel_predictions = getattr(self.controller, 'tunnel_predictions', [])
            
            base_points = 0
            total_points = 0
            matched_balls = []
            
            # Calculate points for each ball individually
            for i, sector in enumerate(sectors):
                ball_base_points = self.color_points.get(sector, 0)
                base_points += ball_base_points
                
                if sector in led_colors_set:
                    ball_final_points = ball_base_points * 2
                    matched_balls.append(f"Ball {i+1} ({sector})")
                    print(f"[FINAL ROUND] Ball {i+1} ({sector}): {ball_base_points} × 2 = {ball_final_points} (LED match!)")
                else:
                    ball_final_points = ball_base_points
                    print(f"[FINAL ROUND] Ball {i+1} ({sector}): {ball_final_points} points (no LED match)")
                
                total_points += ball_final_points
            
            # 🎯 CALCULATE TUNNEL PREDICTION BONUS
            tunnel_predictions = getattr(self.controller, 'tunnel_predictions', [])
            tunnel_passages = getattr(self.controller, 'tunnel_passages', [])
            prediction_bonus = 0
            correct_predictions = 0
            
            if tunnel_predictions:
                print(f"[TUNNEL PREDICTIONS] Player predicted: {tunnel_predictions}")
                print(f"[TUNNEL PASSAGES] Actual passages: {tunnel_passages}")
                
                # Check each prediction against actual tunnel passages
                for predicted_tunnel in tunnel_predictions:
                    if predicted_tunnel in tunnel_passages:
                        correct_predictions += 1
                        # Award 50 bonus points per correct prediction
                        prediction_bonus += 50
                        print(f"[PREDICTION MATCH] ✅ {predicted_tunnel} - +50 bonus points!")
                    else:
                        print(f"[PREDICTION MISS] ❌ {predicted_tunnel} - no bonus")
                
                if correct_predictions > 0:
                    total_points += prediction_bonus
                    print(f"[PREDICTION BONUS] {correct_predictions}/3 correct predictions = +{prediction_bonus} bonus points!")
                else:
                    print(f"[PREDICTION RESULT] No correct predictions - no bonus")
            else:
                print(f"[PREDICTION ERROR] No tunnel predictions found!")
            
            sectors_string = getattr(self.controller, 'final_sectors_string', 'Unknown')
            print(f"[FINAL ROUND] Ball positions: {sectors_string}")
            print(f"[FINAL ROUND] LED colors: {led_colors}")
            
            if matched_balls:
                print(f"[FINAL ROUND] 🎆 LED MATCHES: {', '.join(matched_balls)}")
                print(f"[FINAL ROUND] Base points: {base_points}, LED bonus: {total_points - base_points - prediction_bonus}, Prediction bonus: {prediction_bonus}")
            else:
                print(f"[FINAL ROUND] No LED color matches")
                
            print(f"[FINAL ROUND] TOTAL FINAL SCORE: {total_points} points")
                
            # Store final points in controller for end screen (including prediction bonus)
            self.controller.final_total_points = total_points
            self.controller.prediction_bonus = prediction_bonus
            self.controller.correct_predictions = correct_predictions
            
            # 🎯 HANDLE POST-GAME SEQUENCE: STEPPER & ULTRASONIC
            self.start_post_game_sequence(matched_balls)
        else:
            print("[FINAL ROUND] No ball position data available")
            self.controller.final_total_points = 0
            self.controller.prediction_bonus = 0
            self.controller.correct_predictions = 0
            self.start_post_game_sequence([])  # No bonus, but still run sequence

    def start_post_game_sequence(self, matched_balls):
        """Handle the post-game sequence: stepper motor and ultrasonic verification"""
        print(f"🔄 STARTING POST-GAME SEQUENCE...")
        
        # If LED bonus occurred, beacon should already be ON from update_ball_display
        # Wait a moment for celebration, then start stepper sequence
        if matched_balls:
            print(f"🎊 LED BONUS CELEBRATION - Beacon is ON, waiting for celebration...")
            # Wait 3 seconds for celebration, then start stepper
            self.after(3000, self.run_stepper_sequence)
        else:
            print(f"📦 No LED bonus - proceeding directly to ball collection...")
            # No celebration needed, start stepper immediately
            self.run_stepper_sequence()

    def run_stepper_sequence(self):
        """Run the stepper motor to drop/collect balls"""
        print(f"🔄 RUNNING STEPPER MOTOR TO COLLECT BALLS...")
        
        # Turn off beacon if it was on
        if hasattr(self.controller, 'has_led_multiplier') and self.controller.has_led_multiplier:
            if hasattr(self.controller, 'send_esp2_command'):
                self.controller.send_esp2_command("BEACON_OFF")
                print(f"🚨 BEACON_OFF sent to ESP2")
        
        # Run stepper motor to drop/collect balls
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("STEPPER_RUN")
            print(f"🔄 STEPPER_RUN sent to ESP2")
        
        # Wait for stepper to complete, then start ultrasonic verification
        print(f"⏳ Waiting for stepper to complete ball collection...")
        self.after(5000, self.run_ultrasonic_verification)  # Wait 5 seconds for stepper

    def run_ultrasonic_verification(self):
        """Run ultrasonic sensor to verify all balls are collected"""
        print(f"📡 STARTING ULTRASONIC VERIFICATION...")
        
        # Start ultrasonic scan to verify ball collection
        if hasattr(self.controller, 'send_esp2_command'):
            self.controller.send_esp2_command("ULTRA_SCAN")
            print(f"📡 ULTRA_SCAN sent to ESP2")
        
        # Wait for ultrasonic verification to complete
        print(f"🔍 Verifying all balls are in container...")
        self.after(3000, self.complete_verification)  # Wait 3 seconds for verification

    def complete_verification(self):
        """Complete the verification process and proceed to end screen"""
        print(f"✅ POST-GAME SEQUENCE COMPLETE!")
        print(f"📦 All balls should now be in container")
        print(f"🎮 Proceeding to end screen...")
        
        # Proceed to end screen
        self.controller.show_frame("EndScreen")
