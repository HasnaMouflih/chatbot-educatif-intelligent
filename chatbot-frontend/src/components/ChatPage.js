// src/components/ChatPage.js (Version Complète et Corrigée)

// --- Imports ---
import React, { useState, useEffect, useCallback } from 'react';

// --- Composants ---
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';

// --- Fonctions API (incluant deleteChatHistory) ---
import { fetchChatHistory, askChatbot, deleteChatHistory } from '../api';

// --- Styles ---
import '../style/ChatPage.css'; // Assurez-vous que ce chemin est correct

// --- Fonctions Utilitaires ---
const getNewChatId = () => `chat_${Date.now()}`;
const initialBotMessage = { role: 'assistant', content: ' Bonjour ! Comment puis-je vous aider avec Python aujourd\'hui ?' };

// --- Composant Principal ---
function ChatPage({ userEmail, onLogout }) {
  // --- États ---
  const [currentChatId, setCurrentChatId] = useState(null); // ID du chat actif
  const [messages, setMessages] = useState([initialBotMessage]); // Liste des messages affichés
  const [loading, setLoading] = useState(false); // Indicateur de chargement (API en cours)
  const [error, setError] = useState(''); // Message d'erreur à afficher
  const [refreshHistory, setRefreshHistory] = useState(0); // Déclencheur pour MàJ la sidebar

  // --- Effets ---
  // Charge l'historique quand currentChatId change
  useEffect(() => {
    const loadMessages = async () => {
      // Si c'est un nouveau chat, afficher juste le message initial
      if (!currentChatId) {
        setMessages([initialBotMessage]);
        return; // Pas besoin de charger depuis l'API
      }
      // Sinon, charger depuis l'API
      setLoading(true);
      setError('');
      try {
        const history = await fetchChatHistory(currentChatId);
        // Si l'historique chargé est vide, afficher le message initial
        setMessages(history.length > 0 ? history : [initialBotMessage]);
      } catch (err) {
        setError("Erreur lors du chargement de l'historique.");
        console.error("Load history error:", err);
        setMessages([initialBotMessage]); // Afficher message initial en cas d'erreur
      } finally {
        setLoading(false);
      }
    };
    loadMessages();
  }, [currentChatId]); // Se redéclenche si currentChatId change

  // --- Gestionnaires d'Événements (Callbacks) ---
  // Sélectionne un chat dans la sidebar
  const handleSelectChat = useCallback((chatId) => {
    setCurrentChatId(chatId);
  }, []);

  // Crée un nouveau chat
  const handleNewChat = useCallback(() => {
    setCurrentChatId(null); // Met l'ID à null
    setMessages([initialBotMessage]); // Affiche le message d'accueil
  }, []);

  // Envoie un message au backend
  const handleSendMessage = async (userMessage) => {
    let chatIdToUse = currentChatId;
    let isNewChat = false;

    // Si c'est le 1er message d'un nouveau chat
    if (chatIdToUse === null) {
      chatIdToUse = getNewChatId();
      setCurrentChatId(chatIdToUse); // Mémorise le nouvel ID pour les prochains messages
      isNewChat = true;
      // Remplace le message d'accueil par le 1er message utilisateur
      setMessages([]);
    }

    const newUserMessage = { role: 'user', content: userMessage };
    // Affichage optimiste : ajoute le message utilisateur tout de suite
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setLoading(true); // Active l'indicateur de chargement
    setError('');

    try {
      const botResponse = await askChatbot(chatIdToUse, userMessage);
      const newBotMessage = { role: 'assistant', content: botResponse };
      // Ajoute la réponse du bot quand elle arrive
      setMessages((prevMessages) => [...prevMessages, newBotMessage]);

      // Si c'était un nouveau chat, on force la sidebar à se mettre à jour
      if (isNewChat) {
        setRefreshHistory(prev => prev + 1);
      }
    } catch (err) {
      setError("Erreur lors de l'envoi du message.");
      console.error("Send message error:", err);
      // Annule l'affichage optimiste si l'API échoue
      setMessages((prevMessages) => prevMessages.slice(0, -1));
    } finally {
      setLoading(false); // Désactive l'indicateur de chargement
    }
  };

  // --- AJOUT DE LA FONCTION DE SUPPRESSION ---
  // Supprime une conversation
  const handleDeleteChat = async (chatIdToDelete) => {
    setError(''); // Efface les erreurs précédentes
    try {
      await deleteChatHistory(chatIdToDelete); // Appel API pour supprimer
      setRefreshHistory(prev => prev + 1); // Force la MàJ de la sidebar
      // Si on a supprimé le chat actif, on revient à un "Nouveau Chat"
      if (currentChatId === chatIdToDelete) {
        handleNewChat();
      }
    } catch (err) {
      // Affiche une erreur si la suppression échoue
      setError(`Erreur lors de la suppression du chat.`);
      console.error("Delete chat error:", err);
      // Afficher l'erreur dans la console ou via une notification serait mieux
    }
  };
  // --- FIN AJOUT ---


  // --- Rendu JSX ---
  return (
    <div className="chat-page-container">
      <Sidebar
        userEmail={userEmail}
        onLogout={onLogout}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        currentChatId={currentChatId}
        refreshCounter={refreshHistory} // Passe le déclencheur
        onDeleteChat={handleDeleteChat} // Passe la fonction de suppression
      />
      <div className="main-chat-area">
        <ChatWindow messages={messages} loading={loading} error={error} />
        <MessageInput onSendMessage={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}

export default ChatPage;