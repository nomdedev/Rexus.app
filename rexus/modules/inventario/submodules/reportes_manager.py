"""
Reportes Manager - Generación de reportes y estadísticas del inventario
Refactorizado de InventarioModel para mejor mantenibilidad

Responsabilidades:
- Generación de reportes de inventario
- Estadísticas de movimientos y stock
- Análisis de tendencias y patrones
- Reportes de productos críticos
- Exportación de datos en diferentes formatos
- Dashboards y métricas KPI
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal, InvalidOperation
import json

# Configurar logging
logger = logging.getLogger(__name__)

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback al script loader
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            # Construir nombre del script sin extensión
            script_name = filename.replace(".sql", "")
            return self.sql_loader(script_name)

        def execute_query(self, query, params=None):
            # Placeholder para compatibilidad
            return None

# DataSanitizer unificado - Usar sistema unificado de sanitización
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer as DataSanitizer
except ImportError:
    try:
        from rexus.utils.data_sanitizer import DataSanitizer
    except ImportError:
        # Fallback seguro
        class DataSanitizer:
            def sanitize_dict(self, data):
                """Sanitiza un diccionario de datos de forma segura."""
                if not isinstance(data, dict):
                    return {}
                
                sanitized = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        # Sanitización básica de strings
                        sanitized[key] = str(value).strip()
                    else:
                        sanitized[key] = value
                return sanitized

            def sanitize_text(self, text):
                """Sanitiza texto de forma segura."""
                return str(text).strip() if text else ""

# Importar utilidades base si están disponibles
try:
    from .base_utilities import BaseUtilities, TABLA_INVENTARIO, TABLA_MOVIMIENTOS, TABLA_RESERVAS
    BASE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Error importando utilidades base: {e}")
    BASE_AVAILABLE = False
    BaseUtilities = None
    TABLA_INVENTARIO = "inventario_perfiles"
    TABLA_MOVIMIENTOS = "historial"
    TABLA_RESERVAS = "reserva_materiales"


class ReportesManager:
    """Manager especializado para generación de reportes y estadísticas."""
    
    # Tipos de reportes disponibles
    TIPOS_REPORTE = {
        'STOCK_ACTUAL': 'Reporte de Stock Actual',
        'MOVIMIENTOS': 'Reporte de Movimientos',
        'RESERVAS': 'Reporte de Reservas',
        'PRODUCTOS_CRITICOS': 'Productos con Stock Crítico',
        'VALORACION_INVENTARIO': 'Valoración de Inventario',
        'ANALISIS_ABC': 'Análisis ABC de Productos',
        'TENDENCIAS': 'Análisis de Tendencias',
        'KPI_DASHBOARD': 'Dashboard de KPIs'
    }
    
    # Formatos de exportación soportados
    FORMATOS_EXPORT = {
        'JSON': 'json',
        'CSV': 'csv',
        'DICT': 'dict'
    }
    
    def __init__(self, db_connection=None):
        """
        Inicializa el manager de reportes.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.data_sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/inventario/reportes"
        self.logger = logging.getLogger(__name__)
        
        # Inicializar utilidades base si están disponibles
        if BASE_AVAILABLE and db_connection:
            self.base_utils = BaseUtilities(db_connection)
        else:
            self.base_utils = None
            logger.warning("Utilidades base no disponibles en ReportesManager")
    
    def _validar_conexion(self) -> bool:
        """Valida la conexión a la base de datos."""
        if not self.db_connection:
            self.logger.error("Sin conexión a base de datos")
            return False
        
        if self.base_utils and hasattr(self.base_utils, 'validar_conexion_db'):
            return self.base_utils.validar_conexion_db()
        
        # Validación básica como fallback
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            self.logger.error(f"Error validando conexión: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_stock_actual(self, filtros: Optional[Dict[str, Any]] = None, 
                                   formato: str = 'DICT') -> Dict[str, Any]:
        """
        Genera reporte completo del stock actual de todos los productos.
        
        Args:
            filtros: Filtros opcionales (categoria, proveedor, etc.)
            formato: Formato de salida
            
        Returns:
            Dict con el reporte de stock
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            cursor = self.db_connection.cursor()
            
            # Query base para stock actual
            query = f"""
                SELECT 
                    i.id, i.codigo, i.descripcion, i.categoria,
                    i.precio_unitario, i.stock_actual, i.stock_minimo, i.stock_maximo,
                    i.proveedor, i.unidad_medida, i.ubicacion,
                    i.fecha_creacion, i.fecha_modificacion,
                    -- Calcular estado de stock
                    CASE 
                        WHEN i.stock_actual = 0 THEN 'CRITICO'
                        WHEN i.stock_actual <= i.stock_minimo THEN 'BAJO'
                        WHEN i.stock_actual >= i.stock_maximo THEN 'EXCESO'
                        ELSE 'NORMAL'
                    END as estado_stock,
                    -- Calcular valor total
                    (i.stock_actual * i.precio_unitario) as valor_total,
                    -- Obtener stock reservado
                    ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0) as stock_reservado,
                    -- Calcular stock disponible
                    (i.stock_actual - ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0)) as stock_disponible
                FROM {TABLA_INVENTARIO} i
                WHERE i.activo = 1
            """
            
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('categoria'):
                    query += " AND i.categoria = ?"
                    params.append(self.data_sanitizer.sanitize_text(filtros['categoria']))
                
                if filtros.get('proveedor'):
                    query += " AND i.proveedor LIKE ?"
                    params.append(f"%{self.data_sanitizer.sanitize_text(filtros['proveedor'])}%")
                
                if filtros.get('estado_stock'):
                    estado_filtro = filtros['estado_stock']
                    if estado_filtro == 'CRITICO':
                        query += " AND i.stock_actual = 0"
                    elif estado_filtro == 'BAJO':
                        query += " AND i.stock_actual > 0 AND i.stock_actual <= i.stock_minimo"
                    elif estado_filtro == 'EXCESO':
                        query += " AND i.stock_actual >= i.stock_maximo"
                    elif estado_filtro == 'NORMAL':
                        query += " AND i.stock_actual > i.stock_minimo AND i.stock_actual < i.stock_maximo"
                
                if filtros.get('codigo_like'):
                    query += " AND i.codigo LIKE ?"
                    params.append(f"%{self.data_sanitizer.sanitize_text(filtros['codigo_like'])}%")
                
                if filtros.get('descripcion_like'):
                    query += " AND i.descripcion LIKE ?"
                    params.append(f"%{self.data_sanitizer.sanitize_text(filtros['descripcion_like'])}%")
            
            query += " ORDER BY i.categoria, i.codigo"
            
            cursor.execute(query, params)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            cursor.close()
            
            # Procesar resultados
            productos = []
            resumen = {
                'total_productos': 0,
                'valor_total_inventario': 0,
                'productos_criticos': 0,
                'productos_bajo_stock': 0,
                'productos_exceso': 0,
                'productos_normales': 0
            }
            
            for fila in filas:
                producto = dict(zip(columnas, fila))
                productos.append(producto)
                
                # Actualizar resumen
                resumen['total_productos'] += 1
                resumen['valor_total_inventario'] += float(producto.get('valor_total', 0) or 0)
                
                estado = producto.get('estado_stock', 'NORMAL')
                if estado == 'CRITICO':
                    resumen['productos_criticos'] += 1
                elif estado == 'BAJO':
                    resumen['productos_bajo_stock'] += 1
                elif estado == 'EXCESO':
                    resumen['productos_exceso'] += 1
                else:
                    resumen['productos_normales'] += 1
            
            # Construir reporte final
            reporte = {
                'tipo_reporte': 'STOCK_ACTUAL',
                'fecha_generacion': datetime.now().isoformat(),
                'filtros_aplicados': filtros or {},
                'resumen': resumen,
                'productos': productos,
                'total_registros': len(productos)
            }
            
            return {
                'success': True,
                'data': self._formatear_reporte(reporte, formato)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de stock actual: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_movimientos(self, fecha_desde: Optional[str] = None,
                                  fecha_hasta: Optional[str] = None,
                                  producto_id: Optional[int] = None,
                                  tipo_movimiento: Optional[str] = None,
                                  formato: str = 'DICT') -> Dict[str, Any]:
        """
        Genera reporte de movimientos de inventario en un período específico.
        
        Args:
            fecha_desde: Fecha inicio del período (YYYY-MM-DD)
            fecha_hasta: Fecha fin del período (YYYY-MM-DD)
            producto_id: Filtrar por producto específico
            tipo_movimiento: Filtrar por tipo de movimiento
            formato: Formato de salida
            
        Returns:
            Dict con el reporte de movimientos
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            # Validar fechas
            if not fecha_desde:
                fecha_desde = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not fecha_hasta:
                fecha_hasta = datetime.now().strftime('%Y-%m-%d')
            
            cursor = self.db_connection.cursor()
            
            # Query para obtener movimientos con información del producto
            query = f"""
                SELECT 
                    m.id, m.producto_id, m.tipo_movimiento, m.cantidad,
                    m.stock_anterior, m.stock_posterior, m.fecha_movimiento,
                    m.observaciones, m.usuario, m.obra_id,
                    p.codigo, p.descripcion, p.categoria, p.unidad_medida,
                    p.precio_unitario,
                    -- Calcular valor del movimiento
                    (ABS(m.cantidad) * p.precio_unitario) as valor_movimiento,
                    o.nombre as obra_nombre
                FROM {TABLA_MOVIMIENTOS} m
                INNER JOIN {TABLA_INVENTARIO} p ON m.producto_id = p.id
                LEFT JOIN obras o ON m.obra_id = o.id
                WHERE m.fecha_movimiento >= ? AND m.fecha_movimiento <= ?
            """
            
            params = [fecha_desde + ' 00:00:00', fecha_hasta + ' 23:59:59']
            
            # Aplicar filtros adicionales
            if producto_id:
                query += " AND m.producto_id = ?"
                params.append(producto_id)
            
            if tipo_movimiento:
                query += " AND m.tipo_movimiento = ?"
                params.append(self.data_sanitizer.sanitize_text(tipo_movimiento))
            
            query += " ORDER BY m.fecha_movimiento DESC"
            
            cursor.execute(query, params)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            
            # Query para estadísticas agregadas
            query_stats = f"""
                SELECT 
                    m.tipo_movimiento,
                    COUNT(*) as cantidad_movimientos,
                    SUM(ABS(m.cantidad)) as cantidad_total,
                    SUM(ABS(m.cantidad) * p.precio_unitario) as valor_total
                FROM {TABLA_MOVIMIENTOS} m
                INNER JOIN {TABLA_INVENTARIO} p ON m.producto_id = p.id
                WHERE m.fecha_movimiento >= ? AND m.fecha_movimiento <= ?
            """
            
            params_stats = [fecha_desde + ' 00:00:00', fecha_hasta + ' 23:59:59']
            
            if producto_id:
                query_stats += " AND m.producto_id = ?"
                params_stats.append(producto_id)
                
            if tipo_movimiento:
                query_stats += " AND m.tipo_movimiento = ?"
                params_stats.append(tipo_movimiento)
            
            query_stats += " GROUP BY m.tipo_movimiento"
            
            cursor.execute(query_stats, params_stats)
            stats_filas = cursor.fetchall()
            cursor.close()
            
            # Procesar movimientos
            movimientos = []
            for fila in filas:
                movimiento = dict(zip(columnas, fila))
                movimientos.append(movimiento)
            
            # Procesar estadísticas
            estadisticas_por_tipo = {}
            total_movimientos = 0
            total_valor = 0
            
            for stat_fila in stats_filas:
                tipo, cantidad, cantidad_total, valor_total = stat_fila
                estadisticas_por_tipo[tipo] = {
                    'cantidad_movimientos': cantidad,
                    'cantidad_total': float(cantidad_total or 0),
                    'valor_total': float(valor_total or 0)
                }
                total_movimientos += cantidad
                total_valor += float(valor_total or 0)
            
            # Construir reporte final
            reporte = {
                'tipo_reporte': 'MOVIMIENTOS',
                'fecha_generacion': datetime.now().isoformat(),
                'periodo': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                },
                'filtros_aplicados': {
                    'producto_id': producto_id,
                    'tipo_movimiento': tipo_movimiento
                },
                'resumen': {
                    'total_movimientos': total_movimientos,
                    'total_valor_movido': total_valor,
                    'estadisticas_por_tipo': estadisticas_por_tipo
                },
                'movimientos': movimientos,
                'total_registros': len(movimientos)
            }
            
            return {
                'success': True,
                'data': self._formatear_reporte(reporte, formato)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de movimientos: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    @auth_required
    @permission_required("view_reportes")
    def generar_dashboard_kpis(self, formato: str = 'DICT') -> Dict[str, Any]:
        """
        Genera dashboard con KPIs principales del inventario.
        
        Args:
            formato: Formato de salida
            
        Returns:
            Dict con métricas KPI del dashboard
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            cursor = self.db_connection.cursor()
            
            # KPI 1: Resumen de inventario actual
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_productos,
                    SUM(stock_actual * precio_unitario) as valor_total_inventario,
                    SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as productos_sin_stock,
                    SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo,
                    AVG(stock_actual) as promedio_stock,
                    MAX(stock_actual) as stock_maximo_producto,
                    MIN(stock_actual) as stock_minimo_producto
                FROM {TABLA_INVENTARIO}
                WHERE activo = 1
            """)
            
            kpi_inventario = cursor.fetchone()
            
            # KPI 2: Movimientos del último mes
            fecha_hace_30_dias = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_movimientos_mes,
                    SUM(CASE WHEN cantidad > 0 THEN 1 ELSE 0 END) as entradas_mes,
                    SUM(CASE WHEN cantidad < 0 THEN 1 ELSE 0 END) as salidas_mes,
                    SUM(ABS(cantidad)) as cantidad_total_movida,
                    COUNT(DISTINCT producto_id) as productos_con_movimiento
                FROM {TABLA_MOVIMIENTOS}
                WHERE fecha_movimiento >= ?
            """, (fecha_hace_30_dias,))
            
            kpi_movimientos = cursor.fetchone()
            
            # KPI 3: Reservas activas
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_reservas_activas,
                    SUM(cantidad_reservada) as cantidad_total_reservada,
                    COUNT(DISTINCT producto_id) as productos_reservados,
                    COUNT(CASE WHEN fecha_vencimiento < GETDATE() THEN 1 END) as reservas_vencidas
                FROM {TABLA_RESERVAS}
                WHERE estado = 'ACTIVA'
            """)
            
            kpi_reservas = cursor.fetchone()
            
            # KPI 4: Top productos por movimiento
            cursor.execute(f"""
                SELECT TOP 10
                    p.codigo, p.descripcion,
                    COUNT(m.id) as total_movimientos,
                    SUM(ABS(m.cantidad)) as cantidad_total_movida
                FROM {TABLA_INVENTARIO} p
                INNER JOIN {TABLA_MOVIMIENTOS} m ON p.id = m.producto_id
                WHERE m.fecha_movimiento >= ?
                GROUP BY p.id, p.codigo, p.descripcion
                ORDER BY COUNT(m.id) DESC
            """, (fecha_hace_30_dias,))
            
            top_productos = cursor.fetchall()
            
            # KPI 5: Productos críticos que requieren atención
            cursor.execute(f"""
                SELECT 
                    codigo, descripcion, stock_actual, stock_minimo,
                    (stock_minimo - stock_actual) as faltante,
                    precio_unitario,
                    categoria
                FROM {TABLA_INVENTARIO}
                WHERE activo = 1 AND stock_actual <= stock_minimo
                ORDER BY (stock_minimo - stock_actual) DESC
            """)
            
            productos_criticos = cursor.fetchall()
            cursor.close()
            
            # Construir dashboard de KPIs
            dashboard = {
                'tipo_reporte': 'KPI_DASHBOARD',
                'fecha_generacion': datetime.now().isoformat(),
                'periodo_analisis': '30 días',
                
                # Métricas principales
                'metricas_inventario': {
                    'total_productos': int(kpi_inventario[0] or 0),
                    'valor_total_inventario': float(kpi_inventario[1] or 0),
                    'productos_sin_stock': int(kpi_inventario[2] or 0),
                    'productos_stock_bajo': int(kpi_inventario[3] or 0),
                    'promedio_stock': float(kpi_inventario[4] or 0),
                    'stock_maximo_producto': int(kpi_inventario[5] or 0),
                    'stock_minimo_producto': int(kpi_inventario[6] or 0)
                },
                
                'metricas_movimientos': {
                    'total_movimientos_mes': int(kpi_movimientos[0] or 0),
                    'entradas_mes': int(kpi_movimientos[1] or 0),
                    'salidas_mes': int(kpi_movimientos[2] or 0),
                    'cantidad_total_movida': float(kpi_movimientos[3] or 0),
                    'productos_con_movimiento': int(kpi_movimientos[4] or 0)
                },
                
                'metricas_reservas': {
                    'total_reservas_activas': int(kpi_reservas[0] or 0),
                    'cantidad_total_reservada': float(kpi_reservas[1] or 0),
                    'productos_reservados': int(kpi_reservas[2] or 0),
                    'reservas_vencidas': int(kpi_reservas[3] or 0)
                },
                
                # Rankings y análisis
                'top_productos_movimiento': [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'total_movimientos': row[2],
                        'cantidad_total_movida': float(row[3])
                    }
                    for row in top_productos
                ],
                
                'productos_criticos': [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'stock_actual': row[2],
                        'stock_minimo': row[3],
                        'faltante': row[4],
                        'precio_unitario': float(row[5]),
                        'categoria': row[6]
                    }
                    for row in productos_criticos
                ],
                
                # Indicadores calculados
                'indicadores': {
                    'porcentaje_productos_criticos': (
                        float(kpi_inventario[3] or 0) / max(float(kpi_inventario[0] or 1), 1) * 100
                    ),
                    'rotacion_inventario': (
                        float(kpi_movimientos[2] or 0) / max(float(kpi_inventario[0] or 1), 1)
                    ),
                    'eficiencia_reservas': (
                        (float(kpi_reservas[0] or 0) - float(kpi_reservas[3] or 0)) / 
                        max(float(kpi_reservas[0] or 1), 1) * 100
                    )
                }
            }
            
            return {
                'success': True,
                'data': self._formatear_reporte(dashboard, formato)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando dashboard de KPIs: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    @auth_required
    @permission_required("view_reportes")
    def generar_analisis_abc(self, criterio: str = 'valor', formato: str = 'DICT') -> Dict[str, Any]:
        """
        Genera análisis ABC de productos basado en criterio específico.
        
        Args:
            criterio: Criterio de análisis ('valor', 'movimiento', 'cantidad')
            formato: Formato de salida
            
        Returns:
            Dict con análisis ABC
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            cursor = self.db_connection.cursor()
            
            # Definir query según criterio
            if criterio == 'valor':
                # ABC por valor de inventario
                query = f"""
                    SELECT 
                        p.id, p.codigo, p.descripcion, p.categoria,
                        p.stock_actual, p.precio_unitario,
                        (p.stock_actual * p.precio_unitario) as valor_total
                    FROM {TABLA_INVENTARIO} p
                    WHERE p.activo = 1 AND p.stock_actual > 0
                    ORDER BY (p.stock_actual * p.precio_unitario) DESC
                """
                campo_analisis = 'valor_total'
                
            elif criterio == 'movimiento':
                # ABC por frecuencia de movimientos (último trimestre)
                fecha_trimestre = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
                query = f"""
                    SELECT 
                        p.id, p.codigo, p.descripcion, p.categoria,
                        p.stock_actual, p.precio_unitario,
                        COUNT(m.id) as total_movimientos,
                        SUM(ABS(m.cantidad)) as cantidad_movida
                    FROM {TABLA_INVENTARIO} p
                    LEFT JOIN {TABLA_MOVIMIENTOS} m ON p.id = m.producto_id 
                        AND m.fecha_movimiento >= ?
                    WHERE p.activo = 1
                    GROUP BY p.id, p.codigo, p.descripcion, p.categoria, p.stock_actual, p.precio_unitario
                    ORDER BY COUNT(m.id) DESC, SUM(ABS(m.cantidad)) DESC
                """
                params = [fecha_trimestre]
                campo_analisis = 'total_movimientos'
                
            else:  # cantidad
                # ABC por cantidad en stock
                query = f"""
                    SELECT 
                        p.id, p.codigo, p.descripcion, p.categoria,
                        p.stock_actual, p.precio_unitario,
                        p.stock_actual as cantidad_stock
                    FROM {TABLA_INVENTARIO} p
                    WHERE p.activo = 1 AND p.stock_actual > 0
                    ORDER BY p.stock_actual DESC
                """
                params = []
                campo_analisis = 'cantidad_stock'
            
            cursor.execute(query, params if 'params' in locals() else [])
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            cursor.close()
            
            if not filas:
                return {
                    'success': False,
                    'error': 'No hay datos suficientes para análisis ABC',
                    'data': None
                }
            
            # Procesar datos para análisis ABC
            productos = []
            total_valor_analisis = 0
            
            for fila in filas:
                producto = dict(zip(columnas, fila))
                valor_analisis = float(producto.get(campo_analisis, 0) or 0)
                producto['valor_analisis'] = valor_analisis
                total_valor_analisis += valor_analisis
                productos.append(producto)
            
            # Clasificar en categorías ABC
            productos_clasificados = []
            acumulado = 0
            
            for i, producto in enumerate(productos):
                valor_analisis = producto['valor_analisis']
                acumulado += valor_analisis
                porcentaje_acumulado = (acumulado / total_valor_analisis) * 100 if total_valor_analisis > 0 else 0
                
                # Clasificación ABC estándar
                if porcentaje_acumulado <= 80:
                    categoria_abc = 'A'
                elif porcentaje_acumulado <= 95:
                    categoria_abc = 'B'
                else:
                    categoria_abc = 'C'
                
                producto['categoria_abc'] = categoria_abc
                producto['porcentaje_individual'] = (valor_analisis / total_valor_analisis) * 100 if total_valor_analisis > 0 else 0
                producto['porcentaje_acumulado'] = porcentaje_acumulado
                producto['posicion'] = i + 1
                
                productos_clasificados.append(producto)
            
            # Calcular resumen por categoría
            resumen_abc = {'A': [], 'B': [], 'C': []}
            contadores = {'A': 0, 'B': 0, 'C': 0}
            valores = {'A': 0, 'B': 0, 'C': 0}
            
            for producto in productos_clasificados:
                cat = producto['categoria_abc']
                resumen_abc[cat].append(producto)
                contadores[cat] += 1
                valores[cat] += producto['valor_analisis']
            
            # Construir reporte final
            analisis = {
                'tipo_reporte': 'ANALISIS_ABC',
                'fecha_generacion': datetime.now().isoformat(),
                'criterio_analisis': criterio,
                'campo_analisis': campo_analisis,
                
                'resumen': {
                    'total_productos_analizados': len(productos_clasificados),
                    'total_valor_analizado': total_valor_analisis,
                    'categoria_A': {
                        'cantidad_productos': contadores['A'],
                        'porcentaje_productos': (contadores['A'] / len(productos)) * 100,
                        'valor_total': valores['A'],
                        'porcentaje_valor': (valores['A'] / total_valor_analisis) * 100 if total_valor_analisis > 0 else 0
                    },
                    'categoria_B': {
                        'cantidad_productos': contadores['B'],
                        'porcentaje_productos': (contadores['B'] / len(productos)) * 100,
                        'valor_total': valores['B'],
                        'porcentaje_valor': (valores['B'] / total_valor_analisis) * 100 if total_valor_analisis > 0 else 0
                    },
                    'categoria_C': {
                        'cantidad_productos': contadores['C'],
                        'porcentaje_productos': (contadores['C'] / len(productos)) * 100,
                        'valor_total': valores['C'],
                        'porcentaje_valor': (valores['C'] / total_valor_analisis) * 100 if total_valor_analisis > 0 else 0
                    }
                },
                
                'productos_por_categoria': resumen_abc,
                'todos_los_productos': productos_clasificados
            }
            
            return {
                'success': True,
                'data': self._formatear_reporte(analisis, formato)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando análisis ABC: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_valoracion_inventario(self, fecha_corte: Optional[str] = None, 
                                            formato: str = 'DICT') -> Dict[str, Any]:
        """
        Genera reporte de valoración completa del inventario.
        
        Args:
            fecha_corte: Fecha para la valoración (YYYY-MM-DD), por defecto hoy
            formato: Formato de salida
            
        Returns:
            Dict con la valoración del inventario
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            if not fecha_corte:
                fecha_corte = datetime.now().strftime('%Y-%m-%d')
            
            cursor = self.db_connection.cursor()
            
            # Valoración detallada por producto
            query = f"""
                SELECT 
                    i.id, i.codigo, i.descripcion, i.categoria, i.proveedor,
                    i.stock_actual, i.precio_unitario, i.unidad_medida,
                    i.fecha_creacion, i.fecha_modificacion,
                    (i.stock_actual * i.precio_unitario) as valor_total,
                    -- Stock reservado
                    ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0) as stock_reservado,
                    -- Valor de stock reservado
                    (ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0) * i.precio_unitario) as valor_reservado,
                    -- Stock disponible
                    (i.stock_actual - ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0)) as stock_disponible,
                    -- Valor disponible
                    ((i.stock_actual - ISNULL((
                        SELECT SUM(r.cantidad_reservada) 
                        FROM {TABLA_RESERVAS} r 
                        WHERE r.producto_id = i.id AND r.estado = 'ACTIVA'
                    ), 0)) * i.precio_unitario) as valor_disponible
                FROM {TABLA_INVENTARIO} i
                WHERE i.activo = 1
                ORDER BY (i.stock_actual * i.precio_unitario) DESC
            """
            
            cursor.execute(query)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            
            # Resumen por categoría
            query_categoria = f"""
                SELECT 
                    i.categoria,
                    COUNT(*) as total_productos,
                    SUM(i.stock_actual) as total_unidades,
                    SUM(i.stock_actual * i.precio_unitario) as valor_total_categoria,
                    AVG(i.precio_unitario) as precio_promedio,
                    MAX(i.precio_unitario) as precio_maximo,
                    MIN(i.precio_unitario) as precio_minimo
                FROM {TABLA_INVENTARIO} i
                WHERE i.activo = 1
                GROUP BY i.categoria
                ORDER BY SUM(i.stock_actual * i.precio_unitario) DESC
            """
            
            cursor.execute(query_categoria)
            categorias = cursor.fetchall()
            cursor.close()
            
            # Procesar datos de productos
            productos = []
            totales = {
                'productos': 0,
                'valor_total': 0,
                'valor_reservado': 0,
                'valor_disponible': 0,
                'stock_total': 0,
                'stock_reservado': 0,
                'stock_disponible': 0
            }
            
            for fila in filas:
                producto = dict(zip(columnas, fila))
                productos.append(producto)
                
                # Actualizar totales
                totales['productos'] += 1
                totales['valor_total'] += float(producto.get('valor_total', 0) or 0)
                totales['valor_reservado'] += float(producto.get('valor_reservado', 0) or 0)
                totales['valor_disponible'] += float(producto.get('valor_disponible', 0) or 0)
                totales['stock_total'] += float(producto.get('stock_actual', 0) or 0)
                totales['stock_reservado'] += float(producto.get('stock_reservado', 0) or 0)
                totales['stock_disponible'] += float(producto.get('stock_disponible', 0) or 0)
            
            # Procesar datos por categoría
            valoracion_por_categoria = []
            for cat_fila in categorias:
                categoria_info = {
                    'categoria': cat_fila[0],
                    'total_productos': cat_fila[1],
                    'total_unidades': float(cat_fila[2] or 0),
                    'valor_total_categoria': float(cat_fila[3] or 0),
                    'precio_promedio': float(cat_fila[4] or 0),
                    'precio_maximo': float(cat_fila[5] or 0),
                    'precio_minimo': float(cat_fila[6] or 0),
                    'porcentaje_valor': (
                        (float(cat_fila[3] or 0) / totales['valor_total']) * 100 
                        if totales['valor_total'] > 0 else 0
                    )
                }
                valoracion_por_categoria.append(categoria_info)
            
            # Construir reporte final
            valoracion = {
                'tipo_reporte': 'VALORACION_INVENTARIO',
                'fecha_generacion': datetime.now().isoformat(),
                'fecha_corte_valoracion': fecha_corte,
                
                'resumen_general': totales,
                
                'valoracion_por_categoria': valoracion_por_categoria,
                
                'productos_detallados': productos,
                
                'indicadores_financieros': {
                    'valor_promedio_producto': (
                        totales['valor_total'] / totales['productos'] 
                        if totales['productos'] > 0 else 0
                    ),
                    'porcentaje_valor_reservado': (
                        (totales['valor_reservado'] / totales['valor_total']) * 100 
                        if totales['valor_total'] > 0 else 0
                    ),
                    'porcentaje_valor_disponible': (
                        (totales['valor_disponible'] / totales['valor_total']) * 100 
                        if totales['valor_total'] > 0 else 0
                    ),
                    'categoria_mayor_valor': (
                        max(valoracion_por_categoria, key=lambda x: x['valor_total_categoria'])['categoria']
                        if valoracion_por_categoria else 'N/A'
                    )
                },
                
                'total_registros': len(productos)
            }
            
            return {
                'success': True,
                'data': self._formatear_reporte(valoracion, formato)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de valoración: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    # Métodos auxiliares
    
    def _formatear_reporte(self, reporte: Dict[str, Any], formato: str) -> Any:
        """Formatea el reporte según el formato solicitado."""
        try:
            if formato.upper() == 'JSON':
                return json.dumps(reporte, indent=2, default=str, ensure_ascii=False)
            elif formato.upper() == 'CSV':
                return self._convertir_a_csv(reporte)
            else:  # DICT por defecto
                return reporte
        except Exception as e:
            self.logger.error(f"Error formateando reporte: {e}")
            return reporte
    
    def _convertir_a_csv(self, reporte: Dict[str, Any]) -> str:
        """Convierte un reporte a formato CSV básico."""
        try:
            import io
            import csv
            
            output = io.StringIO()
            
            # Escribir metadatos del reporte
            output.write(f"# Reporte: {reporte.get('tipo_reporte', 'Desconocido')}\n")
            output.write(f"# Fecha: {reporte.get('fecha_generacion', 'N/A')}\n")
            output.write(f"# Total registros: {reporte.get('total_registros', 0)}\n")
            output.write("\n")
            
            # Identificar datos tabulares principales
            datos_principales = None
            
            if 'productos' in reporte:
                datos_principales = reporte['productos']
            elif 'movimientos' in reporte:
                datos_principales = reporte['movimientos']
            elif 'productos_detallados' in reporte:
                datos_principales = reporte['productos_detallados']
            elif 'todos_los_productos' in reporte:
                datos_principales = reporte['todos_los_productos']
            
            if datos_principales and len(datos_principales) > 0:
                # Escribir encabezados CSV
                headers = list(datos_principales[0].keys())
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writeheader()
                
                # Escribir datos
                for fila in datos_principales:
                    writer.writerow(fila)
            else:
                output.write("No hay datos tabulares para exportar en CSV\n")
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error convirtiendo a CSV: {e}")
            return f"Error generando CSV: {str(e)}"