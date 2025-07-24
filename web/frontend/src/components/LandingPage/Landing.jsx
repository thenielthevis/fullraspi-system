import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Prizes and Players array data
const prizes = [
  {
    name: "Amazon Gift Card",
    description: "Redeemable on Amazon for any purchase.",
    image: "/images/prizes/amazon.png",
    points: 500,
  },
  {
    name: "Bluetooth Speaker",
    description: "Portable speaker with high-quality sound.",
    image: "/images/prizes/speaker.png",
    points: 800,
  },
  {
    name: "T-shirt",
    description: "Official event T-shirt.",
    image: "/images/prizes/tshirt.png",
    points: 300,
  },
  {
    name: "Coffee Mug",
    description: "Ceramic mug with event branding.",
    image: "/images/prizes/mug.png",
    points: 200,
  },
  {
    name: "Gaming Headset",
    description: "Premium gaming headset with surround sound.",
    image: "/images/prizes/headset.png",
    points: 1000,
  },
  {
    name: "Wireless Mouse",
    description: "High-precision wireless gaming mouse.",
    image: "/images/prizes/mouse.png",
    points: 600,
  },
];

const players = [
  { id: 1, name: "Alice", points: 120 },
  { id: 2, name: "Bob", points: 110 },
  { id: 3, name: "Charlie", points: 95 },
  { id: 4, name: "Diana", points: 80 },
  { id: 5, name: "Eve", points: 75 },
  { id: 6, name: "Frank", points: 65 },
  { id: 7, name: "Grace", points: 50 },
  { id: 8, name: "Henry", points: 45 },
];

