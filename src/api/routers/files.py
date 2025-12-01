"""
TextLoom API - File Browser Endpoints

Handles file system browsing operations within user's home directory.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from pydantic import BaseModel
from api.router_utils import raise_http_error

router = APIRouter()


class FileItem(BaseModel):
    id: str
    name: str
    path: str
    is_dir: bool
    size: int | None = None


class BrowseResponse(BaseModel):
    current_path: str
    parent_path: str | None
    items: List[FileItem]


def validate_path_security(target: Path, home: Path):
    try:
        target.relative_to(home)
    except ValueError:
        raise_http_error(403, "access_denied", "Cannot browse outside home directory")


def is_valid_symlink(item: Path, home: Path) -> bool:
    if not item.is_symlink():
        return True

    try:
        resolved = item.resolve()
        resolved.relative_to(home)
        return True
    except (ValueError, OSError):
        return False


def create_file_item(item: Path) -> FileItem | None:
    try:
        if item.name.startswith('.'):
            return None

        is_dir = item.is_dir()
        size = None if is_dir else item.stat().st_size

        return FileItem(
            id=str(item),
            name=item.name,
            path=str(item),
            is_dir=is_dir,
            size=size
        )
    except (FileNotFoundError, PermissionError, OSError):
        return None


def list_directory_items(target: Path, home: Path) -> List[FileItem]:
    try:
        items = []
        for item in target.iterdir():
            if not is_valid_symlink(item, home):
                continue

            file_item = create_file_item(item)
            if file_item:
                items.append(file_item)

        items.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        return items
    except PermissionError:
        raise_http_error(403, "permission_denied", "Cannot read directory")


@router.get("/files/browse", response_model=BrowseResponse)
def browse_directory(path: str = "~") -> BrowseResponse:
    try:
        target_path = Path(path).expanduser().resolve()
        home_path = Path.home().resolve()

        validate_path_security(target_path, home_path)

        if not target_path.exists():
            raise_http_error(404, "path_not_found", f"Path not found: {path}")

        if not target_path.is_dir():
            raise_http_error(400, "not_a_directory", f"Path is not a directory: {path}")

        parent_path = str(target_path.parent) if target_path != home_path else None
        items = list_directory_items(target_path, home_path)

        return BrowseResponse(
            current_path=str(target_path),
            parent_path=parent_path,
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "browse_error", f"Error browsing directory: {str(e)}")
