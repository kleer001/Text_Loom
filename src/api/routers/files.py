"""
Files Router - File system browsing endpoints

Provides API endpoints for browsing the local filesystem.
Security: Only allows browsing under the user's home directory.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from pydantic import BaseModel

router = APIRouter()


class FileItem(BaseModel):
    """Represents a file or directory in the filesystem"""
    id: str
    name: str
    path: str
    is_dir: bool
    size: int | None = None


class BrowseResponse(BaseModel):
    """Response for file browsing requests"""
    current_path: str
    parent_path: str | None
    items: List[FileItem]


@router.get("/files/browse", response_model=BrowseResponse)
def browse_directory(path: str = "~") -> BrowseResponse:
    """
    Browse files and directories at the specified path.

    Security: Only allows browsing within the user's home directory.

    Args:
        path: Directory path to browse (defaults to home directory)

    Returns:
        BrowseResponse containing current path, parent path, and items

    Raises:
        HTTPException: If path is outside home directory or doesn't exist
    """
    try:
        # Expand user home and resolve to absolute path
        target_path = Path(path).expanduser().resolve()
        home_path = Path.home().resolve()

        # Security check: ensure we're within home directory
        try:
            target_path.relative_to(home_path)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Cannot browse outside home directory"
            )

        # Check if path exists and is a directory
        if not target_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Path not found: {path}"
            )

        if not target_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {path}"
            )

        # Get parent path (None if at home directory)
        parent_path = str(target_path.parent) if target_path != home_path else None

        # List directory contents
        items = []
        try:
            # Get items first, then sort safely
            dir_items = list(target_path.iterdir())

            # Filter and process items
            for item in dir_items:
                try:
                    # Skip hidden files/directories (starting with .)
                    if item.name.startswith('.'):
                        continue

                    # Follow symlinks but check they're within home
                    if item.is_symlink():
                        try:
                            resolved = item.resolve()
                            # Security: ensure symlink target is within home directory
                            resolved.relative_to(home_path)
                        except (ValueError, OSError):
                            # Broken symlink or points outside home - skip
                            continue

                    # Get file info (may fail on race conditions)
                    try:
                        is_dir = item.is_dir()
                        size = None if is_dir else item.stat().st_size
                    except (FileNotFoundError, OSError):
                        # File disappeared or inaccessible - skip
                        continue

                    items.append(FileItem(
                        id=str(item),
                        name=item.name,
                        path=str(item),
                        is_dir=is_dir,
                        size=size
                    ))
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue

            # Sort after filtering (safer than sorting during iteration)
            items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: Cannot read directory {path}"
            )

        return BrowseResponse(
            current_path=str(target_path),
            parent_path=parent_path,
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error browsing directory: {str(e)}"
        )
