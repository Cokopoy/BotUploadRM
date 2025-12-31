from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config
import os


class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.initialize_drive()

    def initialize_drive(self):
        """Initialize Google Drive service using Service Account"""
        try:
            credentials = Credentials.from_service_account_file(
                config.CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=credentials)
        except FileNotFoundError:
            raise Exception(f"Credentials file not found: {config.CREDENTIALS_FILE}")
        except Exception as e:
            raise Exception(f"Failed to initialize Google Drive service: {str(e)}")

    def upload_pdf(self, file_path, folder_id, file_name):
        """
        Upload PDF to Google Drive
        Returns: file_id or None
        """
        try:
            if not os.path.exists(file_path):
                return None

            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            return file.get('id')

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def delete_file(self, file_id):
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file {file_id}: {str(e)}")
            return False

    def get_file_info(self, file_id):
        """Get file information"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, createdTime, webViewLink'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None

    def check_folder_exists(self, folder_id):
        """Check if folder exists"""
        try:
            folder = self.service.files().get(
                fileId=folder_id,
                fields='id, name'
            ).execute()
            return True
        except Exception as e:
            print(f"Folder {folder_id} not found or error: {str(e)}")
            return False
