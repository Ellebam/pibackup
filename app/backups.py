import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zipfile import ZipFile, ZIP_LZMA
import shutil
import subprocess
from datetime import datetime

# Save directories
TEMP_FILES_FOLDER = os.getenv('TEMP_FILES_FOLDER', '../tempbackups')  # Temp directory to store copied files
BACKUP_FOLDER = os.getenv('BACKUP_FOLDER', '../backups')  # Directory to store final backup zip files

# List of remote folders to copy
REMOTE_FOLDERS = os.getenv('REMOTE_FOLDERS', 'DriveSyncFiles').split(',')

# Email config
SUBJECT = 'Backup status'
FROM_EMAIL = os.getenv('GMAIL_USERNAME')
FROM_PASSWORD = os.getenv('GMAIL_PASSWORD')
TO_EMAIL = os.getenv('GMAIL_RECEIVER')
SEND_EMAIL = bool(int(os.getenv('SEND_EMAIL', 0)))

def rclone_copy(remote_folder, backup_folder):
    """Copy files from the remote folder to the local backup folder."""
    try:
        subprocess.run(["rclone", "copy", "-v", "--update", "--ignore-existing", "--config", "rclone.conf", "--drive-shared-with-me", 
                        f"mygdrive:{remote_folder}", backup_folder], check=True)
    except subprocess.CalledProcessError as e:
        handle_error(f"Failed to copy files from {remote_folder}: {str(e)}")

def zip_files(temp_folder, backup_folder):
    """Zip all files in the temp directory and move to backup directory."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"backup_{timestamp}.zip"
    try:
        with ZipFile(Path(backup_folder) / zip_filename, 'w', ZIP_LZMA, allowZip64=True) as zipf:
            for root, dirs, files in os.walk(temp_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, temp_folder))
    except Exception as e:
        handle_error(f"Failed to zip files: {str(e)}")


def clean_up_temp_folder(temp_folder):
    """Delete all files and directories in the temporary files folder."""
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            handle_error(f"Failed to delete {file_path}. Reason: {e}")

def manage_backups(backup_folder):
    """Manage backups in the backup directory according to defined rules."""
    try:
        daily_files = []
        weekly_files = []
        monthly_files = []
        yearly_files = []

        for filename in os.listdir(backup_folder):
            timestamp = filename[7:15]  # extract date from filename
            timestamp = datetime.strptime(timestamp, "%Y%m%d")
            if timestamp.strftime("%j") == "001":
                yearly_files.append(filename)
            elif timestamp.strftime("%d") == "01":
                monthly_files.append(filename)
            elif timestamp.strftime("%w") == "1":
                weekly_files.append(filename)
            else:
                daily_files.append(filename)

        # Sort the lists in descending order of dates
        daily_files.sort(reverse=True)
        weekly_files.sort(reverse=True)
        monthly_files.sort(reverse=True)
        yearly_files.sort(reverse=True)

        print(f"Daily files: {daily_files}")
        print(f"Weekly files: {weekly_files}")
        print(f"Monthly files: {monthly_files}")
        print(f"Yearly files: {yearly_files}")

        # Remove all but the most recent daily file
        for file in daily_files[1:]:
            os.unlink(os.path.join(backup_folder, file))

        # Remove all but the most recent weekly file
        for file in weekly_files[1:]:
            os.unlink(os.path.join(backup_folder, file))

        # Remove all but the most recent monthly file
        for file in monthly_files[1:]:
            os.unlink(os.path.join(backup_folder, file))

        # Remove all but the most recent yearly file
        for file in yearly_files[1:]:
            os.unlink(os.path.join(backup_folder, file))
    except Exception as e:
        handle_error(f"Failed to manage backups. Reason: {e}")





def handle_error(message):
    """Handle error by logging and sending an email."""
    print(message)  # log the error
    if SEND_EMAIL:
        send_email(message)  # send an email if enabled

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
    for folder in REMOTE_FOLDERS:
        rclone_copy(folder.strip(), TEMP_FILES_FOLDER)
    zip_files(TEMP_FILES_FOLDER, BACKUP_FOLDER)
    clean_up_temp_folder(TEMP_FILES_FOLDER)
    manage_backups(BACKUP_FOLDER)

if __name__ == "__main__":
    main()
