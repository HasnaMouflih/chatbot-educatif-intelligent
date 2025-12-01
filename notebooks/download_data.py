import os
from kaggle.api.kaggle_api_extended import KaggleApi

# --- 1. TES IDENTIFIANTS KAGGLE (Colle-les ici) ---
# Remplace "ton_username" et "ta_cle_secrete" par ce qu'il y a dans ton token
KAGGLE_USERNAME = "HASNA_MOUFLIH1"  # Ex: 
KAGGLE_KEY = "KGAT_8914fb63e33e7c185402468c01bfbae7"      # Ex: "a1b2c3d4..."

# --- 2. CONFIGURATION ---
DATASET_NAME = "chinmayadatt/dataset-python-question-answer"
OUTPUT_DIR = "../data/raw"

def download_with_token():
    print("🚀 Configuration de l'accès Kaggle...")

    # On force les variables d'environnement pour que Kaggle croie que le fichier existe
    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_KEY

    try:
        # Authentification
        api = KaggleApi()
        api.authenticate()
        print(f"✅ Connecté en tant que : {KAGGLE_USERNAME}")

        # Création du dossier
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"📂 Dossier créé : {OUTPUT_DIR}")

        # Téléchargement
        print(f"⬇️ Téléchargement du dataset '{DATASET_NAME}'...")
        
        api.dataset_download_files(
            DATASET_NAME, 
            path=OUTPUT_DIR, 
            unzip=True
        )
        
        print(f"🎉 SUCCÈS ! Données téléchargées dans '{OUTPUT_DIR}'")
        print("   Fichiers :", os.listdir(OUTPUT_DIR))

    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("👉 Vérifie que tu as bien copié le username et la key sans espaces.")

if __name__ == "__main__":
    download_with_token()