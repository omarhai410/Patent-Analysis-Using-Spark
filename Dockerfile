FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb

# Installer ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver

# Copier le fichier requirements.txt et installer les bibliothèques Python nécessaires
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir google-cloud-storage

COPY extraction_metadata.py /app/extraction_metadata.py
COPY upload_to_gcs.py /app/upload_to_gcs.py

COPY patent.txt /app/patent.txt

WORKDIR /app

CMD ["python", "extraction_metadata.py"]
