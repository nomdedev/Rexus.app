"""
BaseModuleView extendida con soporte de paginación inteligente
Extiende la funcionalidad base con paginación optimizada para tablas grandes

Fecha: 13/08/2025
Objetivo: Proporcionar base común para módulos con paginación
"""

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import pyqtSignal

# Importar clase base y componentes
from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.components.pagination_widget import PaginationWidget
from rexus.utils.pagination_manager import PaginationManager


class BaseModuleViewWithPagination(BaseModuleView):
    """
    Vista base extendida con soporte completo de paginación.

    Características adicionales:
    - PaginationWidget integrado
    - PaginationManager automático
    - Métodos virtuales para sobrescribir
    - Cache inteligente integrado
    - Búsqueda con debounce
    """

    # Señales adicionales para paginación
    pagination_data_loaded = pyqtSignal(dict)  # Datos cargados
    pagination_error = pyqtSignal(str)  # Error en paginación

    def __init__(self, parent=None):
        super().__init__(parent)

        # Componentes de paginación
        self.pagination_widget = None
        self.pagination_manager = None
        self.table_name = ""  # Debe ser establecido por subclases

        # Estado de paginación
        self.current_search_term = ""
        self.current_filters = {}
        self.is_loading = False

        self._init_pagination_ui()
        self._connect_pagination_signals()

    def _init_pagination_ui(self):
        """Inicializa los componentes UI de paginación."""
        # Crear widget de paginación
        self.pagination_widget = PaginationWidget()

        # Configurar callbacks
        self.pagination_widget.set_data_loader(self.load_paginated_data)
        self.pagination_widget.set_search_loader(self.search_paginated_data)

        # Agregar al layout principal
        if hasattr(self, 'main_layout'):
            self.main_layout.addWidget(self.pagination_widget)
        else:
            # Si no hay layout principal, crear uno básico
            if not self.layout():
                main_layout = QVBoxLayout(self)
                main_layout.addWidget(self.pagination_widget)

    def _connect_pagination_signals(self):
        """Conecta las señales de paginación."""
        if self.pagination_widget:
            self.pagination_widget.page_changed.connect(self.on_page_changed)
            self.pagination_widget.page_size_changed.connect(self.on_page_size_changed)
            self.pagination_widget.search_requested.connect(self.on_search_requested)
            self.pagination_widget.refresh_requested.connect(self.on_refresh_requested)

    def setup_pagination_manager(self, table_name: str, db_connection=None):
        """
        Configura el gestor de paginación.

        Args:
            table_name: Nombre de la tabla principal
            db_connection: Conexión a la base de datos
        """
        self.table_name = table_name
        self.pagination_manager = PaginationManager(table_name, db_connection)

        # Configuración inicial
        self.pagination_manager.default_page_size = 50
        self.pagination_manager.max_page_size = 500

        print(f"[PAGINATION] Gestor configurado para tabla '{table_name}'")

    def load_paginated_data(self, page: int, page_size: int) -> dict:
        """
        Carga datos paginados desde el modelo.

        Método virtual - debe ser implementado por subclases.

        Args:
            page: Número de página
            page_size: Tamaño de página

        Returns:
            dict: Resultado con 'data', 'total', 'page', 'page_size'
        """
        if hasattr(self, 'model') and \
            hasattr(self.model, 'obtener_datos_paginados'):
            return self.model.obtener_datos_paginados(page,
page_size,
                self.current_search_term,
                self.current_filters)

        # Fallback para compatibilidad
        print(f"[PAGINATION] load_paginated_data no implementado en {self.__class__.__name__}")
        return {
            'data': [],
            'total_records': 0,
            'current_page': page,
            'page_size': page_size,
            'total_pages': 1,
            'has_next': False,
            'has_previous': False
        }

    def search_paginated_data(self,
search_term: str,
        page: int,
        page_size: int) -> dict:
        """
        Busca datos paginados desde el modelo.

        Método virtual - puede ser sobrescrito por subclases.

        Args:
            search_term: Término de búsqueda
            page: Número de página
            page_size: Tamaño de página

        Returns:
            dict: Resultado de búsqueda paginada
        """
        self.current_search_term = search_term
        return self.load_paginated_data(page, page_size)

    def on_page_changed(self, page: int):
        """
        Maneja el cambio de página.

        Args:
            page: Nueva página
        """
        if self.is_loading:
            return

        try:
            self.set_loading_state(True)

            # Cargar datos de la nueva página
            result = self.load_paginated_data(page, self.pagination_widget.get_page_size())

            # Actualizar tabla/vista con los nuevos datos
            self.update_table_data(result['data'])

            # Actualizar información de paginación
            self.pagination_widget.update_pagination_info(
                result['total_records'],
                result['current_page']
            )

            # Emitir señal de datos cargados
            self.pagination_data_loaded.emit(result)

            # Precargar páginas siguientes si está habilitado
            if self.pagination_manager:
                self.pagination_manager.prefetch_next_pages(
                    page,
                    self.pagination_widget.get_page_size(),
                    self.current_search_term,
                    self.current_filters
                )

        except Exception as e:
            error_msg = f"Error cargando página {page}: {str(e)}"
            print(f"[PAGINATION ERROR] {error_msg}")
            self.pagination_error.emit(error_msg)

        finally:
            self.set_loading_state(False)

    def on_page_size_changed(self, page_size: int):
        """
        Maneja el cambio de tamaño de página.

        Args:
            page_size: Nuevo tamaño de página
        """
        # Recargar primera página con nuevo tamaño
        self.on_page_changed(1)

    def on_search_requested(self, search_term: str):
        """
        Maneja las solicitudes de búsqueda.

        Args:
            search_term: Término de búsqueda
        """
        if self.is_loading:
            return

        try:
            self.set_loading_state(True)
            self.current_search_term = search_term

            # Realizar búsqueda desde la primera página
            result = self.search_paginated_data(search_term, 1, self.pagination_widget.get_page_size())

            # Actualizar vista
            self.update_table_data(result['data'])
            self.pagination_widget.update_pagination_info(
                result['total_records'],
                result['current_page']
            )

            self.pagination_data_loaded.emit(result)

        except Exception as e:
            error_msg = f"Error en búsqueda '{search_term}': {str(e)}"
            print(f"[PAGINATION ERROR] {error_msg}")
            self.pagination_error.emit(error_msg)

        finally:
            self.set_loading_state(False)

    def on_refresh_requested(self):
        """Maneja las solicitudes de actualización."""
        # Invalidar cache si existe
        if self.pagination_manager:
            self.pagination_manager.invalidate_cache()

        # Recargar página actual
        current_page = self.pagination_widget.get_current_page()
        self.on_page_changed(current_page)

    def set_loading_state(self, loading: bool):
        """
        Establece el estado de carga.

        Args:
            loading: True si está cargando
        """
        self.is_loading = loading
        if self.pagination_widget:
            self.pagination_widget.set_loading_state(loading)

        # Deshabilitar otros controles durante la carga
        if hasattr(self, 'table') and self.table:
            self.table.setEnabled(not loading)

    def update_table_data(self, data: list):
        """
        Actualiza los datos de la tabla principal.

        Método virtual - debe ser implementado por subclases.

        Args:
            data: Lista de datos para mostrar
        """
        print(f"[PAGINATION] update_table_data no implementado en {self.__class__.__name__}")
        print(f"[PAGINATION] Datos recibidos: {len(data)} registros")

    def set_filters(self, filters: dict):
        """
        Establece filtros adicionales para la paginación.

        Args:
            filters: Diccionario de filtros
        """
        self.current_filters = filters or {}
        # Recargar primera página con nuevos filtros
        self.on_page_changed(1)

    def get_pagination_statistics(self) -> dict:
        """
        Obtiene estadísticas de la paginación.

        Returns:
            dict: Estadísticas del gestor de paginación
        """
        if self.pagination_manager:
            return self.pagination_manager.get_statistics()
        return {}

    def invalidate_pagination_cache(self, pattern: str = None):
        """
        Invalida el cache de paginación.

        Args:
            pattern: Patrón específico a invalidar
        """
        if self.pagination_manager:
            self.pagination_manager.invalidate_cache(pattern)

    def go_to_first_page(self):
        """Navega a la primera página."""
        if self.pagination_widget:
            self.pagination_widget.go_to_first_page()

    def go_to_last_page(self):
        """Navega a la última página."""
        if self.pagination_widget:
            self.pagination_widget.go_to_last_page()

    def refresh_pagination(self):
        """Actualiza completamente la paginación."""
        self.on_refresh_requested()


# Ejemplo de uso en módulos específicos
"""
class InventarioViewWithPagination(BaseModuleViewWithPagination):
    def __init__(self):
        super().__init__()

        # Configurar paginación
        self.setup_pagination_manager('inventario', db_connection)

        # Configurar tabla
        self.setup_table()

    def update_table_data(self, data: list):
        # Implementar actualización específica de la tabla de inventario
        self.table.clear()
        for item in data:
            # Agregar items a la tabla
            pass

    def load_paginated_data(self, page: int, page_size: int) -> dict:
        # Usar el modelo específico del módulo
        return self.model.obtener_productos_paginados(
            page=page,
            page_size=page_size,
            search_term=self.current_search_term,
            filters=self.current_filters
        )
"""
