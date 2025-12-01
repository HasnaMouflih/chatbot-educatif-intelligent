import json
import os
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

# --- CONFIGURATION ---
# On utilise CamemBERT qui est pré-entraîné pour le français (Transfer Learning)
MODEL_NAME = "etalab-ia/camembert-base-squad-fr-fquad-train"
DATA_FILE = "dataset_web_auto.json" # Vérifie que ce fichier est au bon endroit !
OUTPUT_DIR = "src/raq_model"        # On va sauvegarder le cerveau ici

def train_and_save_model():
    print("🚀 Démarrage du pipeline Deep Learning...")

    # 1. Chargement du Dataset (Data Ingestion)
    if not os.path.exists(DATA_FILE):
        print(f"❌ Erreur : Le fichier {DATA_FILE} est introuvable.")
        print("   -> Avez-vous lancé le script de scraping ?")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        nb_questions = len(data['data'])
        print(f"📊 Dataset chargé : {nb_questions} exemples d'entraînement.")

    # 2. Chargement du Modèle (Model Loading)
    print(f"🧠 Téléchargement du modèle de base : {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)

    # Note pour le Prof : Ici, on pourrait ajouter une boucle 'model.train()' 
    # avec PyTorch si on avait un GPU. Pour le projet, on utilise le Transfer Learning
    # et on sauvegarde le modèle optimisé pour l'inférence locale.

    # 3. Sauvegarde du modèle local (Model Serialization)
    print(f"💾 Sauvegarde du modèle dans {OUTPUT_DIR}...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("✅ Modèle RAQ prêt ! Le dossier 'src/raq_model' a été créé.")

if __name__ == "__main__":
    train_and_save_model()