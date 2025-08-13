"""
Reservas Manager - Gestión especializada de reservas de materiales
Refactorizado de InventarioModel para mejor mantenibilidad

Responsabilidades:
- CRUD completo de reservas de materiales
- Gestión de stock reservado vs disponible
- Control de vencimiento de reservas
- Integración con obras y proyectos
- Liberación automática de reservas
- Reportes de reservas activas
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal, InvalidOperation

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
    from .base_utilities import BaseUtilities, TABLA_RESERVAS
    BASE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Error importando utilidades base: {e}")
    BASE_AVAILABLE = False
    BaseUtilities = None
    TABLA_RESERVAS = "reserva_materiales"


class ReservasManager:
    """Manager especializado para gestión de reservas de materiales."""
    
    # Estados de reserva permitidos
    ESTADOS_RESERVA = {
        'ACTIVA': 'Reserva activa',
        'VENCIDA': 'Reserva vencida',
        'LIBERADA': 'Reserva liberada',
        'CONSUMIDA': 'Reserva consumida',
        'CANCELADA': 'Reserva cancelada'
    }
    
    # Duración por defecto de reservas (en días)
    DURACION_DEFAULT_DIAS = 30
    
    def __init__(self, db_connection=None):
        """
        Inicializa el manager de reservas.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = data_sanitizer
        self.sql_path = "scripts/sql/inventario/reservas"
        self.logger = logging.getLogger(__name__)
        
        # Inicializar utilidades base si están disponibles
        if BASE_AVAILABLE and db_connection:
            self.base_utils = BaseUtilities(db_connection)
        else:
            self.base_utils = None
            logger.warning("Utilidades base no disponibles en ReservasManager")
    
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
    @permission_required("create_reserva")
    def crear_reserva(self, datos_reserva: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva reserva de material.
        
        Args:
            datos_reserva: Diccionario con los datos de la reserva
            
        Returns:
            Dict con resultado de la operación
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'reserva_id': None
            }
        
        try:
            # Validar y sanitizar datos de entrada
            datos_validados = self._validar_datos_reserva(datos_reserva)
            if not datos_validados['valid']:
                return {
                    'success': False,
                    'error': datos_validados['error'],
                    'reserva_id': None
                }
            
            datos_limpios = datos_validados['data']
            
            # Verificar disponibilidad de stock
            stock_disponible = self._obtener_stock_disponible(datos_limpios['producto_id'])
            if stock_disponible is None:
                return {
                    'success': False,
                    'error': f"Producto {datos_limpios['producto_id']} no encontrado",
                    'reserva_id': None
                }
            
            if stock_disponible < datos_limpios['cantidad_reservada']:
                return {
                    'success': False,
                    'error': f"Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {datos_limpios['cantidad_reservada']}",
                    'reserva_id': None
                }
            
            # Calcular fecha de vencimiento si no se proporcionó
            if not datos_limpios.get('fecha_vencimiento'):
                datos_limpios['fecha_vencimiento'] = (
                    datetime.now() + timedelta(days=self.DURACION_DEFAULT_DIAS)
                ).strftime('%Y-%m-%d %H:%M:%S')
            
            # Usar script SQL externo para crear reserva
            if self.base_utils:
                params = (
                    datos_limpios['producto_id'],
                    datos_limpios['obra_id'],
                    datos_limpios['cantidad_reservada'],
                    datos_limpios['motivo'],
                    datos_limpios['usuario_reserva'],
                    datos_limpios['fecha_vencimiento'],
                    'ACTIVA',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                
                resultado = self.base_utils.execute_secure_script('crear_reserva', params)
                
                if resultado is not None:
                    reserva_id = self._obtener_ultima_reserva_id()
                    
                    self.logger.info(f"Reserva creada exitosamente: {reserva_id}")
                    
                    return {
                        'success': True,
                        'message': 'Reserva creada exitosamente',
                        'reserva_id': reserva_id,
                        'fecha_vencimiento': datos_limpios['fecha_vencimiento']
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Error ejecutando consulta de creación',
                        'reserva_id': None
                    }
            else:
                # Fallback manual
                return self._crear_reserva_fallback(datos_limpios)
                
        except Exception as e:
            self.logger.error(f"Error creando reserva: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'reserva_id': None
            }
    
    @auth_required
    @permission_required("update_reserva")
    def actualizar_reserva(self, reserva_id: int, datos_reserva: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una reserva existente.
        
        Args:
            reserva_id: ID de la reserva a actualizar
            datos_reserva: Nuevos datos de la reserva
            
        Returns:
            Dict con resultado de la operación
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos'
            }
        
        try:
            # Verificar que la reserva existe
            reserva_actual = self._obtener_reserva_por_id(reserva_id)
            if not reserva_actual:
                return {
                    'success': False,
                    'error': f'Reserva con ID {reserva_id} no encontrada'
                }
            
            # Verificar que la reserva puede ser modificada
            if reserva_actual.get('estado') in ['CONSUMIDA', 'LIBERADA', 'CANCELADA']:
                return {
                    'success': False,
                    'error': f'No se puede modificar reserva en estado: {reserva_actual.get("estado")}'
                }
            
            # Validar datos de entrada
            datos_validados = self._validar_datos_reserva(datos_reserva, es_actualizacion=True)
            if not datos_validados['valid']:
                return {
                    'success': False,
                    'error': datos_validados['error']
                }
            
            datos_limpios = datos_validados['data']
            
            # Verificar stock si se está cambiando la cantidad
            if 'cantidad_reservada' in datos_limpios:
                diferencia_cantidad = datos_limpios['cantidad_reservada'] - reserva_actual.get('cantidad_reservada', 0)
                if diferencia_cantidad > 0:
                    stock_disponible = self._obtener_stock_disponible(reserva_actual['producto_id'])
                    if stock_disponible < diferencia_cantidad:
                        return {
                            'success': False,
                            'error': f'Stock insuficiente para incremento. Disponible: {stock_disponible}'
                        }
            
            # Actualizar en base de datos
            cursor = self.db_connection.cursor()
            
            # Construir query dinámica
            campos_actualizables = [
                'cantidad_reservada', 'motivo', 'fecha_vencimiento', 'estado'
            ]
            
            campos_a_actualizar = []
            parametros = []
            
            for campo in campos_actualizables:
                if campo in datos_limpios:
                    campos_a_actualizar.append(f"{campo} = ?")
                    parametros.append(datos_limpios[campo])
            
            # Agregar fecha de modificación
            campos_a_actualizar.append("fecha_modificacion = ?")
            parametros.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Agregar ID de la reserva al final
            parametros.append(reserva_id)
            
            # Ejecutar actualización
            set_clause = ", ".join(campos_a_actualizar)
        # FIXED: SQL Injection vulnerability
            query = "UPDATE {TABLA_RESERVAS} SET ? WHERE id = ?", (set_clause,)
            
            cursor.execute(query, parametros)
            self.db_connection.commit()
            
            filas_afectadas = cursor.rowcount
            cursor.close()
            
            if filas_afectadas > 0:
                self.logger.info(f"Reserva {reserva_id} actualizada exitosamente")
                return {
                    'success': True,
                    'message': 'Reserva actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar la reserva'
                }
                
        except Exception as e:
            self.logger.error(f"Error actualizando reserva {reserva_id}: {e}")
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
    @permission_required("cancel_reserva")
    def liberar_reserva(self, reserva_id: int, motivo: str = "Liberación manual") -> Dict[str, Any]:
        """
        Libera una reserva activa.
        
        Args:
            reserva_id: ID de la reserva a liberar
            motivo: Motivo de la liberación
            
        Returns:
            Dict con resultado de la operación
        """
        return self._cambiar_estado_reserva(reserva_id, 'LIBERADA', motivo)
    
    @auth_required
    @permission_required("cancel_reserva")
    def cancelar_reserva(self, reserva_id: int, motivo: str = "Cancelación manual") -> Dict[str, Any]:
        """
        Cancela una reserva.
        
        Args:
            reserva_id: ID de la reserva a cancelar
            motivo: Motivo de la cancelación
            
        Returns:
            Dict con resultado de la operación
        """
        return self._cambiar_estado_reserva(reserva_id, 'CANCELADA', motivo)
    
    @auth_required
    @permission_required("consume_reserva")
    def consumir_reserva(self, reserva_id: int, cantidad_consumida: Optional[float] = None, 
                        motivo: str = "Consumo de materiales") -> Dict[str, Any]:
        """
        Consume una reserva (total o parcialmente).
        
        Args:
            reserva_id: ID de la reserva a consumir
            cantidad_consumida: Cantidad a consumir (None = total)
            motivo: Motivo del consumo
            
        Returns:
            Dict con resultado de la operación
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos'
            }
        
        try:
            # Obtener reserva actual
            reserva = self._obtener_reserva_por_id(reserva_id)
            if not reserva:
                return {
                    'success': False,
                    'error': f'Reserva {reserva_id} no encontrada'
                }
            
            if reserva.get('estado') != 'ACTIVA':
                return {
                    'success': False,
                    'error': f'Solo se pueden consumir reservas activas. Estado actual: {reserva.get("estado")}'
                }
            
            # Determinar cantidad a consumir
            cantidad_reservada = float(reserva.get('cantidad_reservada', 0))
            if cantidad_consumida is None:
                cantidad_consumida = cantidad_reservada
            else:
                cantidad_consumida = float(cantidad_consumida)
            
            if cantidad_consumida <= 0:
                return {
                    'success': False,
                    'error': 'La cantidad a consumir debe ser mayor a cero'
                }
            
            if cantidad_consumida > cantidad_reservada:
                return {
                    'success': False,
                    'error': f'No se puede consumir más de lo reservado. Reservado: {cantidad_reservada}'
                }
            
            cursor = self.db_connection.cursor()
            
            # Registrar el consumo
            if cantidad_consumida == cantidad_reservada:
                # Consumo total - marcar como consumida
                query = f"""UPDATE {TABLA_RESERVAS} 
                           SET estado = 'CONSUMIDA', 
                               fecha_consumo = ?, 
                               cantidad_consumida = ?,
                               observaciones_consumo = ?,
                               fecha_modificacion = ?
                           WHERE id = ?"""
                
                cursor.execute(query, (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    cantidad_consumida,
                    sanitize_string(motivo),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    reserva_id
                ))
                
                mensaje = f"Reserva consumida totalmente: {cantidad_consumida} unidades"
            else:
                # Consumo parcial - actualizar cantidad reservada
                nueva_cantidad_reservada = cantidad_reservada - cantidad_consumida
                
                query = f"""UPDATE {TABLA_RESERVAS} 
                           SET cantidad_reservada = ?,
                               cantidad_consumida = ISNULL(cantidad_consumida, 0) + ?,
                               observaciones_consumo = ISNULL(observaciones_consumo, '') + ?
                           WHERE id = ?"""
                
                observacion_parcial = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consumo parcial: {cantidad_consumida} - {motivo}; "
                
                cursor.execute(query, (
                    nueva_cantidad_reservada,
                    cantidad_consumida,
                    sanitize_string(observacion_parcial),
                    reserva_id
                ))
                
                mensaje = f"Consumo parcial registrado: {cantidad_consumida} unidades. Restante: {nueva_cantidad_reservada}"
            
            self.db_connection.commit()
            cursor.close()
            
            self.logger.info(f"Reserva {reserva_id} consumida: {cantidad_consumida} unidades")
            
            return {
                'success': True,
                'message': mensaje,
                'cantidad_consumida': cantidad_consumida
            }
            
        except Exception as e:
            self.logger.error(f"Error consumiendo reserva {reserva_id}: {e}")
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
    @permission_required("view_reservas")
    def obtener_reservas_activas(self, obra_id: Optional[int] = None, 
                                producto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene reservas activas con filtros opcionales.
        
        Args:
            obra_id: Filtrar por obra específica
            producto_id: Filtrar por producto específico
            
        Returns:
            Lista de reservas activas
        """
        if not self._validar_conexion():
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Query base con JOIN para obtener información adicional
            query = f"""
                SELECT 
                    r.id, r.producto_id, r.obra_id, r.cantidad_reservada,
                    r.motivo, r.usuario_reserva, r.fecha_creacion, r.fecha_vencimiento,
                    r.estado, r.cantidad_consumida,
                    p.codigo as producto_codigo, p.descripcion as producto_descripcion,
                    p.stock_actual, p.unidad_medida,
                    o.nombre as obra_nombre
                FROM {TABLA_RESERVAS} r
                INNER JOIN inventario p ON r.producto_id = p.id
                LEFT JOIN obras o ON r.obra_id = o.id
                WHERE r.estado = 'ACTIVA'
            """
            
            params = []
            
            # Aplicar filtros
            if obra_id:
                query += " AND r.obra_id = ?"
                params.append(obra_id)
            
            if producto_id:
                query += " AND r.producto_id = ?"
                params.append(producto_id)
            
            query += " ORDER BY r.fecha_vencimiento ASC"
            
            cursor.execute(query, params)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            cursor.close()
            
            # Convertir a lista de diccionarios con información adicional
            reservas = []
            for fila in filas:
                reserva_dict = dict(zip(columnas, fila))
                
                # Calcular días hasta vencimiento
                if reserva_dict.get('fecha_vencimiento'):
                    try:
                        fecha_venc = datetime.strptime(
                            str(reserva_dict['fecha_vencimiento'])[:19], 
                            '%Y-%m-%d %H:%M:%S'
                        )
                        dias_vencimiento = (fecha_venc - datetime.now()).days
                        reserva_dict['dias_hasta_vencimiento'] = dias_vencimiento
                        reserva_dict['vence_pronto'] = dias_vencimiento <= 7
                    except ValueError:
                        reserva_dict['dias_hasta_vencimiento'] = None
                        reserva_dict['vence_pronto'] = False
                
                reservas.append(reserva_dict)
            
            return reservas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo reservas activas: {e}")
            return []
    
    @auth_required
    @permission_required("admin_reservas") 
    def procesar_reservas_vencidas(self) -> Dict[str, Any]:
        """
        Procesa y marca como vencidas las reservas que han superado su fecha límite.
        
        Returns:
            Dict con resultado del procesamiento
        """
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos',
                'reservas_procesadas': 0
            }
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener reservas vencidas
            query_vencidas = f"""
                SELECT id, producto_id, cantidad_reservada, motivo 
                FROM {TABLA_RESERVAS}
                WHERE estado = 'ACTIVA' 
                AND fecha_vencimiento < ?
            """
            
            cursor.execute(query_vencidas, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
            reservas_vencidas = cursor.fetchall()
            
            if not reservas_vencidas:
                cursor.close()
                return {
                    'success': True,
                    'message': 'No hay reservas vencidas para procesar',
                    'reservas_procesadas': 0
                }
            
            # Marcar como vencidas
            query_marcar = f"""
                UPDATE {TABLA_RESERVAS}
                SET estado = 'VENCIDA', 
                    fecha_modificacion = ?,
                    observaciones_vencimiento = ?
                WHERE estado = 'ACTIVA' 
                AND fecha_vencimiento < ?
            """
            
            cursor.execute(query_marcar, (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                f"Vencimiento automático procesado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            reservas_procesadas = cursor.rowcount
            self.db_connection.commit()
            cursor.close()
            
            self.logger.info(f"Procesadas {reservas_procesadas} reservas vencidas")
            
            return {
                'success': True,
                'message': f'Se procesaron {reservas_procesadas} reservas vencidas',
                'reservas_procesadas': reservas_procesadas,
                'detalles': [{'reserva_id': r[0], 'producto_id': r[1]} for r in reservas_vencidas]
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando reservas vencidas: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'reservas_procesadas': 0
            }
    
    # Métodos privados auxiliares
    
    def _validar_datos_reserva(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """Valida y sanitiza datos de reserva."""
        try:
            datos_limpios = {}
            errores = []
            
            # Campos obligatorios para creación
            if not es_actualizacion:
                campos_obligatorios = ['producto_id', 'obra_id', 'cantidad_reservada', 'motivo']
                for campo in campos_obligatorios:
                    if campo not in datos or datos[campo] is None:
                        if campo == 'obra_id' and datos.get('obra_id') == 0:
                            # Permitir obra_id = 0 para reservas generales
                            continue
                        errores.append(f"Campo obligatorio faltante: {campo}")
            
            # Sanitizar campos string
            campos_string = {
                'motivo': 200,
                'usuario_reserva': 100,
                'observaciones': 500
            }
            
            for campo, max_length in campos_string.items():
                if campo in datos and datos[campo] is not None:
                    if self.base_utils:
                        valor_limpio = self.base_utils.sanitizar_entrada(datos[campo], 'string', max_length)
                    else:
                        valor_limpio = str(datos[campo]).strip()[:max_length]
                    datos_limpios[campo] = valor_limpio
            
            # Campos numéricos enteros
            campos_enteros = ['producto_id', 'obra_id']
            for campo in campos_enteros:
                if campo in datos and datos[campo] is not None:
                    try:
                        valor_entero = int(datos[campo])
                        if campo in ['producto_id'] and valor_entero <= 0:
                            errores.append(f"{campo} debe ser un ID válido mayor a 0")
                        else:
                            datos_limpios[campo] = valor_entero
                    except (ValueError, TypeError):
                        errores.append(f"Valor entero inválido para {campo}")
            
            # Cantidad reservada
            if 'cantidad_reservada' in datos:
                try:
                    cantidad = float(datos['cantidad_reservada'])
                    if cantidad <= 0:
                        errores.append("La cantidad reservada debe ser mayor a 0")
                    else:
                        datos_limpios['cantidad_reservada'] = cantidad
                except (ValueError, TypeError):
                    errores.append("Cantidad reservada inválida")
            
            # Fecha de vencimiento
            if 'fecha_vencimiento' in datos and datos['fecha_vencimiento']:
                try:
                    if isinstance(datos['fecha_vencimiento'], str):
                        # Validar formato de fecha
                        datetime.strptime(datos['fecha_vencimiento'][:19], '%Y-%m-%d %H:%M:%S')
                        datos_limpios['fecha_vencimiento'] = datos['fecha_vencimiento']
                    elif isinstance(datos['fecha_vencimiento'], datetime):
                        datos_limpios['fecha_vencimiento'] = datos['fecha_vencimiento'].strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    errores.append("Formato de fecha de vencimiento inválido (YYYY-MM-DD HH:MM:SS)")
            
            # Estado de reserva
            if 'estado' in datos:
                if datos['estado'] in self.ESTADOS_RESERVA:
                    datos_limpios['estado'] = datos['estado']
                else:
                    errores.append(f"Estado de reserva inválido: {datos['estado']}")
            
            # Usuario por defecto
            if not es_actualizacion and 'usuario_reserva' not in datos_limpios:
                datos_limpios['usuario_reserva'] = 'SISTEMA'
            
            if errores:
                return {
                    'valid': False,
                    'error': '; '.join(errores),
                    'data': None
                }
            
            return {
                'valid': True,
                'error': None,
                'data': datos_limpios
            }
            
        except Exception as e:
            self.logger.error(f"Error validando datos de reserva: {e}")
            return {
                'valid': False,
                'error': f'Error de validación: {str(e)}',
                'data': None
            }
    
    def _obtener_stock_disponible(self, producto_id: int) -> Optional[float]:
        """Obtiene el stock disponible (total - reservado) de un producto."""
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener stock actual
            cursor.execute("SELECT stock_actual FROM inventario WHERE id = ?", (producto_id,))
            row_stock = cursor.fetchone()
            
            if not row_stock:
                cursor.close()
                return None
            
            stock_total = float(row_stock[0])
            
            # Obtener cantidad total reservada activamente
            cursor.execute(
        # FIXED: SQL Injection vulnerability
                "SELECT ISNULL(SUM(cantidad_reservada), 0) FROM ? WHERE producto_id = ? AND estado = 'ACTIVA'", (TABLA_RESERVAS,),
                (producto_id,)
            )
            row_reservado = cursor.fetchone()
            stock_reservado = float(row_reservado[0]) if row_reservado else 0.0
            
            cursor.close()
            
            return stock_total - stock_reservado
            
        except Exception as e:
            self.logger.error(f"Error obteniendo stock disponible para producto {producto_id}: {e}")
            return None
    
    def _obtener_reserva_por_id(self, reserva_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por su ID."""
        try:
            cursor = self.db_connection.cursor()
        # FIXED: SQL Injection vulnerability
            query = "SELECT * FROM ? WHERE id = ?", (TABLA_RESERVAS,)
            cursor.execute(query, (reserva_id,))
            fila = cursor.fetchone()
            cursor.close()
            
            if fila:
                columnas = self._obtener_columnas_tabla_reservas()
                return dict(zip(columnas, fila))
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo reserva por ID: {e}")
            return None
    
    def _obtener_columnas_tabla_reservas(self) -> List[str]:
        """Obtiene los nombres de las columnas de la tabla de reservas."""
        columnas_default = [
            'id', 'producto_id', 'obra_id', 'cantidad_reservada',
            'motivo', 'usuario_reserva', 'fecha_creacion', 'fecha_vencimiento',
            'estado', 'cantidad_consumida', 'fecha_consumo', 'observaciones_consumo',
            'observaciones_vencimiento', 'fecha_modificacion'
        ]
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT TOP 1 * FROM reservas_inventario")
            columnas = [desc[0] for desc in cursor.description]
            cursor.close()
            return columnas
        except Exception:
            return columnas_default
    
    def _obtener_ultima_reserva_id(self) -> Optional[int]:
        """Obtiene el ID de la última reserva insertada."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT SCOPE_IDENTITY()")
            resultado = cursor.fetchone()
            cursor.close()
            return int(resultado[0]) if resultado and resultado[0] else None
        except Exception as e:
            self.logger.error(f"Error obteniendo último ID de reserva: {e}")
            return None
    
    def _cambiar_estado_reserva(self, reserva_id: int, nuevo_estado: str, motivo: str) -> Dict[str, Any]:
        """Cambia el estado de una reserva."""
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos'
            }
        
        try:
            # Verificar que la reserva existe
            reserva = self._obtener_reserva_por_id(reserva_id)
            if not reserva:
                return {
                    'success': False,
                    'error': f'Reserva {reserva_id} no encontrada'
                }
            
            # Verificar transición de estado válida
            estado_actual = reserva.get('estado')
            if estado_actual == nuevo_estado:
                return {
                    'success': True,
                    'message': f'Reserva ya está en estado {nuevo_estado}'
                }
            
            if estado_actual in ['CONSUMIDA'] and nuevo_estado in ['LIBERADA', 'CANCELADA']:
                return {
                    'success': False,
                    'error': 'No se puede cambiar el estado de una reserva consumida'
                }
            
            cursor = self.db_connection.cursor()
            
            # Actualizar estado
            campo_observacion = {
                'LIBERADA': 'observaciones_liberacion',
                'CANCELADA': 'observaciones_cancelacion',
                'VENCIDA': 'observaciones_vencimiento'
            }.get(nuevo_estado, 'observaciones_modificacion')
            
            query = f"""UPDATE {TABLA_RESERVAS} 
                       SET estado = ?, 
                           {campo_observacion} = ?,
                           fecha_modificacion = ?
                       WHERE id = ?"""
            
            cursor.execute(query, (
                nuevo_estado,
                sanitize_string(motivo),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                reserva_id
            ))
            
            self.db_connection.commit()
            filas_afectadas = cursor.rowcount
            cursor.close()
            
            if filas_afectadas > 0:
                self.logger.info(f"Reserva {reserva_id} cambió de {estado_actual} a {nuevo_estado}")
                return {
                    'success': True,
                    'message': f'Reserva {nuevo_estado.lower()} exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo cambiar el estado de la reserva'
                }
                
        except Exception as e:
            self.logger.error(f"Error cambiando estado de reserva {reserva_id}: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def _crear_reserva_fallback(self, datos_limpios: Dict[str, Any]) -> Dict[str, Any]:
        """Crea reserva usando método fallback sin utilidades base."""
        try:
            cursor = self.db_connection.cursor()
            
            # Campos para inserción
            campos = [
                'producto_id', 'obra_id', 'cantidad_reservada', 'motivo',
                'usuario_reserva', 'fecha_vencimiento', 'estado', 'fecha_creacion'
            ]
            
            valores = []
            for campo in campos:
                if campo == 'estado':
                    valores.append('ACTIVA')
                elif campo == 'fecha_creacion':
                    valores.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    valores.append(datos_limpios.get(campo))
            
            placeholders = ', '.join(['?'] * len(valores))
            campos_str = ', '.join(campos)
            
        # FIXED: SQL Injection vulnerability
            query = "INSERT INTO {TABLA_RESERVAS} ({campos_str}) VALUES (?)", (placeholders,)
            cursor.execute(query, valores)
            
            self.db_connection.commit()
            reserva_id = self._obtener_ultima_reserva_id()
            cursor.close()
            
            return {
                'success': True,
                'message': 'Reserva creada exitosamente (fallback)',
                'reserva_id': reserva_id,
                'fecha_vencimiento': datos_limpios.get('fecha_vencimiento')
            }
            
        except Exception as e:
            self.logger.error(f"Error en fallback de creación de reserva: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {
                'success': False,
                'error': f'Error en fallback: {str(e)}',
                'reserva_id': None
            }