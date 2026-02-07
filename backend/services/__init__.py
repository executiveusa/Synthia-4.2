"""Synthia services package - The Pauli Effect."""

from .voice import VoiceService, LanguageCode, get_voice_service
from .media_generation import (
    MediaGenerationService,
    ImageProvider,
    VideoProvider,
    GeneratedImage,
    GeneratedVideo,
    get_media_service,
)
from .browser_service import (
    BrowserService,
    BrowserSession,
    ScrapedData,
    BrowserAction,
    get_browser_service,
)
from .cloud_storage import (
    CloudStorageService,
    CloudFile,
    CloudFolder,
    StorageProvider,
    GoogleDriveService,
    DropboxService,
    get_cloud_storage_service,
)

__all__ = [
    # Voice
    "VoiceService",
    "LanguageCode",
    "get_voice_service",
    # Media Generation
    "MediaGenerationService",
    "ImageProvider",
    "VideoProvider",
    "GeneratedImage",
    "GeneratedVideo",
    "get_media_service",
    # Browser Automation
    "BrowserService",
    "BrowserSession",
    "ScrapedData",
    "BrowserAction",
    "get_browser_service",
    # Cloud Storage
    "CloudStorageService",
    "CloudFile",
    "CloudFolder",
    "StorageProvider",
    "GoogleDriveService",
    "DropboxService",
    "get_cloud_storage_service",
]
