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
from typing import Dict, Any, List, Optional
from datetime import datetime

# Importar SQLQueryManager
from ....utils.sql_query_manager import SQLQueryManager

logger = logging.getLogger(__name__)


class CategoriasManager:
    """Manager especializado para la gestión de categorías de productos"""
    
    TABLA_INVENTARIO = '02_inventario'
    TABLA_CATEGORIAS = 'categorias'
    CATEGORIAS_DEFAULT = [
        'VIDRIOS', 'HERRAJES', 'PERFILERIA', 'ADHESIVOS', 
        'HERRAMIENTAS', 'CONSUMIBLES', 'ACCESORIOS'
    ]
    
    def __init__(self, db_connection=None, base_utils=None):
        self.db_connection = db_connection
        self.base_utils = base_utils
        self.sql_manager = SQLQueryManager()
        self.logger = logger
    
    def _validar_conexion(self) -> bool:
        """Valida que exista conexión a la base de datos"""
        return self.db_connection is not None
        
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
                    FROM {self.TABLA_INVENTARIO}
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
                    FROM {self.TABLA_INVENTARIO}
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error obteniendo categorías: {e}")
            return []
    
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
            nombre_limpio = self._sanitizar_string(nombre_categoria)
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
                descripcion_limpia = self._sanitizar_string(descripcion)[:500]
                categoria_padre_limpia = None

                if categoria_padre:
                    categoria_padre_limpia = self._sanitizar_string(categoria_padre).upper()
                    if not self._existe_categoria(categoria_padre_limpia):
                        cursor.close()
                        return {
                            'success': False,
                            'error': f'Categoría padre "{categoria_padre_limpia}" no existe'
                        }

                query = f"""
                    INSERT INTO {self.TABLA_CATEGORIAS} (
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error creando categoría: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
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
            categoria_actual_limpia = self._sanitizar_string(categoria_actual).upper()
            categoria_nueva_limpia = self._sanitizar_string(categoria_nueva).upper()

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

            query = self.sql_manager.get_query('02_inventario', 'count_productos_por_categoria')
            cursor.execute(query, (categoria_actual_limpia,))
            productos_existentes = cursor.fetchone()[0]

            if productos_existentes == 0:
                cursor.close()
                return {
                    'success': False,
                    'error': f'No se encontraron productos con categoría "{categoria_actual_limpia}"',
                    'productos_actualizados': 0
                }

            # Verificar que la nueva categoría no existe (para evitar conflictos)
            query = self.sql_manager.get_query('02_inventario', 'count_productos_por_categoria')
            cursor.execute(query, (categoria_nueva_limpia,))
            productos_nueva_categoria = cursor.fetchone()[0]

            if productos_nueva_categoria > 0:
                cursor.close()
                return {
                    'success': False,
                    'error': f'Ya existen productos con categoría "{categoria_nueva_limpia}". Use migrar_categoria para combinar.',
                    'productos_actualizados': 0
                }

            # Realizar el renombrado
            query_update = self.sql_manager.get_query('02_inventario', 'update_categoria_productos')
            cursor.execute(query_update, (categoria_nueva_limpia, categoria_actual_limpia))
            productos_actualizados = cursor.rowcount

            # Actualizar tabla de categorías si existe
            if self._tabla_categorias_existe():
                query_cat = self.sql_manager.get_query('02_inventario', 'update_categoria_tabla')
                cursor.execute(query_cat, (categoria_nueva_limpia, categoria_actual_limpia))

            self.db_connection.commit()
            cursor.close()

            self.logger.info(f"Categoría renombrada: {categoria_actual_limpia} -> {categoria_nueva_limpia}, {productos_actualizados} productos actualizados")

            return {
                'success': True,
                'message': f'Categoría renombrada exitosamente de "{categoria_actual_limpia}" a "{categoria_nueva_limpia}"',
                'productos_actualizados': productos_actualizados
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error renombrando categoría: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'productos_actualizados': 0
            }
    
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
            origen_limpia = self._sanitizar_string(categoria_origen).upper()
            destino_limpia = self._sanitizar_string(categoria_destino).upper()

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
            query = self.sql_manager.get_query('02_inventario', 'count_productos_por_categoria')
            cursor.execute(query, (origen_limpia,))
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
                UPDATE {self.TABLA_INVENTARIO}
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error migrando productos: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'productos_migrados': 0
            }
    
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
                FROM {self.TABLA_CATEGORIAS} c
                LEFT JOIN {self.TABLA_INVENTARIO} i ON c.nombre = i.categoria
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
                UPDATE {self.TABLA_CATEGORIAS}
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error limpiando categorías vacías: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'categorias_eliminadas': 0
            }
    
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
                    SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo
                FROM {self.TABLA_INVENTARIO} i
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
                FROM {self.TABLA_INVENTARIO}
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error generando reporte de categorías: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'data': None
            }

    # Métodos privados auxiliares
    def _tabla_categorias_existe(self) -> bool:
        """Verifica si existe una tabla independiente de categorías."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = ?
            """, (self.TABLA_CATEGORIAS,))

            exists = cursor.fetchone()[0] > 0
            cursor.close()
            return exists

        except (AttributeError, RuntimeError, ConnectionError):
            return False

    def _existe_categoria(self, nombre_categoria: str) -> bool:
        """Verifica si existe una categoría con el nombre dado."""
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar en tabla de 02_inventario
            query = self.sql_manager.get_query('02_inventario', 'count_productos_por_categoria')
            cursor.execute(query, (nombre_categoria,))
            existe_en_02_inventario = cursor.fetchone()[0] > 0
            
            # Verificar en tabla de categorías si existe
            if self._tabla_categorias_existe():
                query_cat = self.sql_manager.get_query('02_inventario', 'check_categoria_activa')
                cursor.execute(query_cat, (nombre_categoria,))
                existe_en_categorias = cursor.fetchone()[0] > 0
            else:
                existe_en_categorias = False
                
            cursor.close()
            return existe_en_02_inventario or existe_en_categorias

        except (AttributeError, RuntimeError, ConnectionError):
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

        except (KeyError, TypeError, ValueError):
            return 'DESCONOCIDO'

    def _sanitizar_string(self, input_string: str) -> str:
        """Sanitiza una cadena de texto para uso seguro."""
        if not input_string:
            return ""
        
        # Remover caracteres peligrosos y limpiar
        sanitized = str(input_string).strip()
        # Remover caracteres especiales SQL
        caracteres_peligrosos = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        for char in caracteres_peligrosos:
            sanitized = sanitized.replace(char, "")
        
        return sanitized[:200]  # Limitar longitud