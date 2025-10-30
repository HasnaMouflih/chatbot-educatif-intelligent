// src/components/ChatWindow.js
import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown'; // Pour afficher le Markdown

function ChatWindow({ messages, loading, error }) {
  const messagesEndRef = useRef(null); // Référence pour scroller en bas

  // Fait défiler vers le bas quand les messages changent
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div key={index} className={`message-bubble ${msg.role}`}>
          {/* Utilise ReactMarkdown pour afficher le contenu */}
          <ReactMarkdown>{msg.content || ''}</ReactMarkdown>
        </div>
      ))}
      {/* Affiche un indicateur de chargement */}
      {loading && (
        <div className="message-bubble assistant loading">
          <span></span><span></span><span></span> {/* Indicateur simple */}
        </div>
      )}
      {/* Affiche les erreurs */}
      {error && <p className="error-message chat-error">{error}</p>}
      {/* Élément vide à la fin pour le scroll */}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatWindow;