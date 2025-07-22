import cv2
import numpy as np
import math
import time
from picamera2 import Picamera2

# ========== CAMERA SETUP ==========
FRAME_WIDTH, FRAME_HEIGHT = 1280, 960
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# ========== SETTLING TIME CONFIG ==========
SETTLING_TIME = 4  # seconds to wait after detecting 3 balls
first_detection_time = None
balls_settled = False

# ========== DISC CENTER (manually set if needed) ==========
DISC_CENTER = (615, 430)  # Adjust this to match your actual disc's center

# ========== SECTOR SETUP ==========
# Custom angle ranges (label, start_angle, end_angle)
sectors = [
    ("Red",    -35,  23),
    ("Yellow", 25, 80),
    ("Blue", 82, 145),
    ("Green",147, 202),
    ("Orange",205, 263),
    ("Black",265, 324)
]

# ========== BALL COLOR DETECTION ==========
lower_ball = np.array([129, 102, 194])
upper_ball = np.array([179, 255, 255])

# ========== VISUAL SETTINGS ==========
VISUAL_CONFIG = {
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

# ========== HELPER FUNCTIONS ==========
def get_sector_label(center):
    dx = center[0] - DISC_CENTER[0]
    dy = DISC_CENTER[1] - center[1]  # Y inverted in image coords
    angle = math.degrees(math.atan2(dy, dx))
    angle = (angle + 360) % 360  # normalize to [0, 360)

    for label, start, end in sectors:
        if start <= angle < end:
            return label
    return "Unknown"

def draw_sectors(frame):
    """Draw colorful sector lines and labels"""
    for label, angle_start, angle_end in sectors:
        # Get color for this sector
        color = VISUAL_CONFIG['sector_colors'].get(label, (200, 200, 200))
        
        # Draw start line
        angle_rad = math.radians(angle_start)
        x2 = int(DISC_CENTER[0] + VISUAL_CONFIG['line_length'] * math.cos(angle_rad))
        y2 = int(DISC_CENTER[1] - VISUAL_CONFIG['line_length'] * math.sin(angle_rad))
        cv2.line(frame, DISC_CENTER, (x2, y2), color, VISUAL_CONFIG['line_thickness'])

        # Draw label in middle of sector with colored background
        mid_angle = math.radians((angle_start + angle_end) / 2)
        lx = int(DISC_CENTER[0] + 250 * math.cos(mid_angle))
        ly = int(DISC_CENTER[1] - 250 * math.sin(mid_angle))
        
        # Add colored background for text
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (lx - text_size[0]//2 - 5, ly - text_size[1] - 5), 
                     (lx + text_size[0]//2 + 5, ly + 5), color, -1)
        cv2.putText(frame, label, (lx - text_size[0]//2, ly), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def detect_multiple_balls_and_sectors(frame, hsv):
    """Detect multiple balls and return their sectors using advanced separation techniques"""
    detected_sectors = []
    
    # Threshold for ball color
    mask = cv2.inRange(hsv, lower_ball, upper_ball)

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
        if area < 300:  # Minimum area for a ball (reduced from 500)
            continue
            
        # Find contour for this ball
        contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
            
        contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)
        
        # Additional validation: check if radius is reasonable for a ball
        if radius < 8 or radius > 100:  # Adjust these values based on your ball size
            continue
            
        ball_count += 1
        
        # Draw colorful ball detection
        cv2.circle(frame, center, radius, (0, 255, 255), VISUAL_CONFIG['ball_circle_thickness'])
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        
        # Add ball number
        cv2.putText(frame, f"Ball {ball_count}", (center[0] - 25, center[1] - radius - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        sector_label = get_sector_label(center)
        detected_sectors.append(sector_label)
        
        # Show sector for each ball
        cv2.putText(frame, sector_label, (center[0] - 20, center[1] + radius + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                   VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 2)
    
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
                if cv2.contourArea(contour) > 300:  # ignore small noise
                    # Check if this is likely multiple balls by analyzing the contour
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    contour_area = cv2.contourArea(contour)
                    solidity = float(contour_area) / hull_area
                    
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)
                    
                    # If solidity is low, might be multiple touching balls
                    if solidity < 0.7 and radius > 25:
                        # Try to estimate number of balls based on area
                        estimated_ball_area = np.pi * (radius / 1.5) ** 2
                        num_balls = max(1, int(contour_area / estimated_ball_area))
                        
                        # Create multiple detection points for touching balls
                        moments = cv2.moments(contour)
                        if moments['m00'] != 0:
                            cx = int(moments['m10'] / moments['m00'])
                            cy = int(moments['m01'] / moments['m00'])
                            
                            for i in range(min(num_balls, 3)):  # Max 3 balls
                                ball_count += 1
                                offset_x = (i - 1) * radius // 2
                                ball_center = (cx + offset_x, cy)
                                
                                cv2.circle(frame, ball_center, radius // 2, (0, 255, 255), VISUAL_CONFIG['ball_circle_thickness'])
                                cv2.circle(frame, ball_center, 5, (0, 0, 255), -1)
                                
                                cv2.putText(frame, f"Ball {ball_count}", (ball_center[0] - 25, ball_center[1] - radius // 2 - 10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                
                                sector_label = get_sector_label(ball_center)
                                detected_sectors.append(sector_label)
                                
                                cv2.putText(frame, sector_label, (ball_center[0] - 20, ball_center[1] + radius // 2 + 20), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                                           VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 2)
                    else:
                        # Single ball
                        ball_count += 1
                        
                        cv2.circle(frame, center, radius, (0, 255, 255), VISUAL_CONFIG['ball_circle_thickness'])
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)
                        
                        cv2.putText(frame, f"Ball {ball_count}", (center[0] - 25, center[1] - radius - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        sector_label = get_sector_label(center)
                        detected_sectors.append(sector_label)
                        
                        cv2.putText(frame, sector_label, (center[0] - 20, center[1] + radius + 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                                   VISUAL_CONFIG['sector_colors'].get(sector_label, (255, 255, 255)), 2)
    
    return detected_sectors, ball_count

def get_sectors_as_string(detected_sectors):
    """Convert detected sectors to a formatted string"""
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

# ========== MAIN LOOP ==========
while True:
    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Detect all balls and their sectors
    detected_sectors, ball_count = detect_multiple_balls_and_sectors(frame, hsv)
    
    # Get sectors as string for use in other files
    sectors_string = get_sectors_as_string(detected_sectors)
    
    # Display ball count and sectors summary
    cv2.putText(frame, f"Balls detected: {ball_count}", (20, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    
    if detected_sectors:
        cv2.putText(frame, f"Sectors: {sectors_string}", (20, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        # Only print during detection phase, not during settling
        if first_detection_time is None:
            print(f"Balls in sectors: {sectors_string}")
    
    # Check if we have exactly 3 balls with valid sectors
    valid_sectors = [sector for sector in detected_sectors if sector != "Unknown"]
    
    # Handle settling time logic
    if len(valid_sectors) == 3 and not balls_settled:
        if first_detection_time is None:
            first_detection_time = time.time()
            print(f"🕒 3 balls detected! Waiting {SETTLING_TIME} seconds for balls to settle...")
        
        # Calculate remaining time
        elapsed_time = time.time() - first_detection_time
        remaining_time = SETTLING_TIME - elapsed_time
        
        if remaining_time > 0:
            # Display countdown
            cv2.putText(frame, f"Settling... {remaining_time:.1f}s", (20, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 3)
            cv2.putText(frame, "Balls detected, waiting to settle", (20, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            balls_settled = True
            print(f"✅ Balls have settled! Final count validation...")
            # Print the final result only once when timer completes
            print(f"🎯 Final ball positions: {sectors_string}")
    
    elif len(valid_sectors) != 3:
        # Reset if ball count changes
        first_detection_time = None
        balls_settled = False
    
    # Only proceed with game completion if balls have settled
    if len(valid_sectors) == 3 and balls_settled:
        print(f"\n🎯 GAME COMPLETE! All 3 balls detected with valid sectors:")
        print(f"Final result: {sectors_string}")
        
        
        cv2.putText(frame, "Press Any Key To commence final round", (20, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw colorful sector lines and labels
        draw_sectors(frame)
        
        # Draw enhanced disc center
        cv2.circle(frame, DISC_CENTER, VISUAL_CONFIG['center_dot_size'], (255, 255, 255), -1)
        cv2.circle(frame, DISC_CENTER, VISUAL_CONFIG['center_dot_size'] + 2, (0, 0, 0), 2)
        
        # Show final frame
        cv2.imshow("Ball Tracker", frame)
        cv2.waitKey(0)  # Wait for any key press
        break

    # Draw colorful sector lines and labels
    draw_sectors(frame)

    # Draw enhanced disc center
    cv2.circle(frame, DISC_CENTER, VISUAL_CONFIG['center_dot_size'], (255, 255, 255), -1)
    cv2.circle(frame, DISC_CENTER, VISUAL_CONFIG['center_dot_size'] + 2, (0, 0, 0), 2)

    # Show output
    cv2.imshow("Ball Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.close()




