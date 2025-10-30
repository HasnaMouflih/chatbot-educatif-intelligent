import requests
from bs4 import BeautifulSoup, Tag # Import Tag for type checking
import pandas as pd
import time
import re

# --- Configuration ---
SOURCES = [
    # Glossaire (Structure spécifique)
    {
        "url": "https://docs.python.org/fr/3/glossary.html",
        "parser_func": "parse_python_glossary",
        "description": "Glossaire Officiel Python"
    },
    # Pages W3Schools (Structure similaire)
    {
        "url": "https://www.w3schools.com/python/python_variables.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Variables"
    },
    {
        "url": "https://www.w3schools.com/python/python_datatypes.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Data Types"
    },
    {
        "url": "https://www.w3schools.com/python/python_numbers.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Numbers"
    },
     {
        "url": "https://www.w3schools.com/python/python_strings.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Strings"
    },
     {
        "url": "https://www.w3schools.com/python/python_booleans.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Booleans"
    },
    {
        "url": "https://www.w3schools.com/python/python_lists.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Lists" # Ajouté
    },
     {
        "url": "https://www.w3schools.com/python/python_tuples.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Tuples" # Ajouté
    },
     {
        "url": "https://www.w3schools.com/python/python_sets.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Sets" # Ajouté
    },
    {
        "url": "https://www.w3schools.com/python/python_dictionaries.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Dictionaries" # Ajouté
    },
    {
        "url": "https://www.w3schools.com/python/python_conditions.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - If...Else" # Ajouté
    },
    {
        "url": "https://www.w3schools.com/python/python_for_loops.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - For Loops" # Ajouté
    },
     {
        "url": "https://www.w3schools.com/python/python_functions.asp",
        "parser_func": "parse_w3schools_page",
        "description": "W3Schools - Functions" # Ajouté
    },
    # Tutoriel Python Officiel (Structure différente)
    {
        "url": "https://docs.python.org/fr/3/tutorial/introduction.html",
        "parser_func": "parse_python_tutorial_section",
        "description": "Tutoriel Python - Introduction" # Ajouté
    },
    {
        "url": "https://docs.python.org/fr/3/tutorial/controlflow.html",
        "parser_func": "parse_python_tutorial_section",
        "description": "Tutoriel Python - Structures de Contrôle" # Ajouté
    },
    {
        "url": "https://docs.python.org/fr/3/tutorial/datastructures.html",
        "parser_func": "parse_python_tutorial_section",
        "description": "Tutoriel Python - Structures de Données" # Ajouté
    },

]
OUTPUT_FILE = "dataset_python_brut_large.csv" # Nouveau nom de fichier
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
SLEEP_TIME = 0.5 # Augmenter la pause pour être plus respectueux

# --- Fonctions Utilitaires ---
def clean_html_text(tag):
    """Nettoie le texte extrait d'une balise BeautifulSoup."""
    if not tag:
        return ""
    # Utilise .stripped_strings pour mieux gérer les espaces et retours chariots
    text = ' '.join(tag.stripped_strings)
    # Remplacer les espaces multiples restants
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Fonctions de Parsing Spécifiques ---

def parse_python_glossary(soup):
    """Extrait Q/R du glossaire Python (<dt>/<dd>)."""
    data_list = []
    terms = soup.find_all('dt')
    print(f"  Trouvé {len(terms)} termes (glossaire).")
    for term_tag in terms:
        term_text = clean_html_text(term_tag).replace('¶', '')
        definition_tag = term_tag.find_next_sibling('dd')
        definition_text = clean_html_text(definition_tag)
        if term_text and definition_text:
            question = f"Définis le terme Python : '{term_text}'"
            reponse = definition_text
            data_list.append({'question': question, 'reponse': reponse, 'source': 'Glossaire Python'})
        else:
            print(f"  AVERTISSEMENT (Glossaire): Données manquantes pour '{term_text}'")
    return data_list

