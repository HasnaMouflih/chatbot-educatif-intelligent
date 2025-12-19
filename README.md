1. Backend

FastAPI : API rapide et sécurisée.

MongoDB Atlas : Gestion des utilisateurs et historique.

Pydantic : Validation des données.

OAuth2 + JWT : Authentification sécurisée.

pypdf : Extraction de texte à partir de fichiers PDF.

HuggingFace Inference API (Zephyr) : Accès au LLM pour explications détaillées.

2. IA / Machine Learning

Transformers (BERT) fine-tuné pour le RAQ.

Pipeline QA pour répondre aux questions.

Similarity Matching pour le retrieval.

RAG pour combiner la mémoire locale avec le modèle de génération.

3. Data

Pandas pour le traitement.

Dataset nettoyé : dataset_cleaned_readable.csv.

4. Fonctionnalités

Création de compte et connexion sécurisée.

Mise à jour du profil.

Chat IA intelligent.

Upload et analyse automatique de PDF.

Historique complet des chats.

Suppression partielle ou totale.

Chats épinglés (Pin).

RAQ pour la mémoire locale.

IA Zephyr pour explications détaillées.

## 🏎️ Lancement (Installation Locale)

... (Toutes les instructions pour le Backend et le Frontend) ...

### ⚠️ Étape Importante : Télécharger le Modèle IA et le Dataset

Les fichiers du modèle IA (fine-tuné) et du dataset sont trop volumineux pour GitHub et doivent être téléchargés séparément.

1.  **Téléchargez les fichiers .zip** depuis ce lien Google Drive :
    [Lien Google Drive vers les Modèles/Datasets](https://drive.google.com/drive/folders/1wf5FAhGWktXx-dmWFF2phxh__nYb2bVF?usp=drive_link)
    *(Contient : `mon_chatbot_EN_v22.zip` et `dataset_educatif.csv1.zip`)*

2.  **Décompressez le modèle** (`mon_chatbot_EN_v22.zip`).
3.  **Placez** le dossier décompressé (ex: `mon_chatbot_EN_v2`) à l'intérieur du dossier `/models_saved/` de ce projet.
4.  (Le fichier `dataset_educatif.csv1.zip` n'est nécessaire que pour refaire l'entraînement).
5.  Assurez-vous que le chemin dans `src/model_utils.py` correspond bien (`nom_modele_ou_chemin = "models_saved/mon_chatbot_EN_v2"`).

**5. Lancer l'Application**


... (Instructions `uvicorn` et `npm start`) ...
