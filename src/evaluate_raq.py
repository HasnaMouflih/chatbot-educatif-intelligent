"""
Model Evaluation for Retrieval-based Answering (RAQ)

This script evaluates the Question Answering model
using Exact Match (EM) and F1-score metrics,
commonly used in QA benchmarks (SQuAD / FQuAD).
"""

import torch
import numpy as np
from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# ==========================================
# CONFIGURATION
# ==========================================
MODEL_DIR = "src/raq_model"
DATASET_DIR = "data/processed/tokenized_data"
MAX_ANSWER_LENGTH = 30

device = "cuda" if torch.cuda.is_available() else "cpu"

# ==========================================
# METRICS
# ==========================================
def normalize_text(text):
    return " ".join(text.lower().strip().split())

def exact_match(prediction, ground_truth):
    return normalize_text(prediction) == normalize_text(ground_truth)

def f1_score(prediction, ground_truth):
    pred_tokens = normalize_text(prediction).split()
    gt_tokens = normalize_text(ground_truth).split()
    
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * precision * recall / (precision + recall)

# ==========================================
# LOAD MODEL & DATA
# ==========================================
print("🧠 Chargement du modèle...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForQuestionAnswering.from_pretrained(MODEL_DIR).to(device)
model.eval()

print("📂 Chargement du dataset tokenisé...")
dataset = load_from_disk(DATASET_DIR)["test"]

# ==========================================
# EVALUATION LOOP
# ==========================================
em_scores = []
f1_scores = []

print("🔍 Évaluation en cours...")
for example in dataset.select(range(min(50, len(dataset)))):  # échantillon
    inputs = {
        "input_ids": torch.tensor(example["input_ids"]).unsqueeze(0).to(device),
        "attention_mask": torch.tensor(example["attention_mask"]).unsqueeze(0).to(device)
    }

    with torch.no_grad():
        outputs = model(**inputs)

    start_idx = torch.argmax(outputs.start_logits)
    end_idx = torch.argmax(outputs.end_logits) + 1

    pred_answer = tokenizer.decode(
        example["input_ids"][start_idx:end_idx],
        skip_special_tokens=True
    )

    # Ici, la vérité terrain = tout le contexte
    true_answer = tokenizer.decode(
        example["input_ids"][example["start_positions"]:example["end_positions"]],
        skip_special_tokens=True
    )

    em_scores.append(exact_match(pred_answer, true_answer))
    f1_scores.append(f1_score(pred_answer, true_answer))

# ==========================================
# RESULTS
# ==========================================
print("-" * 40)
print(f"Exact Match (EM): {np.mean(em_scores):.3f}")
print(f"F1 Score        : {np.mean(f1_scores):.3f}")
print("✅ Évaluation terminée.")
