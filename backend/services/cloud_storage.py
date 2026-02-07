"""
Synthia Cloud Storage Service - The Pauli Effect

Integrates Google Drive and Dropbox for file management.
Enables Synthia to read, write, and manage files in cloud storage.
"""

import os
import io
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import base64


@dataclass
class CloudFile:
    """Represents a file in cloud storage."""
    id: str
    name: str
    mime_type: str
    size: int
    modified_time: str
    parent_id: Optional[str] = None
    web_view_link: Optional[str] = None
    content: Optional[bytes] = None


@dataclass
class CloudFolder:
    """Represents a folder in cloud storage."""
    id: str
    name: str
    parent_id: Optional[str] = None
    file_count: int = 0


class StorageProvider(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"


class GoogleDriveService:
    """Google Drive integration for Synthia."""
    
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "/app/config/google_credentials.json")
        self.service = None
        
    def _get_service(self):
        """Initialize Google Drive service."""
        if self.service is None:
            try:
                from googleapiclient.discovery import build
                from google.oauth2 import service_account
                
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=credentials)
            except Exception as e:
                raise ValueError(f"Failed to initialize Google Drive: {e}")
        return self.service
    
    async def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[CloudFile]:
        """List files in Google Drive."""
        service = self._get_service()
        
        q = []
        if folder_id:
            q.append(f"'{folder_id}' in parents")
        if query:
            q.append(f"name contains '{query}'")
        q.append("trashed = false")
        
        query_string = " and ".join(q) if q else None
        
        results = service.files().list(
            q=query_string,
            pageSize=100,
            fields="files(id, name, mimeType, size, modifiedTime, webViewLink, parents)"
        ).execute()
        
        files = results.get('files', [])
        
        return [
            CloudFile(
                id=f['id'],
                name=f['name'],
                mime_type=f['mimeType'],
                size=int(f.get('size', 0)),
                modified_time=f['modifiedTime'],
                parent_id=f.get('parents', [None])[0],
                web_view_link=f.get('webViewLink')
            )
            for f in files
        ]
    
    async def download_file(self, file_id: str) -> CloudFile:
        """Download a file from Google Drive."""
        service = self._get_service()
        
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType, size, modifiedTime").execute()
        
        # Download content
        request = service.files().get_media(fileId=file_id)
        content = request.execute()
        
        return CloudFile(
            id=file_metadata['id'],
            name=file_metadata['name'],
            mime_type=file_metadata['mimeType'],
            size=int(file_metadata.get('size', 0)),
            modified_time=file_metadata['modifiedTime'],
            content=content
        )
    
    async def upload_file(self, name: str, content: bytes, mime_type: str, folder_id: Optional[str] = None) -> CloudFile:
        """Upload a file to Google Drive."""
        service = self._get_service()
        
        from googleapiclient.http import MediaIoBaseUpload
        
        file_metadata = {'name': name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, size, modifiedTime, webViewLink'
        ).execute()
        
        return CloudFile(
            id=file['id'],
            name=file['name'],
            mime_type=file['mimeType'],
            size=int(file.get('size', 0)),
            modified_time=file['modifiedTime'],
            web_view_link=file.get('webViewLink')
        )
    
    async def create_folder(self, name: str, parent_id: Optional[str] = None) -> CloudFolder:
        """Create a folder in Google Drive."""
        service = self._get_service()
        
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(body=file_metadata, fields='id, name, parents').execute()
        
        return CloudFolder(
            id=folder['id'],
            name=folder['name'],
            parent_id=folder.get('parents', [None])[0]
        )
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive."""
        service = self._get_service()
        
        try:
            service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False


class DropboxService:
    """Dropbox integration for Synthia."""
    
    def __init__(self):
        self.access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        self.dbx = None
        
    def _get_client(self):
        """Initialize Dropbox client."""
        if self.dbx is None:
            try:
                import dropbox
                self.dbx = dropbox.Dropbox(self.access_token)
            except Exception as e:
                raise ValueError(f"Failed to initialize Dropbox: {e}")
        return self.dbx
    
    async def list_files(self, path: str = "", query: Optional[str] = None) -> List[CloudFile]:
        """List files in Dropbox."""
        dbx = self._get_client()
        
        result = dbx.files_list_folder(path if path else "")
        
        files = []
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                if query is None or query.lower() in entry.name.lower():
                    files.append(CloudFile(
                        id=entry.id,
                        name=entry.name,
                        mime_type=entry.content_type or "application/octet-stream",
                        size=entry.size,
                        modified_time=entry.server_modified.isoformat()
                    ))
        
        return files
    
    async def download_file(self, path: str) -> CloudFile:
        """Download a file from Dropbox."""
        dbx = self._get_client()
        
        metadata, response = dbx.files_download(path)
        content = response.content
        
        return CloudFile(
            id=metadata.id,
            name=metadata.name,
            mime_type=metadata.content_type or "application/octet-stream",
            size=metadata.size,
            modified_time=metadata.server_modified.isoformat(),
            content=content
        )
    
    async def upload_file(self, path: str, content: bytes) -> CloudFile:
        """Upload a file to Dropbox."""
        dbx = self._get_client()
        
        result = dbx.files_upload(content, path)
        
        return CloudFile(
            id=result.id,
            name=result.name,
            mime_type="application/octet-stream",
            size=result.size,
            modified_time=result.server_modified.isoformat()
        )
    
    async def create_folder(self, path: str) -> CloudFolder:
        """Create a folder in Dropbox."""
        dbx = self._get_client()
        
        result = dbx.files_create_folder_v2(path)
        
        return CloudFolder(
            id=result.metadata.id,
            name=result.metadata.name
        )
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file from Dropbox."""
        dbx = self._get_client()
        
        try:
            dbx.files_delete_v2(path)
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False


class CloudStorageService:
    """
    Unified cloud storage service for Synthia.
    Supports Google Drive and Dropbox.
    """
    
    def __init__(self):
        self.google_drive = GoogleDriveService()
        self.dropbox = DropboxService()
    
    async def list_files(self, provider: StorageProvider, **kwargs) -> List[CloudFile]:
        """List files from specified provider."""
        if provider == StorageProvider.GOOGLE_DRIVE:
            return await self.google_drive.list_files(**kwargs)
        elif provider == StorageProvider.DROPBOX:
            return await self.dropbox.list_files(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def download_file(self, provider: StorageProvider, **kwargs) -> CloudFile:
        """Download file from specified provider."""
        if provider == StorageProvider.GOOGLE_DRIVE:
            return await self.google_drive.download_file(**kwargs)
        elif provider == StorageProvider.DROPBOX:
            return await self.dropbox.download_file(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def upload_file(self, provider: StorageProvider, **kwargs) -> CloudFile:
        """Upload file to specified provider."""
        if provider == StorageProvider.GOOGLE_DRIVE:
            return await self.google_drive.upload_file(**kwargs)
        elif provider == StorageProvider.DROPBOX:
            return await self.dropbox.upload_file(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Singleton instance
_cloud_storage_service: Optional[CloudStorageService] = None


def get_cloud_storage_service() -> CloudStorageService:
    """Get or create cloud storage service singleton."""
    global _cloud_storage_service
    if _cloud_storage_service is None:
        _cloud_storage_service = CloudStorageService()
    return _cloud_storage_service
