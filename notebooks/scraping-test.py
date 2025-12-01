import requests
from bs4 import BeautifulSoup
import json
import re
import time

# Liste des 10 pages (Chapitres) de la documentation officielle
URLS = [
    "https://docs.python.org/fr/3/tutorial/appetite.html",      # 1. Introduction
    "https://docs.python.org/fr/3/tutorial/introduction.html",  # 2. Les nombres et chaines
    "https://docs.python.org/fr/3/tutorial/controlflow.html",   # 3. If, For, Range
    "https://docs.python.org/fr/3/tutorial/datastructures.html",# 4. Listes et Tuples
    "https://docs.python.org/fr/3/tutorial/modules.html",       # 5. Modules
    "https://docs.python.org/fr/3/tutorial/inputoutput.html",   # 6. Fichiers
    "https://docs.python.org/fr/3/tutorial/errors.html",        # 7. Exceptions (Try/Except)
    "https://docs.python.org/fr/3/tutorial/classes.html",       # 8. Classes (POO)
    "https://docs.python.org/fr/3/tutorial/stdlib.html",        # 9. Librairie Standard
    "https://docs.python.org/fr/3/faq/design.html"              # 10. FAQ Conception
]

HEADERS = {'User-Agent': 'EtudiantProjectBot/1.0'}

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text) # Enlève les notes [1]
    text = text.replace('\n', ' ').strip()
    return re.sub(r'\s+', ' ', text)

def generate_qa_rules(text):
    """
    Génère des questions basées sur des règles grammaticales (Extraction Intelligente)
    """
    qa_pairs = []
    
    # Règle 1 : Définitions ("X est un Y")
    match_def = re.search(r"^([A-Z][\w\s]+) (est|sont) (un|une|le|la|des) ([\w\s,']{10,100})\.", text)
    if match_def:
        sujet = match_def.group(1)
        definition = match_def.group(4)
        qa_pairs.append({
            "question": f"Qu'est-ce que {sujet} ?",
            "answer": f"{match_def.group(3)} {definition}"
        })

    # Règle 2 : Utilité ("permet de", "sert à")
    if "permet de" in text:
        parts = text.split("permet de")
        if len(parts) == 2 and len(parts[0]) < 50: # Le sujet doit être court
            sujet = parts[0].strip()
            action = parts[1].split('.')[0].strip()
            qa_pairs.append({
                "question": f"Que permet de faire {sujet} ?",
                "answer": f"permet de {action}"
            })

    # Règle 3 : Mots clés techniques (Detection simple)
    keywords = ["boucle for", "liste", "tuple", "dictionnaire", "fonction", "classe", "exception"]
    for k in keywords:
        if k in text.lower() and len(text) < 200:
            qa_pairs.append({
                "question": f"Que peux-tu dire sur : {k} ?",
                "answer": text # La phrase entière sert de contexte/réponse
            })

    return qa_pairs

def scrape_all():
    all_entries = []
    total_questions = 0

    print(f"🚀 Démarrage du scraping sur {len(URLS)} pages...")

    for i, url in enumerate(URLS):
        print(f"   🌍 ({i+1}/10) Lecture de : {url}...")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"      ❌ Erreur {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Dans la doc Python, le contenu est souvent dans 'div.body' ou 'section'
            content = soup.find('div', {'class': 'body'}) or soup.find('section')
            
            if not content:
                print("      ⚠️ Pas de contenu détecté.")
                continue

            paragraphs = content.find_all('p')
            
            for p in paragraphs:
                text = clean_text(p.get_text())
                if len(text) < 40: continue

                # Génération des questions
                pairs = generate_qa_rules(text)
                
                for pair in pairs:
                    # Calcul start_index pour le Deep Learning
                    start_idx = text.find(pair['answer'])
                    # Si on ne trouve pas la réponse exacte (à cause du nettoyage), on cherche une approximation
                    if start_idx == -1: 
                        # Fallback : on prend les 20 premiers caractères
                        snippet = pair['answer'][:20]
                        start_idx = text.find(snippet)

                    if start_idx != -1:
                        entry = {
                            "title": f"Doc_Python_Part_{i+1}",
                            "paragraphs": [{
                                "context": text,
                                "qas": [{
                                    "id": str(abs(hash(pair['question'] + str(time.time())))),
                                    "question": pair['question'],
                                    "answers": [{"text": pair['answer'], "answer_start": start_idx}],
                                    "is_impossible": False
                                }]
                            }]
                        }
                        all_entries.append(entry)
                        total_questions += 1

            print(f"      ✅ {len(pairs)} questions extraites de cette page.")
            time.sleep(1) # Pause pour être poli avec le serveur

        except Exception as e:
            print(f"      ❌ Erreur script : {e}")

    # Sauvegarde finale
    final_json = {"version": "v2.0", "data": all_entries}
    output_path = "dataset_python_final.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 TERMINÉ ! Dataset complet généré.")
    print(f"📊 Total : {total_questions} questions/réponses prêtes pour l'entraînement.")
    print(f"📂 Fichier : {output_path}")

if __name__ == "__main__":
    scrape_all()