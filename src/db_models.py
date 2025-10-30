# Fichier: src/db_models.py
# (NOUVEAU - Modèles de données Pydantic)

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# --- Modèles pour l'Authentification ---

class UserCreate(BaseModel):
    """ Modèle pour la création d'un compte """
    username: EmailStr = Field(..., description="L'email de l'utilisateur, sert d'identifiant")
    password: str = Field(..., min_length=8, description="Mot de passe (min 8 caractères)")

class UserLogin(BaseModel):
    """ Modèle pour la connexion """
    username: EmailStr
    password: str

class Token(BaseModel):
    """ Modèle pour renvoyer le token JWT """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """ Modèle pour les données contenues dans le token """
    username: Optional[str] = None

# --- Modèles pour le Chatbot ---

class ChatQuestion(BaseModel):
    """ Modèle pour une question posée au chatbot """
    chat_id: str = Field(..., description="ID unique de la conversation")
    question: str = Field(..., description="Question de l'utilisateur")