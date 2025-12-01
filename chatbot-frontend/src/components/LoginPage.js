// src/components/LoginPage.js
import React, { useState } from 'react';
import { loginUser, signupUser } from '../api';
import '../style/LoginPage.css';

// ATTENTION : La prop doit s'appeler 'onLogin' pour correspondre à App.js
function LoginPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      let data;

      // 1. SCÉNARIO INSCRIPTION
      if (!isLogin) {
        if (password !== confirmPassword) {
          setError('Les mots de passe ne correspondent pas.');
          setLoading(false);
          return;
        }
        if (password.length < 8) {
          setError('Le mot de passe doit faire au moins 8 caractères.');
          setLoading(false);
          return;
        }
        // Appel API Inscription
        data = await signupUser(email, password);
      } 
      
      // 2. SCÉNARIO CONNEXION
      else {
        // Appel API Login
        data = await loginUser(email, password);
      }

      // --- CRUCIAL POUR EVITER L'ERREUR 401 ---
      // On sauvegarde le token immédiatement sous le bon nom ('authToken')
      localStorage.setItem('authToken', data.access_token);
      
      // On informe App.js que c'est réussi
      onLogin(data.access_token, email);

    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erreur de connexion. Vérifiez vos identifiants.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Bienvenue sur le Chatbot Éducatif Python</h1>
      <p>{isLogin ? 'Connectez-vous pour accéder à vos cours.' : 'Créez un compte pour commencer.'}</p>

      <div className="login-toggle">
        <button onClick={() => setIsLogin(true)} className={isLogin ? 'active' : ''}>
           Se Connecter
        </button>
        <button onClick={() => setIsLogin(false)} className={!isLogin ? 'active' : ''}>
           Créer un Compte
        </button>
      </div>

      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="votreadresse@email.com"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Mot de passe</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder={isLogin ? 'Votre mot de passe' : 'Minimum 8 caractères'}
          />
        </div>

        {!isLogin && (
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Retapez votre mot de passe"
            />
          </div>
        )}

        {error && <p className="error-message">{error}</p>}
        
        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Chargement...' : (isLogin ? 'Se Connecter' : 'Créer un Compte')}
        </button>
      </form>
    </div>
  );
}

export default LoginPage;