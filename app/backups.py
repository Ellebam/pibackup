import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zipfile import ZipFile
import glob
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# Google Drive settings
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Email settings
SUBJECT = 'Backup status'
FROM_EMAIL = os.environ.get('GMAIL_USERNAME')
FROM_PASSWORD = os.environ.get('GMAIL_PASSWORD')
TO_EMAIL = os.environ.get('GMAIL_RECEIVER')

def authenticate_gdrive():
    """Authenticate to Google Drive using a service account."""
    creds_json_file = os.environ.get('SERVICE_ACCOUNT_FILE')
    creds = service_account.Credentials.from_service_account_file(creds_json_file, scopes=SCOPES)
    return creds

def download_all_files_from_gdrive():
    """Download all files from Google Drive."""
    try:
        creds = authenticate_gdrive()
        service = build('drive', 'v3', credentials=creds)
        items = service.files().list().execute()
        for item in items['files']:
            request = service.files().get_media(fileId=item['id'])
            fh = open(f"/app/backup/{item['name']}", 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.close()
    except Exception as e:
        send_email(f"Failed to download files from Google Drive: {e}")
        raise

def zip_files():
    """Zip all files in the backup directory."""
    try:
        with ZipFile('/app/backup/backup.zip', 'w') as zipf:
            for file in glob.glob('/app/backup/*'):
                zipf.write(file)
    except Exception as e:
        send_email(f"Failed to zip files: {e}")
        raise

def clean_directory():
    """Clean the backup directory by removing unzipped files."""
    try:
        files = glob.glob('/app/backup/*')
        for f in files:
            if f != '/app/backup/backup.zip':
                os.remove(f)
    except Exception as e:
        send_email(f"Failed to clean the backup directory: {e}")
        raise


def send_email(body):
    """Send an email."""
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(FROM_EMAIL, FROM_PASSWORD)
    text = msg.as_string()
    server.sendmail(FROM_EMAIL, TO_EMAIL, text)
    server.quit()

def main():
    """Main function."""
    try:
        download_all_files_from_gdrive()
        zip_files()
        clean_directory()
        send_email("Backup completed successfully.")
    except Exception as e:
        send_email(f"Backup failed: {e}")

if __name__ == "__main__":
    main()
