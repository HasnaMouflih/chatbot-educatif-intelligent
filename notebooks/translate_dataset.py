import pandas as pd
from googletrans import Translator
import time
import os

# --- Configuration ---
# Le fichier CSV anglais (de Kaggle) doit être dans le dossier 'kaggle_data'
INPUT_CSV = os.path.join("kaggle_data", "Python Programming Questions Dataset.csv")
# Le nouveau fichier qu'on va créer
OUTPUT_CSV_FR = os.path.join("kaggle_data", "kaggle_python_qa_dataset_FR.csv") 

# Pour reprendre là où on s'est arrêté (si le script plante)
START_INDEX = 0 

print(f"--- Début de la traduction de {INPUT_CSV} ---")

try:
    # Charger le dataset anglais
    df = pd.read_csv(INPUT_CSV)
    print(f"Dataset anglais chargé : {len(df)} lignes.")

    # Préparer le traducteur
    translator = Translator()

    translated_rows = []

    # Reprendre si un fichier de sortie existe déjà
    if os.path.exists(OUTPUT_CSV_FR):
        print("Fichier de sortie existant trouvé. Reprise...")
        df_fr = pd.read_csv(OUTPUT_CSV_FR)
        translated_rows = df_fr.to_dict('records')
        START_INDEX = len(translated_rows)
        print(f"Reprise à partir de la ligne {START_INDEX}.")

    # Itérer sur les lignes (à partir de START_INDEX)
    # df.iloc[START_INDEX:] : [ligne_debut:]
    for index, row in df.iloc[START_INDEX:].iterrows():

        # Extraire la question et la réponse (le code)
        question_en = str(row['Instruction'])
        reponse_code = str(row['Output']) # La réponse (code) reste la même

        # Ignorer si vide
        if not question_en or not reponse_code:
            continue

        try:
            # --- TRADUCTION ---
            # On traduit la question anglaise en français
            traduction = translator.translate(question_en, src='en', dest='fr')
            question_fr = traduction.text
            # ------------------

            # Ajouter la paire (question FR, réponse Code) à notre liste
            translated_rows.append({'question': question_fr, 'reponse': reponse_code})

            # Afficher la progression
            if (index + 1) % 10 == 0:
                print(f"Ligne {index + 1}/{len(df)} : Traduit '{question_en[:30]}...' -> '{question_fr[:30]}...'")

            # --- SAUVEGARDE FRÉQUENTE ---
            # Sauvegarder toutes les 100 lignes (au cas où ça plante)
            if (index + 1) % 100 == 0:
                pd.DataFrame(translated_rows).to_csv(OUTPUT_CSV_FR, index=False, encoding='utf-8-sig')
                print(f"*** Sauvegarde intermédiaire ({len(translated_rows)} lignes) ***")

            # --- PAUSE OBLIGATOIRE ---
            # Faire une pause pour ne pas être banni par Google
            time.sleep(0.5) # 0.5 seconde

        except Exception as e_translate:
            print(f"!!! ERREUR Ligne {index}: {e_translate}. On continue...")
            time.sleep(5) # Pause plus longue en cas d'erreur

    # --- Sauvegarde Finale ---
    print("\nTraduction terminée. Sauvegarde finale...")
    final_df = pd.DataFrame(translated_rows)
    final_df.drop_duplicates(inplace=True) # Enlever les doublons
    final_df.to_csv(OUTPUT_CSV_FR, index=False, encoding='utf-8-sig')
    print(f"--- Fichier français sauvegardé avec succès dans {OUTPUT_CSV_FR} ({len(final_df)} lignes) ---")

except FileNotFoundError:
    print(f"!!! ERREUR : Fichier d'entrée '{INPUT_CSV}' non trouvé.")
except Exception as e_main:
    print(f"!!! ERREUR inattendue : {e_main}")