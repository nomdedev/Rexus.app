"""
Sistema de paginación para Rexus.app

Proporciona componentes de paginación para tablas grandes
mejorando el rendimiento y la experiencia de usuario.
"""


import logging
logger = logging.getLogger(__name__)

                - get_paginated_data(offset,
limit,
        filters=None) -> Tuple[List[Dict],
        int]
    """

    def __init__(self):
        self.pagination_info = PaginationInfo()
        self.current_filters = {}

    def get_paginated_results(self, page: int = 1, page_size: int = 50,
                            filters: Optional[Dict] = None) -> Tuple[List[Dict], PaginationInfo]:
        """
        Obtiene resultados paginados.

        Args:
            page: Número de página (empezando desde 1)
            page_size: Elementos por página
            filters: Filtros adicionales

        Returns:
            Tupla (datos, información_paginación)
        """
        # Actualizar filtros si se proporcionan
        if filters is not None:
            self.current_filters = filters

        # Calcular offset
        offset = (page - 1) * page_size

        try:
            # Obtener datos y total (debe implementarse en la clase hija)
            data, total_items = self.get_paginated_data(offset,
                                                       page_size,
                                                       self.current_filters)

            # Crear información de paginación
            pagination_info = PaginationInfo(page, page_size, total_items)

            self.pagination_info = pagination_info
            return data, pagination_info

        except Exception as e:
            logger.info(f"Error obteniendo datos paginados: {e}")
            return [], PaginationInfo(page, page_size, 0)

    def get_paginated_data(self, offset: int, limit: int,
                          filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
        """
        Método que debe implementarse en las clases hijas.

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filters: Diccionario con filtros adicionales

        Returns:
            Tupla (lista_datos, total_elementos)

        Raises:
            NotImplementedError: Si no se implementa en la clase hija
        """
        raise NotImplementedError("Las clases hijas deben implementar get_paginated_data()")


def create_pagination_query(base_query: str, count_query: str = None) -> Tuple[str, str]:
    """
    Crea consultas SQL con paginación.

    Args:
        base_query: Consulta SQL base (SELECT ... FROM ... WHERE ...)
        count_query: Consulta de conteo opcional

    Returns:
        Tupla (consulta_paginada, consulta_conteo)
    """
    # Consulta paginada con OFFSET y FETCH
    paginated_query = f"""
        {base_query}
        ORDER BY id DESC
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY
    """

    # Consulta de conteo
    if count_query is None:
        # Extraer la parte SELECT y reemplazar por COUNT
        if "SELECT" in base_query.upper() and "FROM" in base_query.upper():
            from_index = base_query.upper().find("FROM")
            from_part = base_query[from_index:]
            count_query = f"SELECT COUNT(*) {from_part}"
        else:
            count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_subquery"

    return paginated_query.strip(), count_query.strip()


# Ejemplos de uso y funciones de utilidad

def apply_pagination_to_table(table_widget: QTableWidget, data: List[Dict],
                             columns: List[str]):
    """
    Aplica datos paginados a un QTableWidget.

    Args:
        table_widget: Widget de tabla
        data: Lista de datos a mostrar
        columns: Lista de nombres de columnas
    """
    table_widget.setRowCount(len(data))
    table_widget.setColumnCount(len(columns))
    table_widget.setHorizontalHeaderLabels(columns)

    for row, item in enumerate(data):
        for col, column_name in enumerate(columns):
            value = item.get(column_name, "")
            table_widget.setItem(row, col, QTableWidgetItem(str(value)))


def get_optimized_page_size(total_items: int) -> int:
    """
    Calcula un tamaño de página optimizado basado en el total de elementos.

    Args:
        total_items: Número total de elementos

    Returns:
        Tamaño de página optimizado
    """
    if total_items <= 100:
        return 25
    elif total_items <= 1000:
        return 50
    elif total_items <= 10000:
        return 100
    else:
        return 200
