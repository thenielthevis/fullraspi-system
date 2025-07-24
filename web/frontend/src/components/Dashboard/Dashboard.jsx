import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const prizes = [
  { name: "Amazon Gift Card", description: "Redeemable on Amazon for any purchase.", points: 500 },
  { name: "Bluetooth Speaker", description: "Portable speaker with high-quality sound.", points: 800 },
  { name: "T-shirt", description: "Official event T-shirt.", points: 300 },
  { name: "Coffee Mug", description: "Ceramic mug with event branding.", points: 200 },
  { name: "Gaming Headset", description: "Premium gaming headset with surround sound.", points: 1000 },
  { name: "Wireless Mouse", description: "High-precision wireless gaming mouse.", points: 600 },
];

const claimablePoints = [
  { key: 'daily', label: 'Daily Login', points: 100, desc: 'Claim once per day for logging in.' },
  { key: 'weekly', label: 'Weekly Bonus', points: 500, desc: 'Claim once per week for being active.' },
  { key: 'event', label: 'Event Reward', points: 300, desc: 'Special event reward. Claim once!' },
];

const Dashboard = () => {
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isVisible, setIsVisible] = useState({});
  const [notif, setNotif] = useState({ show: false, message: '', type: 'success' });
  const [currentPrizeIndex, setCurrentPrizeIndex] = useState(0);
  const [claimed, setClaimed] = useState(() => {
    // Try to load from localStorage/sessionStorage if you want persistence
    const saved = localStorage.getItem('claimedPoints');
    return saved ? JSON.parse(saved) : {};
  });
  const [claimedPrizes, setClaimedPrizes] = useState([]);
  const [claimedKeys, setClaimedKeys] = useState([]);
  const navigate = useNavigate();

  const visiblePrizes = prizes.slice(currentPrizeIndex, currentPrizeIndex + 3);

  const nextPrizes = () => {
    setCurrentPrizeIndex((prev) =>
      prev + 3 >= prizes.length ? 0 : prev + 3
    );
  };

  const prevPrizes = () => {
    setCurrentPrizeIndex((prev) =>
      prev - 3 < 0 ? Math.max(0, prizes.length - 3) : prev - 3
    );
  };

  useEffect(() => {
    const playerData = localStorage.getItem('playerData');
    const rfid = localStorage.getItem('rfid');

    if (playerData) {
      setPlayer(JSON.parse(playerData));
      setLoading(false);
    } else if (rfid) {
      fetchPlayerData(rfid);
    } else {
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    if (player) {
      // Fetch claimed prizes for the user
      axios.get(`http://localhost:8000/players/claimed_prizes/`, {
        params: { rfid_number: player.rfid_number }
      }).then(res => setClaimedPrizes(res.data));
    }
  }, [player]);

  useEffect(() => {
    if (player) {
      axios.get("http://localhost:8000/players/claimed_points/", {
        params: { rfid_number: player.rfid_number }
      }).then(res => setClaimedKeys(res.data));
    }
  }, [player]);

  const fetchPlayerData = async (rfid) => {
    try {
      const response = await axios.get(`http://localhost:8000/players/rfid/${rfid}`);
      if (response.status === 200) {
        setPlayer(response.data);
        localStorage.setItem('playerData', JSON.stringify(response.data));
      }
    } catch (error) {
      console.error('Error fetching player data:', error);
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const isPrizeClaimed = (prize) => claimedPrizes.includes(prize.name);

  const claimPrize = async (prize) => {
    if (isPrizeClaimed(prize)) {
      showNotification("You already claimed this prize.", 'error');
      return;
    }
    if (player.points >= prize.points) {
      try {
        const res = await axios.post("http://localhost:8000/players/claim_prizes/", null, {
          params: {
            rfid_number: player.rfid_number,
            prize_name: prize.name,
            points: prize.points
          }
        });
        setPlayer(prev => ({ ...prev, points: res.data.new_points }));
        localStorage.setItem('playerData', JSON.stringify({ ...player, points: res.data.new_points }));
        showNotification(`You have successfully claimed the prize: ${prize.name}`, 'success');
        // Optionally update claimedPrizes state here
        setClaimedPrizes(prev => [...prev, prize.name]);
      } catch (error) {
        showNotification(error.response?.data?.detail || "Failed to claim prize.", 'error');
      }
    } else {
      showNotification("You do not have enough points to claim this prize.", 'error');
    }
  };

  const claimPrizePoints = async (pointsToClaim = 100) => {
    try {
      const res = await axios.post("http://localhost:8000/players/claim_points/", null, {
        params: {
          rfid_number: player.rfid_number,
          points: pointsToClaim
        }
      });
      setPlayer(prev => ({ ...prev, points: res.data.new_points }));
      localStorage.setItem('playerData', JSON.stringify({ ...player, points: res.data.new_points }));
      showNotification(`You claimed ${pointsToClaim} points!`, 'success');
    } catch (err) {
      showNotification("Failed to claim points.", 'error');
    }
  };

  const isPointsPrizeClaimed = (item) => claimedKeys.includes(item.key);

  const claimPointsPrize = async (item) => {
    if (isPointsPrizeClaimed(item)) return;
    try {
      const res = await axios.post("http://localhost:8000/players/claim_points/", null, {
        params: {
          rfid_number: player.rfid_number,
          key: item.key,
          points: item.points
        }
      });
      setPlayer(prev => ({ ...prev, points: res.data.new_points }));
      setClaimedKeys(prev => [...prev, item.key]);
      showNotification(`You claimed ${item.points} points for ${item.label}!`, 'success');
    } catch (err) {
      showNotification(
        err.response?.data?.detail === "Already claimed"
          ? "You already claimed this reward."
          : "Failed to claim points.",
        'error'
      );
    }
  };

  const showNotification = (message, type) => {
    setNotif({ show: true, message, type });
    setTimeout(() => {
      setNotif({ show: false, message: '', type: 'success' });
    }, 3000);
  };

  const handleLogout = () => {
    localStorage.removeItem('playerData');
    localStorage.removeItem('rfid');
    navigate('/login');
  };

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('data-id');
          setIsVisible(prev => ({ ...prev, [id]: true }));
        }
      });
    }, {
      threshold: 0.1
    });

    const elements = document.querySelectorAll('[data-id]');
    elements.forEach(el => observer.observe(el));

    return () => {
      elements.forEach(el => observer.unobserve(el));
    };
  }, []);

  if (loading) {
    return <div style={styles.loading}>Loading...</div>;
  }

  if (!player) {
    return <div style={styles.error}>Player data not found</div>;
  }

  return (
    <div style={styles.dashboardPage}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🎮</span>
          <span style={styles.logoText}>Player Dashboard</span>
        </div>
        <div style={styles.playerInfo}>
          <span style={styles.pointsIcon}>⭐</span>
          <span>{player.points} PTS</span>
          <button style={styles.logoutButton} onClick={handleLogout}>Logout</button>
         
        </div>
      </div>

      {/* Main Content */}
      <div style={styles.heroSection}>
        <div style={styles.heroContent}>
          <h2 style={styles.subtitle}>Welcome Back</h2>
          <h1 style={styles.title}>{player.name}</h1>
          <p style={styles.description}>
            Check your stats, claim prizes, and climb the leaderboard!
          </p>
        </div>
      </div>

      {/* Prizes Section - Carousel Style */}
      <div style={styles.prizesSection}>
        <h1 style={styles.prizesTitle}>Claim Your Prizes</h1>
        {/* Container box for prizes */}
        <div style={{
          ...styles.prizesContainer,
          boxShadow: '0 6px 32px rgba(162, 89, 255, 0.15)',
          background: 'rgba(44, 27, 105, 0.15)',
          border: '2px solid #a259ff',
          borderRadius: '24px',
          marginTop: '2rem',
          marginBottom: '2rem',
          minHeight: '340px',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <button
            style={styles.navArrow}
            onClick={prevPrizes}
            disabled={currentPrizeIndex === 0}
            aria-label="Previous"
          >
            &#8592;
          </button>
          <div style={styles.prizesList}>
            {visiblePrizes.map((prize, idx) => (
              <div key={currentPrizeIndex + idx} style={styles.prizeCard} data-id={`prize-${currentPrizeIndex + idx}`}>
                <div style={styles.prizeImg}>
                  {/* Example icon, you can use a real image if you want */}
                  {prize.name === "Amazon Gift Card" && <span role="img" aria-label="gift">🎁</span>}
                  {prize.name === "Bluetooth Speaker" && <span role="img" aria-label="speaker">🔊</span>}
                  {prize.name === "T-shirt" && <span role="img" aria-label="tshirt">👕</span>}
                  {prize.name === "Coffee Mug" && <span role="img" aria-label="mug">☕</span>}
                  {prize.name === "Gaming Headset" && <span role="img" aria-label="headset">🎧</span>}
                  {prize.name === "Wireless Mouse" && <span role="img" aria-label="mouse">🖱️</span>}
                </div>
                <h2 style={styles.prizeHeading}>{prize.name}</h2>
                <div style={styles.prizeDesc}>{prize.description}</div>
                <div style={styles.prizePoints}>
                  <span>Points required:</span> <strong>{prize.points}</strong>
                </div>
                <button
                  style={{
                    ...styles.claimBtn,
                    background: isPrizeClaimed(prize) ? '#ccc' : styles.claimBtn.background,
                    cursor: isPrizeClaimed(prize) ? 'not-allowed' : 'pointer',
                    opacity: isPrizeClaimed(prize) ? 0.7 : 1,
                  }}
                  onClick={() => claimPrize(prize)}
                  disabled={isPrizeClaimed(prize)}
                >
                  {isPrizeClaimed(prize) ? "Claimed" : "Claim"}
                </button>
              </div>
            ))}
          </div>
          <button
            style={styles.navArrow}
            onClick={nextPrizes}
            disabled={currentPrizeIndex + 3 >= prizes.length}
            aria-label="Next"
          >
            &#8594;
          </button>
        </div>
        {/* Indicator */}
        <div style={styles.prizesIndicator}>
          {Array.from({ length: Math.ceil(prizes.length / 3) }, (_, i) => (
            <div
              key={i}
              style={{
                ...styles.indicator,
                ...(Math.floor(currentPrizeIndex / 3) === i ? styles.indicatorActive : {})
              }}
            />
          ))}
        </div>
      </div>

      {/* Claimable Points Section */}
      <div style={{
        display: 'flex',
        gap: '2rem',
        justifyContent: 'center',
        margin: '2rem 0'
      }}>
        {claimablePoints.map(item => (
          <div key={item.key} style={{
            background: 'rgba(255,255,255,0.07)',
            borderRadius: '20px',
            padding: '2rem',
            minWidth: '220px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(162, 89, 255, 0.08)',
            border: '1px solid rgba(162, 89, 255, 0.2)',
            opacity: claimed[item.key] ? 0.5 : 1
          }}>
            <h2 style={{ color: '#a259ff', marginBottom: 8 }}>{item.label}</h2>
            <div style={{ color: '#c7b6f7', marginBottom: 16 }}>{item.desc}</div>
            <div style={{ color: '#6c38cc', fontWeight: 700, fontSize: 18, marginBottom: 16 }}>
              +{item.points} Points
            </div>
            <button
              style={{
                ...styles.claimBtn,
                background: claimed[item.key] ? '#ccc' : styles.claimBtn.background,
                cursor: claimed[item.key] ? 'not-allowed' : 'pointer'
              }}
              onClick={() => claimPointsPrize(item)}
              disabled={claimed[item.key]}
            >
              {claimed[item.key] ? 'Claimed' : 'Claim'}
            </button>
          </div>
        ))}
      </div>

      {/* Notification */}
      {notif.show && (
        <div style={{
          position: 'fixed',
          top: '2rem',
          right: '2rem',
          background: notif.type === 'error'
            ? 'linear-gradient(90deg, #ff4e50, #f9d423)'
            : 'linear-gradient(90deg, #a259ff, #6c38cc)',
          color: 'white',
          padding: '1.2rem 2.5rem',
          borderRadius: '18px',
          boxShadow: '0 6px 32px rgba(162, 89, 255, 0.2)',
          fontWeight: 700,
          fontSize: '1.1rem',
          zIndex: 2000,
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          animation: 'fadeInNotif 0.5s'
        }}>
          <span>{notif.message}</span>
          <button onClick={() => setNotif({ show: false, message: '', type: 'success' })} style={{
            background: 'transparent',
            border: 'none',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '1.3rem',
            cursor: 'pointer'
          }}>×</button>
          <style>
            {`@keyframes fadeInNotif {
              from { opacity: 0; transform: translateY(-30px);}
              to { opacity: 1; transform: translateY(0);}
            }`}
          </style>
        </div>
      )}
    </div>
  );
};

const styles = {
  dashboardPage: {
    height: '100vh',
    width: '100vw',
    background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
    color: 'white',
    fontFamily: "'Press Start 2P', Tahoma, Geneva, Verdana, sans-serif",
    overflowX: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '2rem 2rem',
    background: 'linear-gradient(to right, #6c2ebf, #b266ff)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    backdropFilter: 'blur(10px)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '2.3rem',
    fontWeight: 'bold',
    color: 'white',
  },
  logoIcon: {
    fontSize: '1.8rem',
    marginRight: '8px',
  },
  playerInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
  },
  pointsIcon: {
    marginRight: '0.5rem',
    fontSize: '1.2rem',
  },
  logoutButton: {
    backgroundColor: 'white',
    color: '#8f00ff',
    padding: '0.6rem 1.2rem',
    fontWeight: 'bold',
    border: 'none',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 10px rgba(255, 255, 255, 0.2)',
  },
  heroSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
    padding: '6rem 3rem',
    minHeight: '80vh',
    position: 'relative',
  },
  heroContent: {
    maxWidth: '800px',
    zIndex: 2,
  },
  subtitle: {
    color: '#b266ff',
    fontSize: '1.5rem',
    textTransform: 'uppercase',
    fontWeight: 600,
    letterSpacing: '1.5px',
    marginBottom: '1rem',
  },
  title: {
    fontSize: '5rem',
    fontWeight: 900,
    lineHeight: '1.2',
    marginBottom: '1rem',
    color: 'white',
    textShadow: '0 4px 20px rgba(162, 89, 255, 0.3)',
  },
  description: {
    fontSize: '1.5rem',
    color: '#cccccc',
    marginBottom: '2.5rem',
    maxWidth: '600px',
    margin: '0 auto 2.5rem',
  },
  prizesSection: {
    padding: '2rem',
    textAlign: 'center',
  },
  prizesTitle: {
    fontSize: '2rem',
    marginBottom: '1rem',
  },
  prizesContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '1.5rem',
    margin: '0 auto',
    maxWidth: '900px',
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '20px',
    boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
    padding: '2rem 1rem',
  },
  navArrow: {
    fontSize: '2rem',
    background: 'none',
    border: 'none',
    color: '#a259ff',
    cursor: 'pointer',
    padding: '0.5rem 1rem',
    borderRadius: '50%',
    transition: 'background 0.2s',
    userSelect: 'none',
    outline: 'none',
    minWidth: '48px',
    minHeight: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  prizesList: {
    display: 'flex',
    gap: '2rem',
    justifyContent: 'center',
    flexWrap: 'nowrap',
    overflow: 'visible',
    width: '700px',
    minHeight: '320px',
  },
  prizeCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '20px',
    border: '1px solid rgba(162, 89, 255, 0.3)',
    boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
    padding: '2rem',
    width: '260px',
    minHeight: '320px',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    transition: 'all 0.3s ease',
    backdropFilter: 'blur(10px)',
    opacity: 1,
    animation: 'fadeInUp 0.8s both',
  },
  prizeImg: {
    width: '100px',
    height: '80px',
    backgroundColor: '#a259ff',
    borderRadius: '5  0%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '2rem',
    color: 'white',
    marginBottom: '1rem',
    fontWeight: 'bold',
  },
  prizeHeading: {
    color: '#a259ff',
    marginBottom: '10px',
    fontSize: '1.15rem',
    fontWeight: 700,
  },
  prizeDesc: {
    color: '#c7b6f7',
    marginBottom: '1.5rem',
    fontSize: '1rem',
    flexGrow: 1,
    
  },
  prizePoints: {
    color: '#6c38cc',
    fontSize: '1.1rem',
    fontWeight: 600,
    marginBottom: '1.5rem',
  },
  claimBtn: {
    background: 'linear-gradient(90deg, #a259ff, #6c38cc)',
    color: 'white',
    fontWeight: '700',
    fontSize: '1rem',
    border: 'none',
    borderRadius: '8px',
    padding: '0.8rem 2rem',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 10px rgba(162, 89, 255, 0.3)',
  },
  prizesIndicator: {
    display: 'flex',
    justifyContent: 'center',
    gap: '0.5rem',
    marginTop: '1rem',
  },
  indicator: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: '#c7b6f7',
    opacity: 0.5,
    transition: 'all 0.2s',
  },
  indicatorActive: {
    background: '#a259ff',
    opacity: 1,
    boxShadow: '0 0 8px #a259ff88',
  },
};

export default Dashboard;