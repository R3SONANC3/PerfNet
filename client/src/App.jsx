import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // import useNavigate
import './style.css';
import Logo from '../assets/logo.png';

function App() {
  const [http, setHttp] = useState('http');  // Default to 'http'
  const [domain, setDomain] = useState('');
  const [port, setPort] = useState('');

  const navigate = useNavigate(); // Initialize useNavigate

  const handleEnter = () => {
    if (http && domain && port) {
      const url = `${http}://${domain}:${port}`;
      navigate(`/dashboard?url=${encodeURIComponent(url)}`); // Pass the constructed URL as a query parameter
    } else {
      alert("Please enter valid HTTP scheme, domain, and port.");
    }
  };

  return (
    <>
      <header className="header">
        <h1>PERFNET</h1>
      </header>
      <div className='home-container'>
        <main className="main">
          <div className="content">
            <img className="logo" src={Logo} alt="Logo" />
            <h2>PERFNET</h2>
            <p>Check for server errors in real time.</p>
          </div>

          <div className="input-container">
            <input
              type="text"
              placeholder="HTTP (http or https)"
              value={http}
              onChange={(e) => setHttp(e.target.value)}
              className="input-field"
            />
            <input
              type="text"
              placeholder="Enter domain (e.g., 34.143.248.148)"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="input-field"
            />
            <input
              type="text"
              placeholder="Enter port (e.g., 9090)"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              className="input-field"
            />
            <button onClick={handleEnter} className="submit-button">Enter</button>
          </div>
        </main>
      </div>
    </>

  );
}

export default App;
