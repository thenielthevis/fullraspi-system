import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [notification, setNotification] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const navigate = useNavigate();

  const handleRfidScan = async () => {
    setIsScanning(true);
    setNotification({
      type: 'info',
      message: 'Please tap your RFID card on the scanner...',
    });

    try {
      // Call the RFID scan API
      const scanResponse = await axios.post('http://localhost:3001/rfid-scan');
      
      if (scanResponse.data.success) {
        const rfidUid = scanResponse.data.uid;
        
        // Now check if this RFID is registered
        const playerResponse = await axios.get(`http://localhost:8000/players/rfid/${rfidUid}`);
        
        if (playerResponse.status === 200) {
          const playerData = playerResponse.data;
          localStorage.setItem('playerData', JSON.stringify(playerData));
          localStorage.setItem('rfid', rfidUid);

          // Redirect based on admin status
          if (playerData.is_admin) {
            navigate('/admin-dashboard');
          } else {
            navigate('/dashboard');
          }
        } else {
          setNotification({
            type: 'error',
            message: 'RFID not registered. Please sign up first.',
          });
        }
      }
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setNotification({
          type: 'error',
          message: 'RFID not registered. Please sign up first.',
        });
      } else if (error.response && error.response.status === 408) {
        setNotification({
          type: 'error',
          message: 'RFID scan timeout. Please try again.',
        });
      } else {
        setNotification({
          type: 'error',
          message: 'An error occurred. Please check your connection.',
        });
      }
    } finally {
      setIsScanning(false);
    }
  };

  const closeNotification = () => {
    setNotification(null);
  };

  return (
    <div style={styles.loginPage}>
      <div style={styles.loginContainer}>
        <div style={styles.loginLeft}>
          <svg style={styles.arcadePixel} viewBox="0 0 48 48">
            <rect x="6" y="18" width="36" height="12" rx="6" fill="#b266ff" stroke="#fff" strokeWidth="2"/>
            <circle cx="16" cy="24" r="3" fill="#fff"/>
            <circle cx="32" cy="24" r="3" fill="#fff"/>
            <rect x="22" y="22" width="4" height="4" fill="#fff"/>
          </svg>
          <div style={styles.loginTitle}>Welcome to ArPi</div>
          <div style={styles.loginDescription}>
            Enter the world of ArPi!<br />
            Tap the button below and scan your RFID to log in.<br />
            <span style={{fontSize: '0.9em', color: '#fff', opacity: 0.7}}>
              A Raspberry Pi Arcade Game
            </span>
          </div>
        </div>
        <div style={styles.loginRight}>
          <div style={styles.loginForm}>
            <h1 style={styles.loginFormTitle}>Game Login</h1>
            <div style={{ height: 24 }} /> {/* Spacer */}
            <div style={styles.scanInstructions}>
              Tap your RFID card on the scanner when prompted
            </div>
            <div style={{ height: 24 }} /> {/* Spacer */}
            <button 
              type="button" 
              style={{
                ...styles.button,
                ...(isScanning ? styles.buttonScanning : {})
              }}
              onClick={handleRfidScan}
              disabled={isScanning}
            >
              {isScanning ? 'Scanning...' : 'Scan RFID to Log In'}
            </button>
            <div style={{ height: 24 }} /> {/* Spacer */}
            <div style={styles.loginFooter}>Powered by Project-Arpi</div>
            <div style={{ marginTop: '18px', textAlign: 'center' }}>
              <span style={{ color: '#b266ff', fontSize: '1rem', cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => navigate('/register')}>
                I don't have an account yet
              </span>
            </div>

               <div style={{ marginTop: '18px', textAlign: 'center' }}>
              <span style={{ color: '#b266ff', fontSize: '1rem', cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => navigate('/')}>
                Go back to homepage
              </span>
            </div>
              <div style={{ height: 24 }} /> {/* Spacer */}
          </div>
        </div>
      </div>

      {notification && (
        <div style={{
          ...styles.notification, 
          ...(notification.type === 'error' ? styles.notificationError : 
              notification.type === 'info' ? styles.notificationInfo : {})
        }}>
          <div style={styles.notificationMessage}>{notification.message}</div>
          <button style={styles.notificationBtn} onClick={closeNotification}>OK</button>
        </div>
      )}
    </div>
  );
};

const styles = {
  loginPage: {
    height: '100vh', 
    width: '100%', 
    background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  
  },
  loginContainer: {
 display: 'flex',
    width: '100vw',
    height: '100vh',
    background: 'rgba(18, 0, 26, 0.5)',
    overflow: 'hidden',
    backdropFilter: 'blur(4px)',
  },
  loginLeft: {
    flex: 1.2,
    background: 'linear-gradient(135deg, #12001a 60%, #3c096c 100%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    textAlign: 'center',
    position: 'relative',
    zIndex: 1,
    boxShadow: '2px 0 24px rgba(108, 46, 191, 0.266) inset',
  },
  arcadePixel: {
    width: '60px',
    height: '60px',
    display: 'block',
    filter: 'drop-shadow(0 0 8px #b266ff)',
  },
  loginTitle: {
    fontFamily: "'Press Start 2P', 'Orbitron', 'Segoe UI', Arial, sans-serif",
    fontSize: '2.2rem',
    color: '#fff',
    textShadow: '0 0 16px #b266ff, 0 2px 24px #6c2ebf',
    letterSpacing: '2px',
    background: 'linear-gradient(90deg, #b266ff, #fff, #6c2ebf)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  loginDescription: {
    fontFamily: "'Orbitron', 'Segoe UI', Arial, sans-serif",
    fontSize: '1.2rem',
    color: '#b266ff',
    textShadow: '0 0 8px #000',
    letterSpacing: '1px',
  },
  loginRight: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(36, 0, 70, 0.8)',
    position: 'relative',
    boxShadow: '-2px 0 24px rgba(108, 46, 191, 0.266) inset',
  },
  loginForm: {
    width: '200%',
    maxWidth: '400px',
    background: 'rgba(36, 0, 70, 0.8)',
    border: '2px solid #b266ff',
    borderRadius: '18px',
    boxShadow: '0 0 32px rgba(178, 102, 255, 0.333), 0 0 8px rgba(0, 0, 0, 0.5) inset',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    position: 'relative',
    zIndex: 2,
    backdropFilter: 'blur(2px)',
    
  },
  loginFormTitle: {
    color: '#fff',
    fontSize: '1.5rem',
    fontFamily: "'Press Start 2P', 'Orbitron', 'Segoe UI', Arial, sans-serif",
    textShadow: '0 0 8px #b266ff, 0 2px 16px #6c2ebf',
    letterSpacing: '2px',
    textAlign: 'center',
    background: 'linear-gradient(90deg, #b266ff, #fff, #6c2ebf)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  input: {
    width: '100%',
    border: '2px solid #6c2ebf',
    borderRadius: '10px',
    background: '#12001a',
    color: '#fff',
    fontSize: '1rem',
    fontFamily: "'Press Start 2P', 'Orbitron', 'Segoe UI', Arial, sans-serif",
    outline: 'none',
    boxShadow: '0 2px 8px rgba(108, 46, 191, 0.133)',
    transition: 'background 0.2s, border 0.2s',
    textAlign: 'center',
    letterSpacing: '1px',
  },
  inputFocus: {
    background: '#240046',
    border: '2px solid #b266ff',
  },
  button: {
    width: '100%',
    background: 'linear-gradient(90deg, #b266ff 0%, #6c2ebf 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '12px',
    fontSize: '1.1rem',
    fontFamily: "'Press Start 2P', 'Orbitron', 'Segoe UI', Arial, sans-serif",
    cursor: 'pointer',
    boxShadow: '0 2px 16px rgba(178, 102, 255, 0.6), 0 0 8px rgba(108, 46, 191, 0.333) inset',
    transition: 'background 0.2s, transform 0.2s, box-shadow 0.2s',
    letterSpacing: '2px',
    textShadow: '0 1px 4px #000',
  },
  buttonHover: {
    background: 'linear-gradient(90deg, #6c2ebf 0%, #b266ff 100%)',
    transform: 'translateY(-2px) scale(1.05)',
    boxShadow: '0 4px 24px rgba(178, 102, 255, 0.8)',
  },
  buttonScanning: {
    background: 'linear-gradient(90deg, #4a1a5c 0%, #6c2ebf 100%)',
    opacity: 0.7,
    cursor: 'not-allowed',
  },
  scanInstructions: {
    color: '#b266ff',
    fontSize: '1rem',
    textAlign: 'center',
    fontFamily: "'Orbitron', 'Segoe UI', Arial, sans-serif",
    letterSpacing: '1px',
    opacity: 0.9,
  },
  loginFooter: {
    color: '#b266ff',
    fontSize: '0.8rem',
    textAlign: 'center',
    opacity: 0.8,
    letterSpacing: '1px',
    textShadow: '0 0 8px #000',
  },
  notification: {
    position: 'fixed',
    top: '20%',
    left: '50%',
    transform: 'translateX(-50%)',
    backgroundColor: '#6c2ebf',
    color: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
    zIndex: 1000,
    maxWidth: '400px',
    width: '100%',
    textAlign: 'center',
    transition: 'opacity 0.5s ease, top 0.5s ease',
  },
  notificationError: {
    backgroundColor: '#240046',
  },
  notificationInfo: {
    backgroundColor: '#4a1a5c',
    border: '2px solid #b266ff',
  },
  notificationMessage: {
    fontSize: '1.2rem',
  },
  notificationBtn: {
    backgroundColor: '#fff',
    color: '#6c2ebf',
    padding: '8px 16px',
    fontSize: '1rem',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  notificationBtnHover: {
    backgroundColor: '#b266ff',
  },
};

export default Login;