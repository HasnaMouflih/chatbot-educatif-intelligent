// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Peut contenir des styles globaux si besoin
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);