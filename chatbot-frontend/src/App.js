// src/App.js
import React, { useState, useEffect } from 'react';
import LoginPage from './components/LoginPage';
import ChatPage from './components/ChatPage';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail'));

  // Effet pour vérifier le token au démarrage
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedEmail = localStorage.getItem('userEmail');
    if (storedToken && storedEmail) {
      setToken(storedToken);
      setUserEmail(storedEmail);
      // TODO: Idéalement, vérifier ici si le token est encore valide avec une requête API
    }
  }, []);

  const handleLoginSuccess = (newToken, email) => {
    localStorage.setItem('authToken', newToken);
    localStorage.setItem('userEmail', email);
    setToken(newToken);
    setUserEmail(email);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setToken(null);
    setUserEmail(null);
  };

  return (
    <div className="App">
      {token && userEmail ? (
        <ChatPage userEmail={userEmail} onLogout={handleLogout} />
      ) : (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;