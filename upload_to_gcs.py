from google.cloud import storage
import uuid

def upload_to_gcs(bucket_name, source_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Générer un nom de blob unique
    destination_blob_name = f"{uuid.uuid4()}.json"
    
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(f"Fichier {source_file_name} téléchargé vers {destination_blob_name} dans le bucket {bucket_name}.")

if __name__ == '__main__':
    bucket_name = 'patent-data-bucket'  
    source_file_name = 'patents_data.json'  

    upload_to_gcs(bucket_name, source_file_name)
