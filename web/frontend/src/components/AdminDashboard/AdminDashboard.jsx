import React, { useEffect, useState } from 'react';
import { BarChart, PieChart, LineChart, AreaChart, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend, Pie, Cell, XAxis, YAxis, Line, Area, Bar } from 'recharts';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a259ff', '#ffbb28', '#00C49F', '#FF8042'];

const styles = {
  page: {
    minHeight: '100vh',
    width: '100vw',
    background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
    color: 'white',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    overflowX: 'hidden',
    paddingBottom: '3rem',
    letterSpacing: '0.03em',
  },
  navbar: {
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
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '1.3rem',
    letterSpacing: '0.05em',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '2.3rem',
    fontWeight: 'bold',
    color: 'white',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.08em',
  },
  logoIcon: {
    fontSize: '1.8rem',
    marginRight: '8px',
  },
  logoutBtn: {
    background: '#3f058aff',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    padding: '0.7rem 1.5rem',
    fontSize: '1rem',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    cursor: 'pointer',
    fontWeight: 700,
    transition: 'background 0.2s',
    marginLeft: '2rem',
    letterSpacing: '0.04em',
  },
  section: {
    maxWidth: '1500px',
    margin: '3rem auto 0 auto',
    padding: '2rem',
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '20px',
    boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  sectionTitle: {
    color: '#a259ff',
    fontSize: '2.2rem',
    fontWeight: 800,
    marginBottom: '2rem',
    letterSpacing: '0.08em',
    textAlign: 'center',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  chartsRow: {
    display: 'flex',
    gap: '2rem',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  chartCard: {
    flex: 1,
    minWidth: 350,
    background: 'rgba(255,255,255,0.07)',
    borderRadius: '20px',
    padding: '2rem',
    marginBottom: '2rem',
    boxShadow: '0 4px 20px rgba(162, 89, 255, 0.08)',
    border: '1px solid rgba(162, 89, 255, 0.2)',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '1.1rem',
    letterSpacing: '0.04em',
  },
  playerList: {
    background: 'rgba(255,255,255,0.07)',
    borderRadius: '20px',
    padding: '2rem',
    marginTop: '2rem',
    boxShadow: '0 4px 20px rgba(162, 89, 255, 0.08)',
    border: '1px solid rgba(162, 89, 255, 0.2)',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '1.1rem',
    letterSpacing: '0.04em',
  },
  playerItem: {
    color: '#c7b6f7',
    fontSize: '1.15rem',
    marginBottom: '1.2rem',
    fontWeight: 500,
    display: 'flex',
    justifyContent: 'space-evenly',
    alignItems: 'center',
    padding: '0.8rem 0.5rem',
    borderBottom: '1px solid rgba(162, 89, 255, 0.1)',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.04em',
    lineHeight: 1.5,
  },
  playerName: {
    flex: 1,
    textAlign: 'center',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '1.1rem',
    letterSpacing: '0.04em',
    lineHeight: 1.4,
    wordBreak: 'break-word',
  },
  playerRfid: {
    flex: 1,
    textAlign: 'center',
    color: '#82ca9d',
    fontSize: '1.1rem',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.04em',
    lineHeight: 1.4,
    wordBreak: 'break-word',
  },
  playerPoints: {
    flex: 1,
    textAlign: 'center',
    color: '#a259ff',
    fontWeight: 'bold',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    fontSize: '1.1rem',
    letterSpacing: '0.04em',
    lineHeight: 1.4,
    wordBreak: 'break-word',
  },
  adminBadge: {
    backgroundColor: '#ff8042',
    color: 'white',
    padding: '0.2rem 0.5rem',
    borderRadius: '5px',
    fontSize: '0.9rem',
    marginLeft: '1rem',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.04em',
  },
  loadingText: {
    color: '#a259ff',
    fontSize: '1.2rem',
    textAlign: 'center',
    padding: '2rem',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.04em',
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: '1.2rem',
    textAlign: 'center',
    padding: '2rem',
    fontFamily: "'Orbitron', 'Press Start 2P', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    letterSpacing: '0.04em',
  },
};

const getActiveUsersByCredits = (players, count = 5) =>
  [...players]
    .filter(p => p.credits > 0)
    .sort((a, b) => b.credits - a.credits)
    .slice(0, count)
    .map(p => ({ name: p.name, credits: p.credits }));

// Top 5 Active Users (by points)
const getTopActiveUsers = (players, count = 5) =>
  [...players]
    .sort((a, b) => b.points - a.points)
    .slice(0, count)
    .map(p => ({ name: p.name, points: p.points, rfid: p.rfid_number }));

// Top 5 Players with Highest Credits
const getTopPlayersByCredits = (players, count = 5) =>
  [...players]
    .sort((a, b) => b.credit - a.credit)
    .slice(0, count)
    .map(p => ({ name: p.name, credit: p.credit, rfid: p.rfid_number }));

const getPlayersWithMoreGames = (players, count = 5) =>
  [...players]
    .sort((a, b) => b.points - a.points)
    .slice(0, count)
    .map(p => ({
      name: p.name,
      points: p.points,
      rfid: p.rfid_number
    }));

// Most Players with Deducted Points (lowest points)
const getPlayersWithMostDeductedPoints = (players, count = 5) =>
  [...players]
    .sort((a, b) => a.points - b.points)
    .slice(0, count)
    .map(p => ({ name: p.name, points: p.points, rfid: p.rfid_number }));

// Weekly Credits Claimed (simulate)
const getWeeklyCreditsClaimed = (players) => {
  const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
  return weeks.map((week, i) => ({
    week,
    credits: players
      .filter((_, idx) => idx % 4 === i)
      .reduce((sum, p) => sum + (p.credit || 0), 0)
  }));
};

const getCombinedRanking = (players, count = 5) =>
  [...players]
    .map(p => ({
      name: p.name,
      total: (p.points || 0) + (p.credits || 0)
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, count);

const AdminDashboard = () => {

  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch players from backend server.js
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        // Use the correct backend port (3001)
        const response = await axios.get('http://localhost:3001/players/all');
        setPlayers(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load players. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchPlayers();
  }, []);

 // Logout handler
  const handleLogout = () => {
       localStorage.clear();
    navigate('/login');
    // Show success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #00C49F, #82ca9d);
      color: white;
      padding: 1rem 2rem;
      border-radius: 10px;
      font-family: 'Press Start 2P', Tahoma, Geneva, Verdana, sans-serif;
      font-size: 0.9rem;
      z-index: 10000;
      box-shadow: 0 4px 20px rgba(0, 196, 159, 0.3);
      animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = '✓ Successfully logged out!';
    
    // Add slide-in animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
      notification.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
        if (style.parentNode) {
          style.parentNode.removeChild(style);
        }
      }, 300);
    }, 3000);
  };

  // Custom tooltip styles
  const customTooltipStyle = {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    border: '1px solid #a259ff',
    borderRadius: '8px',
    color: 'white',
    fontSize: '12px',
    padding: '8px'
  };


  return (
    <div style={styles.page}>
      {/* Navbar */}
      <div style={styles.navbar}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🎮</span>
          <span>ArPi Admin</span>
        </div>
        <div style={{display: 'flex', alignItems: 'center'}}>
          <div style={{fontSize: '1.1rem', color: '#fff', fontWeight: 'bold'}}>Dashboard</div>
          <button style={styles.logoutBtn} onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {/* Analytics Section */}
      <div style={styles.section}>
        <div style={styles.sectionTitle}>Analytics</div>
        
        {/* Row 1 */}
        <div style={styles.chartsRow}>
          {/* 1. Top 5 Active Users (Most Credits) */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Top 5 Active Users (Points)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getTopActiveUsers(players)}>
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Bar dataKey="points" fill="#00C49F" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* 2. Top 5 Players with Highest Credits */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Top 5 Players with Highest Credits</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getTopPlayersByCredits(players)}
                  dataKey="credit"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#82ca9d"
                  label={entry => `${entry.name} (${entry.rfid})`}
                >
                  {getTopPlayersByCredits(players).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Row 2 */}
        <div style={styles.chartsRow}>
          {/* 3. Most Players with Deducted Points */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Players with Most Deducted Points</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={getPlayersWithMostDeductedPoints(players)}>
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Line type="monotone" dataKey="points" stroke="#ff8042" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {/* 4. Weekly Credits Claimed */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Weekly Credits Claimed</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={getWeeklyCreditsClaimed(players)}>
                <XAxis dataKey="week" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Area type="monotone" dataKey="credits" stroke="#ffc658" fill="#ffc658" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Row 3 */}
        <div style={styles.chartsRow}>
          {/* 5. Top 5 Players (Points + Credits) */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Top 5 Players (Points + Credits)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={getCombinedRanking(players)}>
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Area type="monotone" dataKey="total" stroke="#ffbb28" fill="#ffbb28" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          {/* 6. Players with Most Games Played (Radar Chart) */}
          <div style={styles.chartCard}>
            <h2 style={{color: '#a259ff'}}>Players with Most Games Played</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={getPlayersWithMoreGames(players)}>
                <PolarGrid />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis />
                <Radar name="Points" dataKey="points" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Tooltip />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

     {/* Player List Section */}
      <div style={styles.section}>
        <div style={styles.sectionTitle}>All Players ({players.length})</div>
        <div style={styles.playerList}>
          {loading ? (
            <div style={styles.loadingText}>Loading players...</div>
          ) : error ? (
            <div style={styles.errorText}>{error}</div>
          ) : players.length === 0 ? (
            <div style={styles.loadingText}>No players found.</div>
          ) : (
            <div>
              {players.map(player => (
                <div key={player.id} style={styles.playerItem}>
                  <div style={styles.playerName}>
                    {player.name}
                    {player.is_admin && (
                      <span style={styles.adminBadge}>ADMIN</span>
                    )}
                  </div>
                  <div style={{ flex: 1, textAlign: 'center', color: '#82ca9d', fontSize: '1.1rem' }}>
                    RFID: {player.uid}
                  </div>
                  <div style={styles.playerPoints}>
                    {player.points || 0} pts
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;