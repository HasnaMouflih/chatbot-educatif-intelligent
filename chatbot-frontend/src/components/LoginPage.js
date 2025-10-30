// src/components/LoginPage.js
import React, { useState } from 'react';
import { loginUser, signupUser } from '../api';
import '../style/LoginPage.css'; // Créez ce fichier CSS

function LoginPage({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true); // Pour alterner Login/Signup
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    if (!isLogin) { // Mode Inscription
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
      try {
        const data = await signupUser(email, password);
        onLoginSuccess(data.access_token, email);
      } catch (err) {
        setError(err.response?.data?.detail || 'Erreur lors de la création du compte.');
      } finally {
        setLoading(false);
      }
    } else { // Mode Connexion
      try {
        const data = await loginUser(email, password);
        onLoginSuccess(data.access_token, email);
      } catch (err) {
        setError(err.response?.data?.detail || 'Erreur lors de la connexion.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="login-container">
      <h1>Bienvenue sur le Chatbot Éducatif Python</h1>
      <p>Connectez-vous ou créez un compte pour commencer.</p>

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
          <label htmlFor="email">Email (identifiant)</label>
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