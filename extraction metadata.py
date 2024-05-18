from selenium import webdriver
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient


# Connexion à la base de données MongoDB
client = MongoClient('localhost', 27017)  # Assurez-vous que MongoDB est en cours d'exécution sur localhost sur le port par défaut
db = client['spark']  # Sélectionner la base de données
collection = db['data']  # Sélectionner la collection

with open('patent.txt', 'r') as file:
    lines = file.readlines()

# Initialiser une liste pour stocker les URLs
urls = []

# Remplacer JP2012165709A par chaque ligne du fichier patent.txt
for line in lines[3007:]:  # Commence à partir de la ligne 218
    # Supprimer les sauts de ligne
    line = line.strip()
    # Ajouter l'URL avec le code de brevet remplacé
    urls.append(f'https://patents.google.com/patent/{line}/')

# Initialiser une liste pour stocker les données de chaque brevet
patents_data = []

# Chemin vers le fichier exécutable de Chrome
chrome_path = r"C:\Users\Dell\Downloads\chrome-win\chrome-win\chrome.exe"

# Configuration de Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_path

# Initialiser le navigateur Chrome
driver = webdriver.Chrome(options=chrome_options)


for url in urls:
    # Accéder à l'URL
    driver.get(url)

    # Attendre un peu pour que la page soit complètement chargée
    driver.implicitly_wait(10)

    # Obtenir le contenu HTML de la page après le chargement complet avec JavaScript
    html_content = driver.page_source

    # Créer une instance de BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialiser un dictionnaire pour stocker les données du brevet actuel
    patent_data = {}

    # Trouver la balise h1 par son id
    title_tag = soup.find('h1', {'id': 'title'})
    if title_tag:
        # Extraire le texte du titre
        title = title_tag.text.strip()
        patent_data['title'] = title

    # Trouver la balise abstract par son nom et classe
    abstract_tag = soup.find('patent-text', {'name': 'abstract', 'class': 'style-scope patent-result'})
    if abstract_tag:
        # Extraire le texte de l'abstract
        abstract_div = abstract_tag.find('div', {'class': 'abstract style-scope patent-text'})
        if abstract_div:
            abstract = abstract_div.text.strip()
            patent_data['abstract'] = abstract

    # Trouver tous les contributeurs avec le schéma 'inventor'
    all_inventors = soup.find_all('meta', attrs={'name': 'DC.contributor', 'scheme': 'inventor'})
    # Initialiser une liste pour stocker tous les inventeurs
    inventors = []
    if all_inventors:
        for inventor in all_inventors:
            inventor_content = inventor.get('content')
            if inventor_content:
                inventors.append(inventor_content.strip())
        patent_data['inventors'] = inventors

    # Trouver la balise de description
    description_paragraphs = soup.find_all('div', class_='description-line')
    if description_paragraphs:
        patent_data['description'] = [paragraph.text.strip() for paragraph in description_paragraphs]
    else:
        description_tag = soup.find('patent-text', {'name': 'description', 'class': 'style-scope patent-result'})
        if description_tag:
            description_paragraphs = description_tag.find_all('div', {'class': 'description-paragraph style-scope patent-text'})
            patent_data['description'] = [paragraph.text.strip() for paragraph in description_paragraphs]

    # Trouver la balise div avec la classe 'publication'
    publication_date_tag = soup.find('div', {'class': 'publication style-scope application-timeline'})
    if publication_date_tag:
        # Extraire le texte de la date de publication
        publication_date = publication_date_tag.text.strip()
        patent_data['publication_date'] = publication_date

    # Trouver la balise image-carousel
    image_carousel_tag = soup.find('image-carousel', {'id': 'figures'})
    if image_carousel_tag:
        # Trouver toutes les balises img à l'intérieur de la balise image-carousel
        image_tags = image_carousel_tag.find_all('img', {'class': 'style-scope image-carousel'})
        patent_data['images'] = [image_tag['src'] for image_tag in image_tags]

    # Trouver la balise <p> avec la classe 'tagline style-scope patent-result'
    country_tag = soup.find('p', {'class': 'tagline style-scope patent-result'})
    if country_tag:
        # Extraire le texte du pays
        country = country_tag.text.strip()
        patent_data['country'] = country

    # Trouver la balise div avec la classe 'priority style-scope application-timeline'
    date_div = soup.find('div', {'class': 'priority style-scope application-timeline'})
    if date_div:
        # Extraire le texte de la date
        event_date = date_div.text.strip()
        patent_data['event_date'] = event_date

    # Trouver la classe des publications similaires
    publications_class = soup.find('div', {'class': 'responsive-table style-scope patent-result'})
    if publications_class:
        similar_publications = []
        publications = publications_class.find_all('div', {'class': 'tr style-scope patent-result'})
        for publication in publications:
            link_element = publication.find('a', {'class': 'style-scope state-modifier'})
            if link_element:
                publication_number = link_element.text.strip()
                publication_date = publication.find('span', {'class': 'td style-scope patent-result'}).text.strip()
                publication_title = publication.find('span', {'class': 'td style-scope patent-result'}).find_next_sibling().text.strip()
                similar_publications.append({
                    "publication_number": publication_number,
                    "publication_date": publication_date,
                    "publication_title": publication_title
                })
        patent_data['similar_publications'] = similar_publications

    # Trouver l'assignataire actuel
    current_assignee = "Null"
    current_assignee_tag = soup.find('meta', attrs={'name': 'DC.contributor', 'scheme': 'assignee'})
    if current_assignee_tag:
        current_assignee = current_assignee_tag.get('content').strip()
    patent_data['current_assignees'] = [current_assignee]

    # Trouver la balise div pour la date de priorité
    priority_date_div = soup.find('div', {'class': 'priority style-scope application-timeline'})
    if priority_date_div:
        # Extraire le texte de la balise div
        priority_date = priority_date_div.text.strip()
        patent_data['priority_date'] = priority_date

    # Trouver la balise <a> pour le lien de téléchargement du PDF
    pdf_link_tag = soup.find('a', {'class': 'style-scope patent-result'})
    if pdf_link_tag:
        # Extraire la valeur de l'attribut href (le lien)
        pdf_link = pdf_link_tag.get('href')
        patent_data['pdf_link'] = pdf_link

    h2_tag = soup.find('h2', class_='style-scope patent-result')
    if h2_tag:
        pub_id = h2_tag.text.strip()
        patent_data['ID'] = pub_id

    link_element = soup.select_one('dd.style-scope.patent-result a.style-scope.state-modifier')
    if link_element:
        link = link_element['href']
        text = link_element.get_text()
        patent_data['other_language'] = text

    date_element = soup.find('div', class_='filed style-scope application-timeline')
    if date_element:
        application_date = date_element.get_text()
        patent_data['application_date'] = application_date

    claims_list = soup.find_all('li', class_='claim-dependent style-scope patent-text')
    claims_texts = []

    for claim in claims_list:
        claim_div = claim.find('div', class_='claim-text style-scope patent-text')
        if claim_div:
            claim_text = claim_div.text.strip()
            claims_texts.append(claim_text)

    # Si des revendications ont été trouvées, les ajouter au dictionnaire patent_data
    if claims_texts:
        patent_data['claims'] = claims_texts

    # Ajouter les données du brevet actuel à la liste
    patents_data.append(patent_data)

    collection.insert_one(patent_data)




# Fermer le navigateur
driver.quit()

# Nom du fichier JSON de sortie
output_file = 'patents_data.json'

# Écrire les données dans le fichier JSON
with open(output_file, 'w') as json_file:
    json.dump(patents_data, json_file, indent=4)

print("Les données ont été stockées avec succès dans", output_file)
