"""
TextLoom API - Global Variables Endpoints

Handles global variable operations:
- List all globals
- Get single global
- Set/update global
- Delete global
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel
from api.models import SuccessResponse, ErrorResponse
from api.router_utils import raise_http_error
from core.global_store import GlobalStore

router = APIRouter()


class GlobalValue(BaseModel):
    value: Any


class GlobalResponse(BaseModel):
    key: str
    value: Any


class GlobalsListResponse(BaseModel):
    globals: Dict[str, Any]


def validate_global_exists(key: str):
    if not GlobalStore.has(key):
        raise_http_error(404, "global_not_found", f"Global variable '{key}' does not exist")


@router.get(
    "/globals",
    response_model=GlobalsListResponse,
    summary="List all global variables",
    description="Returns all global variables in the system.",
)
def list_globals() -> GlobalsListResponse:
    return GlobalsListResponse(globals=GlobalStore.list())


@router.get(
    "/globals/{key}",
    response_model=GlobalResponse,
    summary="Get a global variable",
    description="Returns the value of a specific global variable.",
    responses={
        404: {"description": "Global not found", "model": ErrorResponse}
    }
)
def get_global(key: str = Path(..., description="Global variable key")) -> GlobalResponse:
    try:
        validate_global_exists(key)
        return GlobalResponse(key=key, value=GlobalStore.get(key))
    except ValueError as e:
        raise_http_error(400, "invalid_key", str(e))


@router.put(
    "/globals/{key}",
    response_model=GlobalResponse,
    status_code=status.HTTP_200_OK,
    summary="Set/update a global variable",
    description="Sets or updates a global variable. Key must be uppercase, 2+ characters, and not start with $.",
    responses={
        400: {"description": "Invalid key format", "model": ErrorResponse}
    }
)
def set_global(key: str = Path(..., description="Global variable key"), body: GlobalValue = ...) -> GlobalResponse:
    try:
        GlobalStore.set(key, body.value)
        return GlobalResponse(key=key, value=body.value)
    except ValueError as e:
        raise_http_error(400, "invalid_key", str(e))
    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to set global: {str(e)}")


@router.delete(
    "/globals/{key}",
    response_model=SuccessResponse,
    summary="Delete a global variable",
    description="Removes a global variable from the system.",
    responses={
        404: {"description": "Global not found", "model": ErrorResponse}
    }
)
def delete_global(key: str = Path(..., description="Global variable key")) -> SuccessResponse:
    try:
        validate_global_exists(key)
        GlobalStore.cut(key)
        return SuccessResponse(success=True, message=f"Global variable '{key}' deleted successfully")
    except ValueError as e:
        raise_http_error(400, "invalid_key", str(e))
    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to delete global: {str(e)}")
