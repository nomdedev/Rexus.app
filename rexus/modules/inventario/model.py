from rexus.utils.unified_sanitizer import unified_sanitizer
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.core.query_optimizer import cached_query, track_performance

# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
"""
Modelo de Inventario

Maneja la lógica de negocio y acceso a datos para el inventario.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.

MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.
"""

import datetime
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlite3 import IntegrityError

import qrcode

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("inventario.model")
except ImportError:
    import logging
    logger = logging.getLogger("inventario.model")

# Importar sistema de paginación
from rexus.utils.pagination import PaginatedTableMixin

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir / "src"))

    from rexus.utils.sql_security import SQLSecurityValidator

    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security utilities not available in inventario: {e}")
    SECURITY_AVAILABLE = False

# Importar nueva utilidad de seguridad SQL
try:
    from rexus.utils.sql_script_loader import sql_script_loader
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name

    SQL_SECURITY_AVAILABLE = True
except ImportError:
    logger.warning("SQL security utilities not available in inventario")
    SQL_SECURITY_AVAILABLE = False
    sql_script_loader = None

# Importar managers especializados
try:
    from rexus.modules.inventario.submodules.base_utilities import BaseUtilities
    from rexus.modules.inventario.submodules.productos_manager import ProductosManager
    from rexus.modules.inventario.submodules.movimientos_manager import MovimientosManager
    from rexus.modules.inventario.submodules.reservas_manager import ReservasManager
    from rexus.modules.inventario.submodules.reportes_manager import ReportesManager
    from rexus.modules.inventario.submodules.categorias_manager import CategoriasManager

    SUBMODULES_AVAILABLE = True
    print("OK [INVENTARIO] Submódulos especializados cargados")
except ImportError as e:
    logger.warning(f"Submódulos especializados no disponibles en inventario: {e}")
    SUBMODULES_AVAILABLE = False
    BaseUtilities = None
    ProductosManager = None
    MovimientosManager = None
    ReservasManager = None
    ReportesManager = None
    CategoriasManager = None

# Importar ConsultasManager (mantener compatibilidad)
try:
    from rexus.modules.inventario.submodules.consultas_manager import (
        ConsultasManager,
    )

    CONSULTAS_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ConsultasManager not available in inventario: {e}")
    CONSULTAS_MANAGER_AVAILABLE = False
    ConsultasManager = None


