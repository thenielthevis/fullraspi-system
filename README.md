# Raspberry Pi Arcade System

A complete arcade game system built for Raspberry Pi with camera-based ball detection, RFID user authentication, and MQTT hardware control.

## Features

- **Multi-ball Detection**: Advanced computer vision using watershed algorithm and sector-based color detection
- **RFID Authentication**: User registration and authentication system
- **MQTT Hardware Control**: Communication with ESP32 controllers for sensors, LEDs, and motors
- **Real-time Camera Feed**: Live video processing with ball tracking and sector identification
- **Audio Integration**: Sound effects and background music using pygame
- **Database Management**: SQLite database for user management and scoring
- **Multiple Game Screens**: Complete arcade experience with welcome, instructions, gameplay, and rewards

## Hardware Requirements

- Raspberry Pi 4 (recommended)
- Pi Camera Module
- RFID Reader
- ESP32 microcontrollers for hardware control
- LEDs, sensors, and other arcade hardware
- Audio system/speakers

## Software Dependencies

See `requirements.txt` for Python package requirements:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/fullraspi-system.git
cd fullraspi-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python DbSetup.py
```

4. Configure hardware connections and MQTT settings in the respective files

5. Run the main application:
```bash
python main.py
```

## File Structure

- `main.py` - Main application entry point
- `screens/` - All game screen implementations
  - `welcome.py` - Welcome/start screen
  - `gameplay.py` - Main gameplay with camera feed
  - `add_credit.py` - Credit management
  - `instructions.py` - Game instructions
  - `final_screen.py` - Game completion screen
  - `rewards.py` - Rewards and scoring
- `DbSetup.py` - Database setup and user management
- `TESTCONTROLLER.py` - MQTT communication with hardware
- `objectTest.py` - Advanced ball detection and sector identification
- `Track.py` - HSV color calibration tool
- `assets/` - Images, sounds, and fonts
- `.gitignore` - Git ignore rules for clean repository

## Game Logic

1. **User Authentication**: RFID scan to identify registered users
2. **Credit System**: Coin insertion adds credits to user account
3. **Ball Detection**: Camera tracks up to 3 balls on the game disc
4. **Sector Identification**: Balls are identified by color-coded sectors (Red, Yellow, Blue, Green, Orange, Black)
5. **Settling Time**: 4-second waiting period for balls to settle before final detection
6. **Scoring**: Points awarded based on successful ball placement
7. **Hardware Integration**: LEDs, motors, and sensors controlled via MQTT

## Camera Detection

The system uses advanced computer vision techniques:
- HSV color space conversion for robust color detection
- Morphological operations for noise reduction
- Watershed algorithm for separating touching balls
- Distance transform for precise ball center detection
- Real-time sector identification with angle-based classification

## MQTT Communication

Hardware control via MQTT topics:
- `esp32/control/esp1` - Primary controller (RFID, proximity sensors)
- `esp32/control/esp2` - Secondary controller (LEDs, motors)

## Development

- **Language**: Python 3.11+
- **GUI Framework**: tkinter
- **Computer Vision**: OpenCV, NumPy
- **Hardware Communication**: MQTT (paho-mqtt)
- **Database**: SQLite3
- **Audio**: pygame

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Camera Issues
- Ensure Pi Camera is enabled in `raspi-config`
- Check camera module connections
- Verify picamera2 installation

### MQTT Connection Issues
- Check ESP32 IP addresses and network connectivity
- Verify MQTT broker is running
- Check firewall settings

### Database Issues
- Ensure proper file permissions for `arpi.sqlite`
- Run `DbSetup.py` to recreate database if corrupted

### Performance Issues
- Consider reducing camera resolution for better performance
- Adjust detection parameters in `gameplay.py`
- Ensure adequate power supply for Raspberry Pi
