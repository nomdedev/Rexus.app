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
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, filename):
            script_name = filename
            return self.sql_loader.load_script(script_name)

logger = logging.getLogger(__name__)

class ReservasManager:
    """Manager especializado para la gestión de reservas de materiales"""
    
    DURACION_DEFAULT_DIAS = 30
    ESTADOS_RESERVA = ['ACTIVA', 'CONSUMIDA', 'LIBERADA', 'CANCELADA']
    TABLA_RESERVAS = 'reservas_materiales'
    
    def __init__(self, db_connection=None, base_utils=None):
        self.db_connection = db_connection
        self.base_utils = base_utils
        self.logger = logger
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'inventario/reservas'
    
    def _validar_conexion(self) -> bool:
        """Valida que exista conexión a la base de datos"""
        return self.db_connection is not None
        
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error creando reserva: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
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
                query = self.sql_manager.get_query('update_consumo_total')

                cursor.execute(query, (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    cantidad_consumida,
                    motivo,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    reserva_id
                ))

                mensaje = f"Reserva consumida totalmente: {cantidad_consumida} unidades"
            else:
                # Consumo parcial - actualizar cantidad reservada
                nueva_cantidad_reservada = cantidad_reservada - cantidad_consumida

                query = self.sql_manager.get_query('update_consumo_parcial')

                observacion_parcial = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consumo parcial: {cantidad_consumida} - {motivo}; "

                cursor.execute(query, (
                    nueva_cantidad_reservada,
                    cantidad_consumida,
                    observacion_parcial,
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error consumiendo reserva: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
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
            # Determinar qué query usar según los filtros
            if obra_id and producto_id:
                query = self.sql_manager.get_query('sql/inventario/select_reservas_activas_obra_producto.sql')
                params = {'obra_id': obra_id, 'producto_id': producto_id}
            elif obra_id:
                query = self.sql_manager.get_query('sql/inventario/select_reservas_activas_por_obra.sql')
                params = {'obra_id': obra_id}
            elif producto_id:
                query = self.sql_manager.get_query('sql/inventario/select_reservas_activas_por_producto.sql')
                params = {'producto_id': producto_id}
            else:
                query = self.sql_manager.get_query('sql/inventario/select_reservas_activas.sql')
                params = {}

            cursor = self.db_connection.cursor()
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
                else:
                    reserva_dict['dias_hasta_vencimiento'] = None
                    reserva_dict['vence_pronto'] = False

                reservas.append(reserva_dict)

            return reservas

        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.logger.error(f"Error obteniendo reservas activas: {e}")
            return []

    def _validar_datos_reserva(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """Valida y sanitiza datos de reserva."""
        try:
            datos_limpios = {}
            errores = []

            # Validaciones separadas
            errores += self._validar_campos_obligatorios(datos, es_actualizacion)
            datos_limpios.update(self._sanitizar_campos_string(datos))
            errores += self._validar_campos_enteros(datos, datos_limpios)
            cantidad_result = self._validar_cantidad_reservada(datos)
            if cantidad_result['error']:
                errores.append(cantidad_result['error'])
            elif cantidad_result['value'] is not None:
                datos_limpios['cantidad_reservada'] = cantidad_result['value']
            fecha_result = self._validar_fecha_vencimiento(datos)
            if fecha_result['error']:
                errores.append(fecha_result['error'])
            elif fecha_result['value'] is not None:
                datos_limpios['fecha_vencimiento'] = fecha_result['value']
            estado_result = self._validar_estado(datos)
            if estado_result['error']:
                errores.append(estado_result['error'])
            elif estado_result['value'] is not None:
                datos_limpios['estado'] = estado_result['value']
            self._asignar_usuario_por_defecto(datos, datos_limpios, es_actualizacion)

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

        except (ValueError, TypeError, AttributeError) as e:
            self.logger.error(f"Error validando datos de reserva: {e}")
            return {
                'valid': False,
                'error': f'Error de validación: {str(e)}',
                'data': None
            }

    def _validar_campos_obligatorios(self, datos: Dict[str, Any], es_actualizacion: bool) -> List[str]:
        errores = []
        if not es_actualizacion:
            campos_obligatorios = ['producto_id', 'obra_id', 'cantidad_reservada', 'motivo']
            for campo in campos_obligatorios:
                if campo not in datos or datos[campo] is None:
                    if campo == 'obra_id' and datos.get('obra_id') == 0:
                        continue
                    errores.append(f"Campo obligatorio faltante: {campo}")
        return errores

    def _sanitizar_campos_string(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        datos_limpios = {}
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
        return datos_limpios

    def _validar_campos_enteros(self, datos: Dict[str, Any], datos_limpios: Dict[str, Any]) -> List[str]:
        errores = []
        campos_enteros = ['producto_id', 'obra_id']
        for campo in campos_enteros:
            if campo in datos and datos[campo] is not None:
                try:
                    valor_entero = int(datos[campo])
                    if campo == 'producto_id' and valor_entero <= 0:
                        errores.append(f"{campo} debe ser un ID válido mayor a 0")
                    else:
                        datos_limpios[campo] = valor_entero
                except (ValueError, TypeError):
                    errores.append(f"Valor entero inválido para {campo}")
        return errores

    def _validar_cantidad_reservada(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if 'cantidad_reservada' in datos:
            try:
                cantidad = float(datos['cantidad_reservada'])
                if cantidad <= 0:
                    return {'error': "La cantidad reservada debe ser mayor a 0", 'value': None}
                else:
                    return {'error': None, 'value': cantidad}
            except (ValueError, TypeError):
                return {'error': "Cantidad reservada inválida", 'value': None}
        return {'error': None, 'value': None}

    def _validar_fecha_vencimiento(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if 'fecha_vencimiento' in datos and datos['fecha_vencimiento']:
            try:
                if isinstance(datos['fecha_vencimiento'], str):
                    datetime.strptime(datos['fecha_vencimiento'][:19], '%Y-%m-%d %H:%M:%S')
                    return {'error': None, 'value': datos['fecha_vencimiento']}
                elif isinstance(datos['fecha_vencimiento'], datetime):
                    return {'error': None, 'value': datos['fecha_vencimiento'].strftime('%Y-%m-%d %H:%M:%S')}
            except ValueError:
                return {'error': "Formato de fecha de vencimiento inválido (YYYY-MM-DD HH:MM:SS)", 'value': None}
        return {'error': None, 'value': None}

    def _validar_estado(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if 'estado' in datos:
            if datos['estado'] in self.ESTADOS_RESERVA:
                return {'error': None, 'value': datos['estado']}
            else:
                return {'error': f"Estado de reserva inválido: {datos['estado']}", 'value': None}
        return {'error': None, 'value': None}

    def _asignar_usuario_por_defecto(self, datos: Dict[str, Any], datos_limpios: Dict[str, Any], es_actualizacion: bool):
        if not es_actualizacion and 'usuario_reserva' not in datos_limpios:
            datos_limpios['usuario_reserva'] = 'SISTEMA'

        return {
            'valid': True,
            'error': None,
            'data': datos_limpios
        }

    def _obtener_reserva_por_id(self, reserva_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por su ID."""
        try:
            cursor = self.db_connection.cursor()
            self.sql_manager.ejecutar_consulta_archivo('sql/inventario/select_reservas_materiales_1.sql', params)
            cursor.execute(query, (reserva_id,))
            fila = cursor.fetchone()
            cursor.close()

            if fila:
                columnas = self._obtener_columnas_tabla_reservas()
                return dict(zip(columnas, fila))
            return None

        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.logger.error(f"Error obteniendo reserva por ID: {e}")
            return None

    def _obtener_ultima_reserva_id(self) -> Optional[int]:
        """Obtiene el ID de la última reserva insertada."""
        try:
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query("02_inventario/reservas", "get_scope_identity")
            cursor.execute(query)
            resultado = cursor.fetchone()
            cursor.close()
            return int(resultado[0]) if resultado and resultado[0] else None
        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.logger.error(f"Error obteniendo último ID: {e}")
            return None

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

            query = f"INSERT INTO {self.TABLA_RESERVAS} ({campos_str}) VALUES ({placeholders})"
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error en fallback: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error en fallback: {str(e)}',
                'reserva_id': None
            }

    def _cambiar_estado_reserva(self, reserva_id: int, nuevo_estado: str, motivo: str) -> Dict[str, Any]:
        """Cambia el estado de una reserva."""
        if not self._validar_conexion():
            return {
                'success': False,
                'error': 'Sin conexión a base de datos'
            }

        try:
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query("02_inventario/reservas", "update_estado_reserva_fallback")
            
            cursor.execute(query, (
                nuevo_estado,
                motivo,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                reserva_id
            ))
            
            self.db_connection.commit()
            cursor.close()

            return {
                'success': True,
                'message': f'Reserva {reserva_id} {nuevo_estado.lower()} exitosamente'
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.logger.error(f"Error cambiando estado: {e}")
            try:
                if self.db_connection:
                    self.db_connection.rollback()
            except (AttributeError, RuntimeError):
                pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

    def _obtener_stock_disponible(self, producto_id: int) -> Optional[float]:
        """Obtiene el stock disponible de un producto."""
        try:
            cursor = self.db_connection.cursor()
            self.sql_manager.ejecutar_consulta_archivo('sql/inventario/select_inventario_2.sql', params)
            cursor.execute(query, (producto_id,))
            resultado = cursor.fetchone()
            cursor.close()
            return float(resultado[0]) if resultado else None
        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.logger.error(f"Error obteniendo stock: {e}")
            return None

    def _obtener_columnas_tabla_reservas(self) -> List[str]:
        """Obtiene las columnas de la tabla de reservas."""
        return [
            'id', 'producto_id', 'obra_id', 'cantidad_reservada', 'motivo',
            'usuario_reserva', 'fecha_creacion', 'fecha_vencimiento', 'estado',
            'cantidad_consumida', 'observaciones', 'fecha_modificacion'
        ]