class InventarioModel(PaginatedTableMixin):
    """
    Modelo para gestionar el inventario de productos.

    MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
    para prevenir inyección SQL y mejorar mantenibilidad.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de inventario con utilidades de seguridad.

        Args:
            db_connection: Conexión a la base de datos
        """
        # Inicializar mixin de paginación
        super().__init__()

        self.db_connection = db_connection
        # [LOCK] Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()  # Para consultas SQL seguras
        self.tabla_inventario = "inventario_perfiles"  # Usar tabla real de la BD
        self.tabla_movimientos = "historial"  # Usar tabla historial existente
        self.tabla_reservas = "reserva_materiales"  # Tabla para reservas por obra

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available:
            self.data_sanitizer = unified_sanitizer
            self.sql_validator = SQLSecurityValidator()
            print("OK [INVENTARIO] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = unified_sanitizer  # Usar sanitizer por defecto
            self.sql_validator = None
            print("WARNING [INVENTARIO] Utilidades de seguridad no disponibles")

        # Inicializar SQL script loader
        self.sql_loader_available = (
            SQL_SECURITY_AVAILABLE and sql_script_loader is not None
        )
        if self.sql_loader_available:
            self.script_loader = sql_script_loader
            print("OK [INVENTARIO] SQL script loader disponible")
        else:
            self.script_loader = None
            print("WARNING [INVENTARIO] SQL script loader no disponible")

        # Inicializar managers especializados
        if SUBMODULES_AVAILABLE:
            try:
                self.base_utils = BaseUtilities(db_connection=self.db_connection)
                self.productos_manager = ProductosManager(db_connection=self.db_connection)
                self.movimientos_manager = MovimientosManager(db_connection=self.db_connection)
                self.reservas_manager = ReservasManager(db_connection=self.db_connection)
                self.reportes_manager = ReportesManager(db_connection=self.db_connection)
                self.categorias_manager = CategoriasManager(db_connection=self.db_connection)
                print("OK [INVENTARIO] Managers especializados inicializados")
                self.managers_available = True
            except (ImportError, AttributeError, RuntimeError) as e:
                print(f"[ERROR INVENTARIO] Error inicializando managers especializados: {e}")
                self.managers_available = False
                self._init_fallback_managers()
        else:
            print("WARNING [INVENTARIO] Submódulos no disponibles, usando modo de compatibilidad")
            self.managers_available = False
            self._init_fallback_managers()

        # Inicializar ConsultasManager (mantener compatibilidad)
        if CONSULTAS_MANAGER_AVAILABLE and ConsultasManager:
            self.consultas_manager = ConsultasManager(db_connection=self.db_connection)
            print("OK [INVENTARIO] ConsultasManager inicializado")
        else:
            self.consultas_manager = None
            print("WARNING [INVENTARIO] ConsultasManager no disponible")

        if not self.db_connection:
            print(
                "[ERROR INVENTARIO] No hay conexión a la base de datos. El módulo no funcionará correctamente."
            )
        self._verificar_tablas()

    def _init_fallback_managers(self):
        """Inicializa managers básicos como fallback cuando los submódulos no están disponibles."""
        self.base_utils = None
        self.productos_manager = None
        self.movimientos_manager = None
        self.reservas_manager = None
        self.reportes_manager = None
        self.categorias_manager = None
        print("INFO [INVENTARIO] Usando funciones integradas como fallback")

    # ===========================================
    # MÉTODOS DE PROXY PARA COMPATIBILIDAD
    # ===========================================

    def crear_producto(self,
datos_producto: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Proxy para crear producto - usa ProductosManager si está disponible."""
        if self.managers_available and self.productos_manager:
            return self.productos_manager.crear_producto(datos_producto)
        else:
            # Fallback al método original (si existe)
            return self._crear_producto_fallback(datos_producto)

    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Proxy para obtener producto por código."""
        if self.managers_available and self.productos_manager:
            return self.productos_manager.obtener_producto_por_codigo(codigo)
        else:
            return self._obtener_producto_por_codigo_fallback(codigo)

    def actualizar_stock_producto(self, producto_id: int, nuevo_stock: Union[int, float],
                                razon: str = "Ajuste manual") -> Dict[str, Any]:
        """Proxy para actualizar stock de producto."""
        if self.managers_available and self.productos_manager:
            return self.productos_manager.actualizar_stock(producto_id, nuevo_stock, razon)
        else:
            return self._actualizar_stock_fallback(producto_id, nuevo_stock, razon)

    def registrar_movimiento_stock(self,
datos_movimiento: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Proxy para registrar movimiento de stock."""
        if self.managers_available and self.movimientos_manager:
            return self.movimientos_manager.registrar_movimiento(
                datos_movimiento['producto_id'],
                datos_movimiento['tipo_movimiento'],
                datos_movimiento['cantidad'],
                datos_movimiento.get('observaciones', ''),
                datos_movimiento.get('obra_id'),
                datos_movimiento.get('usuario', 'SISTEMA')
            )
        else:
            return self._registrar_movimiento_fallback(datos_movimiento)

    def crear_reserva_material(self,
datos_reserva: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Proxy para crear reserva de material."""
        if self.managers_available and self.reservas_manager:
            return self.reservas_manager.crear_reserva(datos_reserva)
        else:
            return self._crear_reserva_fallback(datos_reserva)

    def generar_reporte_inventario(self, tipo_reporte: str, filtros: Optional[Dict] = None,
                                 formato: str = 'DICT') -> Dict[str, Any]:
        """Proxy para generar reportes de inventario."""
        if self.managers_available and self.reportes_manager:
            if tipo_reporte == 'STOCK_ACTUAL':
                return self.reportes_manager.generar_reporte_stock_actual(filtros, formato)
            elif tipo_reporte == 'MOVIMIENTOS':
                return self.reportes_manager.generar_reporte_movimientos(
                    filtros.get('fecha_desde') if filtros else None,
                    filtros.get('fecha_hasta') if filtros else None,
                    filtros.get('producto_id') if filtros else None,
                    filtros.get('tipo_movimiento') if filtros else None,
                    formato
                )
            elif tipo_reporte == 'KPI_DASHBOARD':
                return self.reportes_manager.generar_dashboard_kpis(formato)
            elif tipo_reporte == 'ANALISIS_ABC':
                criterio = filtros.get('criterio', 'valor') if filtros else 'valor'
                return self.reportes_manager.generar_analisis_abc(criterio, formato)
            elif tipo_reporte == 'VALORACION_INVENTARIO':
                fecha_corte = filtros.get('fecha_corte') if filtros else None
                return self.reportes_manager.generar_reporte_valoracion_inventario(fecha_corte, formato)
            else:
                return {'success': False, 'error': f'Tipo de reporte no soportado: {tipo_reporte}'}
        else:
            return self._generar_reporte_fallback(tipo_reporte, filtros, formato)

    def obtener_categorias(self, incluir_estadisticas: bool = False) -> List[Dict[str, Any]]:
        """Proxy para obtener categorías."""
        if self.managers_available and self.categorias_manager:
            return self.categorias_manager.obtener_todas_categorias(incluir_estadisticas)
        else:
            return self._obtener_categorias_fallback(incluir_estadisticas)

    def _execute_secure_script(
        self, script_name: str, params: list = None, fallback_query: str = None
    ):
        """
        Ejecuta un script SQL de forma segura con parámetros.

        Args:
            script_name: Nombre del script SQL a ejecutar
            params: Lista de parámetros para el script
            fallback_query: Query de respaldo si el script no está disponible

        Returns:
            Lista de resultados o None si hay error
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            if self.sql_loader_available:
                try:
                    script_content = self.script_loader.load_script(script_name)
                    if script_content:
                        cursor.execute(script_content, params or [])
                        return cursor.fetchall()
                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error ejecutando script {script_name}: {e}")

            # Usar query de respaldo si está disponible
            if fallback_query:
                cursor.execute(fallback_query, params or [])
                return cursor.fetchall()

            return None

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error("Error ejecutando consulta segura: {e}")
            return None

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de la tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            Exception: Si el nombre no es válido o contiene caracteres peligrosos
        """
        if SQL_SECURITY_AVAILABLE:
            try:
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                print(f"[ERROR SEGURIDAD] {str(e)}")
                # Fallback a verificación básica

        # Verificación básica si la utilidad no está disponible
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Nombre de tabla inválido")

        # Eliminar espacios en blanco
        table_name = table_name.strip()

        # Verificar que solo contenga caracteres alfanuméricos y guiones bajos
        if not all(c.isalnum() or c == "_" for c in table_name):
            raise ValueError(
                f"Nombre de tabla contiene caracteres no válidos: {table_name}"
            )

        # Verificar longitud razonable
        if len(table_name) > 64:
            raise ValueError(f"Nombre de tabla demasiado largo: {table_name}")

        return table_name.lower()

    def get_paginated_data(
        self, offset: int, limit: int, filters: Optional[Dict] = None
    ) -> Tuple[List[Dict], int]:
        """
        Implementación requerida por PaginatedTableMixin.
        Obtiene productos del inventario con paginación.

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filters: Filtros adicionales (categoria, activo, etc.)

        Returns:
            Tupla (lista_productos, total_productos)
        """
        if not self.db_connection:
            return [], 0

        try:
            # Usar script SQL externo si está disponible
            if SQL_SECURITY_AVAILABLE and sql_script_loader:
                script_content = sql_script_loader.load_script(
                    "inventario/select_all_productos"
                )
                if script_content:
                    cursor = self.db_connection.cursor()
                    cursor.execute(script_content)
                    productos = []

                    for row in cursor.fetchall():
                        if row and len(row) > 11:
                            productos.append(
                                {
                                    "id": row[0],
                                    "codigo": row[1],
                                    "nombre": row[2] if len(row) > 2 else "",
                                    "categoria": row[3] if len(row) > 3 else "",
                                    "tipo": row[4] if len(row) > 4 else "",
                                    "marca": row[5] if len(row) > 5 else "",
                                    "cantidad_disponible": row[6]
                                    if len(row) > 6
                                    else 0,
                                    "precio_unitario": row[7] if len(row) > 7 else 0.0,
                                    "proveedor": row[8] if len(row) > 8 else "",
                                    "ubicacion_almacen": row[9] if len(row) > 9 else "",
                                    "fecha_creacion": row[10]
                                    if len(row) > 10
                                    else None,
                                    "activo": bool(row[11]) if len(row) > 11 else True,
                                }
                            )

                    # Aplicar paginación
                    total_items = len(productos)
                    productos_paginados = productos[offset : offset + limit]
                    return productos_paginados, total_items

            # [LOCK] Usar consulta SQL externa segura
            params = {
                "categoria": filters.get("categoria") if filters else None,
                "codigo": filters.get("codigo") if filters else None,
                "nombre": filters.get("nombre") if filters else None
            }

            sql = self.sql_manager.get_query('inventario', 'list_productos_with_filters')
            cursor = self.db_connection.cursor()
            cursor.execute(sql, params)
            productos = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            # Aplicar paginación a resultados
            total_items = len(productos)
            productos_paginados = productos[offset:offset + limit]

            return productos_paginados, total_items

            productos = []
            for row in cursor.fetchall():
                producto = {
                    "id": row[0],
                    "codigo": row[1],
                    "nombre": row[2],
                    "categoria": row[3],
                    "tipo": row[4],
                    "marca": row[5],
                    "cantidad_disponible": row[6],
                    "precio_unitario": row[7],
                    "proveedor": row[8],
                    "ubicacion_almacen": row[9],
                    "fecha_creacion": row[10],
                    "activo": bool(row[11]),
                }
                productos.append(producto)

            return productos, total_items

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error obteniendo datos paginados de inventario: {e}")
            return [], 0

    def obtener_productos_paginados(
        self,
        page: int = 1,
        page_size: int = 50,
        categoria: str = None,
        activo: bool = None,
        search: str = None,
    ) -> Tuple[List[Dict], Dict]:
        """
        Obtiene productos del inventario con paginación.

        Args:
            page: Número de página (empezando desde 1)
            page_size: Productos por página
            categoria: Filtrar por categoría
            activo: Filtrar por estado activo
            search: Término de búsqueda

        Returns:
            Tupla (lista_productos, información_paginación)
        """
        filters = {}
        if categoria:
            filters["categoria"] = categoria
        if activo is not None:
            filters["activo"] = activo
        if search:
            filters["search"] = search

        productos, pagination_info = self.get_paginated_results(
            page, page_size, filters
        )
        return productos, pagination_info.to_dict()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos. NO CREA TABLAS."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla principal (crítica)
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_existe')
            cursor.execute(sql_verificar, (self.tabla_inventario,))
            if cursor.fetchone():
                print(
                    f"[INVENTARIO] Tabla principal '{self.tabla_inventario}' verificada correctamente."
                )
            else:
                raise RuntimeError(
                    f"[CRITICAL] Required table '{self.tabla_inventario}' does not exist. Please create it manually."
                )

            # Verificar tablas secundarias (no críticas)
            tablas_secundarias = [self.tabla_movimientos, self.tabla_reservas]

            for tabla in tablas_secundarias:
                sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_existe')
                cursor.execute(sql_verificar, (tabla,))
                if cursor.fetchone():
                    print(f"[INVENTARIO] Tabla '{tabla}' verificada correctamente.")
                else:
                    print(
                        f"[ADVERTENCIA] Tabla secundaria '{tabla}' no existe. Algunas funciones estarán limitadas."
                    )

            print(f"[INVENTARIO] Verificación de tablas completada.")
        except (AttributeError, RuntimeError, ConnectionError) as e:
            print(f"[ERROR INVENTARIO] Error verificando tablas: {e}")
            raise

    def obtener_todos_productos(self, filtros=None):
        """
        Obtiene todos los productos del inventario desde la tabla inventario_perfiles.

        Args:
            filtros (dict): Filtros opcionales (categoria, estado, stock_bajo)

        Returns:
            List[Dict]: Lista de productos
        """
        if not self.db_connection:
            return []

        try:
            self.db_connection.cursor()

            # Construir query con filtros
            conditions = ["1=1"]  # Condición base
            params = []

            if filtros:
                if filtros.get("categoria"):
                    conditions.append("tipo = ?")
                    params.append(filtros["categoria"])

                if filtros.get("estado"):
                    # Estado siempre es ACTIVO para esta tabla
                    pass

                if filtros.get("stock_bajo"):
                    conditions.append("stock_actual <= stock_minimo")

                if filtros.get("busqueda"):
                    conditions.append("(descripcion LIKE ? OR codigo LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            " AND ".join(conditions)

            # Usar la tabla real inventario_perfiles con columnas existentes
            # SECURITY: Validar nombre de tabla para prevenir SQL injection
            tabla_segura = "inventario_perfiles"
            if SQL_SECURITY_AVAILABLE:
                try:
                    # Agregar tabla a lista blanca si no existe
                    from rexus.utils.sql_security import sql_validator

                    if tabla_segura not in sql_validator.ALLOWED_TABLES:
                        sql_validator.add_allowed_table(tabla_segura)
                    validate_table_name(tabla_segura)
                except SQLSecurityError as e:
                    print(f"[SECURITY ERROR] Tabla no válida: {e}")
                    return []
            else:
                pass

            # [LOCK] Usar consulta SQL externa segura
            search_term = filtros.get("search") if filtros else None
            params_query = {
                "search": search_term if search_term else None,
                "categoria": None,  # Agregar filtros según necesidad
                "activo": 1
            }

            productos = self.sql_manager.execute_query(
                "get_productos_estructura_estandar",
                params=params_query
            )

            # Calcular estado del stock para cada producto
            for producto in productos:
                producto["estado_stock"] = self._determinar_estado_stock(producto)

            return productos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo productos: {e}")
            return []

    def _determinar_estado_stock(self, producto):
        """Determina el estado del stock (OK, BAJO, CRÍTICO)."""
        stock_actual = producto.get("stock_actual", 0)
        stock_minimo = producto.get("stock_minimo", 0)

        if stock_actual <= 0:
            return "AGOTADO"
        elif stock_actual <= stock_minimo:
            return "CRÍTICO"
        elif stock_actual <= stock_minimo * 1.5:
            return "BAJO"
        else:
            return "OK"

    def validar_stock_negativo(self, cantidad_nueva, producto_id=None):
        """
        Valida que el stock no sea negativo y esté dentro de límites.

        Args:
            cantidad_nueva: Nueva cantidad de stock a validar
            producto_id: ID del producto (opcional para validaciones adicionales)

        Returns:
            dict: {'valido': bool, 'mensaje': str, 'stock_disponible': int}
        """
        try:
            # Validar que la cantidad no sea negativa
            if cantidad_nueva < 0:
                return {
                    "valido": False,
                    "mensaje": "El stock no puede ser negativo",
                    "stock_disponible": 0,
                }

            # Validar límite máximo (ej: 999999)
            MAX_STOCK = 999999
            if cantidad_nueva > MAX_STOCK:
                return {
                    "valido": False,
                    "mensaje": f"El stock no puede superar {MAX_STOCK} unidades",
                    "stock_disponible": MAX_STOCK,
                }

            # Si se proporciona producto_id, verificar stock actual
            if producto_id and self.db_connection:
                cursor = self.db_connection.cursor()
                sql_stock = self.sql_manager.get_query('inventario', 'obtener_stock_producto')
                cursor.execute(sql_stock, (producto_id,))
                row = cursor.fetchone()

                if row:
                    stock_actual, stock_minimo, stock_maximo = row

                    # Verificar límites específicos del producto
                    if stock_maximo and cantidad_nueva > stock_maximo:
                        return {
                            "valido": False,
                            "mensaje": f"El stock no puede superar el máximo permitido ({stock_maximo})",
                            "stock_disponible": stock_maximo,
                        }

            return {
                "valido": True,
                "mensaje": "Stock válido",
                "stock_disponible": int(cantidad_nueva),
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error validando stock: {e}")
            return {
                "valido": False,
                "mensaje": "Error en validación de stock",
                "stock_disponible": 0,
            }

    def obtener_producto_por_id(self, producto_id):
        """Obtiene un producto específico por ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Usar query externa para seguridad
            sql_select = self.sql_manager.get_query('inventario', 'obtener_perfil_por_id')
            cursor.execute(sql_select, (producto_id,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

            return None

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo producto {producto_id}: {e}")
            return None

    def obtener_producto_por_codigo(self, codigo):
        """Obtiene un producto específico por código."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Usar query externa para seguridad
            sql_select = self.sql_manager.get_query('inventario', 'obtener_perfil_por_codigo')
            cursor.execute(sql_select, (codigo,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

            return None

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo producto por código: {e}")
            return None

    def crear_producto(self, datos_producto, usuario="SISTEMA"):
        """
        Crea un nuevo producto en el inventario.

        Args:
            datos_producto (dict): Datos del producto
            usuario (str): Usuario que crea el producto

        Returns:
            int: ID del producto creado o None si hay error
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Verificar que el código no exista
            if self.obtener_producto_por_codigo(datos_producto.get("codigo")):
                raise Exception(
                    f"Ya existe un producto con código {datos_producto.get('codigo')}"
                )

            # Generar código QR
            codigo_qr = self._generar_codigo_qr(datos_producto.get("codigo"))

            sql_insert = """
            INSERT INTO inventario_perfiles
            (codigo, descripcion, tipo, acabado, stock_actual, stock_minimo,
             stock_maximo, importe, ubicacion, proveedor, unidad,
             activo, usuario_creacion, observaciones, qr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """

            cursor.execute(
                sql_insert,
                (
                    datos_producto.get("codigo"),
                    datos_producto.get("descripcion"),
                    datos_producto.get("tipo", ""),
                    datos_producto.get("acabado", ""),
                    datos_producto.get("stock_actual", 0),
                    datos_producto.get("stock_minimo", 0),
                    datos_producto.get("stock_maximo", 1000),
                    datos_producto.get("importe", 0.00),
                    datos_producto.get("ubicacion", ""),
                    datos_producto.get("proveedor", ""),
                    datos_producto.get("unidad", "Unidad"),
                    usuario,
                    datos_producto.get("observaciones", ""),
                    codigo_qr,
                ),
            )

            # [LOCK] Obtener ID del producto creado de forma segura
            sql = self.sql_manager.get_query('inventario', 'get_last_identity')
            cursor.execute(sql)
            producto_id = cursor.fetchone()[0]

            self.db_connection.commit()

            # Registrar movimiento inicial si hay stock
            stock_inicial = datos_producto.get("stock_actual", 0)
            if stock_inicial > 0:
                self.registrar_movimiento(
                    producto_id=producto_id,
                    tipo_movimiento="ENTRADA",
                    cantidad=stock_inicial,
                    motivo="Stock inicial",
                    usuario=usuario,
                )

            print(f"[INVENTARIO] Producto creado: {datos_producto.get('codigo')}")
            return producto_id

        except (AttributeError, RuntimeError, ConnectionError, ValueError, IntegrityError) as e:
            print(f"[ERROR INVENTARIO] Error creando producto: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return None

    def actualizar_producto(self,
producto_id,
        datos_producto,
        usuario="SISTEMA"):
        """
        Actualiza un producto existente.

        Args:
            producto_id (int): ID del producto a actualizar
            datos_producto (dict): Datos actualizados
            usuario (str): Usuario que actualiza

        Returns:
            bool: True si se actualizó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Obtener datos actuales para auditoría
            producto_actual = self.obtener_producto_por_id(producto_id)
            if not producto_actual:
                raise Exception("Producto no encontrado")

            sql_update = self.sql_manager.get_query('inventario', 'actualizar_producto')

            cursor.execute(
                sql_update,
                (
                    datos_producto.get("descripcion", producto_actual["descripcion"]),
                    datos_producto.get("categoria", producto_actual["categoria"]),
                    datos_producto.get("subcategoria", producto_actual["subcategoria"]),
                    datos_producto.get("stock_minimo", producto_actual["stock_minimo"]),
                    datos_producto.get("stock_maximo", producto_actual["stock_maximo"]),
                    datos_producto.get(
                        "precio_unitario", producto_actual["precio_unitario"]
                    ),
                    datos_producto.get("ubicacion", producto_actual["ubicacion"]),
                    datos_producto.get("proveedor", producto_actual["proveedor"]),
                    datos_producto.get(
                        "unidad_medida", producto_actual["unidad_medida"]
                    ),
                    datos_producto.get(
                        "observaciones", producto_actual["observaciones"]
                    ),
                    usuario,
                    producto_id,
                ),
            )

            self.db_connection.commit()
            print(f"[INVENTARIO] Producto actualizado: {producto_id}")
            return True

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error actualizando producto: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def registrar_movimiento(
        self,
        producto_id,
        tipo_movimiento,
        cantidad,
        motivo="",
        documento_referencia="",
        usuario="SISTEMA",
    ):
        """
        Registra un movimiento de inventario usando la tabla historial.

        Args:
            producto_id (int): ID del producto
            tipo_movimiento (str): ENTRADA, SALIDA, AJUSTE
            cantidad (int): Cantidad del movimiento
            motivo (str): Motivo del movimiento
            documento_referencia (str): Documento de referencia
            usuario (str): Usuario que registra el movimiento

        Returns:
            bool: True si se registró exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Obtener stock actual
            producto = self.obtener_producto_por_id(producto_id)
            if not producto:
                raise Exception("Producto no encontrado")

            stock_anterior = producto["stock_actual"]

            # Calcular nuevo stock según tipo de movimiento
            if tipo_movimiento == "ENTRADA":
                stock_nuevo = stock_anterior + cantidad
            elif tipo_movimiento == "SALIDA":
                stock_nuevo = stock_anterior - cantidad
                if stock_nuevo < 0:
                    raise Exception("Stock insuficiente para la salida")
            elif tipo_movimiento == "AJUSTE":
                stock_nuevo = cantidad  # Cantidad es el stock final deseado
            else:
                raise Exception(f"Tipo de movimiento inválido: {tipo_movimiento}")

            # Verificar si existe la tabla historial
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_existe')
            cursor.execute(sql_verificar, ('historial',))
            if cursor.fetchone():
                # Registrar en historial usando estructura existente
                cantidad_movimiento = (
                    cantidad
                    if tipo_movimiento != "AJUSTE"
                    else (stock_nuevo - stock_anterior)
                )

                detalles = f"Producto ID: {producto_id}, {tipo_movimiento}: {cantidad_movimiento}, Stock anterior: {stock_anterior}, Stock nuevo: {stock_nuevo}, Motivo: {motivo}, Doc: {documento_referencia}"

                sql_historial = self.sql_manager.get_query('inventario', 'insertar_historial')
                cursor.execute(
                    sql_historial,
                    (f"INVENTARIO_{tipo_movimiento}", usuario, detalles),
                )

            # Actualizar stock en inventario_perfiles
            sql_update_stock = self.sql_manager.get_query('inventario', 'actualizar_stock')

            cursor.execute(sql_update_stock,
(stock_nuevo,
                usuario,
                producto_id))

            self.db_connection.commit()
            print(f"[INVENTARIO] Movimiento registrado: {tipo_movimiento} - {cantidad}")
            return True

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error registrando movimiento: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def obtener_movimientos(self, producto_id=None, limite=100):
        """
        Obtiene el historial de movimientos desde la tabla historial.

        Args:
            producto_id (int): ID del producto específico (opcional)
            limite (int): Límite de registros

        Returns:
            List[Dict]: Lista de movimientos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Verificar si existe la tabla historial
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_existe')
            cursor.execute(sql_verificar, ('historial',))
            if not cursor.fetchone():
                print(
                    "[ADVERTENCIA] Tabla historial no existe. No se pueden obtener movimientos."
                )
                return []

            if producto_id:
                sql_select = self.sql_manager.get_query('inventario', 'obtener_movimientos_por_producto')
                params = [f"%Producto ID: {producto_id}%"]
            else:
                sql_select = self.sql_manager.get_query('inventario', 'obtener_movimientos')
                params = []

            sql_select += (
                f" ORDER BY fecha DESC OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"
            )

            cursor.execute(sql_select, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            movimientos = []

            for row in rows:
                movimiento = dict(zip(columns, row))
                # Parse basic info from detalles field
                movimiento.get("detalles", "")
                movimiento["tipo_movimiento"] = movimiento["accion"].replace(
                    "INVENTARIO_", ""
                )
                movimientos.append(movimiento)

            return movimientos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo movimientos: {e}")
            return []

    def _generar_codigo_qr(self, codigo):
        """
        Genera un código QR para el producto.

        Args:
            codigo (str): Código del producto

        Returns:
            str: Nombre del archivo QR generado
        """
        try:
            # Crear directorio para QR si no existe
            import os

            qr_dir = "qr_codes"
            os.makedirs(qr_dir, exist_ok=True)

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(codigo)
            qr.make(fit=True)

            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")

            # Guardar archivo
            filename = f"qr_{codigo}.png"
            filepath = os.path.join(qr_dir, filename)
            img.save(filepath)

            return filename

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error generando QR: {e}")
            return ""

    @cached_query(cache_key="productos_stock_bajo", ttl=300)
    @track_performance
    def obtener_productos_stock_bajo(self):
        """Obtiene productos con stock bajo o crítico con cache."""
        return self.obtener_todos_productos({"stock_bajo": True})

    @cached_query(cache_key="categorias_productos", ttl=1800)
    @track_performance
    def obtener_categorias(self):
        """Obtiene todas las categorías de productos con cache de 30 minutos."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Query optimizada con índice en tipo
            sql_select = """
            SELECT DISTINCT tipo
            FROM inventario_perfiles
            WHERE tipo IS NOT NULL AND tipo != ''
            ORDER BY tipo
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            return [row[0] for row in rows]

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo categorías: {e}")
            return []

    def actualizar_qr_y_campos_por_descripcion(self):
        """Actualiza códigos QR y campos faltantes para productos existentes."""
        if not self.db_connection:
            return

        try:
            productos = self.obtener_todos_productos()
            for producto in productos:
                if not producto.get("codigo_qr"):
                    # Generar QR faltante
                    codigo_qr = self._generar_codigo_qr(producto["codigo"])
                    if codigo_qr:
                        cursor = self.db_connection.cursor()
                        sql_update = """
                        UPDATE inventario_perfiles
                        SET codigo_qr = ? WHERE id = ?
                        """
                        cursor.execute(sql_update, (codigo_qr, producto["id"]))

            self.db_connection.commit()
            print("[INVENTARIO] QRs actualizados")

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error actualizando QRs: {e}")

    def obtener_estadisticas_inventario(self):
        """Obtiene estadísticas generales del inventario."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Total de productos
            sql_count = self.sql_manager.get_query('inventario', 'contar_productos_totales')
            cursor.execute(sql_count)
            total_productos = cursor.fetchone()[0]

            # Productos con stock bajo
            sql_stock_bajo = self.sql_manager.get_query('inventario', 'contar_stock_bajo')
            cursor.execute(sql_stock_bajo)
            stock_bajo = cursor.fetchone()[0]

            # Valor total del inventario
            sql_valor_total = self.sql_manager.get_query('inventario', 'calcular_valor_total')
            cursor.execute(sql_valor_total)
            valor_total = cursor.fetchone()[0] or 0

            # Movimientos del mes actual desde historial
            sql_movimientos_mes = self.sql_manager.get_query('inventario', 'contar_movimientos_mes')
            cursor.execute(sql_movimientos_mes)
            movimientos_mes = cursor.fetchone()[0]

            return {
                "total_productos": total_productos,
                "stock_bajo": stock_bajo,
                "valor_total": float(valor_total),
                "movimientos_mes": movimientos_mes,
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_productos_por_obra(self, obra_id):
        """
        Obtiene todos los productos asignados a una obra específica.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de productos con información de asignación
        """
        if not self.db_connection or not obra_id:
            return []

        try:
            cursor = self.db_connection.cursor()

            sql_select = self.sql_manager.get_query('inventario', 'obtener_productos_por_obra')
            cursor.execute(sql_select, (obra_id,))
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            productos = []

            for row in rows:
                producto = dict(zip(columns, row))
                productos.append(producto)

            return productos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo productos por obra: {e}")
            return []

    def asignar_producto_obra(self, datos_asignacion, usuario="SISTEMA"):
        """
        Asigna un producto a una obra específica.

        Args:
            datos_asignacion (dict): Datos de la asignación
            usuario (str): Usuario que realiza la asignación

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos"

        try:
            # Validar datos mínimos
            if not datos_asignacion.get("producto_id"):
                return False, "ID del producto es obligatorio"

            if not datos_asignacion.get("obra_id"):
                return False, "ID de la obra es obligatorio"

            if (
                not datos_asignacion.get("cantidad")
                or datos_asignacion["cantidad"] <= 0
            ):
                return False, "Cantidad debe ser mayor que cero"

            # Verificar existencia del producto
            producto = self.obtener_producto_por_id(datos_asignacion["producto_id"])
            if not producto:
                return False, "Producto no encontrado"

            # Verificar stock disponible
            if producto["stock_actual"] < datos_asignacion["cantidad"]:
                return (
                    False,
                    f"Stock insuficiente. Disponible: {producto['stock_actual']}",
                )

            # Registrar en materiales_obra
            cursor = self.db_connection.cursor()

            sql_insert = """
            INSERT INTO materiales_obra
            (obra_id, etapa_id, producto_id, cantidad, estado,
             fecha_solicitud, observaciones, usuario_asignacion, fecha_asignacion)
            VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, GETDATE())
            """

            cursor.execute(
                sql_insert,
                (
                    datos_asignacion["obra_id"],
                    datos_asignacion.get("etapa_id"),
                    datos_asignacion["producto_id"],
                    datos_asignacion["cantidad"],
                    datos_asignacion.get("estado", "PENDIENTE"),
                    datos_asignacion.get("observaciones", ""),
                    usuario,
                ),
            )

            # Registrar movimiento de salida
            self.registrar_movimiento(
                producto_id=datos_asignacion["producto_id"],
                tipo_movimiento="SALIDA",
                cantidad=datos_asignacion["cantidad"],
                motivo=f"Asignación a Obra #{datos_asignacion['obra_id']}",
                documento_referencia=f"OBRA-{datos_asignacion['obra_id']}",
                usuario=usuario,
            )

            self.db_connection.commit()
            return True, f"Producto asignado correctamente a la obra"

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error asignando producto a obra: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error al asignar producto: {str(e)}"

    def gestionar_lotes(self, producto_id, datos_lote, usuario="SISTEMA"):
        """
        Gestiona lotes de un producto (vencimiento, seguimiento de series).

        Args:
            producto_id (int): ID del producto
            datos_lote (dict): Información del lote
            usuario (str): Usuario que registra

        Returns:
            bool: True si la operación fue exitosa
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Validar existencia de la tabla
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_lotes')
            cursor.execute(sql_verificar)
            if not cursor.fetchone():
                print("[ADVERTENCIA] Tabla 'lotes_inventario' no existe")
                return False

            # Validar producto
            producto = self.obtener_producto_por_id(producto_id)
            if not producto:
                return False

            # Insertar lote
            sql_insert = """
            INSERT INTO lotes_inventario
            (producto_id, numero_lote, fecha_vencimiento, cantidad,
             proveedor, fecha_recepcion, serie, usuario, observaciones)
            VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, ?)
            """

            cursor.execute(
                sql_insert,
                (
                    producto_id,
                    datos_lote.get("numero_lote"),
                    datos_lote.get("fecha_vencimiento"),
                    datos_lote.get("cantidad", 0),
                    datos_lote.get("proveedor", ""),
                    datos_lote.get("serie", ""),
                    usuario,
                    datos_lote.get("observaciones", ""),
                ),
            )

            # Si se requiere, actualizar stock del producto
            if datos_lote.get("actualizar_stock", False):
                self.registrar_movimiento(
                    producto_id=producto_id,
                    tipo_movimiento="ENTRADA",
                    cantidad=datos_lote.get("cantidad", 0),
                    motivo=f"Ingreso de lote {datos_lote.get('numero_lote', '')}",
                    usuario=usuario,
                )

            self.db_connection.commit()
            return True

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error gestionando lote: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def obtener_lotes_producto(self, producto_id):
        """
        Obtiene los lotes asociados a un producto.

        Args:
            producto_id (int): ID del producto

        Returns:
            List[Dict]: Lista de lotes
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Validar existencia de la tabla
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_lotes')
            cursor.execute(sql_verificar)
            if not cursor.fetchone():
                return []

            sql_select = """
            SELECT id, producto_id, numero_lote, fecha_vencimiento, cantidad,
                   proveedor, fecha_recepcion, serie, observaciones
            FROM lotes_inventario
            WHERE producto_id = ?
            ORDER BY fecha_recepcion DESC, fecha_vencimiento
            """

            cursor.execute(sql_select, (producto_id,))
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            lotes = []

            for row in rows:
                lote = dict(zip(columns, row))

                # Determinar si está vencido o próximo a vencer
                if lote.get("fecha_vencimiento"):
                    hoy = datetime.datetime.now().date()
                    dias_restantes = (lote["fecha_vencimiento"] - hoy).days

                    if dias_restantes < 0:
                        lote["estado_vencimiento"] = "VENCIDO"
                    elif dias_restantes <= 30:
                        lote["estado_vencimiento"] = "PROXIMO_VENCIMIENTO"
                    else:
                        lote["estado_vencimiento"] = "VIGENTE"

                    lote["dias_vencimiento"] = dias_restantes

                lotes.append(lote)

            return lotes

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo lotes: {e}")
            return []

    def generar_reporte_movimientos(self, filtros=None):
        """
        Genera un reporte detallado de movimientos con filtros avanzados.

        Args:
            filtros (dict): Filtros como fecha_inicio,
fecha_fin,
                tipo,
                categoria

        Returns:
            List[Dict]: Lista de movimientos con detalles
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if filtros:
                if filtros.get("fecha_inicio"):
                    conditions.append("m.fecha_movimiento >= ?")
                    params.append(filtros["fecha_inicio"])

                if filtros.get("fecha_fin"):
                    conditions.append("m.fecha_movimiento <= ?")
                    params.append(filtros["fecha_fin"])

                if filtros.get("tipo_movimiento"):
                    conditions.append("m.tipo_movimiento = ?")
                    params.append(filtros["tipo_movimiento"])

                if filtros.get("categoria"):
                    conditions.append("i.categoria = ?")
                    params.append(filtros["categoria"])

                if filtros.get("producto_id"):
                    conditions.append("m.inventario_id = ?")
                    params.append(filtros["producto_id"])

                if filtros.get("usuario"):
                    conditions.append("m.usuario LIKE ?")
                    params.append(f"%{filtros['usuario']}%")

            where_clause = " AND ".join(conditions)

            base_sql = """
            SELECT m.id, m.inventario_id, i.codigo, i.descripcion, i.categoria,
                   m.tipo_movimiento, m.cantidad, m.stock_anterior, m.stock_nuevo,
                   m.motivo, m.documento_referencia, m.fecha_movimiento, m.usuario,
                   i.unidad_medida, i.precio_unitario
            FROM movimientos_inventario m
            INNER JOIN inventario_perfiles i ON m.inventario_id = i.id
            WHERE """
            sql_select = (
                base_sql
                + where_clause
                + """
            ORDER BY m.fecha_movimiento DESC
            """
            )

            # Limitar resultados si no hay filtros específicos
            if len(conditions) <= 1:
        # TODO: MANUAL FIX REQUIRED - SQL Injection via concatenation
        # sql_select += " OFFSET 0 ROWS FETCH NEXT 200 ROWS ONLY"
                sql_select += " OFFSET 0 ROWS FETCH NEXT 200 ROWS ONLY"

            cursor.execute(sql_select, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            movimientos = []

            for row in rows:
                movimiento = dict(zip(columns, row))

                # Calcular valores adicionales
                if movimiento.get("precio_unitario") and \
                    movimiento.get("cantidad"):
                    movimiento["valor_total"] = float(
                        movimiento["precio_unitario"]
                    ) * float(movimiento["cantidad"])

                movimientos.append(movimiento)

            return movimientos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error generando reporte: {e}")
            return []

    def obtener_productos_proximos_vencer(self, dias_limite=30):
        """
        Obtiene productos próximos a vencerse.

        Args:
            dias_limite (int): Días límite para considerar próximos a vencer

        Returns:
            List[Dict]: Lista de productos próximos a vencer
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Validar existencia de la tabla
            sql_verificar = self.sql_manager.get_query('inventario', 'verificar_tabla_lotes')
            cursor.execute(sql_verificar)
            if not cursor.fetchone():
                return []

            fecha_limite = datetime.datetime.now().date() + datetime.timedelta(
                days=dias_limite
            )

            sql_select = """
            SELECT l.id, l.producto_id, l.numero_lote, l.fecha_vencimiento,
                   l.cantidad, l.proveedor, i.codigo, i.descripcion, i.categoria,
                   DATEDIFF(day, GETDATE(), l.fecha_vencimiento) as dias_restantes
            FROM lotes_inventario l
            INNER JOIN inventario_perfiles i ON l.producto_id = i.id
            WHERE l.fecha_vencimiento IS NOT NULL
              AND l.fecha_vencimiento <= ?
              AND l.fecha_vencimiento >= GETDATE()
            ORDER BY l.fecha_vencimiento
            """

            cursor.execute(sql_select, (fecha_limite,))
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            productos = []

            for row in rows:
                producto = dict(zip(columns, row))
                productos.append(producto)

            return productos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(
                f"[ERROR INVENTARIO] Error obteniendo productos próximos a vencer: {e}"
            )
            return []

    def generar_reporte_valoracion_inventario(self, filtros=None):
        """
        Genera un reporte de valoración del inventario.

        Args:
            filtros (dict): Filtros como categoria

        Returns:
            Dict: Datos de valoración del inventario
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            conditions = ["estado = 'ACTIVO'"]
            params = []

            if filtros:
                if filtros.get("categoria"):
                    conditions.append("categoria = ?")
                    params.append(filtros["categoria"])

            where_clause = " AND ".join(conditions)

            # Obtener valoración total
            base_valor_sql = """
            SELECT
                COUNT(*) as total_productos,
                SUM(stock_actual) as total_unidades,
                SUM(stock_actual * precio_unitario) as valor_total
            FROM inventario
            WHERE """
            sql_valor = base_valor_sql + where_clause

            cursor.execute(sql_valor, params)
            row = cursor.fetchone()

            if not row:
                return {}

            valoracion = {
                "total_productos": row[0],
                "total_unidades": row[1],
                "valor_total": float(row[2]) if row[2] else 0,
            }

            # Obtener detalle por categoría
            base_cat_sql = """
            SELECT
                categoria,
                COUNT(*) as productos,
                SUM(stock_actual) as unidades,
                SUM(stock_actual * precio_unitario) as valor
            FROM inventario
            WHERE """
            sql_categorias = (
                base_cat_sql
                + where_clause
                + """
            GROUP BY categoria
            ORDER BY valor DESC
            """
            )

            cursor.execute(sql_categorias, params)
            rows = cursor.fetchall()

            categorias = []
            for row in rows:
                categoria = {
                    "categoria": row[0] if row[0] else "Sin categoría",
                    "productos": row[1],
                    "unidades": row[2],
                    "valor": float(row[3]) if row[3] else 0,
                }
                categorias.append(categoria)

            valoracion["categorias"] = categorias

            # Calcular porcentajes
            if valoracion["valor_total"] > 0:
                for categoria in valoracion["categorias"]:
                    categoria["porcentaje"] = round(
                        (categoria["valor"] / valoracion["valor_total"]) * 100, 2
                    )

            return valoracion

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error generando valoración: {e}")
            return {}

    def obtener_productos_filtrado_avanzado(self, filtros=None):
        """
        Obtiene productos con filtros avanzados.

        SEGURIDAD: Utiliza script SQL externo y validación estricta de parámetros.

        Args:
            filtros (dict): Filtros avanzados (incluye rangos de precio, stock, etc.)

        Returns:
            List[Dict]: Lista de productos filtrados
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Usar script SQL externo como base
            if self.sql_loader_available:
                try:
                    base_query = self.script_loader.load_script(
                        "inventario/select_productos_filtrado_avanzado"
                    )
                    if not base_query:
                        raise Exception("No se pudo cargar script")

                    # Remover comentarios del script para obtener la query base
                    lines = [
                        line.strip()
                        for line in base_query.split("\n")
                        if line.strip() and not line.strip().startswith("--")
                    ]
                    base_query = " ".join(lines)

                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error con script loader: {e}")
                    # Query base de respaldo segura
                    base_query = """
                    SELECT id, codigo, descripcion, tipo as categoria, acabado as subcategoria,
                           stock as stock_actual, stock_minimo, precio as precio_unitario,
                           'unidad' as unidad_medida, ubicacion, proveedor, activo,
                           fecha_creacion, fecha_modificacion
                    FROM inventario_perfiles
                    WHERE activo = 1
                    """
            else:
                # Query base de respaldo segura
                base_query = """
                SELECT id, codigo, descripcion, tipo as categoria, acabado as subcategoria,
                       stock as stock_actual, stock_minimo, precio as precio_unitario,
                       'unidad' as unidad_medida, ubicacion, proveedor, activo,
                       fecha_creacion, fecha_modificacion
                FROM inventario_perfiles
                WHERE activo = 1
                """

            # Construir condiciones de filtros usando parámetros seguros
            additional_conditions = []
            params = []

            if filtros:
                if filtros.get("categoria"):
                    additional_conditions.append("AND tipo = ?")
                    params.append(filtros["categoria"])

                if filtros.get("subcategoria"):
                    additional_conditions.append("AND acabado = ?")
                    params.append(filtros["subcategoria"])

                if filtros.get("proveedor"):
                    additional_conditions.append("AND proveedor LIKE ?")
                    params.append(f"%{filtros['proveedor']}%")

                if filtros.get("precio_min") is not None:
                    additional_conditions.append("AND precio >= ?")
                    params.append(filtros["precio_min"])

                if filtros.get("precio_max") is not None:
                    additional_conditions.append("AND precio <= ?")
                    params.append(filtros["precio_max"])

                if filtros.get("stock_min") is not None:
                    additional_conditions.append("AND stock >= ?")
                    params.append(filtros["stock_min"])

                if filtros.get("stock_max") is not None:
                    additional_conditions.append("AND stock <= ?")
                    params.append(filtros["stock_max"])

                if filtros.get("stock_bajo"):
                    additional_conditions.append("AND stock <= stock_minimo")

                if filtros.get("busqueda"):
                    additional_conditions.append(
                        "AND (descripcion LIKE ? OR codigo LIKE ?)"
                    )
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            # Combinar query base con filtros
            full_query = base_query + " " + " ".join(additional_conditions)

            # Validación estricta del ordenamiento
            orden_sql = "ORDER BY descripcion ASC"  # Ordenamiento por defecto
            if filtros and filtros.get("ordenar_por"):
                orden = filtros["ordenar_por"]
                direccion = "DESC" if filtros.get("descendente") else "ASC"

                # Lista de campos permitidos para ordenamiento (validación estricta)
                campos_validos = {
                    "descripcion": "descripcion",
                    "codigo": "codigo",
                    "categoria": "tipo",
                    "stock_actual": "stock",
                    "precio_unitario": "precio",
                    "fecha_creacion": "fecha_creacion",
                    "fecha_modificacion": "fecha_modificacion",
                }

                if orden in campos_validos:
                    campo_real = campos_validos[orden]
                    # Validación adicional de direccion
                    if direccion not in ["ASC", "DESC"]:
                        direccion = "ASC"
                    orden_sql = f"ORDER BY {campo_real} {direccion}"

            full_query += f" {orden_sql}"

            cursor.execute(full_query, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            productos = []

            for row in rows:
                producto = dict(zip(columns, row))
                # Calcular estado del stock
                producto["estado_stock"] = self._determinar_estado_stock(producto)
                # Calcular valor total
                producto["valor_total"] = float(producto["stock_actual"]) * float(
                    producto["precio_unitario"]
                )
                productos.append(producto)

            return productos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error en filtrado avanzado: {e}")
            return []

    def generar_codigo_barra(self, producto_id):
        """
        Genera un código de barras para un producto específico.

        Args:
            producto_id (int): ID del producto

        Returns:
            bytes: Imagen del código de barras en formato PNG
        """
        try:
            producto = self.obtener_producto_por_id(producto_id)
            if not producto:
                return None

            # Se requiere la librería barcode, instalarla si no está presente
            try:
                import barcode
                from barcode.writer import ImageWriter
            except ImportError:
                logger.error("Se requiere la librería python-barcode")
                return None

            # Generar código EAN13 o CODE128 según el formato del código
            codigo = producto["codigo"].replace("-", "").strip()

            if len(codigo) == 13 and codigo.isdigit():
                # EAN-13
                ean = barcode.get("ean13", codigo, writer=ImageWriter())
            else:
                # CODE128 para cualquier otro formato
                ean = barcode.get("code128", codigo, writer=ImageWriter())

            # Generar imagen
            fp = BytesIO()
            ean.write(fp)
            fp.seek(0)

            return fp.getvalue()

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error generando código de barras: {e}")
            return None

    def actualizar_precios_masivo(self, actualizaciones, usuario="SISTEMA"):
        """
        Actualiza precios de múltiples productos en una sola operación.

        Args:
            actualizaciones (list): Lista de diccionarios con id y precio_nuevo
            usuario (str): Usuario que realiza la actualización

        Returns:
            tuple: (exitosos, fallidos)
        """
        if not self.db_connection:
            return 0, 0

        exitosos = 0
        fallidos = 0

        try:
            cursor = self.db_connection.cursor()

            for item in actualizaciones:
                try:
                    if "id" not in item or "precio_nuevo" not in item:
                        fallidos += 1
                        continue

                    producto_id = item["id"]
                    precio_nuevo = item["precio_nuevo"]

                    # Obtener precio actual para registro de cambio
                    cursor.execute(
                        self.sql_manager.get_query('inventario', 'obtener_precio_perfil'),
                        (producto_id,),
                    )
                    row = cursor.fetchone()

                    if not row:
                        fallidos += 1
                        continue

                    precio_anterior = row[0]

                    # Actualizar precio
                    cursor.execute(
                        """
                    UPDATE inventario
                    SET precio_unitario = ?,
                        fecha_modificacion = GETDATE(),
                        usuario_modificacion = ?
                    WHERE id = ?
                    """,
                        (precio_nuevo, usuario, producto_id),
                    )

                    # Registrar historial de precio si existe la tabla
                    cursor.execute(
                        self.sql_manager.get_query('inventario', 'verificar_tabla_historial_precios')
                    )
                    if cursor.fetchone():
                        cursor.execute(
                            """
                        INSERT INTO historial_precios
                        (producto_id, precio_anterior, precio_nuevo,
                         fecha_cambio, usuario, motivo)
                        VALUES (?, ?, ?, GETDATE(), ?, ?)
                        """,
                            (
                                producto_id,
                                precio_anterior,
                                precio_nuevo,
                                usuario,
                                item.get("motivo", "Actualización masiva"),
                            ),
                        )

                    exitosos += 1

                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    print(
                        f"[ERROR] Fallo en producto {item.get('id', 'desconocido')}: {e}"
                    )
                    fallidos += 1

            self.db_connection.commit()
            return exitosos, fallidos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error actualizando precios masivamente: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return exitosos, fallidos

    def exportar_datos_excel(self, filtros=None):
        """
        Prepara datos para exportación a Excel.

        Args:
            filtros (dict): Filtros para los productos

        Returns:
            List[Dict]: Lista de productos para exportar
        """
        productos = self.obtener_productos_filtrado_avanzado(filtros)

        # Agregar campos calculados útiles para reportes
        for producto in productos:
            producto["valor_total"] = (
                producto["stock_actual"] * producto["precio_unitario"]
            )

            if producto["stock_minimo"] > 0:
                producto["porcentaje_stock"] = (
                    producto["stock_actual"] / producto["stock_minimo"]
                ) * 100
            else:
                producto["porcentaje_stock"] = None

        return productos

    def reservar_material_obra(
        self, producto_id, obra_id, cantidad_reservada, usuario_id, observaciones=None
    ):
        """
        Reserva material para una obra específica.

        Args:
            producto_id (int): ID del producto
            obra_id (int): ID de la obra
            cantidad_reservada (float): Cantidad a reservar
            usuario_id (int): ID del usuario que hace la reserva
            observaciones (str): Observaciones opcionales

        Returns:
            tuple: (bool, str) - (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar stock disponible usando query segura
            disponibilidad = self._execute_secure_script(
                "inventario/select_disponibilidad_material",
                [producto_id],
                """
                SELECT i.id, i.codigo, i.descripcion, i.tipo as categoria, i.stock as stock_actual,
                       i.stock_minimo, i.precio as precio_unitario, 'unidad' as unidad_medida,
                       COALESCE(r.stock_reservado, 0) as stock_reservado,
                       (i.stock - COALESCE(r.stock_reservado, 0)) as stock_disponible
                FROM inventario_perfiles i
                LEFT JOIN (
                    SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
                    FROM reserva_materiales
                    WHERE estado = 'ACTIVA'
                    GROUP BY producto_id
                ) r ON i.id = r.producto_id
                WHERE i.id = ? AND i.activo = 1
                """,
            )

            if not disponibilidad:
                return False, "Producto no encontrado"

            producto = disponibilidad[0]
            stock_disponible = producto[9]  # stock_disponible
            descripcion = producto[2]  # descripcion

            if cantidad_reservada > stock_disponible:
                return (
                    False,
                    f"Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {cantidad_reservada}",
                )

            # Crear reserva usando script seguro
            cursor = self.db_connection.cursor()
            try:
                if self.sql_loader_available:
                    script_content = self.script_loader.load_script(
                        "inventario/insert_reserva_material"
                    )
                    if script_content:
                        cursor.execute(
                            script_content,
                            (obra_id,
producto_id,
                                cantidad_reservada,
                                usuario_id),
                        )
                    else:
                        raise Exception("Script no disponible")
                else:
                    # Query de respaldo segura
                    cursor.execute(
                        """
                        INSERT INTO reserva_materiales
                        (obra_id,
producto_id,
                            cantidad_reservada,
                            fecha_reserva,
                            estado,
                            usuario_id)
                        VALUES (?, ?, ?, GETDATE(), 'ACTIVA', ?)
                    """,
                        (obra_id,
producto_id,
                            cantidad_reservada,
                            usuario_id),
                    )

                # Registrar movimiento usando script seguro
                movimiento_params = [
                    f"INVENTARIO_RESERVA",
                    f"Reserva para obra {obra_id}: {descripcion}",
                    f"USER_{usuario_id}",
                    datetime.datetime.now().isoformat(),
                    f"Producto ID: {producto_id}, Cantidad: {cantidad_reservada}, Obra: {obra_id}",
                ]

                if self.sql_loader_available:
                    mov_script = self.script_loader.load_script(
                        "inventario/insert_movimiento"
                    )
                    if mov_script:
                        cursor.execute(mov_script, movimiento_params)
                    else:
                        # Fallback para historial
                        cursor.execute(
                            """
                            INSERT INTO historial (accion,
descripcion,
                                usuario,
                                fecha,
                                detalles)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            movimiento_params,
                        )
                else:
                    # Fallback para historial
                    cursor.execute(
                        """
                        INSERT INTO historial (accion,
descripcion,
                            usuario,
                            fecha,
                            detalles)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        movimiento_params,
                    )

            except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                logger.error(f"Error usando scripts: {e}")
                # Fallback completo con queries seguras fijas
                cursor.execute(
                    """
                    INSERT INTO reserva_materiales
                    (obra_id,
producto_id,
                        cantidad_reservada,
                        fecha_reserva,
                        estado,
                        usuario_id)
                    VALUES (?, ?, ?, GETDATE(), 'ACTIVA', ?)
                """,
                    (obra_id, producto_id, cantidad_reservada, usuario_id),
                )

                cursor.execute(
                    """
                    INSERT INTO historial (accion,
descripcion,
                        usuario,
                        fecha,
                        detalles)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    movimiento_params,
                )

            self.db_connection.commit()

            return (
                True,
                f"Material '{descripcion}' reservado correctamente para la obra",
            )

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            if self.db_connection:
                self.db_connection.connection.rollback()
            print(f"[ERROR INVENTARIO] Error reservando material: {e}")
            return False, f"Error reservando material: {e}"

    def obtener_reservas_por_obra(self, obra_id):
        """
        Obtiene todas las reservas de una obra específica.

        SEGURIDAD: Utiliza script SQL externo con parámetros seguros.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de reservas
        """
        if not self.db_connection:
            return []

        try:
            # Usar script SQL seguro
            resultado = self._execute_secure_script(
                "inventario/select_reservas_por_obra",
                [obra_id],
                """
                SELECT
                    r.id, r.obra_id, r.producto_id, r.cantidad_reservada,
                    r.fecha_reserva, r.fecha_liberacion, r.estado, r.usuario_id, r.motivo_liberacion,
                    i.codigo as producto_codigo, i.descripcion as producto_descripcion,
                    i.tipo as producto_categoria, i.precio as precio_unitario, 'unidad' as unidad_medida
                FROM reserva_materiales r
                INNER JOIN inventario_perfiles i ON r.producto_id = i.id
                WHERE r.obra_id = ?
                ORDER BY r.fecha_reserva DESC
                """,
            )

            if not resultado:
                return []

            # Convertir resultados a lista de diccionarios
            reservas = []
            for row in resultado:
                reserva = {
                    "id": row[0],
                    "obra_id": row[1],
                    "producto_id": row[2],
                    "cantidad_reservada": row[3],
                    "fecha_reserva": row[4],
                    "fecha_liberacion": row[5],
                    "estado": row[6],
                    "usuario_id": row[7],
                    "motivo_liberacion": row[8],
                    "producto_codigo": row[9],
                    "producto_descripcion": row[10],
                    "producto_categoria": row[11],
                    "precio_unitario": row[12],
                    "unidad_medida": row[13],
                }
                reservas.append(reserva)

            return reservas

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo reservas por obra: {e}")
            return []

    def obtener_reservas_por_producto(self, producto_id):
        """
        Obtiene todas las reservas de un producto específico.

        SEGURIDAD: Utiliza script SQL externo con parámetros seguros.

        Args:
            producto_id (int): ID del producto

        Returns:
            List[Dict]: Lista de reservas
        """
        if not self.db_connection:
            return []

        try:
            # Usar script SQL seguro
            resultado = self._execute_secure_script(
                "inventario/select_reservas_por_producto",
                [producto_id],
                """
                SELECT
                    r.id, r.obra_id, r.producto_id, r.cantidad_reservada,
                    r.fecha_reserva, r.fecha_liberacion, r.estado, r.usuario_id, r.motivo_liberacion,
                    o.nombre as obra_nombre, o.direccion as obra_direccion
                FROM reserva_materiales r
                LEFT JOIN obras o ON r.obra_id = o.id
                WHERE r.producto_id = ?
                ORDER BY r.fecha_reserva DESC
                """,
            )

            if not resultado:
                return []

            # Convertir resultados a lista de diccionarios
            reservas = []
            for row in resultado:
                reserva = {
                    "id": row[0],
                    "obra_id": row[1],
                    "producto_id": row[2],
                    "cantidad_reservada": row[3],
                    "fecha_reserva": row[4],
                    "fecha_liberacion": row[5],
                    "estado": row[6],
                    "usuario_id": row[7],
                    "motivo_liberacion": row[8],
                    "obra_nombre": row[9],
                    "obra_direccion": row[10],
                }
                reservas.append(reserva)

            return reservas

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo reservas por producto: {e}")
            return []

    def liberar_reserva(self, reserva_id, usuario_id, motivo=None):
        """
        Libera una reserva específica.

        SEGURIDAD: Utiliza script SQL externo con parámetros seguros.

        Args:
            reserva_id (int): ID de la reserva
            usuario_id (int): ID del usuario que libera la reserva
            motivo (str): Motivo de la liberación

        Returns:
            tuple: (bool, str) - (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos"

        try:
            # Obtener información de la reserva usando query segura
            reserva_info = self._execute_secure_script(
                None,  # No hay script específico para esta consulta
                None,
                """
                SELECT producto_id, cantidad_reservada, obra_id
                FROM reserva_materiales
                WHERE id = ? AND estado = 'ACTIVA'
                """,
            )

            if not reserva_info:
                return False, "Reserva no encontrada o ya liberada"

            producto_id, cantidad_reservada, obra_id = reserva_info[0]

            cursor = self.db_connection.cursor()

            # Actualizar estado de la reserva usando script seguro
            if self.sql_loader_available:
                try:
                    script_content = self.script_loader.load_script(
                        "inventario/update_liberar_reserva"
                    )
                    if script_content:
                        cursor.execute(
                            script_content,
                            [datetime.datetime.now().isoformat(), motivo, reserva_id],
                        )
                    else:
                        raise Exception("Script no disponible")
                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error usando script: {e}")
                    # Fallback con query segura
                    cursor.execute(
                        """
                        UPDATE reserva_materiales
                        SET estado = 'LIBERADA', fecha_liberacion = ?, motivo_liberacion = ?
                        WHERE id = ? AND estado = 'ACTIVA'
                    """,
                        [datetime.datetime.now().isoformat(), motivo, reserva_id],
                    )
            else:
                # Query de respaldo segura
                cursor.execute(
                    """
                    UPDATE reserva_materiales
                    SET estado = 'LIBERADA', fecha_liberacion = ?, motivo_liberacion = ?
                    WHERE id = ? AND estado = 'ACTIVA'
                """,
                    [datetime.datetime.now().isoformat(), motivo, reserva_id],
                )

            # Registrar movimiento usando script seguro
            movimiento_params = [
                f"INVENTARIO_LIBERACION_RESERVA",
                f"Liberación de reserva {reserva_id}: {motivo or 'Sin motivo especificado'}",
                f"USER_{usuario_id}",
                datetime.datetime.now().isoformat(),
                f"Producto ID: {producto_id}, Cantidad: {cantidad_reservada}, Obra: {obra_id}, Reserva: {reserva_id}",
            ]

            if self.sql_loader_available:
                try:
                    mov_script = self.script_loader.load_script(
                        "inventario/insert_movimiento"
                    )
                    if mov_script:
                        cursor.execute(mov_script, movimiento_params)
                    else:
                        # Fallback para historial
                        cursor.execute(
                            """
                            INSERT INTO historial (accion,
descripcion,
                                usuario,
                                fecha,
                                detalles)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            movimiento_params,
                        )
                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error usando script movimiento: {e}")
                    cursor.execute(
                        """
                        INSERT INTO historial (accion,
descripcion,
                            usuario,
                            fecha,
                            detalles)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        movimiento_params,
                    )
            else:
                # Fallback para historial
                cursor.execute(
                    """
                    INSERT INTO historial (accion,
descripcion,
                        usuario,
                        fecha,
                        detalles)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    movimiento_params,
                )

            self.db_connection.commit()

            return True, "Reserva liberada correctamente"

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            if self.db_connection:
                self.db_connection.connection.rollback()
            print(f"[ERROR INVENTARIO] Error liberando reserva: {e}")
            return False, f"Error liberando reserva: {e}"

    def obtener_disponibilidad_material(self, producto_id=None):
        """
        Obtiene la disponibilidad de materiales (stock, reservado, disponible).

        Args:
            producto_id (int, optional): ID del producto específico

        Returns:
            List[Dict]: Lista de disponibilidad de materiales
        """
        if not self.db_connection:
            return []

        try:
            self.db_connection.cursor()

            where_clause = ""
            params = []

            if producto_id:
                where_clause = "WHERE i.id = ?"
                params.append(producto_id)

            # [LOCK] Usar consulta SQL externa segura para análisis de stock
            params_query = {
                "producto_id": producto_id
            }

            resultados = self.sql_manager.execute_query(
                "analisis_stock_completo",
                params=params_query
            )

            # SQLQueryManager ya devuelve diccionarios, no necesitamos conversión
            return resultados

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo disponibilidad: {e}")
            return []

    def generar_reporte_reservas_obra(self, obra_id):
        """
        Genera un reporte completo de reservas para una obra.

        Args:
            obra_id (int): ID de la obra

        Returns:
            Dict: Reporte de reservas
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Información de la obra
            sql_obra = self.sql_manager.get_query('inventario', 'obtener_obra_info')
            cursor.execute(sql_obra, (obra_id,))
            obra_info = cursor.fetchone()

            if not obra_info:
                return {}

            obra_codigo, obra_nombre = obra_info

            # Reservas activas
            reservas_activas = self.obtener_reservas_por_obra(obra_id)

            # Cálculo de totales
            total_reservas = len(reservas_activas)
            valor_total_reservado = sum(
                r["cantidad_reservada"] * r["precio_unitario"] for r in reservas_activas
            )

            # [LOCK] Usar consulta SQL externa segura para estadísticas de categorías
            categorias = self.sql_manager.execute_query(
                "estadisticas_reservas_categoria",
                params={"obra_id": obra_id}
            )

            reporte = {
                "obra": {"id": obra_id, "codigo": obra_codigo, "nombre": obra_nombre},
                "resumen": {
                    "total_reservas": total_reservas,
                    "valor_total_reservado": valor_total_reservado,
                    "total_categorias": len(categorias),
                },
                "reservas_activas": reservas_activas,
                "por_categoria": categorias,
            }

            return reporte

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error generando reporte: {e}")
            return {}

    def obtener_estadisticas_reservas(self):
        """
        Obtiene estadísticas generales de reservas.

        Returns:
            Dict: Estadísticas de reservas
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # [LOCK] Total de reservas activas usando SQL externo
            sql = self.sql_manager.get_query('inventario', 'count_reservas_activas')
            cursor = self.db_connection.cursor()
            cursor.execute(sql)
            estadisticas["total_reservas_activas"] = cursor.fetchone()[0]

            # [LOCK] Valor total reservado usando SQL externo
            sql = self.sql_manager.get_query('inventario', 'valor_total_reservas_activas')
            cursor.execute(sql)
            resultado = cursor.fetchone()[0]
            estadisticas["valor_total_reservado"] = resultado if resultado else 0

            # [LOCK] Obras con reservas usando SQL externo
            sql = self.sql_manager.get_query('inventario', 'count_obras_con_reservas')
            cursor.execute(sql)
            estadisticas["obras_con_reservas"] = cursor.fetchone()[0]

            # [LOCK] Productos con reservas usando SQL externo
            sql = self.sql_manager.get_query('inventario', 'count_productos_con_reservas')
            cursor.execute(sql)
            estadisticas["productos_con_reservas"] = cursor.fetchone()[0]

            return estadisticas

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            print(f"[ERROR INVENTARIO] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_obras_activas(self):
        """Obtiene las obras activas para el selector."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, codigo, nombre, estado, fecha_inicio, fecha_fin_estimada
                FROM obras
                WHERE estado = 'ACTIVA' OR estado = 'EN_PROCESO'
                ORDER BY fecha_inicio DESC
            """)

            obras = []
            for row in cursor.fetchall():
                obras.append(
                    {
                        "id": row[0],
                        "codigo": row[1],
                        "nombre": row[2],
                        "estado": row[3],
                        "fecha_inicio": row[4],
                        "fecha_fin_estimada": row[5],
                    }
                )

            return obras

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener obras activas: {str(e)}")
            return []

    def obtener_categorias(self):
        """Obtiene las categorías disponibles."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT categoria
                FROM inventario_perfiles
                WHERE categoria IS NOT NULL
                ORDER BY categoria
            """)

            categorias = []
            for row in cursor.fetchall():
                categorias.append(row[0])

            return categorias

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener categorías: {str(e)}")
            return []

    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales del inventario."""
        try:
            cursor = self.db_connection.cursor()

            # Total de productos
            sql_activos = self.sql_manager.get_query('inventario', 'contar_productos_activos')
            cursor.execute(sql_activos)
            total_productos = cursor.fetchone()[0]

            # Valor total
            cursor.execute("""
                SELECT SUM(stock_actual * precio_unitario)
                FROM inventario_perfiles
                WHERE activo = 1
            """)
            valor_total = cursor.fetchone()[0] or 0.0

            # Stock bajo
            cursor.execute("""
                SELECT COUNT(*)
                FROM inventario_perfiles
                WHERE stock_actual <= stock_minimo AND activo = 1
            """)
            stock_bajo = cursor.fetchone()[0]

            # Productos activos
            sql_activos = self.sql_manager.get_query('inventario', 'contar_productos_activos')
            cursor.execute(sql_activos)
            productos_activos = cursor.fetchone()[0]

            return {
                "total_productos": total_productos,
                "valor_total": valor_total,
                "stock_bajo": stock_bajo,
                "productos_activos": productos_activos,
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener estadísticas generales: {str(e)}")
            return {
                "total_productos": 0,
                "valor_total": 0.0,
                "stock_bajo": 0,
                "productos_activos": 0,
            }

    def buscar_productos(self, filtros):
        """Busca productos según los filtros especificados."""
        try:
            cursor = self.db_connection.cursor()

            # [LOCK] Usar consulta SQL externa segura para búsqueda de productos
            sql = self.sql_manager.get_query('inventario', 'buscar_productos_con_stock')
            params = {
                "busqueda": filtros.get("busqueda"),
                "categoria": filtros.get("categoria")
            }

            cursor.execute(sql, params)

            productos = []
            for row in cursor.fetchall():
                productos.append(
                    {
                        "id": row[0],
                        "codigo": row[1],
                        "descripcion": row[2],
                        "categoria": row[3],
                        "stock_actual": row[4],
                        "stock_minimo": row[5],
                        "precio_unitario": row[6],
                        "unidad_medida": row[7],
                        "activo": row[8],
                        "fecha_actualizacion": row[9],
                        "stock_reservado": row[10],
                        "estado_stock": row[11],
                    }
                )

            return productos

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al buscar productos: {str(e)}")
            return []

    def obtener_estadisticas_reservas(self, obra_id):
        """Obtiene estadísticas de reservas para una obra específica."""
        try:
            cursor = self.db_connection.cursor()

            # Total de reservas
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM reservas_inventario
                WHERE obra_id = ? AND estado = 'ACTIVA'
            """,
                (obra_id,),
            )
            total_reservas = cursor.fetchone()[0]

            # Valor reservado
            cursor.execute(
                """
                SELECT SUM(r.cantidad_reservada * i.precio_unitario)
                FROM reservas_inventario r
                JOIN inventario_perfiles i ON r.producto_id = i.id
                WHERE r.obra_id = ? AND r.estado = 'ACTIVA'
            """,
                (obra_id,),
            )
            valor_reservado = cursor.fetchone()[0] or 0.0

            # Productos reservados
            cursor.execute(
                """
                SELECT COUNT(DISTINCT producto_id)
                FROM reservas_inventario
                WHERE obra_id = ? AND estado = 'ACTIVA'
            """,
                (obra_id,),
            )
            productos_reservados = cursor.fetchone()[0]

            # Stock disponible total
            cursor.execute("""
                SELECT SUM(i.stock_actual - COALESCE(r.stock_reservado, 0))
                FROM inventario_perfiles i
                LEFT JOIN (
                    SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
                    FROM reservas_inventario
                    WHERE estado = 'ACTIVA'
                    GROUP BY producto_id
                ) r ON i.id = r.producto_id
                WHERE i.activo = 1
            """)
            stock_disponible = cursor.fetchone()[0] or 0

            return {
                "total_reservas": total_reservas,
                "valor_reservado": valor_reservado,
                "productos_reservados": productos_reservados,
                "stock_disponible": stock_disponible,
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener estadísticas de reservas: {str(e)}")
            return {
                "total_reservas": 0,
                "valor_reservado": 0.0,
                "productos_reservados": 0,
                "stock_disponible": 0,
            }

    def obtener_productos_disponibles_para_reserva(self):
        """
        Obtiene productos que tienen stock disponible para reserva.

        SEGURIDAD: Utiliza script SQL externo con parámetros seguros.

        Returns:
            list: Lista de productos disponibles para reserva
        """
        # Verificar conexión a base de datos
        if not self.db_connection:
            logger.error("Sin conexión a base de datos en obtener_productos_disponibles_para_reserva")
            return []

        try:
            cursor = self.db_connection.cursor()

            # Usar script SQL externo seguro
            if self.sql_loader_available:
                try:
                    script_content = self.script_loader.load_script(
                        "inventario/select_productos_disponibles_reserva"
                    )
                    if script_content:
                        cursor.execute(script_content)
                    else:
                        logger.warning("No se pudo cargar script, usando consulta de respaldo")
                        # Consulta de respaldo parameterizada
                        cursor.execute("""
                            SELECT
                                i.id, i.codigo, i.descripcion, i.tipo as categoria, i.stock as stock_actual,
                                i.precio as precio_unitario, 'unidad' as unidad_medida,
                                COALESCE(r.stock_reservado, 0) as stock_reservado,
                                (i.stock - COALESCE(r.stock_reservado, 0)) as stock_disponible
                            FROM inventario_perfiles i
                            LEFT JOIN (
                                SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
                                FROM reserva_materiales
                                WHERE estado = 'ACTIVA'
                                GROUP BY producto_id
                            ) r ON i.id = r.producto_id
                            WHERE i.activo = 1
                                AND (i.stock - COALESCE(r.stock_reservado, 0)) > 0
                            ORDER BY i.codigo
                        """)
                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error con script loader: {e}")
                    # Consulta de respaldo parameterizada
                    cursor.execute("""
                        SELECT
                            i.id, i.codigo, i.descripcion, i.tipo as categoria, i.stock as stock_actual,
                            i.precio as precio_unitario, 'unidad' as unidad_medida,
                            COALESCE(r.stock_reservado, 0) as stock_reservado,
                            (i.stock - COALESCE(r.stock_reservado, 0)) as stock_disponible
                        FROM inventario_perfiles i
                        LEFT JOIN (
                            SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
                            FROM reserva_materiales
                            WHERE estado = 'ACTIVA'
                            GROUP BY producto_id
                        ) r ON i.id = r.producto_id
                        WHERE i.activo = 1
                            AND (i.stock - COALESCE(r.stock_reservado, 0)) > 0
                        ORDER BY i.codigo
                    """)
            else:
                # Consulta de respaldo parameterizada cuando no hay script loader
                cursor.execute("""
                    SELECT
                        i.id, i.codigo, i.descripcion, i.tipo as categoria, i.stock as stock_actual,
                        i.precio as precio_unitario, 'unidad' as unidad_medida,
                        COALESCE(r.stock_reservado, 0) as stock_reservado,
                        (i.stock - COALESCE(r.stock_reservado, 0)) as stock_disponible
                    FROM inventario_perfiles i
                    LEFT JOIN (
                        SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
                        FROM reserva_materiales
                        WHERE estado = 'ACTIVA'
                        GROUP BY producto_id
                    ) r ON i.id = r.producto_id
                    WHERE i.activo = 1
                        AND (i.stock - COALESCE(r.stock_reservado, 0)) > 0
                    ORDER BY i.codigo
                """)

            # Procesar resultados
            productos = []
            for row in cursor.fetchall():
                producto = {
                    "id": row[0],
                    "codigo": row[1],
                    "descripcion": row[2],
                    "categoria": row[3],
                    "stock_actual": row[4],
                    "precio_unitario": row[5],
                    "unidad_medida": row[6],
                    "stock_reservado": row[7],
                    "stock_disponible": row[8],
                }
                productos.append(producto)

            return productos
        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error en obtener_productos_disponibles_para_reserva: {e}")
            return []

    def obtener_info_obra(self, obra_id):
        """Obtiene información de una obra específica."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT id, codigo, nombre, descripcion, estado,
                       fecha_inicio, fecha_fin_estimada, cliente, responsable
                FROM obras
                WHERE id = ?
            """,
                (obra_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "codigo": row[1],
                    "nombre": row[2],
                    "descripcion": row[3],
                    "estado": row[4],
                    "fecha_inicio": row[5],
                    "fecha_fin_estimada": row[6],
                    "cliente": row[7],
                    "responsable": row[8],
                }

            return None

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener información de obra: {str(e)}")
            return None

    def obtener_detalle_disponibilidad(self, producto_id):
        """Obtiene el detalle de disponibilidad de un producto."""
        try:
            cursor = self.db_connection.cursor()

            # [LOCK] Información del producto usando SQL externo
            sql = self.sql_manager.get_query('inventario', 'detalle_disponibilidad_producto')
            cursor.execute(sql, {"producto_id": producto_id})

            producto = cursor.fetchone()
            if not producto:
                return None

            # Reservas activas
            cursor.execute(
                """
                SELECT COUNT(*), SUM(cantidad_reservada), SUM(cantidad_reservada * ?)
                FROM reservas_inventario
                WHERE producto_id = ? AND estado = 'ACTIVA'
            """,
                (producto[2], producto_id),
            )

            reservas = cursor.fetchone()

            stock_total = producto[0]
            stock_reservado = reservas[1] or 0
            stock_disponible = stock_total - stock_reservado

            return {
                "stock_total": stock_total,
                "stock_reservado": stock_reservado,
                "stock_disponible": stock_disponible,
                "stock_minimo": producto[1],
                "reservas_activas": reservas[0] or 0,
                "valor_reservado": reservas[2] or 0.0,
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error al obtener detalle de disponibilidad: {str(e)}")
            return None

    def _get_productos_demo(self):
        """Datos demo para cuando no hay conexión a base de datos."""
        return [
            {
                "id": 1,
                "codigo": "PER001",
                "descripcion": "Perfil de Aluminio 20x20",
                "categoria": "Perfiles",
                "subcategoria": "Aluminio",
                "stock_actual": 150,
                "stock_minimo": 50,
                "stock_maximo": 200,
                "precio_unitario": 25.50,
                "precio_promedio": 25.50,
                "ubicacion": "Bodega A-1",
                "proveedor": "Aluminios del Valle",
                "unidad_medida": "metros",
                "estado": "ACTIVO",
                "fecha_creacion": "2024-01-15",
                "fecha_modificacion": "2024-01-15",
                "observaciones": "Perfil estándar para ventanas",
                "codigo_qr": "QR001",
                "stock_disponible": 120,
                "stock_reservado": 30,
                "estado_stock": "NORMAL",
            },
            {
                "id": 2,
                "codigo": "VID001",
                "descripcion": "Vidrio Templado 6mm",
                "categoria": "Vidrios",
                "subcategoria": "Templado",
                "stock_actual": 25,
                "stock_minimo": 10,
                "stock_maximo": 50,
                "precio_unitario": 45.00,
                "precio_promedio": 45.00,
                "ubicacion": "Bodega B-2",
                "proveedor": "Cristales Modernos",
                "unidad_medida": "metros²",
                "estado": "ACTIVO",
                "fecha_creacion": "2024-01-16",
                "fecha_modificacion": "2024-01-16",
                "observaciones": "Vidrio para puertas",
                "codigo_qr": "QR002",
                "stock_disponible": 20,
                "stock_reservado": 5,
                "estado_stock": "NORMAL",
            },
            {
                "id": 3,
                "codigo": "HER001",
                "descripcion": "Bisagra Pesada 4x4",
                "categoria": "Herrajes",
                "subcategoria": "Bisagras",
                "stock_actual": 8,
                "stock_minimo": 20,
                "stock_maximo": 100,
                "precio_unitario": 15.75,
                "precio_promedio": 15.75,
                "ubicacion": "Bodega C-1",
                "proveedor": "Herrajes Industriales",
                "unidad_medida": "unidades",
                "estado": "ACTIVO",
                "fecha_creacion": "2024-01-17",
                "fecha_modificacion": "2024-01-17",
                "observaciones": "Stock bajo - reponer",
                "codigo_qr": "QR003",
                "stock_disponible": 8,
                "stock_reservado": 0,
                "estado_stock": "BAJO",
            },
            {
                "id": 4,
                "codigo": "SEL001",
                "descripcion": "Sellante Silicona Transparente",
                "categoria": "Sellantes",
                "subcategoria": "Silicona",
                "stock_actual": 0,
                "stock_minimo": 5,
                "stock_maximo": 30,
                "precio_unitario": 8.50,
                "precio_promedio": 8.50,
                "ubicacion": "Bodega D-1",
                "proveedor": "Químicos Especiales",
                "unidad_medida": "tubos",
                "estado": "ACTIVO",
                "fecha_creacion": "2024-01-18",
                "fecha_modificacion": "2024-01-18",
                "observaciones": "Agotado - pedido urgente",
                "codigo_qr": "QR004",
                "stock_disponible": 0,
                "stock_reservado": 0,
                "estado_stock": "AGOTADO",
            },
        ]

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de la tabla principal.

        SEGURIDAD: Utiliza script SQL externo y validación estricta de filtros.

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filtros: Filtros adicionales a aplicar

        Returns:
            tuple: (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0

            cursor = self.db_connection.cursor()

            # Usar script SQL externo para paginación
            if self.sql_loader_available:
                try:
                    paginated_script = self.script_loader.load_script(
                        "inventario/select_productos_paginados"
                    )
                    if paginated_script:
                        # Remover comentarios del script
                        lines = [
                            line.strip()
                            for line in paginated_script.split("\n")
                            if line.strip() and \
                                not line.strip().startswith("--")
                        ]
                        base_paginated_query = " ".join(lines)
                    else:
                        raise Exception("No se pudo cargar script de paginación")
                except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                    logger.error(f"Error cargando script paginados: {e}")
                    # Query de respaldo
                    base_paginated_query = """
                        SELECT id, codigo, descripcion, tipo as categoria, acabado as subcategoria,
                               stock as stock_actual, stock_minimo, precio as precio_unitario,
                               'unidad' as unidad_medida, ubicacion, proveedor, activo,
                               fecha_creacion, fecha_modificacion
                        FROM inventario_perfiles
                        WHERE activo = 1
                        ORDER BY id DESC
                        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                    """
            else:
                # Query de respaldo
                base_paginated_query = """
                    SELECT id, codigo, descripcion, tipo as categoria, acabado as subcategoria,
                           stock as stock_actual, stock_minimo, precio as precio_unitario,
                           'unidad' as unidad_medida, ubicacion, proveedor, activo,
                           fecha_creacion, fecha_modificacion
                    FROM inventario_perfiles
                    WHERE activo = 1
                    ORDER BY id DESC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """

            # Query de conteo
            count_query = self._get_count_query()

            # Aplicar filtros seguros si existen
            additional_conditions = []
            params = []

            if filtros:
                # Validación estricta de campos permitidos para filtros
                campos_permitidos = {
                    "codigo",
                    "descripcion",
                    "tipo",
                    "acabado",
                    "proveedor",
                }

                for campo, valor in filtros.items():
                    if valor and campo in campos_permitidos:
                        # Mapear campos a nombres reales de la tabla
                        campo_real = campo
                        if campo == "categoria":
                            campo_real = "tipo"
                        elif campo == "subcategoria":
                            campo_real = "acabado"

                        additional_conditions.append(f"AND {campo_real} LIKE ?")
                        params.append(f"%{valor}%")

            # Construir query completa para conteo
            if additional_conditions:
                full_count_query = count_query + " " + " ".join(additional_conditions)
            else:
                full_count_query = count_query

            # Obtener total de registros
            cursor.execute(full_count_query, params)
            total_registros = cursor.fetchone()[0]

            # Construir query completa para datos paginados
            if additional_conditions:
                # Insertar condiciones adicionales antes del ORDER BY
                parts = base_paginated_query.split("ORDER BY")
                if len(parts) == 2:
                    full_paginated_query = f"{parts[0]} {' '.join(additional_conditions)} ORDER BY {parts[1]}"
                else:
                    full_paginated_query = (
                        base_paginated_query + " " + " ".join(additional_conditions)
                    )
            else:
                full_paginated_query = base_paginated_query

            # Obtener datos paginados
            cursor.execute(full_paginated_query, params + [offset, limit])

            datos = []
            for row in cursor.fetchall():
                datos.append(self._row_to_dict(row, cursor.description))

            return datos, total_registros

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error obteniendo datos paginados: {e}")
            return [], 0

    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _, total = self.obtener_datos_paginados(offset=0,
                                                   limit=1,
                                                   filtros=filtros)
            return total
        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"Error obteniendo total de registros: {e}")
            return 0

    def _get_base_query(self):
        """Obtiene la query base para paginación usando scripts SQL seguros."""
        if self.sql_loader_available:
            try:
                script_content = self.script_loader.load_script(
                    "inventario/select_base_paginacion"
                )
                if script_content:
                    return script_content.strip()
            except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                logger.error(f"Error cargando script base: {e}")

        # Query de respaldo segura usando tabla fija
        return self.sql_manager.get_query('inventario', 'obtener_reportes_inventario')

    def _get_count_query(self):
        """Obtiene la query de conteo usando scripts SQL seguros."""
        if self.sql_loader_available:
            try:
                script_content = self.script_loader.load_script(
                    "inventario/count_base_paginacion"
                )
                if script_content:
                    return script_content.strip()
            except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
                logger.error(f"Error cargando script count: {e}")

        # Query de respaldo segura usando tabla fija
        return self.sql_manager.get_query('inventario', 'contar_perfiles_activos')

    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}

    def obtener_productos_paginados_inicial(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros=None,
        orden: str = "descripcion ASC",
    ):
        """
        Obtiene productos con paginación sin autenticación para carga inicial.
        Usa el ConsultasManager para obtener datos reales de la base de datos.
        """
        if self.consultas_manager:
            # Usar ConsultasManager para obtener datos reales
            return self.consultas_manager.obtener_productos_paginados_inicial(
                offset, limit, filtros, orden
            )
        else:
            # Fallback si no hay ConsultasManager
            logger.warning("ConsultasManager no disponible, usando datos de ejemplo")
            return {
                "items": [
                    {
                        "id": 1,
                        "codigo": "PROD001",
                        "descripcion": "Producto de ejemplo 1",
                        "categoria": "Categoria A",
                        "stock": 50,
                        "precio": 100.0,
                    },
                    {
                        "id": 2,
                        "codigo": "PROD002",
                        "descripcion": "Producto de ejemplo 2",
                        "categoria": "Categoria B",
                        "stock": 30,
                        "precio": 150.0,
                    },
                ],
                "total": 2,
                "offset": offset,
                "limit": limit,
            }

    # ===========================================
    # MÉTODOS FALLBACK PARA COMPATIBILIDAD
    # ===========================================

    def _crear_producto_fallback(self,
datos_producto: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Método fallback para crear producto cuando los submódulos no están disponibles."""
        return {
            'success': False,
            'error': 'Submódulos no disponibles. Funcionalidad limitada.',
            'producto_id': None
        }

    def _obtener_producto_por_codigo_fallback(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Método fallback para obtener producto por código."""
        logger.warning(f"Función obtener_producto_por_codigo no disponible para código: {codigo}")
        return None

    def _actualizar_stock_fallback(self, producto_id: int, nuevo_stock: Union[int, float],
                                 razon: str = "Ajuste manual") -> Dict[str, Any]:
        """Método fallback para actualizar stock."""
        return {
            'success': False,
            'error': 'Submódulos no disponibles. No se puede actualizar stock.',
            'stock_anterior': 0,
            'stock_nuevo': nuevo_stock,
            'diferencia': 0
        }

    def _registrar_movimiento_fallback(self,
datos_movimiento: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Método fallback para registrar movimiento."""
        return {
            'success': False,
            'error': 'Submódulos no disponibles. No se puede registrar movimiento.'
        }

    def _crear_reserva_fallback(self,
datos_reserva: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Método fallback para crear reserva."""
        return {
            'success': False,
            'error': 'Submódulos no disponibles. No se puede crear reserva.',
            'reserva_id': None
        }

    def _generar_reporte_fallback(self, tipo_reporte: str, filtros: Optional[Dict] = None,
                                formato: str = 'DICT') -> Dict[str, Any]:
        """Método fallback para generar reportes."""
        return {
            'success': False,
            'error': f'Submódulos no disponibles. No se puede generar reporte: {tipo_reporte}',
            'data': None
        }

    def _obtener_categorias_fallback(self, incluir_estadisticas: bool = False) -> List[Dict[str, Any]]:
        """Método fallback para obtener categorías."""
        # Devolver categorías básicas por defecto
        categorias_default = [
            {'categoria': 'GENERAL', 'total_productos': 0},
            {'categoria': 'HERRAMIENTAS', 'total_productos': 0},
            {'categoria': 'MATERIALES', 'total_productos': 0},
            {'categoria': 'SERVICIOS', 'total_productos': 0},
            {'categoria': 'INSUMOS', 'total_productos': 0},
            {'categoria': 'EQUIPOS', 'total_productos': 0},
            {'categoria': 'CONSUMIBLES', 'total_productos': 0},
            {'categoria': 'REPUESTOS', 'total_productos': 0}
        ]

        if incluir_estadisticas:
            for categoria in categorias_default:
                categoria.update({
                    'total_stock': 0,
                    'valor_total_categoria': 0,
                    'precio_promedio': 0,
                    'precio_minimo': 0,
                    'precio_maximo': 0,
                    'productos_sin_stock': 0,
                    'productos_stock_bajo': 0,
                    'porcentaje_sin_stock': 0,
                    'porcentaje_stock_bajo': 0
                })

        return categorias_default
