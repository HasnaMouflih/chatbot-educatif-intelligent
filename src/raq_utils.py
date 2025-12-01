import os
import pandas as pd
from transformers import pipeline

# ==========================================
# CONFIGURATION
# ==========================================
# Le modèle que vous venez d'entraîner (Dossier créé par le Notebook)
MODEL_PATH = "src/raq_model"
# Vos données nettoyées (Mémoire du robot)
DATA_PATH = "data/processed/dataset_cleaned_readable.csv"

print("🔄 Initialisation du module RAQ...")

qa_pipeline = None
knowledge_base = []

def load_raq_model():
    global qa_pipeline, knowledge_base
    
    # 1. Chargement de la Mémoire (CSV)
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            # On charge toutes les réponses expertes en mémoire
            knowledge_base = df['clean_context'].tolist()
            print(f"📚 Mémoire chargée : {len(knowledge_base)} fiches de connaissances.")
        else:
            print(f"⚠️ Fichier CSV introuvable : {DATA_PATH}")
    except Exception as e:
        print(f"❌ Erreur CSV : {e}")

    # 2. Chargement du Cerveau (Deep Learning)
    try:
        if os.path.exists(MODEL_PATH):
            print(f"🧠 Chargement de votre modèle BERT entraîné...")
            # On charge VOTRE modèle local
            qa_pipeline = pipeline("question-answering", model=MODEL_PATH, tokenizer=MODEL_PATH)
            print("✅ Modèle RAQ chargé avec succès !")
        else:
            print(f"❌ ERREUR : Le dossier {MODEL_PATH} est vide ! L'entraînement a-t-il échoué ?")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")

def get_answer(question):
    """
    Fonction principale : Trouve la réponse technique précise.
    """
    if not qa_pipeline or not knowledge_base:
        return None

    # A. RETRIEVAL (Trouver le bon paragraphe)
    best_context = ""
    best_score = 0
    question_words = set(question.lower().split())

    for context in knowledge_base:
        if not isinstance(context, str): continue
        # Score de similarité simple (mots communs)
        score = sum(1 for word in question_words if word in context.lower())
        if score > best_score:
            best_score = score
            best_context = context
    
    if best_score == 0:
        return None

    # B. READING (Extraction par IA)
    try:
        result = qa_pipeline(question=question, context=best_context)
        
        # On garde si la confiance est raisonnable
        if result['score'] > 0.001: 
            return {
                "answer": result['answer'],
                "confidence": result['score']
            }
    except:
        pass
        
    return None

# Chargement automatique
load_raq_model()