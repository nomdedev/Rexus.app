"""
Pagination System - Rexus.app
Efficient pagination for large datasets and tables.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class PaginationConfig:
    """Configuration for pagination."""
    page_size: int = 50
    max_page_size: int = 500
    show_page_info: bool = True
    show_total_count: bool = True

@dataclass
class PaginationResult:
    """Result of paginated query."""
    data: List[Dict[str, Any]]
    current_page: int
    page_size: int
    total_records: int
    total_pages: int
    has_previous: bool
    has_next: bool
    start_record: int
    end_record: int

class PaginationManager:
    """
    Manages pagination for database queries and large datasets.
    """
    
    def __init__(self, config: PaginationConfig = None):
        """
        Initialize pagination manager.
        
        Args:
            config: Pagination configuration
        """
        self.config = config or PaginationConfig()
    
    def paginate_query(self, base_query: str, count_query: str, 
                      params: List = None, page: int = 1, 
                      page_size: int = None, db_connection=None) -> PaginationResult:
        """
        Execute paginated database query.
        
        Args:
            base_query: Base SQL query (without LIMIT/OFFSET)
            count_query: Query to count total records
            params: Query parameters
            page: Current page number (1-based)
            page_size: Number of records per page
            db_connection: Database connection
            
        Returns:
            PaginationResult with data and pagination info
        """
        if not db_connection:
            return self._empty_result(page, page_size)
        
        # Validate and set page size
        if page_size is None:
            page_size = self.config.page_size
        page_size = min(page_size, self.config.max_page_size)
        page_size = max(page_size, 1)
        
        # Validate page number
        page = max(page, 1)
        
        params = params or []
        
        try:
            cursor = db_connection.cursor()
            
            # Get total count
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Calculate pagination info
            total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
            page = min(page, total_pages)  # Ensure page doesn't exceed total pages
            
            offset = (page - 1) * page_size
            start_record = offset + 1
            end_record = min(offset + page_size, total_records)
            
            # Execute paginated query
            paginated_query = f"{base_query} ORDER BY id DESC OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
            cursor.execute(paginated_query, params)
            
            # Convert results to dictionaries
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            
            return PaginationResult(
                data=data,
                current_page=page,
                page_size=page_size,
                total_records=total_records,
                total_pages=total_pages,
                has_previous=page > 1,
                has_next=page < total_pages,
                start_record=start_record if total_records > 0 else 0,
                end_record=end_record if total_records > 0 else 0
            )
            
        except Exception as e:
            print(f"[ERROR PAGINATION] Database error: {e}")
            return self._empty_result(page, page_size)
    
    def paginate_list(self, data_list: List[Any], page: int = 1, 
                     page_size: int = None) -> PaginationResult:
        """
        Paginate a list in memory.
        
        Args:
            data_list: List to paginate
            page: Current page number (1-based)
            page_size: Number of items per page
            
        Returns:
            PaginationResult with paginated data
        """
        if page_size is None:
            page_size = self.config.page_size
        page_size = min(page_size, self.config.max_page_size)
        page_size = max(page_size, 1)
        
        total_records = len(data_list)
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        page = max(1, min(page, total_pages))
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_data = data_list[start_index:end_index]
        
        return PaginationResult(
            data=paginated_data,
            current_page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
            has_previous=page > 1,
            has_next=page < total_pages,
            start_record=start_index + 1 if total_records > 0 else 0,
            end_record=min(end_index, total_records) if total_records > 0 else 0
        )
    
    def get_pagination_info(self, result: PaginationResult) -> str:
        """
        Get human-readable pagination information.
        
        Args:
            result: Pagination result
            
        Returns:
            Formatted pagination info string
        """
        if result.total_records == 0:
            return "No hay registros para mostrar"
        
        info_parts = []
        
        if self.config.show_page_info:
            info_parts.append(
                f"Página {result.current_page} de {result.total_pages}"
            )
        
        if self.config.show_total_count:
            info_parts.append(
                f"Mostrando {result.start_record}-{result.end_record} de {result.total_records} registros"
            )
        
        return " • ".join(info_parts)
    
    def get_page_numbers(self, result: PaginationResult, 
                        max_visible_pages: int = 7) -> List[int]:
        """
        Get list of page numbers to display in pagination controls.
        
        Args:
            result: Pagination result
            max_visible_pages: Maximum number of page buttons to show
            
        Returns:
            List of page numbers to display
        """
        if result.total_pages <= max_visible_pages:
            return list(range(1, result.total_pages + 1))
        
        current_page = result.current_page
        total_pages = result.total_pages
        
        # Calculate range around current page
        half_visible = max_visible_pages // 2
        start_page = max(1, current_page - half_visible)
        end_page = min(total_pages, start_page + max_visible_pages - 1)
        
        # Adjust start if we're near the end
        if end_page - start_page + 1 < max_visible_pages:
            start_page = max(1, end_page - max_visible_pages + 1)
        
        return list(range(start_page, end_page + 1))
    
    def create_search_pagination(self, base_query: str, search_term: str,
                               search_columns: List[str], params: List = None,
                               page: int = 1, page_size: int = None,
                               db_connection=None) -> PaginationResult:
        """
        Create paginated search results.
        
        Args:
            base_query: Base SQL query
            search_term: Search term
            search_columns: Columns to search in
            params: Additional query parameters
            page: Current page
            page_size: Page size
            db_connection: Database connection
            
        Returns:
            PaginationResult with search results
        """
        if not search_term or not search_columns:
            return self.paginate_query(base_query, f"SELECT COUNT(*) FROM ({base_query}) as count_query",
                                     params, page, page_size, db_connection)
        
        # Build search conditions
        search_conditions = []
        search_params = []
        
        for column in search_columns:
            search_conditions.append(f"{column} LIKE ?")
            search_params.append(f"%{search_term}%")
        
        # Combine search conditions with OR
        search_where = " OR ".join(search_conditions)
        
        # Add WHERE clause to base query
        if "WHERE" in base_query.upper():
            search_query = f"{base_query} AND ({search_where})"
        else:
            search_query = f"{base_query} WHERE ({search_where})"
        
        # Create count query
        count_query = f"SELECT COUNT(*) FROM ({search_query}) as search_count"
        
        # Combine parameters
        all_params = (params or []) + search_params
        
        return self.paginate_query(search_query, count_query, all_params,
                                 page, page_size, db_connection)
    
    def _empty_result(self, page: int, page_size: int) -> PaginationResult:
        """Create empty pagination result."""
        return PaginationResult(
            data=[],
            current_page=page,
            page_size=page_size or self.config.page_size,
            total_records=0,
            total_pages=1,
            has_previous=False,
            has_next=False,
            start_record=0,
            end_record=0
        )

class TablePaginator:
    """
    Specialized paginator for common table operations.
    """
    
    def __init__(self, table_name: str, db_connection=None):
        """
        Initialize table paginator.
        
        Args:
            table_name: Name of the database table
            db_connection: Database connection
        """
        self.table_name = table_name
        self.db_connection = db_connection
        self.pagination_manager = PaginationManager()
    
    def get_all_records(self, columns: List[str] = None, 
                       where_clause: str = "", params: List = None,
                       order_by: str = "id DESC", page: int = 1, 
                       page_size: int = None) -> PaginationResult:
        """
        Get paginated records from table.
        
        Args:
            columns: Columns to select (None for all)
            where_clause: WHERE clause (without WHERE keyword)
            params: Parameters for WHERE clause
            order_by: ORDER BY clause
            page: Current page
            page_size: Page size
            
        Returns:
            PaginationResult with records
        """
        # Build column list
        column_list = ", ".join(columns) if columns else "*"
        
        # Build base query
        base_query = f"SELECT {column_list} FROM {self.table_name}"
        if where_clause:
            base_query += f" WHERE {where_clause}"
        
        # Build count query
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        if where_clause:
            count_query += f" WHERE {where_clause}"
        
        return self.pagination_manager.paginate_query(
            base_query, count_query, params, page, page_size, self.db_connection
        )
    
    def search_records(self, search_term: str, search_columns: List[str],
                      columns: List[str] = None, where_clause: str = "",
                      params: List = None, page: int = 1, 
                      page_size: int = None) -> PaginationResult:
        """
        Search and paginate records.
        
        Args:
            search_term: Term to search for
            search_columns: Columns to search in
            columns: Columns to select
            where_clause: Additional WHERE clause
            params: Parameters for WHERE clause
            page: Current page
            page_size: Page size
            
        Returns:
            PaginationResult with search results
        """
        column_list = ", ".join(columns) if columns else "*"
        base_query = f"SELECT {column_list} FROM {self.table_name}"
        
        if where_clause:
            base_query += f" WHERE {where_clause}"
        
        return self.pagination_manager.create_search_pagination(
            base_query, search_term, search_columns, params,
            page, page_size, self.db_connection
        )

# Global pagination manager
pagination_manager = PaginationManager()

def paginate_query(base_query: str, count_query: str, params: List = None,
                  page: int = 1, page_size: int = 50, 
                  db_connection=None) -> PaginationResult:
    """
    Convenience function for query pagination.
    
    Args:
        base_query: Base SQL query
        count_query: Count query for total records
        params: Query parameters
        page: Current page
        page_size: Records per page
        db_connection: Database connection
        
    Returns:
        PaginationResult
    """
    return pagination_manager.paginate_query(
        base_query, count_query, params, page, page_size, db_connection
    )