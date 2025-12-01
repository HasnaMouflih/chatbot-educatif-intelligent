
Personne A : Ingénieur·e Données (Data Engineer)

Personne B : Ingénieur·e IA / Backend (AI/Backend)

Personne C : Ingénieur·e Frontend / Qualité (Frontend/QA)


L'Architecture Complète (Le Flux de Données)
Imaginez un utilisateur qui pose une question :

L'utilisateur écrit dans le [Frontend].

Le Frontend envoie la question au [Backend].

Le Backend demande au [Modèle IA] de trouver une réponse.

Le Modèle IA renvoie la réponse au Backend.

Le Backend renvoie la réponse au Frontend.

Le Frontend affiche la réponse à l'utilisateur.

# Projet : Chatbot Éducatif IA 🤖📚

... (Toute la description que tu as déjà) ...

---

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