"""
Categorías Manager - Gestión especializada de categorías de productos
Refactorizado de InventarioModel para mejor mantenibilidad

Responsabilidades:
- CRUD completo de categorías de productos
- Gestión jerárquica de categorías y subcategorías
- Validación y organización de categorías
- Estadísticas y reportes por categoría
- Control de relaciones con productos
- Migración y reorganización de categorías
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Configurar logging
logger = logging.getLogger(__name__)

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

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
    from rexus.utils.unified_sanitizer import unified_sanitizer
    data_sanitizer = unified_sanitizer
except ImportError:
    try:
        from rexus.utils.unified_sanitizer import DataSanitizer
        data_sanitizer = DataSanitizer()
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
    from .base_utilities import BaseUtilities, TABLA_INVENTARIO
    BASE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Error importando utilidades base: {e}")
    BASE_AVAILABLE = False
    BaseUtilities = None
    TABLA_INVENTARIO = "inventario_perfiles"

# Tabla de categorías (podría ser independiente o columna en inventario)
TABLA_CATEGORIAS = "categorias_inventario"


class CategoriasManager:
    """Manager especializado para gestión de categorías de productos."""
    
    # Categorías por defecto del sistema
    CATEGORIAS_DEFAULT = [
        'GENERAL',
        'HERRAMIENTAS',
        'MATERIALES',
        'SERVICIOS',
        'INSUMOS',
        'EQUIPOS',
        'CONSUMIBLES',
        'REPUESTOS'
    ]
    
    def __init__(self, db_connection=None):
        """
        Inicializa el manager de categorías.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/inventario/categorias"
        self.logger = logging.getLogger(__name__)
        
        # Inicializar utilidades base si están disponibles
        if BASE_AVAILABLE and db_connection:
            self.base_utils = BaseUtilities(db_connection)
        else:
            self.base_utils = None
            logger.warning("Utilidades base no disponibles en CategoriasManager")
    
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
    @permission_required("view_inventario")
    def obtener_todas_categorias(self, incluir_estadisticas: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene todas las categorías disponibles en el sistema.
        
        Args:
            incluir_estadisticas: Si incluir estadísticas de uso por categoría
            
        Returns:
            Lista de categorías con información opcional de estadísticas
        """
        if not self._validar_conexion():
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            if incluir_estadisticas:
                # Query con estadísticas
                query = f"""
                    SELECT 
                        categoria,
                        COUNT(*) as total_productos,
                        SUM(stock_actual) as total_stock,
                        SUM(stock_actual * precio_unitario) as valor_total_categoria,
                        AVG(precio_unitario) as precio_promedio,
                        MIN(precio_unitario) as precio_minimo,
                        MAX(precio_unitario) as precio_maximo,
                        SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as productos_sin_stock,
                        SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo
                    FROM {TABLA_INVENTARIO}
                    WHERE activo = 1 AND categoria IS NOT NULL AND categoria != ''
                    GROUP BY categoria
                    ORDER BY COUNT(*) DESC
                """
                
                cursor.execute(query)
                columnas = [desc[0] for desc in cursor.description]
                filas = cursor.fetchall()
                
                categorias = []
                for fila in filas:
                    categoria_dict = dict(zip(columnas, fila))
                    # Añadir indicadores calculados
                    categoria_dict['porcentaje_sin_stock'] = (
                        (float(categoria_dict['productos_sin_stock']) / float(categoria_dict['total_productos'])) * 100
                        if categoria_dict['total_productos'] > 0 else 0
                    )
                    categoria_dict['porcentaje_stock_bajo'] = (
                        (float(categoria_dict['productos_stock_bajo']) / float(categoria_dict['total_productos'])) * 100
                        if categoria_dict['total_productos'] > 0 else 0
                    )
                    categorias.append(categoria_dict)
                
            else:
                # Query simple para obtener solo nombres
                query = f"""
                    SELECT DISTINCT categoria, COUNT(*) as total_productos
                    FROM {TABLA_INVENTARIO}
                    WHERE activo = 1 AND categoria IS NOT NULL AND categoria != ''
                    GROUP BY categoria
                    ORDER BY categoria
                """
                
                cursor.execute(query)
                filas = cursor.fetchall()
                
                categorias = []
                for fila in filas:
                    categorias.append({
                        'categoria': fila[0],
                        'total_productos': fila[1]
                    })
            
            cursor.close()
            
            # Si no hay categorías en la BD, devolver las por defecto
            if not categorias:
                return [{'categoria': cat, 'total_productos': 0} for cat in self.CATEGORIAS_DEFAULT]
            
            return categorias
            
        except Exception as e:
            self.logger.error(f"Error obteniendo categorías: {e}")
            # Devolver categorías por defecto en caso de error
            return [{'categoria': cat, 'total_productos': 0} for cat in self.CATEGORIAS_DEFAULT]
    
    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_por_categoria(self, categoria: str, incluir_inactivos: bool = False, 
                                      limite: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Obtiene productos de una categoría específica.
        
        Args:
            categoria: Nombre de la categoría
            incluir_inactivos: Si incluir productos inactivos
            limite: Límite de productos por página
            offset: Desplazamiento para paginación
            
        Returns:
            Dict con productos de la categoría y metadata
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'productos': [],
                'total': 0
            }
        
        try:
            # Sanitizar categoría
            categoria_limpia = sanitize_string(categoria)
            if not categoria_limpia:
                return {
                    'success': False,
                    'error': 'Categoría inválida',
                    'productos': [],
                    'total': 0
                }
            
            cursor = self.db_connection.cursor()
            
            # Query para contar total de productos
            query_count = f"""
                SELECT COUNT(*)
                FROM {TABLA_INVENTARIO}
                WHERE categoria = ?
            """
            params_count = [categoria_limpia]
            
            if not incluir_inactivos:
                query_count += " AND activo = 1"
            
            cursor.execute(query_count, params_count)
            total_productos = cursor.fetchone()[0]
            
            # Query para obtener productos con paginación
            query_productos = f"""
                SELECT 
                    id, codigo, descripcion, categoria, precio_unitario,
                    stock_actual, stock_minimo, stock_maximo, proveedor,
                    unidad_medida, ubicacion, observaciones, activo,
                    fecha_creacion, fecha_modificacion,
                    -- Calcular estado de stock
                    CASE 
                        WHEN stock_actual = 0 THEN 'CRITICO'
                        WHEN stock_actual <= stock_minimo THEN 'BAJO'
                        WHEN stock_actual >= stock_maximo THEN 'EXCESO'
                        ELSE 'NORMAL'
                    END as estado_stock,
                    -- Calcular valor total
                    (stock_actual * precio_unitario) as valor_total
                FROM {TABLA_INVENTARIO}
                WHERE categoria = ?
            """
            params_productos = [categoria_limpia]
            
            if not incluir_inactivos:
                query_productos += " AND activo = 1"
            
            query_productos += f" ORDER BY codigo OFFSET {offset} ROWS FETCH NEXT {limite} ROWS ONLY"
            
            cursor.execute(query_productos, params_productos)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            cursor.close()
            
            # Procesar productos
            productos = []
            valor_total_categoria = 0
            
            for fila in filas:
                producto = dict(zip(columnas, fila))
                productos.append(producto)
                valor_total_categoria += float(producto.get('valor_total', 0) or 0)
            
            return {
                'success': True,
                'categoria': categoria_limpia,
                'productos': productos,
                'total': total_productos,
                'limite': limite,
                'offset': offset,
                'valor_total_categoria': valor_total_categoria,
                'tiene_mas_paginas': (offset + limite) < total_productos
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo productos por categoría {categoria}: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'productos': [],
                'total': 0
            }
    
    @auth_required
    @permission_required("admin_inventario")
    def crear_categoria(self, nombre_categoria: str, descripcion: str = "", 
                       categoria_padre: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una nueva categoría (si el sistema soporta tabla independiente).
        
        Args:
            nombre_categoria: Nombre de la nueva categoría
            descripcion: Descripción opcional de la categoría
            categoria_padre: Categoría padre para jerarquía (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos'
            }
        
        try:
            # Validar y sanitizar nombre
            nombre_limpio = sanitize_string(nombre_categoria)
            if not nombre_limpio or len(nombre_limpio) < 2:
                return {
                    'success': False,
                    'error': 'Nombre de categoría inválido (mínimo 2 caracteres)'
                }
            
            # Convertir a mayúsculas para consistencia
            nombre_limpio = nombre_limpio.upper()
            
            # Verificar si la categoría ya existe
            if self._existe_categoria(nombre_limpio):
                return {
                    'success': False,
                    'error': f'La categoría "{nombre_limpio}" ya existe'
                }
            
            cursor = self.db_connection.cursor()
            
            # Intentar crear en tabla independiente si existe
            if self._tabla_categorias_existe():
                descripcion_limpia = sanitize_string(descripcion)[:500]
                categoria_padre_limpia = None
                
                if categoria_padre:
                    categoria_padre_limpia = sanitize_string(categoria_padre).upper()
                    if not self._existe_categoria(categoria_padre_limpia):
                        cursor.close()
                        return {
                            'success': False,
                            'error': f'Categoría padre "{categoria_padre_limpia}" no existe'
                        }
                
                query = f"""
                    INSERT INTO {TABLA_CATEGORIAS} (
                        nombre, descripcion, categoria_padre, activa,
                        fecha_creacion, fecha_modificacion
                    ) VALUES (?, ?, ?, 1, GETDATE(), GETDATE())
                """
                
                cursor.execute(query, (nombre_limpio, descripcion_limpia, categoria_padre_limpia))
                self.db_connection.commit()
                cursor.close()
                
                self.logger.info(f"Categoría creada en tabla independiente: {nombre_limpio}")
                
                return {
                    'success': True,
                    'message': f'Categoría "{nombre_limpio}" creada exitosamente'
                }
            
            else:
                # Si no existe tabla independiente, simplemente validar que es un nombre válido
                # La categoría se creará implícitamente cuando se asigne a un producto
                cursor.close()
                
                self.logger.info(f"Categoría validada para uso futuro: {nombre_limpio}")
                
                return {
                    'success': True,
                    'message': f'Categoría "{nombre_limpio}" validada para uso futuro'
                }
            
        except Exception as e:
            self.logger.error(f"Error creando categoría {nombre_categoria}: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    @auth_required
    @permission_required("admin_inventario")
    def renombrar_categoria(self, categoria_actual: str, categoria_nueva: str) -> Dict[str, Any]:
        """
        Renombra una categoría existente y actualiza todos los productos.
        
        Args:
            categoria_actual: Nombre actual de la categoría
            categoria_nueva: Nuevo nombre para la categoría
            
        Returns:
            Dict con resultado de la operación
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'productos_actualizados': 0
            }
        
        try:
            # Validar y sanitizar nombres
            categoria_actual_limpia = sanitize_string(categoria_actual).upper()
            categoria_nueva_limpia = sanitize_string(categoria_nueva).upper()
            
            if not categoria_actual_limpia or not categoria_nueva_limpia:
                return {
                    'success': False,
                    'error': 'Nombres de categoría inválidos',
                    'productos_actualizados': 0
                }
            
            if categoria_actual_limpia == categoria_nueva_limpia:
                return {
                    'success': True,
                    'message': 'La categoría ya tiene ese nombre',
                    'productos_actualizados': 0
                }
            
            # Verificar que la categoría actual existe y tiene productos
            cursor = self.db_connection.cursor()
            
            cursor.execute(
                f"SELECT COUNT(*) FROM {TABLA_INVENTARIO} WHERE categoria = ?",
                (categoria_actual_limpia,)
            )
            productos_existentes = cursor.fetchone()[0]
            
            if productos_existentes == 0:
                cursor.close()
                return {
                    'success': False,
                    'error': f'No se encontraron productos con categoría "{categoria_actual_limpia}"',
                    'productos_actualizados': 0
                }
            
            # Verificar que la nueva categoría no existe (para evitar conflictos)
            cursor.execute(
                f"SELECT COUNT(*) FROM {TABLA_INVENTARIO} WHERE categoria = ?",
                (categoria_nueva_limpia,)
            )
            productos_nueva_categoria = cursor.fetchone()[0]
            
            if productos_nueva_categoria > 0:
                cursor.close()
                return {
                    'success': False,
                    'error': f'Ya existen productos con categoría "{categoria_nueva_limpia}". Use migrar_categoria para combinar.',
                    'productos_actualizados': 0
                }
            
            # Realizar el renombrado
            query_update = f"""
                UPDATE {TABLA_INVENTARIO} 
                SET categoria = ?, fecha_modificacion = GETDATE()
                WHERE categoria = ?
            """
            
            cursor.execute(query_update, (categoria_nueva_limpia, categoria_actual_limpia))
            productos_actualizados = cursor.rowcount
            
            # Actualizar tabla de categorías si existe
            if self._tabla_categorias_existe():
                query_cat = f"""
                    UPDATE {TABLA_CATEGORIAS}
                    SET nombre = ?, fecha_modificacion = GETDATE()
                    WHERE nombre = ?
                """
                cursor.execute(query_cat, (categoria_nueva_limpia, categoria_actual_limpia))
            
            self.db_connection.commit()
            cursor.close()
            
            self.logger.info(f"Categoría renombrada: {categoria_actual_limpia} -> {categoria_nueva_limpia}, {productos_actualizados} productos actualizados")
            
            return {
                'success': True,
                'message': f'Categoría renombrada exitosamente de "{categoria_actual_limpia}" a "{categoria_nueva_limpia}"',
                'productos_actualizados': productos_actualizados
            }
            
        except Exception as e:
            self.logger.error(f"Error renombrando categoría: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'productos_actualizados': 0
            }
    
    @auth_required
    @permission_required("admin_inventario")
    def migrar_productos_categoria(self, categoria_origen: str, categoria_destino: str) -> Dict[str, Any]:
        """
        Migra todos los productos de una categoría a otra.
        
        Args:
            categoria_origen: Categoría desde la cual migrar productos
            categoria_destino: Categoría destino para los productos
            
        Returns:
            Dict con resultado de la migración
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'productos_migrados': 0
            }
        
        try:
            # Validar y sanitizar nombres
            origen_limpia = sanitize_string(categoria_origen).upper()
            destino_limpia = sanitize_string(categoria_destino).upper()
            
            if not origen_limpia or not destino_limpia:
                return {
                    'success': False,
                    'error': 'Nombres de categoría inválidos',
                    'productos_migrados': 0
                }
            
            if origen_limpia == destino_limpia:
                return {
                    'success': True,
                    'message': 'Las categorías origen y destino son iguales',
                    'productos_migrados': 0
                }
            
            cursor = self.db_connection.cursor()
            
            # Verificar que existen productos en la categoría origen
            cursor.execute(
                f"SELECT COUNT(*) FROM {TABLA_INVENTARIO} WHERE categoria = ?",
                (origen_limpia,)
            )
            productos_origen = cursor.fetchone()[0]
            
            if productos_origen == 0:
                cursor.close()
                return {
                    'success': False,
                    'error': f'No se encontraron productos en categoría origen "{origen_limpia}"',
                    'productos_migrados': 0
                }
            
            # Realizar la migración
            query_migrar = f"""
                UPDATE {TABLA_INVENTARIO}
                SET categoria = ?, fecha_modificacion = GETDATE()
                WHERE categoria = ?
            """
            
            cursor.execute(query_migrar, (destino_limpia, origen_limpia))
            productos_migrados = cursor.rowcount
            
            self.db_connection.commit()
            cursor.close()
            
            self.logger.info(f"Productos migrados: {productos_migrados} de {origen_limpia} a {destino_limpia}")
            
            return {
                'success': True,
                'message': f'Se migraron {productos_migrados} productos de "{origen_limpia}" a "{destino_limpia}"',
                'productos_migrados': productos_migrados,
                'categoria_origen': origen_limpia,
                'categoria_destino': destino_limpia
            }
            
        except Exception as e:
            self.logger.error(f"Error migrando productos de categoría: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'productos_migrados': 0
            }
    
    @auth_required
    @permission_required("admin_inventario")
    def limpiar_categorias_vacias(self) -> Dict[str, Any]:
        """
        Limpia categorías que no tienen productos asociados (si hay tabla independiente).
        
        Returns:
            Dict con resultado de la limpieza
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'categorias_eliminadas': 0
            }
        
        try:
            if not self._tabla_categorias_existe():
                return {
                    'success': True,
                    'message': 'No hay tabla independiente de categorías para limpiar',
                    'categorias_eliminadas': 0
                }
            
            cursor = self.db_connection.cursor()
            
            # Encontrar categorías sin productos
            query_vacias = f"""
                SELECT c.nombre
                FROM {TABLA_CATEGORIAS} c
                LEFT JOIN {TABLA_INVENTARIO} i ON c.nombre = i.categoria
                WHERE i.categoria IS NULL AND c.activa = 1
            """
            
            cursor.execute(query_vacias)
            categorias_vacias = [row[0] for row in cursor.fetchall()]
            
            if not categorias_vacias:
                cursor.close()
                return {
                    'success': True,
                    'message': 'No se encontraron categorías vacías para eliminar',
                    'categorias_eliminadas': 0
                }
            
            # Desactivar categorías vacías (soft delete)
            query_limpiar = f"""
                UPDATE {TABLA_CATEGORIAS}
                SET activa = 0, fecha_modificacion = GETDATE()
                WHERE nombre IN ({','.join(['?'] * len(categorias_vacias))})
            """
            
            cursor.execute(query_limpiar, categorias_vacias)
            categorias_eliminadas = cursor.rowcount
            
            self.db_connection.commit()
            cursor.close()
            
            self.logger.info(f"Categorías vacías desactivadas: {categorias_eliminadas}")
            
            return {
                'success': True,
                'message': f'Se desactivaron {categorias_eliminadas} categorías vacías',
                'categorias_eliminadas': categorias_eliminadas,
                'categorias_afectadas': categorias_vacias
            }
            
        except Exception as e:
            self.logger.error(f"Error limpiando categorías vacías: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'categorias_eliminadas': 0
            }
    
    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_categorias(self) -> Dict[str, Any]:
        """
        Genera reporte completo de análisis de categorías.
        
        Returns:
            Dict con análisis detallado de categorías
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'data': None
            }
        
        try:
            cursor = self.db_connection.cursor()
            
            # Análisis principal de categorías
            query_principal = f"""
                SELECT 
                    categoria,
                    COUNT(*) as total_productos,
                    COUNT(CASE WHEN activo = 1 THEN 1 END) as productos_activos,
                    COUNT(CASE WHEN activo = 0 THEN 1 END) as productos_inactivos,
                    SUM(stock_actual) as total_stock,
                    SUM(stock_actual * precio_unitario) as valor_total,
                    AVG(precio_unitario) as precio_promedio,
                    MIN(precio_unitario) as precio_minimo,
                    MAX(precio_unitario) as precio_maximo,
                    SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as productos_sin_stock,
                    SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo,
                    -- Productos más y menos costosos
                    (SELECT TOP 1 codigo FROM {TABLA_INVENTARIO} i2 
                     WHERE i2.categoria = i.categoria ORDER BY precio_unitario DESC) as producto_mas_costoso,
                    (SELECT TOP 1 codigo FROM {TABLA_INVENTARIO} i2 
                     WHERE i2.categoria = i.categoria ORDER BY precio_unitario ASC) as producto_menos_costoso
                FROM {TABLA_INVENTARIO} i
                WHERE categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria
                ORDER BY SUM(stock_actual * precio_unitario) DESC
            """
            
            cursor.execute(query_principal)
            columnas = [desc[0] for desc in cursor.description]
            filas_principales = cursor.fetchall()
            
            # Análisis de tendencias (productos nuevos por categoría en último mes)
            query_tendencias = f"""
                SELECT 
                    categoria,
                    COUNT(*) as productos_nuevos_mes
                FROM {TABLA_INVENTARIO}
                WHERE fecha_creacion >= DATEADD(MONTH, -1, GETDATE())
                AND categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria
                ORDER BY COUNT(*) DESC
            """
            
            cursor.execute(query_tendencias)
            tendencias = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.close()
            
            # Procesar datos principales
            categorias_detalle = []
            totales_sistema = {
                'total_categorias': 0,
                'total_productos': 0,
                'valor_total_sistema': 0,
                'categoria_mayor_valor': None,
                'categoria_mas_productos': None
            }
            
            for fila in filas_principales:
                categoria_info = dict(zip(columnas, fila))
                
                # Añadir información de tendencias
                categoria_info['productos_nuevos_mes'] = tendencias.get(categoria_info['categoria'], 0)
                
                # Calcular indicadores adicionales
                categoria_info['porcentaje_productos_sin_stock'] = (
                    (float(categoria_info['productos_sin_stock']) / float(categoria_info['total_productos'])) * 100
                    if categoria_info['total_productos'] > 0 else 0
                )
                
                categoria_info['porcentaje_stock_bajo'] = (
                    (float(categoria_info['productos_stock_bajo']) / float(categoria_info['total_productos'])) * 100
                    if categoria_info['total_productos'] > 0 else 0
                )
                
                categoria_info['salud_categoria'] = self._calcular_salud_categoria(categoria_info)
                
                categorias_detalle.append(categoria_info)
                
                # Actualizar totales del sistema
                totales_sistema['total_categorias'] += 1
                totales_sistema['total_productos'] += categoria_info['total_productos']
                totales_sistema['valor_total_sistema'] += float(categoria_info['valor_total'] or 0)
            
            # Identificar categorías destacadas
            if categorias_detalle:
                totales_sistema['categoria_mayor_valor'] = max(
                    categorias_detalle, key=lambda x: float(x['valor_total'] or 0)
                )['categoria']
                
                totales_sistema['categoria_mas_productos'] = max(
                    categorias_detalle, key=lambda x: x['total_productos']
                )['categoria']
            
            # Construir reporte final
            reporte = {
                'tipo_reporte': 'ANALISIS_CATEGORIAS',
                'fecha_generacion': datetime.now().isoformat(),
                
                'resumen_sistema': totales_sistema,
                
                'categorias_detalle': categorias_detalle,
                
                'top_categorias': {
                    'por_valor': sorted(categorias_detalle, key=lambda x: float(x['valor_total'] or 0), reverse=True)[:5],
                    'por_productos': sorted(categorias_detalle, key=lambda x: x['total_productos'], reverse=True)[:5],
                    'por_crecimiento': sorted(categorias_detalle, key=lambda x: x['productos_nuevos_mes'], reverse=True)[:5]
                },
                
                'alertas': {
                    'categorias_problematicas': [
                        cat for cat in categorias_detalle 
                        if cat['salud_categoria'] == 'PROBLEMATICA'
                    ],
                    'categorias_sin_stock': [
                        cat for cat in categorias_detalle 
                        if cat['porcentaje_productos_sin_stock'] > 50
                    ]
                }
            }
            
            return {
                'success': True,
                'data': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de categorías: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }
    
    # Métodos auxiliares privados
    
    def _existe_categoria(self, nombre_categoria: str) -> bool:
        """Verifica si una categoría existe en el sistema."""
        try:
            cursor = self.db_connection.cursor()
            
            if self._tabla_categorias_existe():
                # Verificar en tabla independiente
                cursor.execute(
                    f"SELECT COUNT(*) FROM {TABLA_CATEGORIAS} WHERE nombre = ? AND activa = 1",
                    (nombre_categoria,)
                )
            else:
                # Verificar en productos
                cursor.execute(
                    f"SELECT COUNT(*) FROM {TABLA_INVENTARIO} WHERE categoria = ?",
                    (nombre_categoria,)
                )
            
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
            
        except Exception as e:
            self.logger.error(f"Error verificando existencia de categoría: {e}")
            return False
    
    def _tabla_categorias_existe(self) -> bool:
        """Verifica si existe una tabla independiente de categorías."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{TABLA_CATEGORIAS}'
            """)
            
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            return exists
            
        except Exception:
            return False
    
    def _calcular_salud_categoria(self, categoria_info: Dict[str, Any]) -> str:
        """Calcula el estado de salud de una categoría basado en métricas."""
        try:
            # Criterios para determinar salud
            porcentaje_sin_stock = categoria_info.get('porcentaje_productos_sin_stock', 0)
            porcentaje_stock_bajo = categoria_info.get('porcentaje_stock_bajo', 0)
            productos_nuevos = categoria_info.get('productos_nuevos_mes', 0)
            total_productos = categoria_info.get('total_productos', 0)
            
            # Lógica de clasificación de salud
            if porcentaje_sin_stock > 30 or porcentaje_stock_bajo > 50:
                return 'PROBLEMATICA'
            elif porcentaje_sin_stock > 10 or porcentaje_stock_bajo > 25:
                return 'ATENCION'
            elif productos_nuevos > 0 and total_productos > 5:
                return 'CRECIMIENTO'
            elif total_productos >= 10 and porcentaje_sin_stock < 5:
                return 'SALUDABLE'
            else:
                return 'ESTABLE'
            
        except Exception:
            return 'DESCONOCIDO'