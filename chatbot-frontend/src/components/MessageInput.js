// src/components/MessageInput.js
import React, { useState } from 'react';

function MessageInput({ onSendMessage, disabled }) {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSend = () => {
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue);
      setInputValue(''); // Vide l'input après envoi
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) { // Envoi avec Entrée (pas Shift+Entrée)
      event.preventDefault(); // Empêche le saut de ligne
      handleSend();
    }
  };

  return (
    <div className="message-input-container">
      <textarea
        value={inputValue}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        placeholder="Posez votre question ici..."
        rows="1" // Commence avec une seule ligne, s'agrandit si besoin
        disabled={disabled}
      />
      <button onClick={handleSend} disabled={disabled || !inputValue.trim()}>
        Envoyer
      </button>
    </div>
  );
}

export default MessageInput;