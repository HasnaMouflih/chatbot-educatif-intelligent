
/projet-chatbot-python/
|
|-- 📂 data/
|   |-- 📂 raw/
|   |   |-- python_tutorial_brut.html
|   |   |-- stackoverflow_posts.json
|   |
|   |-- 📂 processed/
|   |   |-- python_qa_v1.csv   <-- VOTRE DATASET PRINCIPAL
|
|-- 📂 notebooks/
|   |-- 1.0-data-cleaning.ipynb
|   |-- 2.0-model-experiment.ipynb
|
|-- 📂 src/
|   |-- __init__.py
|   |-- 📄 data_loader.py
|   |-- 📄 model_utils.py
|   |-- 📄 app.py              <-- VOTRE API (FLASK / FASTAPI)
|
|-- 📂 models_saved/
|   |-- python_chatbot_v1/
|   |   |-- config.json
|   |   |-- pytorch_model.bin  (ou .h5 pour TensorFlow)
|
|-- 📂 frontend/
|   |-- 📄 index.html
|   |-- 📄 style.css
|   |-- 📄 script.js
|
|-- 📄 .gitignore
|-- 📄 requirements.txt
|-- 📄 README.md


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

[ UTILISATEUR ]
      ↑ ↓
+-----------------------------+
| COUCHE 1 : FRONTEND         |  (L'interface de chat)
| (HTML, CSS, JavaScript)     |
+-----------------------------+
      ↑ ↓ (Question/Réponse en JSON, via HTTP)
+-----------------------------+
| COUCHE 2 : BACKEND (API)    |  (Le serveur logique)
| (Python, Flask/FastAPI)     |
+-----------------------------+
      ↑ ↓ (Appel de fonction Python)
+-----------------------------+
| COUCHE 3 : MODÈLE IA        |  (Le "cerveau" intelligent)
| (Python, Transformers)      |
+-----------------------------+