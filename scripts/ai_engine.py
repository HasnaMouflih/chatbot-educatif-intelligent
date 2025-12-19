# Fichier: src/ai_engine.py
import torch
import csv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

# --- CONFIG ---
LORA_DIR = "../models_saved/flan_t5_base_lora_google_flan-t5-base"
BASE_MODEL = "google/flan-t5-base"
CSV_FILE = "../dataset_prepared.csv"

# --- Fonction pour charger CSV ---
def load_csv(csv_file):
    """
    Charge la base CSV et retourne un dictionnaire question -> answer
    """
    context_db = {}
    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                context_db[row["question"].strip()] = row["answer"].strip()
    except FileNotFoundError:
        print(f"!!! ERREUR : Fichier CSV non trouvé -> {csv_file}")
    return context_db

# --- Fonction pour charger LoRA ---
def load_lora_model():
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(LORA_DIR)

    print("Loading base model...")
    base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)

    print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(base_model, LORA_DIR)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)
    model.to(device)

    return tokenizer, model, device

# --- Nettoyage de la réponse ---
def clean_response(text, max_sentences=3):
    """
    Supprime les phrases répétitives et limite le nombre de phrases.
    """
    sentences = text.split(". ")
    seen = set()
    clean_sentences = []
    for s in sentences:
        s = s.strip()
        if s and s not in seen:
            clean_sentences.append(s)
            seen.add(s)
        if len(clean_sentences) >= max_sentences:
            break
    return ". ".join(clean_sentences)

# --- Fonction principale pour répondre à une question ---
def answer_question(question, context_db, tokenizer, model, device):
    """
    Retourne directement la réponse du CSV si la question y figure.
    Sinon, génère une réponse avec le modèle LoRA.
    """
    if question in context_db:
        return context_db[question]
    else:
        inputs = tokenizer(question, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=150,
                min_length=10,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.9,
                repetition_penalty=1.8,
                no_repeat_ngram_size=4,
                pad_token_id=tokenizer.pad_token_id
            )
        return clean_response(tokenizer.decode(outputs[0], skip_special_tokens=True))

# --- Initialisation globale (au démarrage de l'API) ---
context_db = load_csv(CSV_FILE)
tokenizer, model, device = load_lora_model()

print(f"✅ AI Engine prêt avec {len(context_db)} questions dans le CSV")
