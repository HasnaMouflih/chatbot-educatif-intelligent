// src/components/MessageInput.js
import React, { useState, useRef } from 'react';
import '../style/MessageInput.css';

const MessageInput = ({ onSendMessage, disabled }) => {
    const [inputValue, setInputValue] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    // --- Gestion du Fichier ---
    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
            e.target.value = null; // Reset pour permettre de ré-uploader le même fichier
        }
    };

    const handleIconClick = () => {
        fileInputRef.current.click();
    };

    // --- Gestion de l'Envoi ---
    const handleSend = () => {
        // On envoie si (texte OU fichier) ET pas désactivé
        if ((inputValue.trim() || selectedFile) && !disabled) {
            onSendMessage(inputValue, selectedFile);
            setInputValue('');
            setSelectedFile(null);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="input-wrapper">
            
            {/* 1. PRÉVISUALISATION DU FICHIER (Apparaît au-dessus) */}
            {selectedFile && (
                <div className="file-preview">
                    <div className="file-icon">
                        📄 {/* Icône simple */}
                    </div>
                    <div className="file-info">
                        <span className="file-name">{selectedFile.name}</span>
                        <span className="file-type">Document PDF</span>
                    </div>
                    <button 
                        className="remove-file-btn" 
                        onClick={() => setSelectedFile(null)}
                        title="Retirer le fichier"
                    >
                        ×
                    </button>
                </div>
            )}

            {/* 2. BARRE DE SAISIE (Style Pilule) */}
            <div className="message-input-container">
                
                {/* Input caché pour le fichier */}
                <input 
                    type="file" 
                    accept=".pdf" 
                    ref={fileInputRef} 
                    style={{ display: 'none' }} 
                    onChange={handleFileChange}
                />

                {/* Bouton Trombone */}
                <button 
                    className="upload-button" 
                    onClick={handleIconClick}
                    disabled={disabled}
                    title="Joindre un PDF"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                </button>

                {/* Champ Texte */}
                <textarea
                    className="message-input"
                    placeholder={selectedFile ? "Posez une question sur ce document..." : "Écrivez votre message..."}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    disabled={disabled}
                    rows={1}
                />

                {/* Bouton Envoyer (Rond Bleu avec Avion) */}
                <button 
                    className="send-button" 
                    onClick={handleSend} 
                    disabled={disabled || (!inputValue.trim() && !selectedFile)}
                    title="Envoyer"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="send-icon-svg">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                </button>
            </div>
        </div>
    );
};

export default MessageInput;