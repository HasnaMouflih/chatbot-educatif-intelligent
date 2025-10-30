# Fichier: src/auth_utils.py
# (NOUVEAU - Logique de sécurité et d'authentification)

from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# --- Configuration de la Sécurité ---
# Changez cette clé ! Vous pouvez générer la vôtre avec :
# openssl rand -hex 32
SECRET_KEY = "Kq!8z$T@p9w*G#sVb3N^y&eZ%hXgA+d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Le token expire après 60 minutes

# Contexte pour le hashage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Fonctions de Mot de Passe ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe en clair correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)
# Fichier: src/auth_utils.py

def get_password_hash(password: str) -> str:
    """Génère un hash pour un mot de passe (tronqué à 72 bytes pour bcrypt)"""
    truncated_password_bytes = password.encode('utf-8')[:72]

    # --- AJOUTEZ CETTE LIGNE POUR TESTER ---
    print(f"DEBUG: Hashing password truncated to {len(truncated_password_bytes)} bytes.") 
    # ----------------------------------------

    return pwd_context.hash(truncated_password_bytes)

# --- Fonctions de Token JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un nouveau token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Vérifie un token et renvoie le username (email) s'il est valide"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None # Token invalide
        return username
    except JWTError:
        return None # Token invalide