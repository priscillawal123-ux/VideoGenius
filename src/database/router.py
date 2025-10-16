"""
Database domain router.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_admin_user
from src.auth.schemas import UserResponse
from src.database.dependencies import get_database_service
from src.database.schemas import DatabaseHealth, QueryRequest, QueryResult, TableInfo
from src.database.service import DatabaseService

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/health", response_model=DatabaseHealth)
async def get_database_health(
    db_service: Annotated[DatabaseService, Depends(get_database_service)],
) -> DatabaseHealth:
    """Get database health status."""
    try:
        health = await db_service.health_check()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )


@router.post("/query", response_model=QueryResult)
async def execute_query(
    query_request: QueryRequest,
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    db_service: Annotated[DatabaseService, Depends(get_database_service)],
) -> QueryResult:
    """Execute a database query (admin only)."""
    try:
        result = await db_service.execute_query(query_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query execution failed: {str(e)}",
        )


@router.get("/tables", response_model=List[TableInfo])
async def list_tables(
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    db_service: Annotated[DatabaseService, Depends(get_database_service)],
) -> List[TableInfo]:
    """List all database tables (admin only)."""
    try:
        tables = await db_service.list_tables()
        return tables
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tables: {str(e)}",
        )


@router.get("/tables/{table_name}", response_model=TableInfo)
async def get_table_info(
    table_name: str,
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    db_service: Annotated[DatabaseService, Depends(get_database_service)],
) -> TableInfo:
    """Get information about a specific table (admin only)."""
    try:
        table_info = await db_service.get_table_info(table_name)
        return table_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table not found or error retrieving info: {str(e)}",
        )
