// src/components/ChatPage.js (Version Finale Fluide)

import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';
import { fetchChatHistory, askChatbot, deleteChatHistory, uploadPDF } from '../api';
import '../style/ChatPage.css';

const getNewChatId = () => `chat_${Date.now()}`;
const initialBotMessage = { role: 'assistant', content: 'Bonjour ! Je suis prêt. Vous pouvez m\'envoyer un PDF et poser une question dessus.' };

function ChatPage({ userEmail, onLogout }) {
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([initialBotMessage]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [refreshHistory, setRefreshHistory] = useState(0);

  // --- Chargement Historique ---
  useEffect(() => {
    const loadMessages = async () => {
      if (!currentChatId) {
        setMessages([initialBotMessage]);
        return;
      }
      setLoading(true);
      try {
        const history = await fetchChatHistory(currentChatId);
        setMessages(history.length > 0 ? history : [initialBotMessage]);
      } catch (err) {
        console.error(err);
        setMessages([initialBotMessage]);
      } finally {
        setLoading(false);
      }
    };
    loadMessages();
  }, [currentChatId]);

  // --- Callbacks Sidebar ---
  const handleSelectChat = useCallback((chatId) => setCurrentChatId(chatId), []);
  const handleNewChat = useCallback(() => {
    setCurrentChatId(null);
    setMessages([initialBotMessage]);
  }, []);
  
  const handleDeleteChat = async (chatId) => {
    try {
      await deleteChatHistory(chatId);
      setRefreshHistory(prev => prev + 1);
      if (currentChatId === chatId) handleNewChat();
    } catch (err) { console.error(err); }
  };

  // --- FONCTION D'ENVOI INTELLIGENTE ---
  const handleSendComposite = async (textMessage, file) => {
    let chatIdToUse = currentChatId;
    let isNewChat = false;

    // 1. Initialiser le chat si besoin
    if (chatIdToUse === null) {
      chatIdToUse = getNewChatId();
      setCurrentChatId(chatIdToUse);
      isNewChat = true;
      setMessages([]);
    }

    setLoading(true);
    setError('');

    try {
      // --- CAS A : FICHIER + QUESTION (Le cas que vous voulez) ---
      if (file && textMessage) {
        // 1. On affiche UN SEUL message utilisateur combiné
        const combinedMsg = { role: 'user', content: `📎 ${file.name}\n\n${textMessage}` };
        setMessages(prev => [...prev, combinedMsg]);

        // 2. On upload le PDF (pour que le backend le lise)
        // On attend la fin de l'upload mais on ignore la réponse texte du bot "Bien reçu"
        await uploadPDF(chatIdToUse, file);

        // 3. On pose la question immédiatement
        const botResponse = await askChatbot(chatIdToUse, textMessage);
        
        // 4. On affiche la réponse finale (le résumé/explication)
        const msgBot = { role: 'assistant', content: botResponse };
        setMessages(prev => [...prev, msgBot]);
      }
      
      // --- CAS B : JUSTE UN FICHIER (Sans question) ---
      else if (file) {
        const msgFile = { role: 'user', content: `📎 Envoi du fichier : ${file.name}` };
        setMessages(prev => [...prev, msgFile]);
        const pdfResponse = await uploadPDF(chatIdToUse, file);
        const msgBot = { role: 'assistant', content: pdfResponse.reponse };
        setMessages(prev => [...prev, msgBot]);
      }

      // --- CAS C : JUSTE DU TEXTE ---
      else if (textMessage) {
        const msgText = { role: 'user', content: textMessage };
        setMessages(prev => [...prev, msgText]);
        const botResponse = await askChatbot(chatIdToUse, textMessage);
        const msgBot = { role: 'assistant', content: botResponse };
        setMessages(prev => [...prev, msgBot]);
      }

      if (isNewChat) setRefreshHistory(prev => prev + 1);

    } catch (err) {
      console.error(err);
      setError("Une erreur est survenue.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-page-container">
      <Sidebar
        userEmail={userEmail}
        onLogout={onLogout}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        currentChatId={currentChatId}
        refreshCounter={refreshHistory}
        onDeleteChat={handleDeleteChat}
      />
      <div className="main-chat-area">
        <ChatWindow messages={messages} loading={loading} error={error} />
        
        <MessageInput 
          onSendMessage={handleSendComposite} 
          disabled={loading} 
        />
      </div>
    </div>
  );
}

export default ChatPage;