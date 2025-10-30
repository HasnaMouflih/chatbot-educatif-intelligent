# Fichier: src/model_utils.py (Version V4 - Détection de Langue)

from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import os
import traceback
from langdetect import detect # <-- NOUVEL IMPORT

# --- Variables Globales ---
generative_pipeline = None
# Vérifie bien que ce chemin est correct
nom_modele_ou_chemin = "models_saved/dataset_educatif.csv1" 

# --- Préfixes (dans les deux langues) ---
PREFIX_FR = "Réponds à la question de programmation suivante en français : "
PREFIX_EN = "Answer the following programming question in English: "

# --- Fonctions ---

def load_model():
    """Charge le pipeline de génération de texte (fine-tuné) au démarrage."""
    global generative_pipeline
    if not os.path.exists(nom_modele_ou_chemin) or not os.path.isdir(nom_modele_ou_chemin):
        print(f"!!! ERREUR CRITIQUE : Dossier modèle introuvable : {nom_modele_ou_chemin}")
        generative_pipeline = None
        return
    try:
        print(f"--- Chargement du modèle Génératif BILINGUE ({nom_modele_ou_chemin}) ---")
        device_to_use = 0 if torch.cuda.is_available() else -1
        print(f"--- Utilisation {'GPU' if device_to_use == 0 else 'CPU'}. ---")

        model = AutoModelForSeq2SeqLM.from_pretrained(nom_modele_ou_chemin)
        tokenizer = AutoTokenizer.from_pretrained(nom_modele_ou_chemin)

        generative_pipeline = pipeline(
            "text2text-generation", model=model, tokenizer=tokenizer, device=device_to_use
        )
        print("--- Modèle BILINGUE local chargé avec succès ! ---")
    except Exception as e:
        print(f"!!! ERREUR lors du chargement du modèle local : {e}")
        print(traceback.format_exc())
        generative_pipeline = None


# --- Fonction predict (Corrigée V4 avec Détection de Langue) ---
def predict(question: str) -> str:
    """Génère une réponse à la question (FR ou EN) en utilisant le modèle bilingue."""
    global generative_pipeline, PREFIX_FR, PREFIX_EN

    print(f"--- Génération (bilingue V4) demandée pour : '{question}' ---")

    if generative_pipeline is None:
        return "Désolé, le cerveau IA n'est pas disponible (problème de chargement)."

    try:
        # --- DÉTECTION DE LANGUE ---
        try:
            # Si la question est très courte, la détection peut échouer
            if len(question.strip()) < 10:
               # Supposer l'anglais par défaut ou une autre logique
               # Pour ce test, on va supposer la dernière langue détectée ou 'en'
               lang = 'en' # Simple supposition pour les mots courts
               print(f"Question courte, supposition : {lang}")
            else:
               lang = detect(question)
               print(f"Langue détectée : {lang}")
        except Exception as lang_e:
            print(f"Erreur détection langue ({lang_e}), utilisation Anglais par défaut.")
            lang = 'en'

        # --- CHOIX DU PROMPT (FR ou EN) ---
        if lang == 'fr':
            prompt = PREFIX_FR + question
            prefix_entrainement = PREFIX_FR
        else:
            prompt = PREFIX_EN + question
            prefix_entrainement = PREFIX_EN
        # ---------------------------------

        print(f"Prompt envoyé au modèle : '{prompt}'")

        resultats = generative_pipeline(
            prompt,
            max_new_tokens=768,       # <-- AUGMENTÉ (pour que la réponse ne soit pas coupée)
            num_return_sequences=1,
            no_repeat_ngram_size=3,   # Évite les répétitions
            do_sample=True,           # <-- AJOUTÉ (corrige le warning)
            temperature=0.7,
            top_p=0.95,
            early_stopping=True
        )

        print(f"Résultat brut du modèle : {resultats}")

        if resultats and len(resultats) > 0:
            reponse_generee = resultats[0].get('generated_text')
            reponse_finale = reponse_generee.strip()

            # Nettoyage (enlever le préfixe s'il est répété)
            reponse_lower = reponse_finale.lower()
            if reponse_lower.startswith(prompt.lower()):
                reponse_finale = reponse_finale[len(prompt):].strip()
            elif reponse_lower.startswith(prefix_entrainement.lower()):
                reponse_finale = reponse_finale[len(prefix_entrainement):].strip()

            if not reponse_finale or len(reponse_finale) < 10:
                return "Je n'ai pas pu générer une réponse pertinente. Essayez de reformuler."

            return reponse_finale
        else:
            return "Je n'ai pas pu générer de réponse."

    except Exception as e:
        print(f"!!! ERREUR pendant la génération : {e}")
        print(traceback.format_exc())
        return "Oups, une erreur s'est produite."