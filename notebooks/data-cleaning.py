import pandas as pd
import re
import os

# --- Configuration ---
# Chemin vers les fichiers CSV que tu as déjà
INPUT_CSV_EN = "kaggle_python_qa_dataset.csv" # Le CSV avec questions EN / réponses FR


# Le fichier de sortie final, propre et prêt pour Colab
OUTPUT_FILE_CLEANED = "dataset_bilingue_nettoye_final.csv"

# Les formats de réponse standards que nous voulons
INTRO_FR = "Voici un exemple de code Python :"
INTRO_EN = "Here is a Python code example:"

print("--- Début du nettoyage et de la combinaison des datasets ---")

def load_and_clean_en(filepath):
    """Charge le dataset Anglais et CORRIGE l'intro française."""
    print(f"Chargement du dataset Anglais depuis : {filepath}")
    try:
        df = pd.read_csv(filepath)
        df = df[['question', 'reponse']] # Garder seulement ces colonnes
        
        def format_en_answer(answer_text):
            answer_text = str(answer_text).strip()
            # CORRECTION: Remplacer l'intro française par l'intro anglaise
            if answer_text.startswith(INTRO_FR):
                answer_text = answer_text.replace(INTRO_FR, INTRO_EN, 1) # '1' = remplacer 1 seule fois
            
            # S'assurer que le code est bien formaté
            if not answer_text.startswith(INTRO_EN) and (answer_text.startswith("def ") or answer_text.startswith("class ") or answer_text.startswith("import ")):
                 answer_text = f"{INTRO_EN}\n```python\n{answer_text}\n```"
            return answer_text

        df['reponse'] = df['reponse'].apply(format_en_answer)
        print(f"{len(df)} lignes Anglaises chargées et formatées.")
        return df
        
    except FileNotFoundError:
        print(f"!!! ERREUR : Fichier Anglais '{filepath}' introuvable.")
        return pd.DataFrame() # Retourne un dataframe vide
    except Exception as e:
        print(f"!!! ERREUR chargement dataset Anglais : {e}")
        return pd.DataFrame()

def load_and_clean_fr(filepath):
    """Charge le dataset Français et AJOUTE le format Markdown."""
    print(f"Chargement du dataset Français depuis : {filepath}")
    try:
        df = pd.read_csv(filepath)
        df = df[['question', 'reponse']] # S'assurer qu'on a les bonnes colonnes

        def format_fr_answer(answer_text):
            answer_text = str(answer_text).strip()
            # CORRECTION: Ajouter l'intro et le Markdown au code brut
            if answer_text.startswith("def ") or answer_text.startswith("class ") or answer_text.startswith("import "):
                return f"{INTRO_FR}\n```python\n{answer_text}\n```"
            # Si c'est déjà formaté (au cas où), ne rien faire
            elif answer_text.startswith(INTRO_FR):
                return answer_text
            return answer_text # Retourne le texte tel quel s'il n'est pas reconnu

        df['reponse'] = df['reponse'].apply(format_fr_answer)
        print(f"{len(df)} lignes Françaises chargées et formatées.")
        return df

    except FileNotFoundError:
        print(f"!!! ERREUR : Fichier Français '{filepath}' introuvable.")
        return pd.DataFrame() # Retourne un dataframe vide
    except Exception as e:
        print(f"!!! ERREUR chargement dataset Français : {e}")
        return pd.DataFrame()

# --- Exécution Principale ---
if __name__ == "__main__":
    df_en = load_and_clean_en(INPUT_CSV_EN)
   

    if not df_en.empty and not df_fr.empty:
        # 1. Combiner les deux datasets
        df_final = pd.concat([df_en, df_fr], ignore_index=True)
        print(f"\nDatasets combinés. Total brut : {len(df_final)} lignes.")

        # 2. Nettoyage final (comme ton ancien script)
        df_final.dropna(subset=['question', 'reponse'], inplace=True) # Enlever lignes vides
        
        # Nettoyer les espaces
        df_final['question'] = df_final['question'].astype(str).str.strip().apply(lambda x: re.sub(r'\s+', ' ', x))
        df_final['reponse'] = df_final['reponse'].astype(str).str.strip().apply(lambda x: re.sub(r'\s+', ' ', x))

        df_final.drop_duplicates(subset=['question'], inplace=True) # Supprimer questions dupliquées
        
        # Filtrer par longueur
        df_final = df_final[(df_final['question'].str.len() > 10) & (df_final['reponse'].str.len() > 20)]

        print(f"Nettoyage final terminé. Total : {len(df_final)} lignes uniques.")

        # 3. Sauvegarder
        df_final.to_csv(OUTPUT_FILE_CLEANED, index=False, encoding='utf-8-sig')
        print(f"--- Dataset BILINGUE NETTOYÉ sauvegardé dans : {OUTPUT_FILE_CLEANED} ---")
        print("--- Ce fichier est prêt pour l'entraînement sur Colab ! ---")
    else:
        print("!!! ERREUR : Un des datasets (EN ou FR) est vide ou n'a pas pu être chargé. Sauvegarde annulée.")