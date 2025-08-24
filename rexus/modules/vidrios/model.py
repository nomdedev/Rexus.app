
"""
Modelo de Vidrios - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para vidrios.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class VidriosModel:
    """Modelo para el módulo de vidrios."""
    
    # Tipos de vidrio disponibles
    TIPOS_VIDRIO = {
        'transparente': 'Transparente',
        'templado': 'Templado',
        'laminado': 'Laminado',
        'reflectivo': 'Reflectivo',
        'insulado': 'Insulado'
    }
    
    # Grosores estándar en mm
    GROSORES_ESTANDAR = [3, 4, 5, 6, 8, 10, 12, 15, 19, 25]
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de vidrios."""
        self.db_connection = db_connection
        self.logger = logger
        
    def eliminar_vidrio(self, vidrio_id: int) -> bool:
        """
        Elimina un vidrio (marca como inactivo).

        Args:
            vidrio_id: ID del vidrio a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not self.db_connection:
                self.logger.error("Conexión a base de datos no disponible")
                return False
                
            if not isinstance(vidrio_id, int) or vidrio_id <= 0:
                self.logger.error(f"ID de vidrio inválido: {vidrio_id}")
                return False
                
            cursor = self.db_connection.cursor()
            
            # Verificar si el vidrio existe y está activo
            cursor.execute("SELECT id, tipo FROM vidrios WHERE id = ? AND activo = 1", (vidrio_id,))
            vidrio = cursor.fetchone()
            
            if not vidrio:
                self.logger.warning(f"Vidrio con ID {vidrio_id} no encontrado o ya eliminado")
                return False
                
            # Verificar si está siendo usado en obras
            cursor.execute("""
                SELECT COUNT(*) FROM obra_vidrios 
                WHERE vidrio_id = ? AND obra_estado != 'cancelada'
            """, (vidrio_id,))
            
            obras_activas = cursor.fetchone()[0] if cursor.fetchone() else 0
            
            if obras_activas > 0:
                self.logger.warning(f"Vidrio {vidrio_id} está siendo usado en {obras_activas} obras activas")
                # Marcar como inactivo en lugar de eliminar
                cursor.execute("UPDATE vidrios SET activo = 0, fecha_eliminacion = ? WHERE id = ?", 
                             (datetime.now().isoformat(), vidrio_id))
            else:
                # Eliminación lógica
                cursor.execute("UPDATE vidrios SET activo = 0, fecha_eliminacion = ? WHERE id = ?", 
                             (datetime.now().isoformat(), vidrio_id))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                self.logger.info(f"Vidrio {vidrio_id} eliminado exitosamente")
                return True
            else:
                self.logger.warning(f"No se pudo eliminar el vidrio {vidrio_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error eliminando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def crear_vidrio(self, datos: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo vidrio."""
        try:
            if not self.db_connection:
                self.logger.error("Conexión a base de datos no disponible")
                return None
                
            # Validar datos requeridos
            if not self._validar_datos_vidrio(datos):
                return None
                
            cursor = self.db_connection.cursor()
            
            # Verificar si ya existe un vidrio con las mismas características
            cursor.execute("""
                SELECT id FROM vidrios 
                WHERE tipo = ? AND grosor = ? AND ancho = ? AND alto = ? AND color = ? AND activo = 1
            """, (
                datos.get('tipo'),
                datos.get('grosor'),
                datos.get('ancho'),
                datos.get('alto'),
                datos.get('color', 'transparente')
            ))
            
            if cursor.fetchone():
                self.logger.warning("Ya existe un vidrio con las mismas características")
                return None
                
            # Calcular precio automáticamente si no se proporciona
            precio = datos.get('precio_unitario') or self.calcular_precio(datos)
            
            cursor.execute("""
                INSERT INTO vidrios (
                    tipo, grosor, ancho, alto, color, precio_unitario, 
                    stock_actual, stock_minimo, activo, fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                datos.get('tipo'),
                datos.get('grosor'),
                datos.get('ancho'),
                datos.get('alto'),
                datos.get('color', 'transparente'),
                precio,
                datos.get('stock_actual', 0),
                datos.get('stock_minimo', 5),
                datetime.now().isoformat()
            ))
            
            vidrio_id = cursor.lastrowid
            self.db_connection.commit()
            self.logger.info(f"Vidrio creado exitosamente: {vidrio_id}")
            return vidrio_id
            
        except Exception as e:
            self.logger.error(f"Error creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_vidrio(self, vidrio_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza un vidrio existente."""
        try:
            if not self.db_connection:
                self.logger.error("Conexión a base de datos no disponible")
                return False
                
            if not self._validar_datos_vidrio(datos):
                return False
                
            cursor = self.db_connection.cursor()
            
            # Verificar que el vidrio existe
            cursor.execute("SELECT id FROM vidrios WHERE id = ? AND activo = 1", (vidrio_id,))
            if not cursor.fetchone():
                self.logger.error(f"Vidrio {vidrio_id} no encontrado")
                return False
                
            # Recalcular precio si cambió alguna especificación
            precio = datos.get('precio_unitario') or self.calcular_precio(datos)
            
            cursor.execute("""
                UPDATE vidrios 
                SET tipo = ?, grosor = ?, ancho = ?, alto = ?, color = ?, 
                    precio_unitario = ?, stock_actual = ?, stock_minimo = ?,
                    fecha_modificacion = ?
                WHERE id = ? AND activo = 1
            """, (
                datos.get('tipo'),
                datos.get('grosor'),
                datos.get('ancho'),
                datos.get('alto'),
                datos.get('color'),
                precio,
                datos.get('stock_actual'),
                datos.get('stock_minimo'),
                datetime.now().isoformat(),
                vidrio_id
            ))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                self.logger.info(f"Vidrio {vidrio_id} actualizado exitosamente")
                return True
            else:
                self.logger.warning(f"No se pudo actualizar el vidrio {vidrio_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error actualizando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_vidrio_por_id(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un vidrio por su ID."""
        try:
            if not self.db_connection:
                return None
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
                       stock_actual, stock_minimo, fecha_creacion, fecha_modificacion
                FROM vidrios 
                WHERE id = ? AND activo = 1
            """, (vidrio_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'tipo': row[1],
                    'grosor': row[2],
                    'ancho': row[3],
                    'alto': row[4],
                    'color': row[5],
                    'precio_unitario': row[6],
                    'stock_actual': row[7],
                    'stock_minimo': row[8],
                    'fecha_creacion': row[9],
                    'fecha_modificacion': row[10]
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vidrio por ID: {e}")
            return None

    def obtener_vidrios(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene lista de vidrios con filtros opcionales."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            
            query = """
                SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
                       stock_actual, stock_minimo, fecha_creacion
                FROM vidrios 
                WHERE activo = 1
            """
            params = []
            
            if filtros:
                if filtros.get('tipo'):
                    query += " AND tipo = ?"
                    params.append(filtros['tipo'])
                    
                if filtros.get('grosor'):
                    query += " AND grosor = ?"
                    params.append(filtros['grosor'])
                    
                if filtros.get('color'):
                    query += " AND color = ?"
                    params.append(filtros['color'])
                    
                if filtros.get('stock_bajo'):
                    query += " AND stock_actual <= stock_minimo"
                    
                if filtros.get('busqueda'):
                    query += " AND (tipo LIKE ? OR color LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])
            
            query += " ORDER BY tipo, grosor, ancho, alto"
            
            cursor.execute(query, params)
            
            vidrios = []
            for row in cursor.fetchall():
                vidrios.append({
                    'id': row[0],
                    'tipo': row[1],
                    'grosor': row[2],
                    'ancho': row[3],
                    'alto': row[4],
                    'color': row[5],
                    'precio_unitario': row[6],
                    'stock_actual': row[7],
                    'stock_minimo': row[8],
                    'fecha_creacion': row[9]
                })
            
            return vidrios
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vidrios: {e}")
            return []

    def calcular_precio(self, datos: Dict[str, Any]) -> float:
        """Calcula el precio de un vidrio según sus especificaciones."""
        try:
            ancho = float(datos.get('ancho', 0))
            alto = float(datos.get('alto', 0))
            grosor = float(datos.get('grosor', 0))
            tipo = datos.get('tipo', 'transparente')
            
            if ancho <= 0 or alto <= 0 or grosor <= 0:
                return 0.0
            
            # Calcular área en m²
            area_m2 = (ancho * alto) / 1000000  # Convertir mm² a m²
            
            # Precios base por m² según tipo (en pesos)
            precios_base = {
                'transparente': 2500.0,
                'templado': 4500.0,
                'laminado': 6000.0,
                'reflectivo': 5500.0,
                'insulado': 8500.0
            }
            
            precio_base = precios_base.get(tipo, 2500.0)
            
            # Factor por grosor (grosor base: 6mm)
            factor_grosor = max(0.8, grosor / 6.0)
            
            # Factor por tamaño (áreas grandes son más caras por m²)
            factor_tamano = 1.0
            if area_m2 > 2.0:
                factor_tamano = 1.2
            elif area_m2 > 5.0:
                factor_tamano = 1.4
                
            precio_total = area_m2 * precio_base * factor_grosor * factor_tamano
            
            return round(precio_total, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculando precio: {e}")
            return 0.0

    def actualizar_stock(self, vidrio_id: int, nuevo_stock: int) -> bool:
        """Actualiza el stock de un vidrio."""
        try:
            if not self.db_connection:
                return False
                
            if nuevo_stock < 0:
                self.logger.error("El stock no puede ser negativo")
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE vidrios 
                SET stock_actual = ?, fecha_modificacion = ?
                WHERE id = ? AND activo = 1
            """, (nuevo_stock, datetime.now().isoformat(), vidrio_id))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                self.logger.info(f"Stock actualizado para vidrio {vidrio_id}: {nuevo_stock}")
                return True
            else:
                self.logger.warning(f"No se encontró vidrio activo con ID {vidrio_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error actualizando stock: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los vidrios."""
        try:
            if not self.db_connection:
                return {}
                
            cursor = self.db_connection.cursor()
            
            # Total de vidrios activos
            cursor.execute("SELECT COUNT(*) FROM vidrios WHERE activo = 1")
            total_vidrios = cursor.fetchone()[0] or 0
            
            # Vidrios con stock bajo
            cursor.execute("SELECT COUNT(*) FROM vidrios WHERE activo = 1 AND stock_actual <= stock_minimo")
            stock_bajo = cursor.fetchone()[0] or 0
            
            # Valor total del inventario
            cursor.execute("SELECT SUM(stock_actual * precio_unitario) FROM vidrios WHERE activo = 1")
            valor_total = cursor.fetchone()[0] or 0.0
            
            # Tipos más comunes
            cursor.execute("""
                SELECT tipo, COUNT(*) as cantidad 
                FROM vidrios WHERE activo = 1 
                GROUP BY tipo 
                ORDER BY cantidad DESC 
                LIMIT 5
            """)
            tipos_comunes = [{'tipo': row[0], 'cantidad': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_vidrios': total_vidrios,
                'stock_bajo': stock_bajo,
                'valor_total_inventario': round(valor_total, 2),
                'tipos_mas_comunes': tipos_comunes,
                'porcentaje_stock_bajo': round((stock_bajo / total_vidrios * 100) if total_vidrios > 0 else 0, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def _validar_datos_vidrio(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un vidrio."""
        try:
            # Validaciones requeridas
            if not datos.get('tipo'):
                self.logger.error("El tipo de vidrio es requerido")
                return False
                
            if datos.get('tipo') not in self.TIPOS_VIDRIO:
                self.logger.error(f"Tipo de vidrio inválido: {datos.get('tipo')}")
                return False
                
            # Validar grosor
            grosor = datos.get('grosor')
            if not grosor or not isinstance(grosor, (int, float)) or grosor <= 0:
                self.logger.error("El grosor debe ser un número mayor a 0")
                return False
                
            # Validar dimensiones
            ancho = datos.get('ancho')
            alto = datos.get('alto')
            
            if not ancho or not isinstance(ancho, (int, float)) or ancho <= 0:
                self.logger.error("El ancho debe ser un número mayor a 0")
                return False
                
            if not alto or not isinstance(alto, (int, float)) or alto <= 0:
                self.logger.error("El alto debe ser un número mayor a 0")
                return False
                
            # Validar dimensiones máximas (ejemplo: 6m x 3m)
            if ancho > 6000 or alto > 3000:
                self.logger.warning("Dimensiones muy grandes, verificar si son correctas")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando datos: {e}")
            return False
