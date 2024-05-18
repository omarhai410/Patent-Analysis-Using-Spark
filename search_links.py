import os
import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urlparse

def download_pdf(url, output_directory):
    # Utilisez Rendertron pour rendre la page avec JavaScript
    rendertron_url = f'http://localhost:3000/render/{url}'
    response = requests.get(rendertron_url)
    rendered_html = response.text

    # Utilisez BeautifulSoup pour analyser le HTML rendu
    soup = BeautifulSoup(rendered_html, 'html.parser')

    # Modifiez le sélecteur CSS en fonction de la structure réelle de votre page
    pdf_link_element = soup.select_one('a.style-scope.patent-result')

    if pdf_link_element:
        # Modifiez l'attribut en fonction de la structure réelle de votre page
        pdf_url = pdf_link_element.get('href')

        if pdf_url:
            # Extraire le nom du fichier du chemin de l'URL
            pdf_filename = os.path.join(output_directory, os.path.basename(urlparse(pdf_url).path))
            pdf_filename = pdf_filename.replace('/', '_')  # Remplacer les "/" par "_"

            response = requests.get(pdf_url, stream=True)

            with open(pdf_filename, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            print(f"Downloaded PDF for {url}")
        else:
            print(f"PDF not found for {url}")
    else:
        print(f"PDF link element not found for {url}")

if __name__ == "__main__":
    output_directory = r"C:\spark\output"  # Mettez le chemin correct ici

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open('input.txt', 'r') as file:
        for url in file:
            download_pdf(url.strip(), output_directory)
            sleep(1)
