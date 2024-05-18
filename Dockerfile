FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Installer Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Installer ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/local/bin/chromedriver

# Copier le fichier requirements.txt et installer les bibliothèques Python nécessaires
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script dans le conteneur
COPY extraction_metadata.py /app/extraction_metadata.py

# Copier le fichier patent.txt dans le conteneur
COPY patent.txt /app/patent.txt

# Définir le répertoire de travail
WORKDIR /app

# Définir la commande d'exécution
CMD ["python", "extraction_metadata.py"]
