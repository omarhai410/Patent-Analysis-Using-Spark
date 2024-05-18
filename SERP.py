import requests
import pandas as pd

# Lien de l'API Serpapi avec votre clé
api_key = "2fa3cbdd769a81acd32a52db828a4a1c00f320381106ac120e72d4e56d2ae406"

# Lire les identifiants de brevets à partir du fichier patent.txt
with open("patent.txt", "r") as file:
    patent_ids = file.read().splitlines()

# Créer une liste pour stocker les informations
patent_info_list = []

# Parcourir les identifiants de brevets
for patent_id in patent_ids:
    # Construire l'URL de l'API Serpapi avec l'identifiant de brevet actuel
    api_url = f"https://serpapi.com/search.json?engine=google_patents&q=({patent_id})&api_key={api_key}"

    # Faire la requête à l'API Serpapi
    response = requests.get(api_url)

    # Vérifier si la requête a réussi (code d'état 200)
    if response.status_code == 200:
        # Charger les données JSON à partir de la réponse
        data = response.json()

        # Extraire les informations des résultats organiques
        results = data.get('organic_results', [])

        # Parcourir les résultats
        for result in results:
            patent_info = {
                "patent_id": result.get("patent_id", ""),
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "priority_date": result.get("priority_date", ""),
                "filing_date": result.get("filing_date", ""),
                "grant_date": result.get("grant_date", ""),
                "publication_date": result.get("publication_date", ""),
                "inventor": result.get("inventor", ""),
                "assignee": result.get("assignee", ""),
                "publication_number": result.get("publication_number", ""),
                "language": result.get("language", ""),
                "thumbnail": result.get("thumbnail", ""),
                "pdf": result.get("pdf", ""),
                "figures": result.get("figures", []),
                "country_status": result.get("country_status", {})
            }
            patent_info_list.append(patent_info)
    else:
        print(f"La requête pour le brevet {patent_id} a échoué avec le code d'état {response.status_code}")

# Créer un DataFrame pandas à partir de la liste d'informations
df = pd.DataFrame(patent_info_list)

# Écrire le DataFrame dans un fichier Excel
excel_file_path = "patent_info.xlsx"
df.to_excel(excel_file_path, index=False, engine='openpyxl')

print(f"Les informations des brevets ont été enregistrées dans {excel_file_path}")
