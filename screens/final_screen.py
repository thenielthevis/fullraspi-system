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
                color_label = tk.Label(
                    ball_frame,
                    text=f"  {sector}  ",
                    font=("Press Start 2P", 10),
                    fg="#000000",
                    bg=color_display,
                    relief="raised",
                    bd=2
                )
                color_label.pack(pady=2)
                
                # Points for this ball
                points = self.color_points.get(sector, 0)
                total_points += points
                points_label = tk.Label(
                    ball_frame,
                    text=f"{points} pts",
                    font=("Press Start 2P", 7),
                    fg="#00ff00",
                    bg="#000000"
                )
                points_label.pack()
            
            # Update total points display
            self.points_label.configure(text=f"Total Points Earned: {total_points}")
            
        else:
            # No ball data available
            self.sectors_display.configure(text="No ball position data available")
            self.points_label.configure(text="Points: 0")

    def complete_round(self):
        # Calculate and display final points
        if hasattr(self.controller, 'final_ball_sectors') and self.controller.final_ball_sectors:
            sectors = self.controller.final_ball_sectors
            total_points = sum(self.color_points.get(sector, 0) for sector in sectors)
            sectors_string = getattr(self.controller, 'final_sectors_string', 'Unknown')
            print(f"[FINAL ROUND] Ball positions: {sectors_string}")
            print(f"[FINAL ROUND] Total points awarded: {total_points}")
        else:
            print("[FINAL ROUND] No ball position data available")
        
        self.controller.show_frame("EndScreen")
