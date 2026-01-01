
# 📂 PiBackup: Automated Google Drive Backup Solution

## 📖 Overview

**PiBackup** is a robust, automated DevOps solution designed to backup specific Google Drive folders to a local Linux machine (e.g., a Raspberry Pi or a dedicated server). It utilizes **Rclone** for efficient synchronization, **Python** for retention logic and email notifications, and **Docker** for containerized execution.

**Key Features:**

- **Infrastructure as Code:** Uses Ansible to provision the host machine, install dependencies, and format/mount external storage drives automatically.
    
- **Smart Sync:** Leverages `rclone` to incrementally copy data from Google Drive.
    
- **Automated Archiving:** Compresses backups into timestamped ZIP archives.
    
- **Aggressive Retention Policy:** Automatically manages storage by keeping only the most recent Daily, Weekly, Monthly, and Yearly archives to save space.
    
- **Email Notifications:** Sends SMTP alerts upon success or failure.
    

---

## 🏗️ Repository Structure

- **`app/`**: Contains the core application logic.
    
    - `backups.py`: The main Python script handling sync, compression, retention, and alerting.
        
    - `Dockerfile`: Defines the environment (Python 3.8 + Rclone).
        
    - `rclone.conf`: Configuration for connecting to Google Drive.
        
- **`setup-backup-server.yml`**: An Ansible playbook to prepare the Linux host (installs Docker, formats drives, mounts storage to `/media/vault`).
    
- **`Makefile`**: Automation shortcuts for building, installing dependencies, and running playbooks.
    
- **`generate_test_backups.sh`**: A helper script to generate dummy files for testing the retention logic.
    

---

## ⚙️ Prerequisites

Before starting, ensure you have the following:

1. **Hardware**: A Linux-based server (e.g., Raspberry Pi, Ubuntu Server) with an external Hard Drive attached.
    
2. **Google Cloud Account**: Access to create Service Accounts.
    
3. **Gmail Account**: For sending email notifications (requires an App Password).
    
4. **Local Machine**: To run the Ansible playbook (can be the same as the server or a separate controller).
    

---

## 🚀 Installation & Setup Guide

### Phase 1: Google Cloud Platform (GCP) Setup

To allow the script to access your files without user intervention, you must use a **Service Account**.

1. **Create a Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/?authuser=6) and create a new project.
    
2. **Enable Drive API**: Navigate to "APIs & Services" > "Library". Search for **Google Drive API** and enable it.
    
3. **Create Credentials**:
    
    - Go to "APIs & Services" > "Credentials".
        
    - Click **Create Credentials** > **Service Account**.
        
    - Name it (e.g., `pibackup-bot`) and click **Done**.
        
4. **Generate Key**:
    
    - Click on the newly created Service Account email.
        
    - Go to the **Keys** tab > **Add Key** > **Create new key**.
        
    - Select **JSON**. A file will automatically download.
        
5. **Rename & Place Key**:
    
    - Rename the downloaded JSON file to `serviceaccount.json`.
        
    - Move this file into the `app/` directory of this repository.
        
    - _Security Note: This file contains sensitive keys. Do not commit it to public version control._
        
6. **Share Folders**:
    
    - Copy the **email address** of the Service Account (e.g., `pibackup-bot@project-id.iam.gserviceaccount.com`).
        
    - Go to your Google Drive, right-click the folder you want to backup, and **Share** it with that email address.
        

### Phase 2: Environment Configuration

Create a `.env` file in the root directory of the repository to store your configuration.

Bash

```
# Copy the example or create new
touch .env
```

Add the following content to `.env`:

Ini, TOML

```
# Google Drive folders to backup (Comma separated folder names)
REMOTE_FOLDERS=Documents,Photos,Finance

# Gmail Settings for Notifications
GMAIL_USERNAME=your-email@gmail.com
GMAIL_PASSWORD=your-app-specific-password
GMAIL_RECEIVER=alert-receiver@gmail.com
SEND_EMAIL=1  # Set to 1 to enable, 0 to disable

# Application Paths (Default is usually fine for Docker)
TEMP_FILES_FOLDER=../tempbackups
BACKUP_FOLDER=../backups

# Ansible Target User (for server setup)
USERNAME=your_linux_username
```

### Phase 3: Server Provisioning (Ansible)

This step sets up your Linux machine, installs Docker, and mounts your external hard drive.

1. **Install Ansible Dependencies**:
    
    Bash
    
    ```
    make install
    ```
    
    _This creates a virtual environment and installs necessary Ansible collections._
    
2. Run the Playbook:
    
    Make sure you have SSH access to your target server. Update the inventory (or pass it via command line). By default, the Make command assumes a host named grudge. You may need to edit the Makefile or setup-backup-server.yml to match your hostname.
    
    Bash
    
    ```
    make run-playbooks
    ```
    
3. Drive Selection:
    
    During execution, the playbook will pause and list all connected drives.
    
    - **Action**: Copy the **UUID** of your external backup drive and paste it into the prompt.
        
    - **Warning**: The script will mount this drive to `/media/vault`. Ensure it is the correct drive.
        

---

## 🐳 Deployment (Docker)

Once the server is prepared and the `.env` and `serviceaccount.json` are in place, you can build and run the backup container.

### Option A: Manual Docker Run

1. **Build the Image**:
    
    Bash
    
    ```
    make docker-build
    ```
    
2. **Run the Container**:
    
    Bash
    
    ```
    make docker-run
    ```
    
    This will:
    
    - Start the container named `backup-container`.
        
    - Mount local directories `tempbackups` and `backups` into the container.
        
    - **Note**: If you are running this on the production server, ensure you run the command inside `/media/vault` or update the volume mappings in the `Makefile` to point to `/media/vault`.
        

### Option B: Automated via Ansible (Optional)

The `setup-backup-server.yml` contains commented-out sections for copying the app and running the Docker container. To fully automate deployment:

1. Uncomment the tasks at the bottom of `setup-backup-server.yml`.
    
2. Re-run `make run-playbooks`.
    

---

## 🧹 Retention Policy

The `backups.py` script enforces a strict retention policy to save space. It sorts backup files by date and keeps **only the most recent** file for each category:

- 📅 **Yearly**: Keeps the file from `Jan 01`.
    
- 📆 **Monthly**: Keeps the file from the `1st` of the month.
    
- 🗓️ **Weekly**: Keeps the file from `Monday`.
    
- ☀️ **Daily**: Keeps the most recent file that doesn't match the above criteria.
    

**⚠️ Warning**: All other files in the backup directory will be deleted. Ensure you understand this logic before running on an existing folder.

---

## 🛠️ Troubleshooting

- **Rclone Error**: If you see "Failed to copy files", check that `serviceaccount.json` is in the `app/` folder and that you have shared the Google Drive folder with the Service Account email.
    
- **Docker Permission Errors**: Ensure the user running Docker has permissions to write to the `backups` directory (or `/media/vault`).
    
- **Ansible Connection Issues**: Ensure you have SSH keys set up for the target machine (`ssh-copy-id user@host`) so Ansible can connect without a password.
    

---

## 🧪 Testing

To test the retention logic without waiting for days:

1. Run `make generate-test-backups`.
    
2. This creates 2 years worth of dummy empty zip files in `backups/`.
    
3. Run the python script locally: `make run-python-script`.
    
4. Observe the console output to see which files are preserved and which are deleted.