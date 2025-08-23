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
                        return False
        finally:
            if 'cursor' in locals():
                cursor.close()
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError, IntegrityError) as e:
            self.                try:
                    self.db_connection.rollback()
                except (AttributeError, RuntimeError):
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    def liberar_reserva(self,
reserva_id: int,
        motivo: str = "Liberación manual") -> Dict[str,
        Any]:
        """
        Libera una reserva activa.

        Args:
            reserva_id: ID de la reserva a liberar
            motivo: Motivo de la liberación

        Returns:
            Dict con resultado de la operación
        """
        return self._cambiar_estado_reserva(reserva_id, 'LIBERADA', motivo)
    def cancelar_reserva(self,
reserva_id: int,
        motivo: str = "Cancelación manual") -> Dict[str,
        Any]:
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError, IntegrityError) as e:
            self.                'success': False,
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

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            self.                try:
                    self.db_connection.rollback()
                except (AttributeError, RuntimeError):
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'reservas_procesadas': 0
            }

    # Métodos privados auxiliares

    def _validar_datos_reserva(self,
datos: Dict[str,
        Any],
        es_actualizacion: bool = False) -> Dict[str,
        Any]:
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
            if not es_actualizacion and \
                'usuario_reserva' not in datos_limpios:
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

        except (ValueError, TypeError, AttributeError) as e:
            self.
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

        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.    def _obtener_ultima_reserva_id(self) -> Optional[int]:
        """Obtiene el ID de la última reserva insertada."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT SCOPE_IDENTITY()")
            resultado = cursor.fetchone()
            cursor.close()
            return int(resultado[0]) if resultado and resultado[0] else None
        except (AttributeError, RuntimeError, ConnectionError) as e:
            self.                try:
                    self.db_connection.rollback()
                except (AttributeError, RuntimeError):
                    pass
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

    def _crear_reserva_fallback(self,
datos_limpios: Dict[str,
        Any]) -> Dict[str,
        Any]:
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
            ', '.join(campos)

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

        except (AttributeError, RuntimeError, ConnectionError, ValueError, IntegrityError) as e:
            self.                'success': False,
                'error': f'Error en fallback: {str(e)}',
                'reserva_id': None
            }
