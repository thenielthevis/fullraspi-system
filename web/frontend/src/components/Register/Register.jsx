// import React, { useState } from 'react';
// import axios from 'axios';
// import { useNavigate } from 'react-router-dom';

// const Register = () => {
//   const [name, setName] = useState('');
//   const [rfidNumber, setRfidNumber] = useState('');
//   const [notification, setNotification] = useState(null);
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const response = await axios.post('http://localhost:8000/create-players/', {
//         name: name,
//         rfid_number: rfidNumber,
//       });
//       if (response.status === 200) {
//         const data = response.data;
//         setNotification({
//           type: 'success',
//           message: `Successfully registered: ${data.name} with RFID number: ${data.rfid_number}!`,
//         });
//         setTimeout(() => {
//           navigate('/login');
//         }, 1500);
//       } else {
//         setNotification({
//           type: 'error',
//           message: 'Registration failed. Please try again.',
//         });
//       }
//     } catch (error) {
//       setNotification({
//         type: 'error',
//         message: 'An error occurred. Please check your connection.',
//       });
//     }
//   };

//   const closeNotification = () => {
//     setNotification(null);
//   };

//   return (
//     <div style={styles.registerPage}>
//       <div style={styles.registerContainer}>
//         <div style={styles.registerLeft}>
//           <svg style={styles.arcadePixel} viewBox="0 0 48 48">
//             <rect x="6" y="18" width="36" height="12" rx="6" fill="#b266ff" stroke="#fff" strokeWidth="2" />
//             <circle cx="16" cy="24" r="3" fill="#fff" />
//             <circle cx="32" cy="24" r="3" fill="#fff" />
//             <rect x="22" y="22" width="4" height="4" fill="#fff" />
//           </svg>
//           <div style={styles.registerTitle}>Welcome to ArPi</div>
//           <div style={styles.registerDescription}>
//             Enter the world of ArPi!<br />
//             Register with your name and RFID Number.<br />
//             <span style={{ fontSize: '0.9em', color: '#fff', opacity: 0.7 }}>
//               A Raspberry Pi Arcade Game
//             </span>
//           </div>
//         </div>
//         <div style={styles.registerRight}>
//           <form style={styles.registerForm} onSubmit={handleSubmit}>
//             <h1 style={styles.registerFormTitle}>Register</h1>
//             <div style={{ height: 24 }} /> {/* Spacer */}

//             <input
//               type="text"
//               placeholder="Name"
//               value={name}
//               onChange={(e) => setName(e.target.value)}
//               required
//               style={{
//                 ...styles.input,
//                 fontSize: '1.2rem',
//                 letterSpacing: '2px',
//                 padding: '14px 0',
//               }}
//             />
//             <div style={{ height: 24 }} /> {/* Spacer */}
//             <input
//               type="text"
//               placeholder="RFID Number"
//               value={rfidNumber}
//               onChange={(e) => setRfidNumber(e.target.value)}
//               required
//               style={{
//                 ...styles.input,
//                 fontSize: '1.2rem',
//                 letterSpacing: '2px',
//                 padding: '14px 0',
//               }}
//             />
//             <div style={{ height: 24 }} /> {/* Spacer */}
//             <button type="submit" style={styles.button}>Register</button>
//             <div style={{ height: 24 }} /> {/* Spacer */}
//             <div style={styles.registerFooter}>Powered by Project-Arpi</div>
//             <div style={{ marginTop: '18px', textAlign: 'center' }}>
//               <span style={{ color: '#b266ff', fontSize: '1rem', cursor: 'pointer', textDecoration: 'underline' }}
//                 onClick={() => navigate('/login')}>
//                 I already have an account
//               </span>
//             </div>
//               <div style={{ height: 24 }} /> {/* Spacer */}
//           </form>

//         </div>
//       </div>


//       {notification && (
//         <div style={{ ...styles.notification, ...(notification.type === 'error' ? styles.notificationError : {}) }}>
//           <div style={styles.notificationMessage}>{notification.message}</div>
//           <button style={styles.notificationBtn} onClick={closeNotification}>OK</button>
//         </div>
//       )}

//     </div>


//   );
// };

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [name, setName] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [notification, setNotification] = useState(null);
  const navigate = useNavigate();

  const handleRfidScan = async () => {
    if (!name.trim()) {
      setNotification({
        type: 'error',
        message: 'Please enter your name before scanning your RFID.',
      });
      return;
    }

    setIsScanning(true);
    setNotification({
      type: 'info',
      message: 'Please tap your RFID card on the scanner...',
    });

    try {
      const scanResponse = await axios.post('http://localhost:3001/rfid-scan');
      if (scanResponse.data.success) {
        const rfidUid = scanResponse.data.uid;

        // Proceed to register the user with the scanned RFID
        const response = await axios.post('http://localhost:3001/rfid-register', {
          rfid: rfidUid,
          name: name,
        });

        if (response.status === 200) {
          setNotification({
            type: 'success',
            message: `Successfully registered: ${name} with RFID: ${rfidUid}`,
          });
          setTimeout(() => {
            navigate('/login');
          }, 1500);
        }
      }
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setNotification({
          type: 'error',
          message: 'RFID already registered. Please use a different RFID.',
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
    <div style={styles.registerPage}>
      <div style={styles.registerContainer}>
        <div style={styles.registerLeft}>
          <svg style={styles.arcadePixel} viewBox="0 0 48 48">
            <rect x="6" y="18" width="36" height="12" rx="6" fill="#b266ff" stroke="#fff" strokeWidth="2" />
            <circle cx="16" cy="24" r="3" fill="#fff" />
            <circle cx="32" cy="24" r="3" fill="#fff" />
            <rect x="22" y="22" width="4" height="4" fill="#fff" />
          </svg>
          <div style={styles.registerTitle}>Welcome to ArPi</div>
          <div style={styles.registerDescription}>
            Enter the world of ArPi!<br />
            Register with your name and RFID.<br />
            <span style={{ fontSize: '0.9em', color: '#fff', opacity: 0.7 }}>
              A Raspberry Pi Arcade Game
            </span>
          </div>
        </div>
        <div style={styles.registerRight}>
          <form style={styles.registerForm} onSubmit={(e) => e.preventDefault()}>
            <h1 style={styles.registerFormTitle}>Register</h1>
            <div style={{ height: 24 }} /> 

            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{
                ...styles.input,
                fontSize: '1.2rem',
                letterSpacing: '2px',
                padding: '14px 0',
              }}
            />
            <div style={{ height: 24 }} /> 
            <button
              type="button"
              style={{
                ...styles.button,
                ...(isScanning ? styles.buttonScanning : {}),
              }}
              onClick={handleRfidScan}
              disabled={isScanning}
            >
              {isScanning ? 'Scanning...' : 'Scan RFID to Register'}
            </button>
            <div style={{ height: 24 }} /> 
            <div style={styles.registerFooter}>Powered by Project-Arpi</div>
            <div style={{ marginTop: '18px', textAlign: 'center' }}>
              <span style={{ color: '#b266ff', fontSize: '1rem', cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => navigate('/login')}>
                I already have an account
              </span>
            </div>
            <div style={{ height: 24 }} /> 
          </form>
        </div>
      </div>

      {notification && (
        <div style={{ ...styles.notification, ...(notification.type === 'error' ? styles.notificationError : {}) }}>
          <div style={styles.notificationMessage}>{notification.message}</div>
          <button style={styles.notificationBtn} onClick={closeNotification}>OK</button>
        </div>
      )}
    </div>
  );
};

const styles = {
  registerPage: {
    height: '100vh',
    width: '100%',
    background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflowY: 'auto',
    overflowX: 'hidden',
  },
  registerContainer: {
    display: 'flex',
    width: '100vw',
    height: '100vh',
    background: 'rgba(18, 0, 26, 0.5)',
    overflow: 'hidden',
    backdropFilter: 'blur(4px)',
  },
  registerLeft: {
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
  registerTitle: {
    fontFamily: "'Press Start 2P', 'Orbitron', 'Segoe UI', Arial, sans-serif",
    fontSize: '2.2rem',
    color: '#fff',
    textShadow: '0 0 16px #b266ff, 0 2px 24px #6c2ebf',
    letterSpacing: '2px',
    background: 'linear-gradient(90deg, #b266ff, #fff, #6c2ebf)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  registerDescription: {
    fontFamily: "'Orbitron', 'Segoe UI', Arial, sans-serif",
    fontSize: '1.2rem',
    color: '#b266ff',
    textShadow: '0 0 8px #000',
    letterSpacing: '1px',
  },
  registerRight: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(36, 0, 70, 0.8)',
    position: 'relative',
    zIndex: 2,
    boxShadow: '-2px 0 24px rgba(108, 46, 191, 0.266) inset',
  },
  registerForm: {
    width: '100%',
    maxWidth: '370px',
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
  registerFormTitle: {
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
  inputFocus: { // Apply manually with state if needed
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
  buttonHover: { // Apply manually with state if needed
    background: 'linear-gradient(90deg, #6c2ebf 0%, #b266ff 100%)',
    transform: 'translateY(-2px) scale(1.05)',
    boxShadow: '0 4px 24px rgba(178, 102, 255, 0.8)',
  },
  registerFooter: {
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
  notificationBtnHover: { // Apply manually with state if needed
    backgroundColor: '#b266ff',
  },
};

export default Register;