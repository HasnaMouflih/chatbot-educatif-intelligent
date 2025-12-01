// src/api.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';
const getToken = () => localStorage.getItem('authToken');

const apiClient = axios.create({ baseURL: API_URL });

apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token && !config.url.includes('/login') && !config.url.includes('/signup')) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      window.location.href = "/"; 
    }
    return Promise.reject(error);
  }
);

// Auth
export const loginUser = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const response = await apiClient.post('/users/login', formData);
  return response.data;
};

export const signupUser = async (email, password) => {
  const response = await apiClient.post('/users/signup', { username: email, password: password });
  return response.data;
};

export const updateUserProfile = async (password, fullName) => {
    const payload = {};
    if (password) payload.password = password;
    if (fullName) payload.full_name = fullName;
    const response = await apiClient.put('/users/me', payload);
    return response.data;
};

// Chat
export const fetchChatIds = async () => {
  const response = await apiClient.get('/history/ids');
  // Le backend renvoie maintenant { all_ids: [], pinned_ids: [] }
  return response.data; 
};

export const fetchChatHistory = async (chatId) => {
  if (!chatId) return [];
  const response = await apiClient.get(`/history/${chatId}`);
  return response.data.history || [];
};

export const askChatbot = async (chatId, question) => {
  const response = await apiClient.post('/ask', { chat_id: chatId, question: question });
  return response.data.reponse;
};

export const uploadPDF = async (chatId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post(`/upload_pdf?chat_id=${chatId}`, formData);
  return response.data;
};

// Actions Historique
export const deleteChatHistory = async (chatId) => {
  if (!chatId) return;
  await apiClient.delete(`/history/${chatId}`);
};

export const deleteAllHistory = async () => {
    await apiClient.delete('/history/all');
};

export const togglePinChat = async (chatId) => {
    const response = await apiClient.post(`/history/pin/${chatId}`);
    return response.data.status; // "pinned" ou "unpinned"
};