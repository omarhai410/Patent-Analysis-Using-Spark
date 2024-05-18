import requests
from bs4 import BeautifulSoup
import os

def download_pdf(url, destination_folder):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pdf_link = soup.select_one('a[href$=".pdf"]')

    if pdf_link:
        pdf_url = pdf_link['href']

        local_filename = os.path.join(destination_folder, os.path.basename(pdf_url))

        if not os.path.exists(local_filename):
            # Télécharger le PDF uniquement s'il n'existe pas encore
            response = requests.get(pdf_url, stream=True)
            with open(local_filename, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        pdf_file.write(chunk)

            print(f"Le PDF a été téléchargé avec succès : {local_filename}")
        else:
            print(f"Le fichier existe déjà : {local_filename}")
    else:
        print(f"Aucun lien PDF trouvé sur la page pour le brevet {patent}.")

# Lire les brevets depuis le fichier patent.txt
with open('patent.txt', 'r') as file:
    patents = file.read().splitlines()

# Répertoire de destination pour enregistrer les PDF téléchargés
destination_folder = 'patent_pdfs'
os.makedirs(destination_folder, exist_ok=True)

# Boucle à travers la liste des brevets et télécharger les PDF correspondants
for patent in patents:
    patent_url = f'https://patents.google.com/patent/{patent}/fr'
    download_pdf(patent_url, destination_folder)

