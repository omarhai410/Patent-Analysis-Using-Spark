from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

SERVICE_PATH = r"C:\Users\Dell\Downloads\chrome-win\chrome-win\chrome.exe"

# Terme de recherche dans Google Patents
search_term = "CAPTEURS PORTABLE POUR LES PLANTES"

output_file_path = "patent.txt"

def get_patent_names(search_term):
    options = webdriver.ChromeOptions()
    options.binary_location = SERVICE_PATH
    driver = webdriver.Chrome(options=options)

    # Nombre maximum de pages à parcourir (ajustez selon vos besoins)
    max_pages = 2000
    current_page = 1112

    # Liste pour stocker les noms de brevets
    patent_names = []

    while current_page <= max_pages:
        # Construire l'URL avec le numéro de page
        url = f"https://patents.google.com/?q={search_term}&oq={search_term}&page={current_page}"

        # Accéder à l'URL construit
        driver.get(url)

        # Attendre un moment pour que la page se charge
        time.sleep(2)

        patent_elements = driver.find_elements(By.XPATH, "//a[@class='pdfLink style-scope search-result-item']/span[@class='style-scope search-result-item']")
        patent_names.extend([element.text for element in patent_elements])

        current_page += 1

    driver.quit()

    return patent_names

patent_names = get_patent_names(search_term)

with open(output_file_path, "w", encoding="utf-8") as file:
    for name in patent_names:
        file.write(name + "\n")

print("Noms des brevets trouvés:")
for i, name in enumerate(patent_names, start=1):
    print(f"{i}. {name}")
