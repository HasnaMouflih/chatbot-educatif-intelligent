
import pandas as pd
import re
import ast # Pour évaluer les chaînes de caractères comme des listes Python
import os

# --- Configuration ---
# REMPLACE par le nom de ton fichier CSV téléchargé
INPUT_FILE = "../kaggle/Dataset_Python_Question_Answer.csv" 
OUTPUT_FILE = "datafinal.csv" # Le nouveau fichier nettoyé

print(f"--- Début du nettoyage de : {INPUT_FILE} ---")

def clean_answer_string_list(answer_str):
    """
    Nettoie les réponses qui sont formatées comme des listes de chaînes:
    "['Texte 1', 'Texte 2', '```python...```']" -> "Texte 1 Texte 2 ```python...```"
    """
    if not isinstance(answer_str, str):
        return ""

    text = answer_str.strip()
    
    # Vérifier si c'est une chaîne qui ressemble à une liste
    if text.startswith('[') and text.endswith(']'):
        try:
            # ast.literal_eval convertit la chaîne en une vraie liste Python
            # ex: "['a', 'b']" -> ['a', 'b']
            answer_list = ast.literal_eval(text)
            
            # Joindre tous les éléments de la liste en un seul texte
            # On utilise '\n' (saut de ligne) pour séparer les éléments
            # afin de préserver le formatage (ex: listes à puces)
            full_text = "\n".join(str(item).strip() for item in answer_list)
            return full_text
        except (ValueError, SyntaxError):
            # Si ce n'est pas une liste valide, retourner le texte brut nettoyé
            return text.strip("[]'\"")
    else:
        # Si ce n'est pas une liste, retourner le texte brut
        return text

def final_text_cleanup(text):
    """Effectue un nettoyage final pour enlever les espaces superflus."""
    # Remplacer les sauts de ligne multiples par un seul
    text = re.sub(r'(\n\s*)+', '\n', text)
    # Remplacer les espaces multiples par un seul
    text = re.sub(r'(\t| )+', ' ', text)
    return text.strip()

# --- Exécution Principale ---
try:
    # 1. Charger le dataset
    df = pd.read_csv(INPUT_FILE)
    print(f"Dataset chargé : {len(df)} lignes initiales.")
    
    # S'assurer que les colonnes ont les bons noms (ex: 'Question' -> 'question')
    df = df.rename(columns={
        'Question': 'question',
        'Answer': 'reponse'
    })

    # 2. Nettoyage de base (lignes vides, doublons)
    df.dropna(subset=['question', 'reponse'], inplace=True)
    df.drop_duplicates(subset=['question'], inplace=True) # Supprimer questions en double
    print(f"Après suppression des vides/doublons : {len(df)} lignes.")

    # 3. Nettoyage du format de la réponse (le problème de la "fausse" liste)
    print("Nettoyage du format des réponses (conversion de liste en texte)...")
    df['reponse'] = df['reponse'].apply(clean_answer_string_list)
    
    # 4. Nettoyage final du texte (espaces)
    print("Nettoyage final du texte...")
    df['question'] = df['question'].apply(final_text_cleanup)
    df['reponse'] = df['reponse'].apply(final_text_cleanup)

    # 5. Filtrer les réponses incorrectes connues (basé sur ton extrait)
    print("Filtrage des réponses factuellement incorrectes connues...")
    initial_rows = len(df)
    # Filtrer les réponses qui contiennent des termes de statistiques ou de maths pures
    df = df[~df['reponse'].str.contains("Categorical variable", case=False)]
    df = df[~df['reponse'].str.contains("codomain", case=False)]
    # Filtrer la réponse sur id() qui parle de base de données
    df = df[~df['reponse'].str.contains("assigned to it by the database", case=False)]
    # Filtrer la réponse sur open/close qui parle de trading (broker)
    df = df[~df['reponse'].str.contains("submitted to the broker", case=False)]
    # Filtrer la réponse sur lambda qui dit "only one parameter"
    df = df[~df['reponse'].str.contains("lambda function has only one parameter", case=False)]
    
    rows_after_filter = len(df)
    print(f"  {initial_rows - rows_after_filter} lignes incorrectes supprimées.")
    
    # 6. Filtrer par longueur
    df = df[(df['question'].str.len() > 10) & (df['reponse'].str.len() > 20)]
    print(f"Après filtre de longueur, il reste {len(df)} lignes.")

    # 7. Sauvegarder le dataset nettoyé
    if not df.empty:
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n--- Nettoyage terminé. {len(df)} lignes valides sauvegardées dans {OUTPUT_FILE} ---")
    else:
        print("\n--- Nettoyage terminé. Aucune ligne valide à sauvegarder. ---")

except FileNotFoundError:
    print(f"!!! ERREUR : Le fichier d'entrée '{INPUT_FILE}' n'a pas été trouvé.")
except Exception as e:
    print(f"!!! ERREUR inattendue pendant le nettoyage : {e}")