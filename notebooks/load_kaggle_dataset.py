import kaggle
import pandas as pd
import os
import zipfile

# --- Configuration ---
DATASET_SLUG = "bhaveshmittal/python-programming-questions-dataset"
DOWNLOAD_PATH = "./kaggle_data" 
ZIP_FILE_NAME = "python-programming-questions-dataset.zip"
# --- CORRECTION ICI ---
CSV_FILE_NAME = "Python Programming Questions Dataset.csv" # <-- Nom Correct
# --- FIN CORRECTION ---

os.makedirs(DOWNLOAD_PATH, exist_ok=True)
zip_file_path = os.path.join(DOWNLOAD_PATH, ZIP_FILE_NAME)
csv_file_path = os.path.join(DOWNLOAD_PATH, CSV_FILE_NAME)

def download_kaggle_dataset():
    """Télécharge le dataset depuis Kaggle."""
    print(f"--- Tentative de téléchargement du dataset : {DATASET_SLUG} ---")
    print(f"Vérifiez que votre fichier 'kaggle.json' est bien placé.")
    try:
        kaggle.api.authenticate() 
        print("Authentification Kaggle réussie.")
        kaggle.api.dataset_download_files(DATASET_SLUG, path=DOWNLOAD_PATH, quiet=False, force=False)
        print(f"Dataset téléchargé (ou déjà présent) dans : {zip_file_path}")
        return True
    except Exception as e:
        print(f"!!! ERREUR lors du téléchargement depuis Kaggle : {e}")
        return False

def unzip_dataset():
    """Décompresse le fichier ZIP."""
    print(f"--- Tentative de décompression de : {zip_file_path} ---")
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(DOWNLOAD_PATH) 
        print(f"Fichier décompressé avec succès dans : {DOWNLOAD_PATH}")
        if os.path.exists(csv_file_path):
             print(f"Fichier CSV trouvé : {csv_file_path}")
             return True
        else:
             print(f"!!! ERREUR : Le fichier CSV '{CSV_FILE_NAME}' n'a pas été trouvé après décompression.")
             print("Fichiers extraits :", os.listdir(DOWNLOAD_PATH))
             return False
    except zipfile.BadZipFile:
        print(f"!!! ERREUR : Le fichier téléchargé '{ZIP_FILE_NAME}' n'est pas un ZIP valide.")
        return False
    except Exception as e:
        print(f"!!! ERREUR lors de la décompression : {e}")
        return False

def load_data_from_csv():
    """Charge le CSV dans un DataFrame Pandas."""
    print(f"--- Tentative de chargement du CSV : {csv_file_path} ---")
    try:
        df = pd.read_csv(csv_file_path)
        print("Chargement du CSV dans un DataFrame Pandas réussi.")
        return df
    except FileNotFoundError:
        print(f"!!! ERREUR : Fichier CSV '{csv_file_path}' non trouvé.")
        return None
    except Exception as e:
        print(f"!!! ERREUR lors de la lecture du CSV : {e}")
        return None

# --- Exécution Principale ---
if __name__ == "__main__":
    if download_kaggle_dataset():
        if unzip_dataset():
            dataframe = load_data_from_csv()
            if dataframe is not None:
                print("\n--- Aperçu du Dataset ---")
                print(dataframe.head()) 
                print("\n--- Informations sur le Dataset ---")
                print(dataframe.info())

# --- Code à ajouter après avoir chargé 'dataframe' ---

OUTPUT_QA_FILE = "kaggle_python_qa_dataset.csv" # Nom du fichier final Q/R

def transform_to_qa(df):
    """Transforme le DataFrame Kaggle en format Question/Réponse."""
    print(f"\n--- Transformation en format Q/R ---")
    qa_list = []
    
    for index, row in df.iterrows():
        instruction = str(row['Instruction']).strip() if pd.notna(row['Instruction']) else ""
        input_data = str(row['Input']).strip() if pd.notna(row['Input']) else ""
        output_data = str(row['Output']).strip() if pd.notna(row['Output']) else ""

        # Ignorer si l'instruction ou l'output est vide
        if not instruction or not output_data:
            continue

        # Construire la question
        question = instruction
        if input_data: # Ajouter l'input s'il existe
            question += f" (Exemple d'entrée: {input_data})"
            
        # La réponse est l'output
        reponse = output_data
        
        # Optionnel: Formater le code Python dans la réponse avec Markdown
        # Si la réponse commence par 'def ' ou 'class ', on peut l'enrober
        if reponse.startswith('def ') or reponse.startswith('class '):
             reponse = f"Voici un exemple de code Python :\n```python\n{reponse}\n```"

        qa_list.append({'question': question, 'reponse': reponse})
        
    if not qa_list:
        print("Aucune paire Q/R valide n'a pu être créée.")
        return None
        
    # Créer un nouveau DataFrame
    qa_df = pd.DataFrame(qa_list)
    print(f"{len(qa_df)} paires Q/R créées.")
    
    # Nettoyage simple (doublons, longueur minimale)
    qa_df.drop_duplicates(inplace=True)
    qa_df = qa_df[(qa_df['question'].str.len() > 10) & (qa_df['reponse'].str.len() > 10)]
    print(f"{len(qa_df)} paires Q/R après nettoyage.")
    
    return qa_df

# --- Exécution de la transformation et sauvegarde ---
if dataframe is not None: # Vérifie que le dataframe a bien été chargé
    qa_dataframe = transform_to_qa(dataframe)
    
    if qa_dataframe is not None and not qa_dataframe.empty:
        try:
            qa_dataframe.to_csv(OUTPUT_QA_FILE, index=False, encoding='utf-8-sig')
            print(f"--- Dataset Q/R sauvegardé avec succès dans : {OUTPUT_QA_FILE} ---")
            print("--- N'oubliez pas de relire et potentiellement nettoyer ce fichier manuellement ! ---")
        except Exception as e:
            print(f"!!! ERREUR lors de la sauvegarde du CSV Q/R : {e}")