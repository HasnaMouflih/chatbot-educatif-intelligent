# Fichier: src/app_api.py
# (Version CORRIGÉE et FINALISÉE : Auth + Profil + Chat + PDF + Pin/Delete)

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from datetime import datetime
import os
import io
import pypdf
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Import de votre module RAQ (Cerveau Local)
import src.raq_utils as raq_utils

# IMPORTS PROJET (Auth & Models)
from src.auth_utils import verify_password, get_password_hash, create_access_token, verify_token
from src.db_models import UserCreate, Token, ChatQuestion, UserUpdate

load_dotenv()
app = FastAPI(title="Chatbot Educatif Final")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION IA ---
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
REPO_ID = "HuggingFaceH4/zephyr-7b-beta" 
client = InferenceClient(token=HF_TOKEN)

# --- CONFIGURATION BDD ---
CONNECTION_STRING = "mongodb+srv://chatbot1:1234567887654321@cluster0.0zmgwp5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "chatbot_db1"

client_mongo = None
try:
    client_mongo = MongoClient(CONNECTION_STRING)
    db = client_mongo[DB_NAME]
    users_collection = db["users"]
    chat_collection = db["chat_history"]
    chat_meta_collection = db["chat_metadata"] # Pour les épingles (Pin)
    print("✅ Connexion MongoDB réussie.")
except:
    print("❌ Erreur Connexion MongoDB.")

# Sécurité
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username: raise HTTPException(401, "Token invalide")
    return username

# ==========================================
# 1. AUTHENTIFICATION & PROFIL
# ==========================================

@app.post("/users/signup")
async def signup(user: UserCreate):
    if users_collection.find_one({"_id": user.username}):
        raise HTTPException(400, "Email déjà pris")
    users_collection.insert_one({
        "_id": user.username,
        "hashed_password": get_password_hash(user.password),
        "created_at": datetime.utcnow()
    })
    return {"access_token": create_access_token({"sub": user.username}), "token_type": "bearer"}

@app.post("/users/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"_id": form.username})
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(401, "Erreur login")
    return {"access_token": create_access_token({"sub": form.username}), "token_type": "bearer"}

@app.put("/users/me")
async def update_user(data: UserUpdate, user: str = Depends(get_current_user)):
    updates = {}
    if data.password:
        updates["hashed_password"] = get_password_hash(data.password)
    if data.full_name:
        updates["full_name"] = data.full_name
    
    if updates:
        users_collection.update_one({"_id": user}, {"$set": updates})
        return {"msg": "Profil mis à jour"}
    return {"msg": "Rien à modifier"}

# ==========================================
# 2. CHATBOT INTELLIGENT (RAQ + PDF + LLM)
# ==========================================

@app.post("/ask")
async def ask_question(message: ChatQuestion, user: str = Depends(get_current_user)):
    question = message.question
    print(f"📩 Question : {question}")

    contexte_systeme = "Tu es un assistant pédagogique en Python."
    source_label = ""

    # --- A. RECHERCHE PDF EN MÉMOIRE ---
    # CORRECTION ICI : Ajout du 'r' avant la regex pour éviter l'erreur de syntaxe
    pdf_doc = chat_collection.find_one(
        {"chat_id": message.chat_id, "role": "system", "content": {"$regex": r"^\[CONTEXTE PDF\]"}},
        sort=[("timestamp", -1)]
    )

    if pdf_doc:
        print("📂 PDF détecté en mémoire.")
        contenu_pdf = pdf_doc['content']
        contexte_systeme += f"\nContexte PDF fourni : {contenu_pdf}\nUtilise ce contexte pour répondre."
        source_label = " *(Analyse PDF)*"
    
    # --- B. SINON RECHERCHE RAQ (COURS) ---
    else:
        raq_result = raq_utils.get_answer(question)
        if raq_result:
            print(f"✅ RAQ Trouvé : {raq_result['answer']}")
            contexte_systeme += f"\nINFO COURS : '{raq_result['answer']}'."
            source_label = " *(Source: Cours Officiel)*"
        else:
            print("☁️ Mode Improvisation.")

    # --- C. GÉNÉRATION IA ---
    messages = [
        {"role": "system", "content": contexte_systeme},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat_completion(messages=messages, model=REPO_ID, max_tokens=600, temperature=0.5)
        reponse_finale = response.choices[0].message.content + source_label
    except Exception as e:
        print(f"❌ Erreur IA : {e}")
        reponse_finale = "Désolé, problème de connexion IA."

    # D. Sauvegarde
    chat_collection.insert_many([
        {"user_id": user, "chat_id": message.chat_id, "role": "user", "content": question, "timestamp": datetime.utcnow()},
        {"user_id": user, "chat_id": message.chat_id, "role": "assistant", "content": reponse_finale, "timestamp": datetime.utcnow()}
    ])

    return {"reponse": reponse_finale}

# ==========================================
# 3. UPLOAD PDF
# ==========================================

@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...), 
    chat_id: str = "default", 
    user: str = Depends(get_current_user)
):
    print(f"📂 Réception PDF : {file.filename}")

    try:
        content = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        text_content = ""
        # Limite à 7 pages
        for page in pdf_reader.pages[:7]: 
            text_content += page.extract_text() + "\n"
        
        if len(text_content) > 7000: text_content = text_content[:7000] + "..."
        
        # Sauvegarde contextuelle cachée
        chat_collection.insert_one({
            "user_id": user, 
            "chat_id": chat_id, 
            "role": "system", 
            "content": f"[CONTEXTE PDF] (Fichier: {file.filename}) : {text_content}", 
            "timestamp": datetime.utcnow()
        })
        
        msg_bot = "Bien reçu ! Je suis prêt."
        
        # Sauvegarde visible
        chat_collection.insert_many([
            {"user_id": user, "chat_id": chat_id, "role": "user", "content": f"📎 {file.filename}", "timestamp": datetime.utcnow()},
            {"user_id": user, "chat_id": chat_id, "role": "assistant", "content": msg_bot, "timestamp": datetime.utcnow()}
        ])

        return {"reponse": msg_bot, "filename": file.filename}

    except Exception as e:
        raise HTTPException(400, f"Erreur lecture PDF : {str(e)}")

