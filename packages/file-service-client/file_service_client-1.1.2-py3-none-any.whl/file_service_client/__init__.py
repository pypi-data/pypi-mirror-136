__version__ = "1.1.2"

__all__ = ["FileServiceClient", "FileStoreServiceClient",
    "FileSchema", "FileCreateSchema", "FileStoreSchema"]

try:
    # Attempts to import the client class
    # Allowed to fail importing so the package metadata can be read for building
    from .file_service_client import FileServiceClient
    from .file_store_client import FileStoreServiceClient
    from .models import FileSchema, FileCreateSchema, FileStoreSchema
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    pass  # pragma: no cover
