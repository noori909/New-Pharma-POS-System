"""
Google Drive OAuth2 Cloud Vault Mirror Service for NQS POS v2.0
Handles Google OAuth authentication and daily background ZIP backup uploads.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.database import get_app_data_dir
from app.core.models import get_setting, set_setting

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_credentials_path() -> Path:
    """Returns path to client credentials JSON file."""
    return get_app_data_dir() / "credentials.json"


def get_token_path() -> Path:
    """Returns path to token JSON file."""
    return get_app_data_dir() / "token.json"


def is_gdrive_configured() -> bool:
    """Checks if Google Drive credentials or token exists."""
    return get_token_path().exists() or get_credentials_path().exists()


def authenticate_gdrive() -> bool:
    """
    Executes OAuth authorization flow via browser and saves token.json.
    Returns True if successfully authenticated.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        token_path = get_token_path()
        cred_path = get_credentials_path()

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not cred_path.exists():
                    raise FileNotFoundError(
                        f"Google OAuth client file 'credentials.json' not found at {cred_path}. "
                        "Please upload/select your Google Cloud Desktop Client ID file in Settings."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return True

    except Exception as e:
        print(f"Google Drive Authentication Error: {e}")
        return False


def get_drive_service():
    """Returns Google Drive API service instance."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_path = get_token_path()
    if not token_path.exists():
        raise FileNotFoundError("Google Drive not authenticated. Token file missing.")

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def upload_backup_to_gdrive(zip_filepath: str) -> Dict[str, Any]:
    """
    Uploads a local backup ZIP file to designated Google Drive folder.
    """
    file_p = Path(zip_filepath)
    if not file_p.exists():
        return {'success': False, 'error': f"File not found: {zip_filepath}"}

    try:
        from googleapiclient.http import MediaFileUpload

        service = get_drive_service()
        folder_id = get_setting('gdrive_folder_id', '').strip()

        # If folder_id not explicitly set, search or create 'NQS_POS_Backups' folder
        if not folder_id:
            query = "name = 'NQS_POS_Backups' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])

            if files:
                folder_id = files[0]['id']
            else:
                folder_metadata = {
                    'name': 'NQS_POS_Backups',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = service.files().create(body=folder_metadata, fields='id').execute()
                folder_id = folder.get('id')

            set_setting('gdrive_folder_id', folder_id)

        file_metadata = {
            'name': file_p.name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(str(file_p), mimetype='application/zip', resumable=True)

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        print(f"Backup mirrored to Google Drive: {uploaded_file.get('name')} (ID: {uploaded_file.get('id')})")
        return {
            'success': True,
            'file_id': uploaded_file.get('id'),
            'file_name': uploaded_file.get('name'),
            'link': uploaded_file.get('webViewLink')
        }

    except Exception as e:
        error_msg = f"Google Drive sync failed: {str(e)}"
        print(error_msg)
        return {'success': False, 'error': error_msg}
