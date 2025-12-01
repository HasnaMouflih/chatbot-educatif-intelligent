import React, { useEffect, useRef } from 'react';
import '../style/ChatWindow.css';

/**
 * Composant pour afficher la fenêtre de discussion.
 * @param {string} userEmail - E-mail de l'utilisateur connecté.
 */
function ChatWindow({ messages, loading, error, userEmail }) {
    const endRef = useRef(null);

    // Défilement vers le bas
    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    // Première lettre de l'e-mail
    const userInitial = userEmail
        ? userEmail.charAt(0).toUpperCase()
        : '👤';

    // Rendu de l'icône du bot (image dans /public/)
    const renderBotIcon = () => (
        <div className="bot-icon-container">
            <img
                src={`${process.env.PUBLIC_URL}/favicon.ico`}
                alt="Assistant Icon"
                className="bot-icon"
            />
        </div>
    );

    return (
        <div className="chat-window">
            <div className="messages-list">
                {messages.map((msg, i) => (
                    <div key={i} className={`message-row ${msg.role}`}>

                        {/* Avatar */}
                        <div className="message-avatar">
                            {msg.role === 'assistant' ? (
                                renderBotIcon()
                            ) : (
                                <div className="user-icon-container">
                                    {userInitial}
                                </div>
                            )}
                        </div>

                        {/* Contenu du message */}
                        <div className="message-content">
                            <div className="message-author">
                                {msg.role === 'assistant' ? 'Assistant Python' : 'Vous'}
                            </div>
                            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                        </div>
                    </div>
                ))}

                {/* Loading */}
                {loading && (
                    <div className="message-row assistant">
                        <div className="message-avatar">
                            {renderBotIcon()}
                        </div>
                        <div className="message-content loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}

                {/* Erreur */}
                {error && (
                    <div style={{ color: 'red', textAlign: 'center', marginTop: 10 }}>
                        {error}
                    </div>
                )}

                <div ref={endRef}></div>
            </div>
        </div>
    );
}

export default ChatWindow;