def parse_w3schools_page(soup):
    """Extrait Q/R de W3Schools (h2/h3 -> p, ul, div.w3-code)."""
    data_list = []
    content = soup.find('div', {'id': 'main'})
    if not content:
        print("  AVERTISSEMENT (W3S): Section 'main' non trouvée.")
        return []

    # Cherche tous les titres h2 et h3 comme points de départ
    elements = content.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'div'], recursive=False)
    current_question = None
    current_answer_parts = []

    print(f"  Analyse des éléments principaux (W3S)...")

    for element in elements:
        # Si c'est un titre pertinent, on commence une nouvelle Q/R
        if element.name in ['h2', 'h3']:
            # Sauvegarder la Q/R précédente si elle existe
            if current_question and current_answer_parts:
                reponse = "\n\n".join(current_answer_parts)
                data_list.append({'question': current_question, 'reponse': reponse, 'source': 'W3Schools'})

            # Commencer une nouvelle Q/R
            question_text = clean_html_text(element)
            ignore_keywords = ["Examples", "Test Yourself", "Video", "Exercises", "Reference", "Tutorial", "Next Chapter", "Previous Chapter"]
            if question_text and not any(keyword in question_text for keyword in ignore_keywords):
                current_question = f"Explique '{question_text}' en Python."
                current_answer_parts = [] # Réinitialiser la réponse
            else:
                current_question = None # Ignorer ce titre et ce qui suit jusqu'au prochain titre valide
                current_answer_parts = []

        # Si c'est un paragraphe, une liste ou un bloc de code et qu'on a une question en cours
        elif current_question and isinstance(element, Tag):
            part_text = ""
            code_example = ""
            # Paragraphes et Listes (non cachés)
            if element.name in ['p', 'ul', 'ol'] and 'w3-hide' not in element.get('class', []):
                 part_text = clean_html_text(element)
                 if part_text and "Next Chapter" not in part_text and "Previous Chapter" not in part_text:
                     current_answer_parts.append(part_text)
            # Blocs de code
            elif element.name == 'div' and 'w3-code' in element.get('class', []):
                 code_block = element.find(['pre', 'code'])
                 if code_block:
                     code_example = clean_html_text(code_block)
                     # Formatter le code avec Markdown
                     current_answer_parts.append(f"Exemple:\n```python\n{code_example}\n```")

    # Ne pas oublier de sauvegarder la dernière Q/R après la boucle
    if current_question and current_answer_parts:
        reponse = "\n\n".join(current_answer_parts)
        data_list.append({'question': current_question, 'reponse': reponse, 'source': 'W3Schools'})

    return data_list

def parse_python_tutorial_section(soup):
    """Tente d'extraire Q/R du tutoriel Python (structure section/titre/para/code)."""
    data_list = []
    main_content = soup.find('div', {'role': 'main'}) or soup.find('main')
    if not main_content:
        print("  AVERTISSEMENT (Tutoriel): Zone de contenu principale non trouvée.")
        return []

    # Cibler les titres de section (h2, h3, h4) qui ont un ID (souvent le cas dans la doc)
    headings = main_content.find_all(['h2', 'h3', 'h4'], id=True)
    print(f"  Trouvé {len(headings)} titres avec ID (Tutoriel).")

    for heading in headings:
        # Utiliser l'ID pour trouver le conteneur de la section (souvent un div parent ou la section elle-même)
        section_container = heading.parent.find_parent(['div', 'section'], class_=lambda x: x != 'clearer') or heading.parent
        if not section_container: continue

        question_text = clean_html_text(heading).replace('¶', '')
        if not question_text or len(question_text) < 5 or question_text.lower() == "notes":
            continue

        question = f"Peux-tu expliquer '{question_text}' d'après le tutoriel Python ?"

        answer_parts = []
        # Chercher les éléments *après* le titre, *à l'intérieur* du conteneur de la section
        # Limiter aux paragraphes et blocs de code jusqu'au prochain titre de même niveau ou supérieur
        next_element = heading.find_next_sibling()
        count = 0
        max_parts = 6 # Limite le nombre d'éléments consécutifs pris pour la réponse

        while next_element and isinstance(next_element, Tag) and next_element.name not in ['h2', 'h3', 'h4'] and count < max_parts:
            part_text = ""
            code_example = ""
            if next_element.name == 'p':
                part_text = clean_html_text(next_element)
            elif next_element.name == 'div' and ('highlight-python3' in next_element.get('class', []) or 'highlight-default' in next_element.get('class', [])):
                code_block = next_element.find('pre')
                if code_block:
                    code_example = clean_html_text(code_block)
                    # Éviter les blocs d'output (commençant souvent par >>> ou ...)
                    if not code_example.strip().startswith(('>>>', '...')):
                         code_example = f"Exemple:\n```python\n{code_example}\n```"
                    else: code_example = "" # Ignorer l'output interactif


            if part_text:
                answer_parts.append(part_text)
                count += 1
            if code_example:
                answer_parts.append(code_example)
                count += 1

            next_element = next_element.find_next_sibling()

        if answer_parts:
            reponse = "\n\n".join(answer_parts)
            data_list.append({'question': question, 'reponse': reponse, 'source': 'Tutoriel Python'})

    return data_list

