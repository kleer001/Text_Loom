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
from core.global_store import GlobalStore

router = APIRouter()


class GlobalValue(BaseModel):
    """Request body for setting a global variable."""
    value: Any


class GlobalResponse(BaseModel):
    """Response for a single global variable."""
    key: str
    value: Any


class GlobalsListResponse(BaseModel):
    """Response for listing all globals."""
    globals: Dict[str, Any]


@router.get(
    "/globals",
    response_model=GlobalsListResponse,
    summary="List all global variables",
    description="Returns all global variables in the system.",
    responses={
        200: {"description": "List of all globals"}
    }
)
def list_globals() -> GlobalsListResponse:
    """
    Get all global variables.
    
    Returns a dictionary of all global variables currently set
    in the GlobalStore.
    
    Returns:
        GlobalsListResponse: Dictionary of key-value pairs
    """
    return GlobalsListResponse(globals=GlobalStore.list())


@router.get(
    "/globals/{key}",
    response_model=GlobalResponse,
    summary="Get a global variable",
    description="Returns the value of a specific global variable.",
    responses={
        200: {"description": "Global variable value"},
        404: {"description": "Global not found", "model": ErrorResponse}
    }
)
def get_global(
    key: str = Path(..., description="Global variable key (must be uppercase, 2+ chars)")
) -> GlobalResponse:
    """
    Get a specific global variable.
    
    Args:
        key: The global variable key
        
    Returns:
        GlobalResponse: The key and its value
        
    Raises:
        HTTPException: 404 if global doesn't exist, 400 if key format invalid
    """
    try:
        if not GlobalStore.has(key):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "global_not_found",
                    "message": f"Global variable '{key}' does not exist"
                }
            )
        
        value = GlobalStore.get(key)
        return GlobalResponse(key=key, value=value)
        
    except ValueError as e:
        # Invalid key format
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_key",
                "message": str(e)
            }
        )


@router.put(
    "/globals/{key}",
    response_model=GlobalResponse,
    status_code=status.HTTP_200_OK,
    summary="Set/update a global variable",
    description="Sets or updates a global variable. Key must be uppercase, 2+ characters, and not start with $.",
    responses={
        200: {"description": "Global variable set successfully"},
        400: {"description": "Invalid key format", "model": ErrorResponse}
    }
)
def set_global(
    key: str = Path(..., description="Global variable key"),
    body: GlobalValue = ...
) -> GlobalResponse:
    """
    Set or update a global variable.
    
    Global variable keys must follow these rules:
    - At least 2 characters long
    - All uppercase letters
    - Cannot start with '$'
    
    Args:
        key: The global variable key
        body: The value to set
        
    Returns:
        GlobalResponse: Confirmation with key and value
        
    Raises:
        HTTPException: 400 if key format is invalid
    """
    try:
        GlobalStore.set(key, body.value)
        return GlobalResponse(key=key, value=body.value)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_key",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to set global: {str(e)}"
            }
        )


@router.delete(
    "/globals/{key}",
    response_model=SuccessResponse,
    summary="Delete a global variable",
    description="Removes a global variable from the system.",
    responses={
        200: {"description": "Global deleted successfully"},
        404: {"description": "Global not found", "model": ErrorResponse}
    }
)
def delete_global(
    key: str = Path(..., description="Global variable key")
) -> SuccessResponse:
    """
    Delete a global variable.
    
    Args:
        key: The global variable key to delete
        
    Returns:
        SuccessResponse: Confirmation of deletion
        
    Raises:
        HTTPException: 404 if global doesn't exist, 400 if key format invalid
    """
    try:
        if not GlobalStore.has(key):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "global_not_found",
                    "message": f"Global variable '{key}' does not exist"
                }
            )
        
        GlobalStore.cut(key)
        
        return SuccessResponse(
            success=True,
            message=f"Global variable '{key}' deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_key",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to delete global: {str(e)}"
            }
        )