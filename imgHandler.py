from googleapiclient.discovery import build
from google.oauth2 import service_account
import io, os
from googleapiclient.http import MediaIoBaseDownload

SERVICE_ACCOUNT_FILE = 'key/sice-425317-8ce00dfa057b.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

def dowload_folder(folder_id, local_path):
    """Baixa uma pasta recursivamente

    Args:
        folder_id (id): ID da pasta no drive
        local_path (string): Local onde a pasta será baixada
    """
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    
    for item in items:
        if item['mimeType'] == "application/vnd.google-apps.folder":
            # Cuida do que fazer caso seja uma pasta
            folder_path = os.path.join(local_path, item['name'])
            os.makedirs(folder_path, exist_ok=True)
            dowload_folder(item['id'], folder_path)
        else:
            request = service.files().get_media(fileId=item['id'])
            file_path = os.path.join(local_path, item['name'])
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done == False:
                status, done = downloader.next_chunk()
                print(f"Baixando {item['name']}, progresso em: {int(status.progress() * 100)}%.")
                
folder_name = 'face-db'
results = service.files().list(
    q=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
    fields="nextPageToken, files(id)"
).execute()
item = results.get('files', [])

if not item:
    print(f"pasta '{folder_name}' não encontrada.")
else:
    folder_id = item[0]['id']
    dowload_folder(folder_id, folder_name)