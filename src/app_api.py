# Fichier: src/app_api.py
# (Version complète avec CORS)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from datetime import datetime, timedelta

# --- AJOUT POUR CORS ---
from fastapi.middleware.cors import CORSMiddleware
# --- FIN AJOUT ---

# --- CORRECTION ModuleNotFoundError ---
import src.model_utils as model_utils
from src.auth_utils import (
    verify_password, get_password_hash, create_access_token, verify_token
)
from src.db_models import UserCreate, Token, ChatQuestion

# --- Configuration ---------------------------------------------
# 💡 IMPORTANT : Vérifiez que ceci est votre vraie chaîne de connexion MongoDB
CONNECTION_STRING = "mongodb+srv://chatbot1:1234567887654321@cluster0.0zmgwp5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "chatbot_db1" # Assurez-vous que c'est le bon nom de base de données

# 2. Initialiser l'API FastAPI
app = FastAPI(title="Chatbot API Sécurisée")

# --- AJOUT DU MIDDLEWARE CORS ---
origins = [
    "http://localhost",       # Autorise localhost sans port
    "http://localhost:3000",  # Autorise React (port par défaut de create-react-app)
    # Ajoutez ici l'URL où votre frontend sera déployé si différent
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Liste des origines autorisées
    allow_credentials=True,      # Autorise les cookies/authentification
    allow_methods=["*"],         # Autorise toutes les méthodes (GET, POST, OPTIONS...)
    allow_headers=["*"],         # Autorise tous les headers
)
# --- FIN AJOUT CORS ---


# 3. --- BLOC DE CONNEXION SÉCURISÉ ---
client = None
db = None
users_collection = None
chat_collection = None

try:
    client = MongoClient(CONNECTION_STRING)
    # Teste la connexion immédiatement
    client.admin.command('ping')
    db = client[DB_NAME]
    users_collection = db["users"]
    chat_collection = db["chat_history"]
    print("Connexion à MongoDB Atlas réussie.")
except Exception as e:
    print(f"!!! ERREUR CRITIQUE DE CONNEXION MONGODB: {e}")
# --- FIN DU BLOC DE CONNEXION ---


# 4. Charger le modèle IA (simulé)
model_utils.load_model()

# 5. Schéma de sécurité OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# --- Dépendance de Sécurité -----------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """ Vérifie le token et renvoie le username (email). """
    username = verify_token(token)
    if not username or client is None or users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou BDD non connectée",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = users_collection.find_one({"_id": username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

# --- Endpoints d'Authentification (Publics) ------------------

@app.post("/users/signup", response_model=Token)
async def signup(user: UserCreate):
    """ Crée un nouvel utilisateur. """
    if client is None or users_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    existing_user = users_collection.find_one({"_id": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    hashed_password = get_password_hash(user.password)

    users_collection.insert_one({
        "_id": user.username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    })

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Connecte l'utilisateur et renvoie un token JWT. """
    if client is None or users_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    user = users_collection.find_one({"_id": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoints du Chatbot (PROTÉGÉS) -------------------------

@app.post("/ask")
async def ask_question(
    message: ChatQuestion,
    current_user: str = Depends(get_current_user)
):
    """ Endpoint principal du chat. """
    if client is None or chat_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    question = message.question
    chat_id = message.chat_id
    reponse = model_utils.predict(question)

    log_entry = {
        "user_id": current_user,
        "chat_id": chat_id,
        "role": "user",
        "content": question,
        "timestamp": datetime.utcnow()
    }
    log_entry_bot = {
        "user_id": current_user,
        "chat_id": chat_id,
        "role": "assistant",
        "content": reponse,
        "timestamp": datetime.utcnow()
    }
    chat_collection.insert_many([log_entry, log_entry_bot])

    return {"reponse": reponse}

@app.get("/history/ids")
async def get_all_chat_ids(current_user: str = Depends(get_current_user)):
    """ Récupère les chat_id pour l'utilisateur connecté. """
    if client is None or chat_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    pipeline = [
        {"$match": {"user_id": current_user}},
        {"$group": {"_id": "$chat_id"}},
        {"$sort": {"_id": -1}}
    ]
    chat_ids = [doc["_id"] for doc in chat_collection.aggregate(pipeline)]

    return {"chat_ids": chat_ids}

@app.get("/history/{chat_id}")
async def get_history(chat_id: str, current_user: str = Depends(get_current_user)):
    """ Récupère l'historique d'un chat spécifique pour l'utilisateur. """
    if client is None or chat_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    messages = list(chat_collection.find(
        {"chat_id": chat_id, "user_id": current_user},
        {"_id": 0, "role": 1, "content": 1}
    ).sort("timestamp", 1))

    if not messages:
        raise HTTPException(status_code=404, detail="Historique non trouvé ou accès non autorisé")

    return {"history": messages}
# Fichier: src/app_api.py

# ... (garder tous les imports et le code existant) ...
# --- ENDPOINT POUR SUPPRIMER L'HISTORIQUE ---
@app.delete("/history/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(chat_id: str, current_user: str = Depends(get_current_user)):
    """
    Supprime tous les messages d'un chat_id spécifique pour l'utilisateur connecté.
    """
    # Vérifie si la connexion à la BDD est active
    if client is None or chat_collection is None:
        raise HTTPException(status_code=500, detail="Connexion BDD échouée")

    # Utilise delete_many pour supprimer tous les documents (messages)
    # qui correspondent au chat_id ET à l'user_id de l'utilisateur connecté.
    delete_result = chat_collection.delete_many(
        {"chat_id": chat_id, "user_id": current_user}
    )

    # Affiche dans le terminal combien de messages ont été supprimés (utile pour le debug)
    print(f"{delete_result.deleted_count} messages supprimés pour chat_id {chat_id} par {current_user}.")

    # Si la suppression réussit (ou si rien n'a été trouvé),
    # renvoie une réponse vide avec le statut 204 No Content.
    return None
# --- FIN ENDPOINT SUPPRESSION ---