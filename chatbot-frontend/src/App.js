// Fichier: src/App.js
import React, { useState, useEffect } from 'react';
import LoginPage from './components/LoginPage';
import ChatPage from './components/ChatPage';
import './App.css'; 

function App() {
  // On vérifie s'il y a un token au démarrage
  const [token, setToken] = useState(localStorage.getItem('authToken'));

  // Cette fonction est celle qui est envoyée à LoginPage
  const handleLogin = (newToken, email) => {
    localStorage.setItem('authToken', newToken);
    localStorage.setItem('userEmail', email);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setToken(null);
  };

  return (
    <div className="App">
      {!token ? (
        // IMPORTANT : On passe la fonction handleLogin via la prop 'onLogin'
        <LoginPage onLogin={handleLogin} />
      ) : (
        <ChatPage 
          userEmail={localStorage.getItem('userEmail') || 'Utilisateur'} 
          onLogout={handleLogout} 
        />
      )}
    </div>
  );
}

export default App;

