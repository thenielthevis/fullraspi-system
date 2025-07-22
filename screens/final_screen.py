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
        results_frame.place(relx=0.5, rely=0.35, anchor="center", width=600, height=200)

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
            
            # Create bonus summary text
            if matched_balls:
                bonus_text = f"🎆 LED MATCH BONUS! 🎆\n"
                bonus_text += f"Matched: {', '.join(matched_balls)}\n"
                if regular_points > 0:
                    bonus_text += f"Regular: {regular_points}, Bonus: {bonus_points}\n"
                    bonus_text += f"Total Points: {total_points}"
                else:
                    bonus_text += f"All balls matched LED! Total: {total_points}"
                points_color = "#FFD700"  # Gold for bonus
                print(f"💰 LED BONUS SUMMARY:")
                print(f"   - Matched balls: {matched_balls}")
                print(f"   - Regular points: {regular_points}")
                print(f"   - Bonus points: {bonus_points}")
                print(f"   - Total points: {total_points}")
                
                # 🚨 TRIGGER BEACON AND VISUAL CELEBRATION FOR LED BONUS! 🚨
                print(f"🎆 TRIGGERING LED BONUS CELEBRATION!")
                if hasattr(self.controller, 'send_esp2_command'):
                    self.controller.send_esp2_command("BEACON_ON")
                    print(f"🚨 BEACON_ON sent to ESP2")
                
                # Store that we have a multiplier bonus for the complete_round function
                self.controller.has_led_multiplier = True
                self.controller.led_bonus_balls = matched_balls
                
                # Update points label to flash/animate for bonus
                self.celebration_animation()
            else:
                bonus_text = f"Total Points Earned: {total_points}\n(No LED color matches)"
                points_color = "#00ff00"
                print(f"   - No LED matches found")
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
        # Calculate and display final points with individual ball LED matching bonus
        if hasattr(self.controller, 'final_ball_sectors') and self.controller.final_ball_sectors:
            sectors = self.controller.final_ball_sectors
            led_colors = getattr(self.controller, 'led_colors', [])
            led_colors_set = set(led_colors) if led_colors else set()
            
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
            
            sectors_string = getattr(self.controller, 'final_sectors_string', 'Unknown')
            print(f"[FINAL ROUND] Ball positions: {sectors_string}")
            print(f"[FINAL ROUND] LED colors: {led_colors}")
            
            if matched_balls:
                print(f"[FINAL ROUND] 🎆 LED MATCHES: {', '.join(matched_balls)}")
                print(f"[FINAL ROUND] Base points: {base_points}, Final total: {total_points}")
            else:
                print(f"[FINAL ROUND] No LED color matches - Total points: {total_points}")
                
            # Store final points in controller for end screen
            self.controller.final_total_points = total_points
            
            # 🎯 HANDLE POST-GAME SEQUENCE: STEPPER & ULTRASONIC
            self.start_post_game_sequence(matched_balls)
        else:
            print("[FINAL ROUND] No ball position data available")
            self.controller.final_total_points = 0
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
