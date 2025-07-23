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
        
        # Ball color detection from objectTest.py (restored original)
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
        """Simple and reliable ball detection using basic contour approach"""
        detected_sectors = []
        ball_count = 0
        
        # Threshold for ball color (using original HSV range)
        mask = cv2.inRange(hsv, self.lower_ball, self.upper_ball)
        
        # Debug: Check if any pixels match the color range
        mask_pixels = cv2.countNonZero(mask)
        print(f"[DEBUG] Found {mask_pixels} pixels matching ball color")

        # Simple morphological operations to clean up noise
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Find contours - simple and reliable
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("[DEBUG] No contours found")
            return detected_sectors, ball_count
        
        print(f"[DEBUG] Found {len(contours)} contours")
        
        # Sort contours by area (largest first) to get the most prominent balls
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        valid_balls = []  # Store valid ball detections for overlap checking
        
        # Process each contour with simple validation
        for i, contour in enumerate(contours):
            # Basic area filtering - reasonable ball sizes
            area = cv2.contourArea(contour)
            if area < 500 or area > 5000:  # Simple area range
                print(f"[DEBUG] Contour {i}: area {area} out of range")
                continue
            
            # Get circle properties
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            
            # Simple radius validation - typical ball sizes
            if radius < 12 or radius > 50:  # Conservative radius range
                print(f"[DEBUG] Contour {i}: radius {radius} out of range")
                continue
            
            # Simple circularity check to ensure it's round-ish
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.4:  # Must be reasonably circular
                print(f"[DEBUG] Contour {i}: circularity {circularity:.2f} too low")
                continue
            
            # KEY LOGIC: Circles cannot overlap - check distance between centers
            is_overlapping = False
            for existing_center, existing_radius in valid_balls:
                distance = np.sqrt((center[0] - existing_center[0])**2 + (center[1] - existing_center[1])**2)
                min_distance = (radius + existing_radius) * 1.2  # Circles + 20% buffer
                
                if distance < min_distance:
                    print(f"[DEBUG] Contour {i}: overlapping with existing ball (distance: {distance:.1f}, min: {min_distance:.1f})")
                    is_overlapping = True
                    break
            
            if is_overlapping:
                continue
            
            # This is a valid, non-overlapping ball
            valid_balls.append((center, radius))
            ball_count += 1
            
            print(f"[DEBUG] ✅ Ball {ball_count}: center={center}, radius={radius}, area={area}, circularity={circularity:.2f}")
            
            # Get sector for this ball
            sector_label = self.get_sector_label(center)
            detected_sectors.append(sector_label)
            
            # Draw the ball detection
            cv2.circle(frame, center, radius, (0, 255, 255), self.VISUAL_CONFIG['ball_circle_thickness'])
            cv2.circle(frame, center, 3, (0, 0, 255), -1)  # Center dot
            
            # Add ball number
            cv2.putText(frame, f"Ball {ball_count}", (center[0] - 15, center[1] - radius - 8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Show sector for each ball
            cv2.putText(frame, sector_label, (center[0] - 15, center[1] + radius + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, 
                       self.VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 1)
            
            # Stop after finding 3 balls (game requires exactly 3)
            if ball_count >= 3:
                print(f"[DEBUG] Reached maximum of 3 balls, stopping detection")
                break
        
        print(f"[DEBUG] Final result: {ball_count} balls detected in sectors: {detected_sectors}")
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
                if self.balls_settled:
                    print(f"⚠️ BALL COUNT CHANGED AFTER SETTLING!")
                    print(f"   - Previous state: settled with 3 balls")
                    print(f"   - Current valid sectors: {len(valid_sectors)}")
                    print(f"   - Current sectors: {valid_sectors}")
                    print(f"   - Resetting settling state...")
                
                self.first_detection_time = None
                self.balls_settled = False
                self.settling_label.configure(text="")
            
            # Check for game completion with enhanced validation
            if len(valid_sectors) == 3 and self.balls_settled:
                print(f"🎮 GAME COMPLETION CHECK:")
                print(f"   - Valid sectors: {len(valid_sectors)} (need 3) ✅")
                print(f"   - Balls settled: {self.balls_settled} ✅")
                print(f"   - Current sectors: {valid_sectors}")
                print(f"   - Ball count detected: {self.ball_count}")
                print(f"   - Auto-scored attribute exists: {hasattr(self, 'auto_scored')}")
                if hasattr(self, 'auto_scored'):
                    print(f"   - Auto-scored value: {self.auto_scored}")
                
                self.settling_label.configure(text="🎯 3 BALLS DETECTED! Auto-advancing to results...")
                
                # Auto-trigger ball scored after settling
                if not hasattr(self, 'auto_scored') or not self.auto_scored:
                    print(f"🚀 TRIGGERING AUTO SCORE - All conditions met!")
                    self.auto_scored = True
                    # Reduce delay for faster progression
                    self.after(1500, self.ball_scored)  # 1.5 seconds for final confirmation
                else:
                    print(f"⚠️ Auto-score already triggered, waiting for transition...")

            # Draw colorful sector lines and labels
            self.draw_sectors(frame)

            # Draw enhanced disc center
            cv2.circle(frame, self.DISC_CENTER, self.VISUAL_CONFIG['center_dot_size'], (255, 255, 255), -1)
            cv2.circle(frame, self.DISC_CENTER, self.VISUAL_CONFIG['center_dot_size'] + 2, (0, 0, 0), 2)

            # Convert BGR back to RGB for proper display (OpenCV draws in BGR, PIL expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display full-size camera frame (no resizing for better quality)
            img = Image.fromarray(frame_rgb)
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
        
        # Debug: Log what we're actually storing
        print(f"🔍 STORING FOR FINAL SCREEN:")
        print(f"   - Raw detected_sectors: {self.detected_sectors}")
        print(f"   - Sectors stored: {self.controller.final_ball_sectors}")
        print(f"   - String stored: {self.controller.final_sectors_string}")
        print(f"   - Length of sectors: {len(self.detected_sectors)}")
        
        # Clean up camera before transitioning
        self.cleanup_camera()
            
        self.controller.show_frame("FinalScreen")