"""Custom exceptions for the hub package."""
from bitfount.exceptions import BitfountError


class PodDoesNotExistError(BitfountError):
    """Errors related to references to a non-existent Pod."""

    pass


class SchemaUploadError(BitfountError, ValueError):
    """Could not upload schema to hub."""

    pass