const LandingPage = () => {
  const [activeSection, setActiveSection] = useState("hero");
  const [currentPrizeIndex, setCurrentPrizeIndex] = useState(0);
  const [isVisible, setIsVisible] = useState({});
  const [userPoints, setUserPoints] = useState(0); 
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const scrollToSection = (sectionId) => {
    setActiveSection(sectionId);
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
  };

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

    const handleLoginRedirect = () => {
    navigate('/login');  // Redirect to /login route
  };

  // Intersection Observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible((prev) => ({
            ...prev,
            [entry.target.id]: entry.isIntersecting,
          }));
        });
      },
      { threshold: 0.1 }
    );

    const sections = document.querySelectorAll(".section");
    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  const visiblePrizes = prizes.slice(currentPrizeIndex, currentPrizeIndex + 3);

  // Fetch user info on mount (if logged in)
  useEffect(() => {
    const rfid = localStorage.getItem("rfid");
    if (rfid) {
      axios
        .get(`http://localhost:3001/players/rfid/${rfid}`)
        .then((response) => {
          setUser(response.data);
          setUserPoints(response.data.points);
        })
        .catch(() => {
          navigate("/login");
        });
    }
  }, [navigate]);

  // Claim prize logic
  const claimPrize = async (prize) => {
    if (!user) {
      alert("Please log in first.");
      return;
    }
    if (userPoints >= prize.points) {
      try {
        // Deduct points from user in backend
        const res = await axios.post("http://localhost:3001/players/deduct_points/", null, {
          params: {
            rfid_number: user.rfid_number,
            points: prize.points
          }
        });
        setUserPoints(res.data.new_points);
        alert(`You have claimed the prize: ${prize.name}`);
      } catch (err) {
        alert("Error updating points.");
      }
    } else {
      alert("You do not have enough points to claim this prize.");
    }
  };

  return (
    <div style={styles.landingPage}>
      {/* Navbar */}
      <div style={styles.navbar}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🎮</span>
          <span style={styles.logoText}>ArPi</span>
        </div>
        <nav style={styles.navLinks}>
          <button style={styles.navButton} onClick={() => scrollToSection("hero")}>Home</button>
          <button style={styles.navButton} onClick={() => scrollToSection("prizes")}>Prizes</button>
          <button style={styles.navButton} onClick={() => scrollToSection("leaderboard")}>Leaderboard</button>
        </nav>
        <div style={styles.pointsAndLogin}>
          <div style={styles.pointsDisplay}>
            <span style={styles.pointsIcon}>⭐</span>
            <span>{userPoints} PTS</span>
          </div>
           <button style={styles.LoginBtn} onClick={handleLoginRedirect}>Log In</button> 
           <button style={styles.SignupBtn} onClick={() => navigate('/register')}>Register</button>
        </div>
      </div>

      {/* Hero Section */}
      <div 
        id="hero" 
        className="section" 
        style={{
          ...styles.heroSection,
          ...(isVisible.hero ? styles.fadeInUp : styles.hidden)
        }}
      >
        <div style={styles.heroContent}>
          <h2 style={styles.subtitle}>Welcome to the Event</h2>
          <h1 style={styles.title}>Join the Challenge</h1>
          <p style={styles.description}>
            Participate, earn points, and claim amazing prizes.
          </p>
          <button style={styles.playBtn}>Play Now</button>
        </div>
        <div style={styles.heroGraphics}>
          <div style={{...styles.floatingObject, ...styles.float1}}>🥽</div>
          <div style={{...styles.floatingObject, ...styles.float2}}>🎮</div>
          <div style={{...styles.floatingObject, ...styles.float3}}>🏆</div>
        </div>
      </div>

      {/* Prizes Section */}
      <div 
        id="prizes" 
        className="section" 
        style={{
          ...styles.prizesSection,
          ...(isVisible.prizes ? styles.fadeInUp : styles.hidden)
        }}
      >
        <div style={styles.prizesContainer}>
          <h1 style={styles.prizesTitle}>Claim Your Prizes</h1>
          
          <div style={styles.prizesNavigation}>
            <button 
              style={styles.navArrow} 
              onClick={prevPrizes}
              disabled={currentPrizeIndex === 0}
            >
              ←
            </button>
            
            <div style={styles.prizesList}>
              {visiblePrizes.map((prize, idx) => (
                <div 
                  key={currentPrizeIndex + idx} 
                  style={{
                    ...styles.prizeCard,
                    animationDelay: `${idx * 0.1}s`
                  }}
                >
                  <div style={styles.prizeImg}>{prize.name.charAt(0)}</div>
                  <h2 style={styles.prizeHeading}>{prize.name}</h2>
                  <div style={styles.prizeDesc}>{prize.description}</div>
                  <div style={styles.prizePoints}>
                    <span>Points required:</span> <strong>{prize.points}</strong>
                  </div>
                  <button style={styles.claimBtn} onClick={() => claimPrize(prize)}>Claim</button>
                </div>
              ))}
            </div>
            
            <button 
              style={styles.navArrow} 
              onClick={nextPrizes}
              disabled={currentPrizeIndex + 3 >= prizes.length}
            >
              →
            </button>
          </div>
          
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
      </div>

      {/* Leaderboard Section */}
      <div 
        id="leaderboard" 
        className="section" 
        style={{
          ...styles.leaderboardSection,
          ...(isVisible.leaderboard ? styles.fadeInUp : styles.hidden)
        }}
      >
        <h2 style={styles.leaderboardTitle}>Player Rankings</h2>
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Rank</th>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Points</th>
              </tr>
            </thead>
            <tbody>
              {players.map((player, index) => (
                <tr key={player.id} style={styles.tr}>
                  <td style={styles.td}>{index + 1}</td>
                  <td style={styles.td}>{player.name}</td>
                  <td style={{...styles.td, ...styles.points}}>{player.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

  const styles = {
    landingPage: {
      
     width: '100vw',
    height: '100vh',
    margin: 0,
    padding: 0,
    background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
    color: 'white',
    fontFamily: "'Press Start 2P', Tahoma, Geneva, Verdana, sans-serif",
    overflowX: 'hidden',

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

    logoText: {},

    navLinks: {
      display: 'flex',
      gap: '2rem',
      alignItems: 'center',
    },

    navButton: {
      background: 'transparent',
      color: 'white',
      fontSize: '1.2rem',
      border: 'none',
      cursor: 'pointer',
      transition: 'color 0.3s ease, transform 0.2s ease',
      padding: '0.5rem 1rem',
      borderRadius: '8px',
    },

    pointsAndLogin: {
      display: 'flex',
      alignItems: 'center',
      gap: '1.5rem',
    },

    pointsDisplay: {
      display: 'flex',
      alignItems: 'center',
      background: 'rgba(255, 255, 255, 0.1)',
      padding: '0.5rem 0.5rem',
      borderRadius: '15px',
      fontSize: '1.1rem',
      fontWeight: 'bold',
      color: 'white',
      border: '1px solid rgba(162, 89, 255, 0.3)',
    },

    pointsIcon: {
      marginRight: '0.5rem',
      fontSize: '1.2rem',
    },

    LoginBtn: {
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

    SignupBtn: {
      backgroundColor: 'black',
      color: 'white',
      padding: '0.6rem 1.2rem',
      fontWeight: 'bold',
      border: 'none', 
      borderRadius: '25px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      boxShadow: '0 2px 10px rgba(178, 102, 255, 0.2)',
    },

    heroSection: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',

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

    playBtn: {
      background: 'linear-gradient(90deg, #b266ff, #8f00ff)',
      color: 'white',
      padding: '1rem 2.2rem',
      fontSize: '1.3rem',
      border: 'none',
      borderRadius: '25px',
      cursor: 'pointer',
      fontWeight: 'bold',
      boxShadow: '0 6px 20px rgba(178, 102, 255, 0.4)',
      transition: 'all 0.3s ease',
    },

    heroGraphics: {
      marginTop: '3rem',
      display: 'flex',
      justifyContent: 'center',
      gap: '2rem',
      position: 'relative',
    },

    floatingObject: {
      width: '80px',
      height: '80px',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '2px solid #b266ff',
      borderRadius: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '2rem',
      backdropFilter: 'blur(10px)',
    },

    float1: {
      animation: 'float 4s ease-in-out infinite',
    },

    float2: {
      animation: 'float 4s ease-in-out infinite 1.3s',
    },

    float3: {
      animation: 'float 4s ease-in-out infinite 2.6s',
    },

    prizesSection: {
      padding: '4rem 2rem',
      background: 'linear-gradient(135deg, rgba(44, 27, 105, 0.3) 0%, rgba(108, 46, 191, 0.3) 100%)',
    },

    prizesContainer: {
      maxWidth: '1200px',
      margin: '0 auto',
    },

    prizesTitle: {
      color: '#a259ff',
      marginBottom: '3rem',
      textAlign: 'center',
      fontSize: '2.5rem',
      fontWeight: 800,
      letterSpacing: '1px',
    },

    prizesNavigation: {
      display: 'flex',
      alignItems: 'center',
      gap: '2rem',
      justifyContent: 'center',
      marginBottom: '2rem',
    },

    navArrow: {
      background: 'linear-gradient(90deg, #a259ff, #6c38cc)',
      color: 'white',
      border: 'none',
      borderRadius: '50%',
      width: '50px',
      height: '50px',
      fontSize: '1.5rem',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 15px rgba(162, 89, 255, 0.3)',
    },

    prizesList: {
      display: 'flex',
      gap: '2rem',
      justifyContent: 'center',
    },

    prizeCard: {
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      border: '1px solid rgba(162, 89, 255, 0.3)',
      boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
      padding: '2rem',
      width: '280px',
      minHeight: '400px',
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)',
    },

    prizeImg: {
      width: '80px',
      height: '80px',
      backgroundColor: '#a259ff',
      borderRadius: '50%',
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
      fontSize: '1.35rem',
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
      marginTop: '2rem',
    },

    indicator: {
      width: '12px',
      height: '12px',
      borderRadius: '50%',
      backgroundColor: 'rgba(162, 89, 255, 0.3)',
      transition: 'all 0.3s ease',
    },

    indicatorActive: {
      backgroundColor: '#a259ff',
      transform: 'scale(1.2)',
    },

    leaderboardSection: {
      padding: '4rem 2rem',
      background: 'linear-gradient(135deg, rgba(44, 27, 105, 0.5) 0%, rgba(108, 46, 191, 0.5) 100%)',
    },

    leaderboardTitle: {
      color: '#a259ff',
      textAlign: 'center',
      fontSize: '2.5rem',
      fontWeight: 800,
      marginBottom: '3rem',
    },

    tableWrapper: {
      maxWidth: '800px',
      margin: '0 auto',
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      overflow: 'hidden',
      boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
      backdropFilter: 'blur(10px)',
    },

    table: {
      width: '100%',
      borderCollapse: 'collapse',
    },

    th: {
      backgroundColor: 'rgba(162, 89, 255, 0.2)',
      color: '#a259ff',
      padding: '1rem',
      textAlign: 'left',
      fontWeight: 'bold',
      fontSize: '1.1rem',
    },

    tr: {
      borderBottom: '1px solid rgba(162, 89, 255, 0.1)',
      transition: 'background-color 0.3s ease',
    },

    td: {
      padding: '1rem',
      color: '#c7b6f7',
    },

    points: {
      color: '#a259ff',
      fontWeight: 'bold',
    },

    hidden: {
      opacity: 0,
      transform: 'translateY(50px)',
    },

    fadeInUp: {
      opacity: 1,
      transform: 'translateY(0)',
      transition: 'all 0.8s ease-out',
    },
  };

  export default LandingPage;

// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import axios from 'axios';

// const prizes = [
//   {
//     name: "Amazon Gift Card",
//     description: "Redeemable on Amazon for any purchase.",
//     image: "/images/prizes/amazon.png",
//     points: 500,
//   },
//   {
//     name: "Bluetooth Speaker",
//     description: "Portable speaker with high-quality sound.",
//     image: "/images/prizes/speaker.png",
//     points: 800,
//   },
//   {
//     name: "T-shirt",
//     description: "Official event T-shirt.",
//     image: "/images/prizes/tshirt.png",
//     points: 300,
//   },
//   {
//     name: "Coffee Mug",
//     description: "Ceramic mug with event branding.",
//     image: "/images/prizes/mug.png",
//     points: 200,
//   },
//   {
//     name: "Gaming Headset",
//     description: "Premium gaming headset with surround sound.",
//     image: "/images/prizes/headset.png",
//     points: 1000,
//   },
//   {
//     name: "Wireless Mouse",
//     description: "High-precision wireless gaming mouse.",
//     image: "/images/prizes/mouse.png",
//     points: 600,
//   },
// ];

// const players = [
//   { id: 1, name: "Alice", points: 120 },
//   { id: 2, name: "Bob", points: 110 },
//   { id: 3, name: "Charlie", points: 95 },
//   { id: 4, name: "Diana", points: 80 },
//   { id: 5, name: "Eve", points: 75 },
//   { id: 6, name: "Frank", points: 65 },
//   { id: 7, name: "Grace", points: 50 },
//   { id: 8, name: "Henry", points: 45 },
// ];

// const LandingPage = () => {
//   const [activeSection, setActiveSection] = useState("hero");
//   const [currentPrizeIndex, setCurrentPrizeIndex] = useState(0);
//   const [isVisible, setIsVisible] = useState({});
//   const [userPoints, setUserPoints] = useState(150); 
//   const navigate = useNavigate();

//   const scrollToSection = (sectionId) => {
//     setActiveSection(sectionId);
//     document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
//   };

//   const nextPrizes = () => {
//     setCurrentPrizeIndex((prev) =>
//       prev + 3 >= prizes.length ? 0 : prev + 3
//     );
//   };

//   const prevPrizes = () => {
//     setCurrentPrizeIndex((prev) => 
//       prev - 3 < 0 ? Math.max(0, prizes.length - 3) : prev - 3
//     );
//   };

//     const handleLoginRedirect = () => {
//     navigate('/login');  // Redirect to /login route
//   };

//   // Intersection Observer for animations
//   useEffect(() => {
//     const observer = new IntersectionObserver(
//       (entries) => {
//         entries.forEach((entry) => {
//           setIsVisible((prev) => ({
//             ...prev,
//             [entry.target.id]: entry.isIntersecting,
//           }));
//         });
//       },
//       { threshold: 0.1 }
//     );

//     const sections = document.querySelectorAll(".section");
//     sections.forEach((section) => observer.observe(section));

//     return () => observer.disconnect();
//   }, []);

//   const visiblePrizes = prizes.slice(currentPrizeIndex, currentPrizeIndex + 3);

//     // Handle prize claiming logic
//   const claimPrize = (prize) => {
//     if (userPoints >= prize.points) {
//       // Proceed with claiming the prize
//       setUserPoints(userPoints - prize.points);
//       alert(`You have claimed the prize: ${prize.name}`);
//     } else {
//       alert("You do not have enough points to claim this prize.");
//     }
//   };

//   useEffect(() => {
//     const rfid = localStorage.getItem("rfid");
//     if (rfid) {
//       axios
//         .get(`http://localhost:8000/players/rfid/${rfid}`)
//         .then((response) => {
//           setUser(response.data);
//           setUserPoints(response.data.points); 
//         })
//         .catch((error) => {
//           console.error("Error fetching player info:", error);
//           navigate("/login"); 
//         });
//     } else {
//       navigate("/login"); 
//     }
//   }, [navigate]);


//   return (
//     <div style={styles.landingPage}>
//       {/* Navbar */}
//       <div style={styles.navbar}>
//         <div style={styles.logo}>
//           <span style={styles.logoIcon}>🎮</span>
//           <span style={styles.logoText}>ArPi</span>
//         </div>
//         <nav style={styles.navLinks}>
//           <button style={styles.navButton} onClick={() => scrollToSection("hero")}>Home</button>
//           <button style={styles.navButton} onClick={() => scrollToSection("prizes")}>Prizes</button>
//           <button style={styles.navButton} onClick={() => scrollToSection("leaderboard")}>Leaderboard</button>
//         </nav>
//         <div style={styles.pointsAndLogin}>
//           <div style={styles.pointsDisplay}>
//             <span style={styles.pointsIcon}>⭐</span>
//             <span>{userPoints} PTS</span>
//           </div>
//            <button style={styles.LoginBtn} onClick={handleLoginRedirect}>Log In</button> 
//            <button style={styles.SignupBtn} onClick={() => navigate('/register')}>Register</button>
//         </div>
//       </div>

//       {/* Hero Section */}
//       <div 
//         id="hero" 
//         className="section" 
//         style={{
//           ...styles.heroSection,
//           ...(isVisible.hero ? styles.fadeInUp : styles.hidden)
//         }}
//       >
//         <div style={styles.heroContent}>
//           <h2 style={styles.subtitle}>Welcome to the Event</h2>
//           <h1 style={styles.title}>Join the Challenge</h1>
//           <p style={styles.description}>
//             Participate, earn points, and claim amazing prizes.
//           </p>
//           <button style={styles.playBtn}>Play Now</button>
//         </div>
//         <div style={styles.heroGraphics}>
//           <div style={{...styles.floatingObject, ...styles.float1}}>🥽</div>
//           <div style={{...styles.floatingObject, ...styles.float2}}>🎮</div>
//           <div style={{...styles.floatingObject, ...styles.float3}}>🏆</div>
//         </div>
//       </div>

//       {/* Prizes Section */}
//       <div 
//         id="prizes" 
//         className="section" 
//         style={{
//           ...styles.prizesSection,
//           ...(isVisible.prizes ? styles.fadeInUp : styles.hidden)
//         }}
//       >
//         <div style={styles.prizesContainer}>
//           <h1 style={styles.prizesTitle}>Claim Your Prizes</h1>
          
//           <div style={styles.prizesNavigation}>
//             <button 
//               style={styles.navArrow} 
//               onClick={prevPrizes}
//               disabled={currentPrizeIndex === 0}
//             >
//               ←
//             </button>
            
//             <div style={styles.prizesList}>
//               {visiblePrizes.map((prize, idx) => (
//                 <div 
//                   key={currentPrizeIndex + idx} 
//                   style={{
//                     ...styles.prizeCard,
//                     animationDelay: `${idx * 0.1}s`
//                   }}
//                 >
//                   <div style={styles.prizeImg}>{prize.name.charAt(0)}</div>
//                   <h2 style={styles.prizeHeading}>{prize.name}</h2>
//                   <div style={styles.prizeDesc}>{prize.description}</div>
//                   <div style={styles.prizePoints}>
//                     <span>Points required:</span> <strong>{prize.points}</strong>
//                   </div>
//                   <button style={styles.claimBtn} onClick={() => claimPrize(prize)}>Claim</button>
//                 </div>
//               ))}
//             </div>
            
//             <button 
//               style={styles.navArrow} 
//               onClick={nextPrizes}
//               disabled={currentPrizeIndex + 3 >= prizes.length}
//             >
//               →
//             </button>
//           </div>
          
//           <div style={styles.prizesIndicator}>
//             {Array.from({ length: Math.ceil(prizes.length / 3) }, (_, i) => (
//               <div 
//                 key={i} 
//                 style={{
//                   ...styles.indicator,
//                   ...(Math.floor(currentPrizeIndex / 3) === i ? styles.indicatorActive : {})
//                 }}
//               />
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* Leaderboard Section */}
//       <div 
//         id="leaderboard" 
//         className="section" 
//         style={{
//           ...styles.leaderboardSection,
//           ...(isVisible.leaderboard ? styles.fadeInUp : styles.hidden)
//         }}
//       >
//         <h2 style={styles.leaderboardTitle}>Player Rankings</h2>
//         <div style={styles.tableWrapper}>
//           <table style={styles.table}>
//             <thead>
//               <tr>
//                 <th style={styles.th}>Rank</th>
//                 <th style={styles.th}>Name</th>
//                 <th style={styles.th}>Points</th>
//               </tr>
//             </thead>
//             <tbody>
//               {players.map((player, index) => (
//                 <tr key={player.id} style={styles.tr}>
//                   <td style={styles.td}>{index + 1}</td>
//                   <td style={styles.td}>{player.name}</td>
//                   <td style={{...styles.td, ...styles.points}}>{player.points}</td>
//                 </tr>
//               ))}
//             </tbody>
//           </table>
//         </div>
//       </div>
//     </div>
//   );
// };

// const styles = {
//   landingPage: {
//     height: '100vh', 
//     width: '100%', 
//     background: 'linear-gradient(120deg, #12001a 0%, #240046 100%)',
//     color: 'white',
//     fontFamily: "'Press Start 2P', Tahoma, Geneva, Verdana, sans-serif",
//     overflowY: 'auto', 
//     overflowX: 'hidden',
//   },

//   navbar: {
//     display: 'flex',
//     justifyContent: 'space-between',
//     alignItems: 'center',
//     padding: '2rem 2rem',
//     background: 'linear-gradient(to right, #6c2ebf, #b266ff)',
//     position: 'sticky',
//     top: 0,
//     zIndex: 1000,
//     backdropFilter: 'blur(10px)',
//     boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
//   },

//   logo: {
//     display: 'flex',
//     alignItems: 'center',
//     fontSize: '2.3rem',
//     fontWeight: 'bold',
//     color: 'white',
//   },

//   logoIcon: {
//     fontSize: '1.8rem',
//     marginRight: '8px',
//   },

//   logoText: {},

//   navLinks: {
//     display: 'flex',
//     gap: '2rem',
//     alignItems: 'center',
//   },

//   navButton: {
//     background: 'transparent',
//     color: 'white',
//     fontSize: '1.2rem',
//     border: 'none',
//     cursor: 'pointer',
//     transition: 'color 0.3s ease, transform 0.2s ease',
//     padding: '0.5rem 1rem',
//     borderRadius: '8px',
//   },

//   pointsAndLogin: {
//     display: 'flex',
//     alignItems: 'center',
//     gap: '1.5rem',
//   },

//   pointsDisplay: {
//     display: 'flex',
//     alignItems: 'center',
//     background: 'rgba(255, 255, 255, 0.1)',
//     padding: '0.5rem 0.5rem',
//     borderRadius: '15px',
//     fontSize: '1.1rem',
//     fontWeight: 'bold',
//     color: 'white',
//     border: '1px solid rgba(162, 89, 255, 0.3)',
//   },

//   pointsIcon: {
//     marginRight: '0.5rem',
//     fontSize: '1.2rem',
//   },

//   LoginBtn: {
//     backgroundColor: 'white',
//     color: '#8f00ff',
//     padding: '0.6rem 1.2rem',
//     fontWeight: 'bold',
//     border: 'none',
//     borderRadius: '25px',
//     cursor: 'pointer',
//     transition: 'all 0.3s ease',
//     boxShadow: '0 2px 10px rgba(255, 255, 255, 0.2)',
//   },

//   SignupBtn: {
//     backgroundColor: 'black',
//     color: 'white',
//     padding: '0.6rem 1.2rem',
//     fontWeight: 'bold',
//     border: 'none', 
//     borderRadius: '25px',
//     cursor: 'pointer',
//     transition: 'all 0.3s ease',
//     boxShadow: '0 2px 10px rgba(178, 102, 255, 0.2)',
//   },

//   heroSection: {
//     display: 'flex',
//     flexDirection: 'column',
//     alignItems: 'center',
//     textAlign: 'center',
//     padding: '6rem 3rem',
//     minHeight: '80vh',
//     position: 'relative',
//   },

//   heroContent: {
//     maxWidth: '800px',
//     zIndex: 2,
//   },

//   subtitle: {
//     color: '#b266ff',
//     fontSize: '1.5rem',
//     textTransform: 'uppercase',
//     fontWeight: 600,
//     letterSpacing: '1.5px',
//     marginBottom: '1rem',
//   },

//   title: {
//     fontSize: '5rem',
//     fontWeight: 900,
//     lineHeight: '1.2',
//     marginBottom: '1rem',
//     color: 'white',
//     textShadow: '0 4px 20px rgba(162, 89, 255, 0.3)',
//   },

//   description: {
//     fontSize: '1.5rem',
//     color: '#cccccc',
//     marginBottom: '2.5rem',
//     maxWidth: '600px',
//     margin: '0 auto 2.5rem',
//   },

//   playBtn: {
//     background: 'linear-gradient(90deg, #b266ff, #8f00ff)',
//     color: 'white',
//     padding: '1rem 2.2rem',
//     fontSize: '1.3rem',
//     border: 'none',
//     borderRadius: '25px',
//     cursor: 'pointer',
//     fontWeight: 'bold',
//     boxShadow: '0 6px 20px rgba(178, 102, 255, 0.4)',
//     transition: 'all 0.3s ease',
//   },

//   heroGraphics: {
//     marginTop: '3rem',
//     display: 'flex',
//     justifyContent: 'center',
//     gap: '2rem',
//     position: 'relative',
//   },

//   floatingObject: {
//     width: '80px',
//     height: '80px',
//     background: 'rgba(255, 255, 255, 0.1)',
//     border: '2px solid #b266ff',
//     borderRadius: '20px',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     fontSize: '2rem',
//     backdropFilter: 'blur(10px)',
//   },

//   float1: {
//     animation: 'float 4s ease-in-out infinite',
//   },

//   float2: {
//     animation: 'float 4s ease-in-out infinite 1.3s',
//   },

//   float3: {
//     animation: 'float 4s ease-in-out infinite 2.6s',
//   },

//   prizesSection: {
//     padding: '4rem 2rem',
//     background: 'linear-gradient(135deg, rgba(44, 27, 105, 0.3) 0%, rgba(108, 46, 191, 0.3) 100%)',
//   },

//   prizesContainer: {
//     maxWidth: '1200px',
//     margin: '0 auto',
//   },

//   prizesTitle: {
//     color: '#a259ff',
//     marginBottom: '3rem',
//     textAlign: 'center',
//     fontSize: '2.5rem',
//     fontWeight: 800,
//     letterSpacing: '1px',
//   },

//   prizesNavigation: {
//     display: 'flex',
//     alignItems: 'center',
//     gap: '2rem',
//     justifyContent: 'center',
//     marginBottom: '2rem',
//   },

//   navArrow: {
//     background: 'linear-gradient(90deg, #a259ff, #6c38cc)',
//     color: 'white',
//     border: 'none',
//     borderRadius: '50%',
//     width: '50px',
//     height: '50px',
//     fontSize: '1.5rem',
//     cursor: 'pointer',
//     transition: 'all 0.3s ease',
//     boxShadow: '0 4px 15px rgba(162, 89, 255, 0.3)',
//   },

//   prizesList: {
//     display: 'flex',
//     gap: '2rem',
//     justifyContent: 'center',
//   },

//   prizeCard: {
//     background: 'rgba(255, 255, 255, 0.05)',
//     borderRadius: '20px',
//     border: '1px solid rgba(162, 89, 255, 0.3)',
//     boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
//     padding: '2rem',
//     width: '280px',
//     minHeight: '400px',
//     textAlign: 'center',
//     display: 'flex',
//     flexDirection: 'column',
//     alignItems: 'center',
//     transition: 'all 0.3s ease',
//     backdropFilter: 'blur(10px)',
//   },

//   prizeImg: {
//     width: '80px',
//     height: '80px',
//     backgroundColor: '#a259ff',
//     borderRadius: '50%',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     fontSize: '2rem',
//     color: 'white',
//     marginBottom: '1rem',
//     fontWeight: 'bold',
//   },

//   prizeHeading: {
//     color: '#a259ff',
//     marginBottom: '10px',
//     fontSize: '1.35rem',
//     fontWeight: 700,
//   },

//   prizeDesc: {
//     color: '#c7b6f7',
//     marginBottom: '1.5rem',
//     fontSize: '1rem',
//     flexGrow: 1,
//   },

//   prizePoints: {
//     color: '#6c38cc',
//     fontSize: '1.1rem',
//     fontWeight: 600,
//     marginBottom: '1.5rem',
//   },

//   claimBtn: {
//     background: 'linear-gradient(90deg, #a259ff, #6c38cc)',
//     color: 'white',
//     fontWeight: '700',
//     fontSize: '1rem',
//     border: 'none',
//     borderRadius: '8px',
//     padding: '0.8rem 2rem',
//     cursor: 'pointer',
//     transition: 'all 0.3s ease',
//     boxShadow: '0 2px 10px rgba(162, 89, 255, 0.3)',
//   },

//   prizesIndicator: {
//     display: 'flex',
//     justifyContent: 'center',
//     gap: '0.5rem',
//     marginTop: '2rem',
//   },

//   indicator: {
//     width: '12px',
//     height: '12px',
//     borderRadius: '50%',
//     backgroundColor: 'rgba(162, 89, 255, 0.3)',
//     transition: 'all 0.3s ease',
//   },

//   indicatorActive: {
//     backgroundColor: '#a259ff',
//     transform: 'scale(1.2)',
//   },

//   leaderboardSection: {
//     padding: '4rem 2rem',
//     background: 'linear-gradient(135deg, rgba(44, 27, 105, 0.5) 0%, rgba(108, 46, 191, 0.5) 100%)',
//   },

//   leaderboardTitle: {
//     color: '#a259ff',
//     textAlign: 'center',
//     fontSize: '2.5rem',
//     fontWeight: 800,
//     marginBottom: '3rem',
//   },

//   tableWrapper: {
//     maxWidth: '800px',
//     margin: '0 auto',
//     background: 'rgba(255, 255, 255, 0.05)',
//     borderRadius: '20px',
//     overflow: 'hidden',
//     boxShadow: '0 6px 32px rgba(162, 89, 255, 0.1)',
//     backdropFilter: 'blur(10px)',
//   },

//   table: {
//     width: '100%',
//     borderCollapse: 'collapse',
//   },

//   th: {
//     backgroundColor: 'rgba(162, 89, 255, 0.2)',
//     color: '#a259ff',
//     padding: '1rem',
//     textAlign: 'left',
//     fontWeight: 'bold',
//     fontSize: '1.1rem',
//   },

//   tr: {
//     borderBottom: '1px solid rgba(162, 89, 255, 0.1)',
//     transition: 'background-color 0.3s ease',
//   },

//   td: {
//     padding: '1rem',
//     color: '#c7b6f7',
//   },

//   points: {
//     color: '#a259ff',
//     fontWeight: 'bold',
//   },

//   hidden: {
//     opacity: 0,
//     transform: 'translateY(50px)',
//   },

//   fadeInUp: {
//     opacity: 1,
//     transform: 'translateY(0)',
//     transition: 'all 0.8s ease-out',
//   },
// };

// export default LandingPage;