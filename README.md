# Chatbot Éducatif Intelligent pour Python

## 📝 Description
Ce projet consiste en un **chatbot éducatif hybride** capable de répondre avec précision aux questions académiques liées au langage Python.  
Le système exploite à la fois des **documents locaux** (PDF ou datasets) et un **modèle de Deep Learning fine-tuné**, pour fournir des réponses contextualisées et traçables.  

Le projet couvre toute la **chaîne de valeur de la donnée** :
1. Extraction et nettoyage de données brutes.
2. Modélisation et fine-tuning du modèle NLP.
3. Déploiement via une API sécurisée.
4. Interface utilisateur moderne en React.

---

## 🚀 Fonctionnalités
- Création et gestion de comptes utilisateurs (authentification JWT/OAuth2).  
- Upload et analyse automatique de fichiers PDF.  
- Chat intelligent avec mémoire locale (RAQ).  
- Intégration d’un LLM via API (Zephyr) pour explications détaillées.  
- Historique des conversations avec possibilité de suppression partielle ou totale.  
- Chats épinglés pour un accès rapide.  
- Modèle CamemBERT fine-tuné pour le **Question-Answering en français**.  
- Option LoRA pour entraînements plus légers et rapides.

---

## 🛠 Architecture

### Backend
- **FastAPI** : serveur API rapide et sécurisé.  
- **MongoDB Atlas** : stockage utilisateurs et historique.  
- **Pydantic** : validation des données.  
- **pypdf** : extraction de texte à partir de PDF.  
- Authentification : JWT / OAuth2.

### Machine Learning / IA
- **CamemBERT** fine-tuné pour RAQ (Retrieval-Augmented Question Answering).  
- **RAG** : utilisation de la mémoire locale pour contextualiser les réponses.  
- Fine-tuning avec **LoRA** pour certaines expérimentations.  
- **HuggingFace Transformers & PyTorch** pour l’entraînement et l’inférence.  

### Frontend
- **React.js** pour une interface moderne et réactive.  
- Gestion des fonctionnalités : historique, épinglage de chats, upload PDF.  
- Communication sécurisée avec le backend via JWT.

---

## 🗂 Structure du Projet