# --- Fonction Principale ---
def main():
    all_data = []
    print("--- Début du scraping multi-sources ---")

    for source in SOURCES:
        url = source["url"]
        parser_func_name = source["parser_func"]
        description = source["description"]
        print(f"\nTraitement de : {description} ({url})")

        try:
            print("  Téléchargement...")
            response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=20) # Timeout plus long
            response.raise_for_status()
            response.encoding = response.apparent_encoding # Tenter de deviner le bon encodage
            print("  Page téléchargée.")

            soup = BeautifulSoup(response.text, 'html.parser')
            print("  HTML analysé.")

            parser_function = globals().get(parser_func_name)
            if callable(parser_function):
                print("  Extraction des Q/R...")
                extracted_data = parser_function(soup)
                print(f"  {len(extracted_data)} paires Q/R extraites.")
                all_data.extend(extracted_data)
            else:
                print(f"!!! ERREUR : La fonction de parsing '{parser_func_name}' n'existe pas.")

            print(f"  Pause de {SLEEP_TIME} secondes...")
            time.sleep(SLEEP_TIME)

        except requests.exceptions.Timeout:
             print(f"!!! TIMEOUT lors du téléchargement de {url}")
        except requests.exceptions.RequestException as e:
            print(f"!!! ERREUR de téléchargement pour {url}: {e}")
        except Exception as e:
            print(f"!!! ERREUR inattendue pour {url}: {e}")

    # --- Sauvegarde Finale en CSV ---
    print("\n--- Fin du scraping ---")
    if all_data:
        print(f"Total brut de {len(all_data)} paires Q/R collectées.")
        try:
            df = pd.DataFrame(all_data)
            # Nettoyage final avant sauvegarde
            df.dropna(subset=['question', 'reponse'], inplace=True)
            df['question'] = df['question'].astype(str).str.strip() # Assurer string + strip
            df['reponse'] = df['reponse'].astype(str).str.strip()
            df.drop_duplicates(subset=['question', 'reponse'], inplace=True)
            df = df[df['question'].str.len() > 10] # Enlever questions trop courtes
            df = df[df['reponse'].str.len() > 20] # Enlever réponses trop courtes
            print(f"Total après nettoyage final : {len(df)} paires Q/R.")

            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
            print(f"--- Données brutes combinées sauvegardées dans {OUTPUT_FILE} (CSV) ---")
            print("--- N'oubliez pas de RELIRE et NETTOYER ce fichier MANUELLEMENT ! ---")
        except Exception as e:
             print(f"!!! ERREUR lors de la sauvegarde CSV : {e}")
    else:
        print("Aucune donnée n'a été collectée.")

# --- Point d'entrée ---
if __name__ == "__main__":
    main()