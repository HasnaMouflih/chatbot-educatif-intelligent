// src/api.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000'; // Votre backend FastAPI

// Fonction pour obtenir le token depuis le localStorage
const getToken = () => localStorage.getItem('authToken');

// Créer une instance axios pour ajouter automatiquement le header d'authentification
const apiClient = axios.create({
  baseURL: API_URL,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token && !config.url.includes('/login') && !config.url.includes('/signup')) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Fonctions d'API ---

export const loginUser = async (email, password) => {
  // FastAPI attend les données de login en 'form-data'
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await apiClient.post('/users/login', formData, {
     headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data; // Renvoie { access_token: "...", token_type: "bearer" }
};

export const signupUser = async (email, password) => {
  const response = await apiClient.post('/users/signup', {
    username: email,
    password: password,
  });
  return response.data; // Renvoie { access_token: "...", token_type: "bearer" }
};

export const fetchChatIds = async () => {
  const response = await apiClient.get('/history/ids');
  return response.data.chat_ids || []; // Renvoie ["chat_...", "chat_..."]
};

export const fetchChatHistory = async (chatId) => {
  if (!chatId) return []; // Ne rien faire si chatId est null
  const response = await apiClient.get(`/history/${chatId}`);
  return response.data.history || []; // Renvoie [{role: 'user', content: '...'}, ...]
};

export const askChatbot = async (chatId, question) => {
  const response = await apiClient.post('/ask', {
    chat_id: chatId,
    question: question,
  });
  return response.data.reponse; // Renvoie la réponse du bot (string)
};
// src/api.js
// ... (garder les imports et les autres fonctions) ...

// --- NOUVELLE FONCTION POUR SUPPRIMER ---
export const deleteChatHistory = async (chatId) => {
  if (!chatId) return; // Ne rien faire si chatId est null
  // La réponse sera vide (statut 204), donc on ne s'attend pas à .data
  await apiClient.delete(`/history/${chatId}`);
};
// --- FIN NOUVELLE FONCTION ---

// ... (garder askChatbot, etc.)