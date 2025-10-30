// src/components/Sidebar.js (Version avec menu trois points)

// --- Imports ---
import React, { useState, useEffect } from 'react';
import { fetchChatIds } from '../api';
// Pas besoin d'importer le CSS ici si tu l'as mis dans ChatPage.css

// --- Fonction Utilitaire ---
const formatChatTitle = (chatId) => {
  try {
    const timestamp = parseInt(chatId.split('_')[1], 10);
    const date = new Date(timestamp);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }) + ' ' +
           date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return chatId;
  }
};

// --- Composant Principal ---
function Sidebar({ userEmail, onLogout, onSelectChat, onNewChat, currentChatId, refreshCounter, onDeleteChat }) {
  // --- États ---
  const [chatList, setChatList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  // --- NOUVEL ÉTAT: Pour suivre quel menu est ouvert ---
  const [openMenuId, setOpenMenuId] = useState(null); // null = aucun menu ouvert

  // --- Effet ---
  // Charge la liste des IDs de chat
  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      setError('');
      try {
        const ids = await fetchChatIds();
        setChatList(ids);
      } catch (err) {
        setError('Erreur chargement historique.');
        console.error("Load chat IDs error:", err);
      } finally {
        setLoading(false);
      }
    };
    loadHistory();
  }, [refreshCounter]);

  // --- Gestionnaires d'Événements ---

  // Gère le clic sur les trois points (ouvre/ferme le menu)
  const handleToggleMenu = (e, chatId) => {
    e.stopPropagation(); // Empêche la sélection du chat
    setOpenMenuId(prevId => (prevId === chatId ? null : chatId)); // Ouvre si fermé, ferme si déjà ouvert
  };

  // Gère le clic sur le bouton supprimer DANS le menu
  const handleDeleteClick = (e, chatId) => {
    e.stopPropagation();
    if (window.confirm(`Voulez-vous vraiment supprimer cette conversation (${formatChatTitle(chatId)}) ?`)) {
      onDeleteChat(chatId);
      setOpenMenuId(null); // Ferme le menu après suppression
    }
  };

  // --- Rendu JSX ---
  return (
    <div className="sidebar">
      {/* En-tête */}
      <div className="sidebar-header">
        <h2> Bienvenue,</h2>
        <p className="user-email">{userEmail}</p>
      </div>

      {/* Bouton Nouveau Chat */}
      <button className="new-chat-btn" onClick={onNewChat}>
         Nouveau Chat
      </button>

      {/* Titre Historique */}
      <div className="history-title">Historique</div>

      {/* Liste des conversations */}
      <div className="history-list">
        {loading && <p className="loading-text">Chargement...</p>}
        {error && <p className="error-message">{error}</p>}
        {!loading && !error && chatList.map((chatId) => (
          // Conteneur pour chaque ligne (important pour le positionnement du menu)
          <div key={chatId} className="history-item-container">
            {/* Bouton principal pour sélectionner le chat */}
            <button
              className={`history-item ${chatId === currentChatId ? 'active' : ''}`}
              onClick={() => { setOpenMenuId(null); onSelectChat(chatId); }} // Ferme menu si on sélectionne
              title={formatChatTitle(chatId)}
            >
              <span className="history-item-icon">💬</span> {/* Icône texte */}
              <span className="history-item-text">{formatChatTitle(chatId)}</span> {/* Texte */}
            </button>

            {/* --- MODIFICATION: Bouton Trois Points --- */}
            <button
              className="options-btn"
              onClick={(e) => handleToggleMenu(e, chatId)}
              title="Options"
            >
              ⋮ {/* Ou utilisez une icône SVG/FontAwesome */}
            </button>
            {/* --- FIN MODIFICATION --- */}

            {/* --- MODIFICATION: Menu Supprimer (Conditionnel) --- */}
            {openMenuId === chatId && (
              <div className="delete-menu">
                <button
                  className="delete-menu-btn"
                  onClick={(e) => handleDeleteClick(e, chatId)}
                >
                  <span role="img" aria-label="Supprimer">🗑️</span> Supprimer
                </button>
              </div>
            )}
            {/* --- FIN MODIFICATION --- */}
          </div>
        ))}
        {!loading && !error && chatList.length === 0 && (
          <p className="no-history">Aucun historique trouvé.</p>
        )}
      </div>

      {/* Bouton Déconnexion */}
      <button className="logout-btn" onClick={onLogout}>
        🚪 Se Déconnecter
      </button>
    </div>
  );
}

export default Sidebar;