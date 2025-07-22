import tkinter as tk
import os
from PIL import Image, ImageTk
from picamera2 import Picamera2
import cv2
import numpy as np
import math
import time

class GameplayScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.score = 0
        self.successful_guesses = 0
        self.configure(bg="#000000")

        # --- Full-size Camera Frame for Video (Primary display) ---
        self.camera_frame = tk.Frame(
            self,
            bg="#000000",
            relief="ridge",
            bd=2
        )
        self.camera_frame.place(relwidth=0.85, relheight=1.0, relx=0, rely=0)
        self.camera_label = tk.Label(self.camera_frame, bg="#000000")
        self.camera_label.pack(fill="both", expand=True)

        # --- Right Side Panel for UI Elements ---
        self.ui_panel = tk.Frame(
            self,
            bg="#000000",
            relief="ridge",
            bd=2
        )
        self.ui_panel.place(relwidth=0.15, relheight=1.0, relx=0.85, rely=0)

        # Title at top of right panel
        title = tk.Label(
            self.ui_panel,
            text="GAMEPLAY",
            font=("Press Start 2P", 16),
            fg="#00ffff",
            bg="#000000",
            pady=10
        )
        title.pack(pady=(10, 5))

        # Score labels
        self.score_label = tk.Label(
            self.ui_panel,
            text=f"SCORE:\n{self.score}",
            font=("Press Start 2P", 10),
            fg="#ffffff",
            bg="#000000",
            justify="center"
        )
        self.score_label.pack(pady=5)

        self.guesses_label = tk.Label(
            self.ui_panel,
            text=f"GUESSES:\n{self.successful_guesses}",
            font=("Press Start 2P", 8),
            fg="#ffffff",
            bg="#000000",
            justify="center"
        )
        self.guesses_label.pack(pady=5)

        # Detection Results Display
        detection_title = tk.Label(
            self.ui_panel,
            text="DETECTION:",
            font=("Press Start 2P", 8),
            fg="#00ffff",
            bg="#000000"
        )
        detection_title.pack(pady=(15, 5))
        
        self.balls_count_label = tk.Label(
            self.ui_panel,
            text="Balls: 0",
            font=("Press Start 2P", 8),
            fg="#00ff00",
            bg="#000000"
        )
        self.balls_count_label.pack(pady=2)
        
        self.sectors_label = tk.Label(
            self.ui_panel,
            text="Sectors:\nNone",
            font=("Press Start 2P", 7),
            fg="#ffff00",
            bg="#000000",
            justify="center",
            wraplength=100
        )
        self.sectors_label.pack(pady=2)
        
        self.settling_label = tk.Label(
            self.ui_panel,
            text="",
            font=("Press Start 2P", 7),
            fg="#ff6600",
            bg="#000000",
            justify="center",
            wraplength=100
        )
        self.settling_label.pack(pady=2)

        # Instructions
        instruction_label = tk.Label(
            self.ui_panel,
            text="Watch balls\nenter sectors\nfor points!",
            font=("Press Start 2P", 7),
            fg="#ffffff",
            bg="#000000",
            justify="center"
        )
        instruction_label.pack(pady=(15, 10))

        # Sensor button
        scored_button = tk.Button(
            self.ui_panel,
            text="SENSOR\nDETECTED\nBALL",
            font=("Press Start 2P", 8),
            bg="#0f0f0f",
            fg="#00ffff",
            activebackground="#1e1e1e",
            activeforeground="#ff66cc",
            relief="flat",
            padx=10,
            pady=8,
            command=self.ball_scored,
            justify="center"
        )
        scored_button.pack(pady=10, padx=5, fill="x")

        # ========== CAMERA SETUP FROM objectTest.py ==========
        self.FRAME_WIDTH, self.FRAME_HEIGHT = 1280, 960
        self.picam2 = None  # Initialize as None, will be created when needed
        
        # ========== OBJECT DETECTION SETUP FROM objectTest.py ==========
        # Disc center from objectTest.py
        self.DISC_CENTER = (615, 430)  # Exact center from objectTest.py
        self.sectors = [
            ("Red",    -35,  23),
            ("Yellow", 25, 80),
            ("Blue", 82, 145),
            ("Green",147, 202),
            ("Orange",205, 263),
            ("Black",265, 324)
        ]
        
        # Ball color detection from objectTest.py
        self.lower_ball = np.array([129, 102, 194])
        self.upper_ball = np.array([179, 255, 255])
        
        # Visual config from objectTest.py (exact copy)
        self.VISUAL_CONFIG = {
            'line_thickness': 3,
            'line_length': 400,
            'sector_colors': {
                'Red': (0, 0, 255),
                'Yellow': (0, 255, 255),
                'Blue': (255, 0, 0),
                'Green': (0, 255, 0),
                'Orange': (0, 165, 255),
                'Black': (128, 128, 128)
            },
            'center_dot_size': 8,
            'ball_circle_thickness': 3
        }
        
        # Settling time logic
        self.SETTLING_TIME = 2
        self.first_detection_time = None
        self.balls_settled = False
        self.detected_sectors = []
        self.ball_count = 0
        self.camera_running = False

        # Don't start camera automatically - wait for screen to be shown

    def init_camera(self):
        """Initialize and start the camera when the screen is shown"""
        if self.picam2 is None:
            try:
                print("[Camera] Initializing camera...")
                self.picam2 = Picamera2()
                config = self.picam2.create_preview_configuration(main={"size": (self.FRAME_WIDTH, self.FRAME_HEIGHT), "format": "RGB888"})
                self.picam2.configure(config)
                self.picam2.start()
                self.camera_running = True
                print("[Camera] Camera started successfully")
                self.update_camera()  # Start the camera update loop
            except Exception as e:
                print(f"[Camera Error] Failed to initialize camera: {e}")
                self.camera_running = False

    def cleanup_camera(self):
        """Clean up camera resources"""
        try:
            self.camera_running = False
            if hasattr(self, 'picam2') and self.picam2 is not None:
                print("[Camera] Stopping camera...")
                self.picam2.stop()
                self.picam2.close()
                self.picam2 = None
                print("[Camera] Camera stopped successfully")
        except Exception as e:
            print(f"[Camera Cleanup Error] {e}")

    def tkraise(self, aboveThis=None):
        """Override tkraise to start camera when screen is shown"""
        super().tkraise(aboveThis)
        if not self.camera_running:
            self.init_camera()

    def reset_detection(self):
        """Reset detection state for new game"""
        self.first_detection_time = None
        self.balls_settled = False
        self.detected_sectors = []
        self.ball_count = 0
        self.auto_scored = False
        self.balls_count_label.configure(text="Balls: 0")
        self.sectors_label.configure(text="Sectors:\nNone")
        self.settling_label.configure(text="")

    def on_screen_leave(self):
        """Called when leaving this screen - stop camera to save resources"""
        self.cleanup_camera()

    def get_sector_label(self, center):
        """Get sector label based on ball position - from objectTest.py"""
        dx = center[0] - self.DISC_CENTER[0]
        dy = self.DISC_CENTER[1] - center[1]  # Y inverted in image coords
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 360) % 360  # normalize to [0, 360)

        for label, start, end in self.sectors:
            if start <= angle < end:
                return label
        return "Unknown"

    def draw_sectors(self, frame):
        """Draw colorful sector lines and labels - exact copy from objectTest.py"""
        for label, angle_start, angle_end in self.sectors:
            # Get color for this sector
            color = self.VISUAL_CONFIG['sector_colors'].get(label, (200, 200, 200))
            
            # Draw start line
            angle_rad = math.radians(angle_start)
            x2 = int(self.DISC_CENTER[0] + self.VISUAL_CONFIG['line_length'] * math.cos(angle_rad))
            y2 = int(self.DISC_CENTER[1] - self.VISUAL_CONFIG['line_length'] * math.sin(angle_rad))
            cv2.line(frame, self.DISC_CENTER, (x2, y2), color, self.VISUAL_CONFIG['line_thickness'])

            # Draw label in middle of sector with colored background
            mid_angle = math.radians((angle_start + angle_end) / 2)
            lx = int(self.DISC_CENTER[0] + 250 * math.cos(mid_angle))
            ly = int(self.DISC_CENTER[1] - 250 * math.sin(mid_angle))
            
            # Add colored background for text
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (lx - text_size[0]//2 - 5, ly - text_size[1] - 5), 
                         (lx + text_size[0]//2 + 5, ly + 5), color, -1)
            cv2.putText(frame, label, (lx - text_size[0]//2, ly), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def detect_multiple_balls_and_sectors(self, frame, hsv):
        """Detect multiple balls and return their sectors - from objectTest.py"""
        detected_sectors = []
        
        # Threshold for ball color
        mask = cv2.inRange(hsv, self.lower_ball, self.upper_ball)

        # Enhanced morphology to clean noise and separate touching balls
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Use distance transform and watershed to separate touching balls
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        
        # Find local maxima (ball centers)
        _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        
        # Find sure background area
        sure_bg = cv2.dilate(mask, kernel, iterations=3)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # Apply watershed
        frame_copy = frame.copy()
        markers = cv2.watershed(frame_copy, markers)
        
        ball_count = 0
        
        # Process each detected region
        for marker_id in range(2, markers.max() + 1):
            # Create mask for this specific ball
            ball_mask = np.uint8(markers == marker_id)
            
            # Calculate area to filter out noise
            area = cv2.countNonZero(ball_mask)
            if area < 300:  # Minimum area for a ball from objectTest.py
                continue
                
            # Find contour for this ball
            contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
                
            contour = max(contours, key=cv2.contourArea)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            
            # Additional validation: check if radius is reasonable for a ball (from objectTest.py)
            if radius < 8 or radius > 100:  # Exact values from objectTest.py
                continue
                
            ball_count += 1
            
            # Draw colorful ball detection
            cv2.circle(frame, center, radius, (0, 255, 255), self.VISUAL_CONFIG['ball_circle_thickness'])
            cv2.circle(frame, center, 3, (0, 0, 255), -1)
            
            # Add ball number
            cv2.putText(frame, f"Ball {ball_count}", (center[0] - 15, center[1] - radius - 8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

            sector_label = self.get_sector_label(center)
            detected_sectors.append(sector_label)
            
            # Show sector for each ball
            cv2.putText(frame, sector_label, (center[0] - 15, center[1] + radius + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, 
                       self.VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 1)
        
        # Fallback: if watershed didn't find enough balls, try contour-based detection
        if ball_count < 2:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # Sort contours by area (largest first)
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                # Reset for fallback method
                detected_sectors = []
                ball_count = 0
                
                for contour in contours:
                    if cv2.contourArea(contour) > 300:  # Exact area threshold from objectTest.py
                        (x, y), radius = cv2.minEnclosingCircle(contour)
                        center = (int(x), int(y))
                        radius = int(radius)
                        
                        if radius >= 8 and radius <= 100:  # Exact radius validation from objectTest.py
                            ball_count += 1
                            
                            cv2.circle(frame, center, radius, (0, 255, 255), self.VISUAL_CONFIG['ball_circle_thickness'])
                            cv2.circle(frame, center, 3, (0, 0, 255), -1)
                            
                            cv2.putText(frame, f"Ball {ball_count}", (center[0] - 15, center[1] - radius - 8), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

                            sector_label = self.get_sector_label(center)
                            detected_sectors.append(sector_label)
                            
                            cv2.putText(frame, sector_label, (center[0] - 15, center[1] + radius + 15), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, 
                                       self.VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 1)
        
        return detected_sectors, ball_count

    def get_sectors_as_string(self, detected_sectors):
        """Convert detected sectors to a formatted string - from objectTest.py"""
        if not detected_sectors:
            return "No balls detected"
        
        # Count occurrences of each sector
        sector_counts = {}
        for sector in detected_sectors:
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Format as string
        result_parts = []
        for sector, count in sector_counts.items():
            if count == 1:
                result_parts.append(f"{sector}")
            else:
                result_parts.append(f"{sector}({count})")
        
        return ", ".join(result_parts)

    def update_camera(self):
        # Only update if camera is running and initialized
        if not self.camera_running or self.picam2 is None:
            return
            
        try:
            frame = self.picam2.capture_array()
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

            # Detect all balls and their sectors using objectTest.py logic
            detected_sectors, ball_count = self.detect_multiple_balls_and_sectors(frame, hsv)
            self.detected_sectors = detected_sectors
            self.ball_count = ball_count
            
            # Get sectors as string for display
            sectors_string = self.get_sectors_as_string(detected_sectors)
            
            # Update UI labels
            self.balls_count_label.configure(text=f"Balls: {ball_count}")
            self.sectors_label.configure(text=f"Sectors:\n{sectors_string}")
            
            # Check if we have exactly 3 balls with valid sectors
            valid_sectors = [sector for sector in detected_sectors if sector != "Unknown"]
            
            # Handle settling time logic from objectTest.py
            if len(valid_sectors) == 3 and not self.balls_settled:
                if self.first_detection_time is None:
                    self.first_detection_time = time.time()
                    print(f"🕒 3 balls detected! Waiting {self.SETTLING_TIME} seconds for balls to settle...")
                
                # Calculate remaining time
                elapsed_time = time.time() - self.first_detection_time
                remaining_time = self.SETTLING_TIME - elapsed_time
                
                if remaining_time > 0:
                    # Display countdown
                    self.settling_label.configure(text=f"Settling... {remaining_time:.1f}s")
                else:
                    self.balls_settled = True
                    self.settling_label.configure(text="Balls settled! Ready for final round!")
                    print(f"✅ Balls have settled! Final count validation...")
                    print(f"🎯 Final ball positions: {sectors_string}")
            
            elif len(valid_sectors) != 3:
                # Reset if ball count changes
                self.first_detection_time = None
                self.balls_settled = False
                self.settling_label.configure(text="")
            
            # Check for game completion
            if len(valid_sectors) == 3 and self.balls_settled:
                self.settling_label.configure(text="GAME COMPLETE! Press button below!")
                # Auto-trigger ball scored after settling
                if not hasattr(self, 'auto_scored'):
                    self.auto_scored = True
                    self.after(1000, self.ball_scored)  # Auto-trigger after 1 second

            # Draw colorful sector lines and labels
            self.draw_sectors(frame)

            # Draw enhanced disc center
            cv2.circle(frame, self.DISC_CENTER, self.VISUAL_CONFIG['center_dot_size'], (255, 255, 255), -1)
            cv2.circle(frame, self.DISC_CENTER, self.VISUAL_CONFIG['center_dot_size'] + 2, (0, 0, 0), 2)

            # Display full-size camera frame (no resizing for better quality)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.config(image=imgtk)

            # Continue camera updates only if camera is still running
            if self.camera_running:
                self.after(30, self.update_camera)
                
        except Exception as e:
            print(f"[Camera Update Error] {e}")
            if self.camera_running:
                self.after(100, self.update_camera)  # Retry after a longer delay

    def ball_scored(self):
        self.score += 10
        self.successful_guesses += 1
        self.score_label.configure(text=f"SCORE:\n{self.score}")
        self.guesses_label.configure(text=f"GUESSES:\n{self.successful_guesses}")
        
        # Include sector information in the output
        sectors_string = self.get_sectors_as_string(self.detected_sectors)
        print(f"[GAME COMPLETE] Sensor detected {self.ball_count} balls!")
        print(f"[SECTORS] Final ball positions: {sectors_string}")
        print(f"[SCORE] Successful guesses: {self.successful_guesses}")
        
        # Store the detected sectors in the controller for final screen display
        self.controller.final_ball_sectors = self.detected_sectors.copy()
        self.controller.final_sectors_string = sectors_string
        
        # Clean up camera before transitioning
        self.cleanup_camera()
            
        self.controller.show_frame("FinalScreen")