# ==========================================
# 4. GESTION HISTORIQUE (GET, DELETE, PIN)
# ==========================================

@app.get("/history/ids")
async def get_ids(user: str = Depends(get_current_user)):
    # 1. Tous les chats
    pipeline = [{"$match": {"user_id": user}}, {"$group": {"_id": "$chat_id"}}, {"$sort": {"_id": -1}}]
    raw_ids = [d["_id"] for d in chat_collection.aggregate(pipeline)]
    
    # 2. Les chats épinglés
    pinned_docs = list(chat_meta_collection.find({"user_id": user, "is_pinned": True}))
    pinned_ids = [d["chat_id"] for d in pinned_docs]
    
    return {
        "all_ids": raw_ids,
        "pinned_ids": pinned_ids
    }

@app.get("/history/{chat_id}")
async def get_hist(chat_id: str, user: str = Depends(get_current_user)):
    msgs = list(chat_collection.find(
        {"chat_id": chat_id, "user_id": user, "role": {"$ne": "system"}}, 
        {"_id": 0, "role": 1, "content": 1}
    ).sort("timestamp", 1))
    return {"history": msgs}

@app.delete("/history/{chat_id}")
async def del_hist(chat_id: str, user: str = Depends(get_current_user)):
    chat_collection.delete_many({"chat_id": chat_id, "user_id": user})
    chat_meta_collection.delete_one({"chat_id": chat_id, "user_id": user})
    return None

@app.delete("/history/all")
async def del_all_hist(user: str = Depends(get_current_user)):
    chat_collection.delete_many({"user_id": user})
    chat_meta_collection.delete_many({"user_id": user})
    return {"msg": "Tout supprimé"}

@app.post("/history/pin/{chat_id}")
async def toggle_pin(chat_id: str, user: str = Depends(get_current_user)):
    existing = chat_meta_collection.find_one({"chat_id": chat_id, "user_id": user})
    if existing and existing.get("is_pinned"):
        chat_meta_collection.update_one({"chat_id": chat_id, "user_id": user}, {"$set": {"is_pinned": False}})
        return {"status": "unpinned"}
    else:
        chat_meta_collection.update_one(
            {"chat_id": chat_id, "user_id": user}, 
            {"$set": {"is_pinned": True}}, 
            upsert=True
        )
        return {"status": "pinned"}