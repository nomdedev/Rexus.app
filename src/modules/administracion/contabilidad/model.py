"""
Modelo de Contabilidad

Maneja la lógica de negocio para:
- Libro contable
- Recibos y comprobantes
- Pagos por obra
- Materiales y compras
"""

from datetime import datetime, date
from decimal import Decimal


class ContabilidadModel:
    """Modelo para gestionar contabilidad."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de contabilidad.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_libro_contable = "libro_contable"
        self.tabla_recibos = "recibos"
        self.tabla_pagos_obra = "pagos_obra"
        self.tabla_pagos_materiales = "pagos_materiales"
        self.tabla_departamentos = "departamentos"
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            tablas = [
                self.tabla_libro_contable,
                self.tabla_recibos,
                self.tabla_pagos_obra,
                self.tabla_pagos_materiales,
                self.tabla_departamentos
            ]

            for tabla in tablas:
                cursor.execute(
                    "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                    (tabla,),
                )
                if cursor.fetchone():
                    print(f"[CONTABILIDAD] Tabla '{tabla}' verificada correctamente.")
                else:
                    print(f"[ADVERTENCIA] La tabla '{tabla}' no existe en la base de datos.")

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error verificando tablas: {e}")

    # MÉTODOS PARA LIBRO CONTABLE

    def obtener_asientos_contables(self, fecha_desde=None, fecha_hasta=None, tipo=None):
        """
        Obtiene asientos del libro contable con filtros opcionales.

        Args:
            fecha_desde (date): Fecha desde
            fecha_hasta (date): Fecha hasta
            tipo (str): Tipo de asiento

        Returns:
            List[Dict]: Lista de asientos contables
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if fecha_desde:
                conditions.append("fecha_asiento >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("fecha_asiento <= ?")
                params.append(fecha_hasta)

            if tipo and tipo != "Todos":
                conditions.append("tipo_asiento = ?")
                params.append(tipo)

            query = f"""
                SELECT 
                    id, numero_asiento, fecha_asiento, tipo_asiento, concepto,
                    referencia, debe, haber, saldo, estado, usuario_creacion,
                    fecha_creacion, fecha_modificacion
                FROM {self.tabla_libro_contable}
                WHERE {" AND ".join(conditions)}
                ORDER BY fecha_asiento DESC, numero_asiento DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            asientos = []
            for fila in resultados:
                asiento = dict(zip(columnas, fila))
                asientos.append(asiento)

            return asientos

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo asientos: {e}")
            return []

    def crear_asiento_contable(self, datos_asiento):
        """
        Crea un nuevo asiento contable.

        Args:
            datos_asiento (dict): Datos del asiento

        Returns:
            int: ID del asiento creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Generar número de asiento
            cursor.execute(f"SELECT MAX(numero_asiento) FROM {self.tabla_libro_contable}")
            ultimo_numero = cursor.fetchone()[0]
            numero_asiento = (ultimo_numero or 0) + 1

            # Calcular saldo
            debe = float(datos_asiento.get('debe', 0))
            haber = float(datos_asiento.get('haber', 0))
            saldo = debe - haber

            query = f"""
                INSERT INTO {self.tabla_libro_contable}
                (numero_asiento, fecha_asiento, tipo_asiento, concepto, referencia,
                 debe, haber, saldo, estado, usuario_creacion, fecha_creacion, fecha_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """

            cursor.execute(query, (
                numero_asiento,
                datos_asiento.get('fecha_asiento'),
                datos_asiento.get('tipo_asiento'),
                datos_asiento.get('concepto'),
                datos_asiento.get('referencia', ''),
                debe,
                haber,
                saldo,
                datos_asiento.get('estado', 'ACTIVO'),
                datos_asiento.get('usuario_creacion', 'SYSTEM')
            ))

            # Obtener ID del asiento creado
            cursor.execute("SELECT @@IDENTITY")
            asiento_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[CONTABILIDAD] Asiento contable creado con ID: {asiento_id}")
            return asiento_id

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error creando asiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_asiento_contable(self, asiento_id, datos_asiento):
        """
        Actualiza un asiento contable existente.

        Args:
            asiento_id (int): ID del asiento
            datos_asiento (dict): Nuevos datos del asiento

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Calcular saldo
            debe = float(datos_asiento.get('debe', 0))
            haber = float(datos_asiento.get('haber', 0))
            saldo = debe - haber

            query = f"""
                UPDATE {self.tabla_libro_contable}
                SET fecha_asiento = ?, tipo_asiento = ?, concepto = ?, referencia = ?,
                    debe = ?, haber = ?, saldo = ?, estado = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """

            cursor.execute(query, (
                datos_asiento.get('fecha_asiento'),
                datos_asiento.get('tipo_asiento'),
                datos_asiento.get('concepto'),
                datos_asiento.get('referencia', ''),
                debe,
                haber,
                saldo,
                datos_asiento.get('estado', 'ACTIVO'),
                asiento_id
            ))

            self.db_connection.commit()
            print(f"[CONTABILIDAD] Asiento {asiento_id} actualizado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error actualizando asiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA RECIBOS

    def obtener_recibos(self, fecha_desde=None, fecha_hasta=None, tipo=None):
        """
        Obtiene recibos con filtros opcionales.

        Args:
            fecha_desde (date): Fecha desde
            fecha_hasta (date): Fecha hasta
            tipo (str): Tipo de recibo

        Returns:
            List[Dict]: Lista de recibos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if fecha_desde:
                conditions.append("fecha_emision >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("fecha_emision <= ?")
                params.append(fecha_hasta)

            if tipo and tipo != "Todos":
                conditions.append("tipo_recibo = ?")
                params.append(tipo)

            query = f"""
                SELECT 
                    id, numero_recibo, fecha_emision, tipo_recibo, concepto,
                    beneficiario, monto, moneda, estado, impreso,
                    usuario_creacion, fecha_creacion
                FROM {self.tabla_recibos}
                WHERE {" AND ".join(conditions)}
                ORDER BY fecha_emision DESC, numero_recibo DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            recibos = []
            for fila in resultados:
                recibo = dict(zip(columnas, fila))
                recibos.append(recibo)

            return recibos

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo recibos: {e}")
            return []

    def crear_recibo(self, datos_recibo):
        """
        Crea un nuevo recibo.

        Args:
            datos_recibo (dict): Datos del recibo

        Returns:
            int: ID del recibo creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Generar número de recibo
            cursor.execute(f"SELECT MAX(numero_recibo) FROM {self.tabla_recibos}")
            ultimo_numero = cursor.fetchone()[0]
            numero_recibo = (ultimo_numero or 0) + 1

            query = f"""
                INSERT INTO {self.tabla_recibos}
                (numero_recibo, fecha_emision, tipo_recibo, concepto, beneficiario,
                 monto, moneda, estado, impreso, usuario_creacion, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(query, (
                numero_recibo,
                datos_recibo.get('fecha_emision'),
                datos_recibo.get('tipo_recibo'),
                datos_recibo.get('concepto'),
                datos_recibo.get('beneficiario'),
                float(datos_recibo.get('monto', 0)),
                datos_recibo.get('moneda', 'USD'),
                datos_recibo.get('estado', 'EMITIDO'),
                datos_recibo.get('impreso', False),
                datos_recibo.get('usuario_creacion', 'SYSTEM')
            ))

            # Obtener ID del recibo creado
            cursor.execute("SELECT @@IDENTITY")
            recibo_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[CONTABILIDAD] Recibo creado con ID: {recibo_id}")
            return recibo_id

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error creando recibo: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def marcar_recibo_impreso(self, recibo_id):
        """
        Marca un recibo como impreso.

        Args:
            recibo_id (int): ID del recibo

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                UPDATE {self.tabla_recibos}
                SET impreso = 1, fecha_impresion = GETDATE()
                WHERE id = ?
            """

            cursor.execute(query, (recibo_id,))
            self.db_connection.commit()
            
            print(f"[CONTABILIDAD] Recibo {recibo_id} marcado como impreso")
            return True

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error marcando recibo como impreso: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA PAGOS POR OBRA

    def obtener_pagos_obra(self, obra_id=None, categoria=None):
        """
        Obtiene pagos por obra con filtros opcionales.

        Args:
            obra_id (int): ID específico de la obra
            categoria (str): Categoría de pago

        Returns:
            List[Dict]: Lista de pagos por obra
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if obra_id:
                conditions.append("obra_id = ?")
                params.append(obra_id)

            if categoria and categoria != "Todas":
                conditions.append("categoria = ?")
                params.append(categoria)

            query = f"""
                SELECT 
                    id, obra_id, concepto, categoria, monto, fecha_pago,
                    metodo_pago, estado, usuario_creacion, fecha_creacion,
                    observaciones
                FROM {self.tabla_pagos_obra}
                WHERE {" AND ".join(conditions)}
                ORDER BY fecha_pago DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            pagos = []
            for fila in resultados:
                pago = dict(zip(columnas, fila))
                pagos.append(pago)

            return pagos

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo pagos por obra: {e}")
            return []

    def crear_pago_obra(self, datos_pago):
        """
        Crea un nuevo pago por obra.

        Args:
            datos_pago (dict): Datos del pago

        Returns:
            int: ID del pago creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_pagos_obra}
                (obra_id, concepto, categoria, monto, fecha_pago, metodo_pago,
                 estado, usuario_creacion, fecha_creacion, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
            """

            cursor.execute(query, (
                datos_pago.get('obra_id'),
                datos_pago.get('concepto'),
                datos_pago.get('categoria'),
                float(datos_pago.get('monto', 0)),
                datos_pago.get('fecha_pago'),
                datos_pago.get('metodo_pago'),
                datos_pago.get('estado', 'PAGADO'),
                datos_pago.get('usuario_creacion', 'SYSTEM'),
                datos_pago.get('observaciones', '')
            ))

            # Obtener ID del pago creado
            cursor.execute("SELECT @@IDENTITY")
            pago_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[CONTABILIDAD] Pago por obra creado con ID: {pago_id}")
            return pago_id

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error creando pago por obra: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    # MÉTODOS PARA PAGOS DE MATERIALES

    def obtener_pagos_materiales(self, proveedor=None, estado=None):
        """
        Obtiene pagos de materiales con filtros opcionales.

        Args:
            proveedor (str): Proveedor específico
            estado (str): Estado del pago

        Returns:
            List[Dict]: Lista de pagos de materiales
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if proveedor and proveedor != "Todos":
                conditions.append("proveedor = ?")
                params.append(proveedor)

            if estado and estado != "Todos":
                conditions.append("estado = ?")
                params.append(estado)

            query = f"""
                SELECT 
                    id, producto, proveedor, cantidad, precio_unitario,
                    total, pagado, pendiente, estado, fecha_compra,
                    fecha_pago, usuario_creacion
                FROM {self.tabla_pagos_materiales}
                WHERE {" AND ".join(conditions)}
                ORDER BY fecha_compra DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            pagos = []
            for fila in resultados:
                pago = dict(zip(columnas, fila))
                pagos.append(pago)

            return pagos

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo pagos de materiales: {e}")
            return []

    def crear_pago_material(self, datos_pago):
        """
        Crea un nuevo pago de material.

        Args:
            datos_pago (dict): Datos del pago

        Returns:
            int: ID del pago creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            cantidad = float(datos_pago.get('cantidad', 0))
            precio_unitario = float(datos_pago.get('precio_unitario', 0))
            total = cantidad * precio_unitario
            pagado = float(datos_pago.get('pagado', 0))
            pendiente = total - pagado

            query = f"""
                INSERT INTO {self.tabla_pagos_materiales}
                (producto, proveedor, cantidad, precio_unitario, total, pagado,
                 pendiente, estado, fecha_compra, fecha_pago, usuario_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                datos_pago.get('producto'),
                datos_pago.get('proveedor'),
                cantidad,
                precio_unitario,
                total,
                pagado,
                pendiente,
                datos_pago.get('estado', 'PENDIENTE'),
                datos_pago.get('fecha_compra'),
                datos_pago.get('fecha_pago'),
                datos_pago.get('usuario_creacion', 'SYSTEM')
            ))

            # Obtener ID del pago creado
            cursor.execute("SELECT @@IDENTITY")
            pago_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[CONTABILIDAD] Pago de material creado con ID: {pago_id}")
            return pago_id

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error creando pago de material: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    # MÉTODOS PARA ESTADÍSTICAS Y REPORTES

    def obtener_estadisticas_financieras(self):
        """
        Obtiene estadísticas financieras generales.

        Returns:
            Dict: Estadísticas financieras
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # Total ingresos y egresos del libro contable
            cursor.execute(f"""
                SELECT 
                    SUM(debe) as total_debe,
                    SUM(haber) as total_haber,
                    SUM(saldo) as saldo_total
                FROM {self.tabla_libro_contable}
                WHERE estado = 'ACTIVO'
            """)
            resultado = cursor.fetchone()
            estadisticas['libro_contable'] = {
                'total_debe': float(resultado[0]) if resultado[0] else 0.0,
                'total_haber': float(resultado[1]) if resultado[1] else 0.0,
                'saldo_total': float(resultado[2]) if resultado[2] else 0.0
            }

            # Total recibos emitidos
            cursor.execute(f"""
                SELECT COUNT(*), SUM(monto)
                FROM {self.tabla_recibos}
                WHERE estado = 'EMITIDO'
            """)
            resultado = cursor.fetchone()
            estadisticas['recibos'] = {
                'total_recibos': resultado[0] if resultado[0] else 0,
                'monto_total': float(resultado[1]) if resultado[1] else 0.0
            }

            # Total pagos por obra
            cursor.execute(f"""
                SELECT COUNT(*), SUM(monto)
                FROM {self.tabla_pagos_obra}
                WHERE estado = 'PAGADO'
            """)
            resultado = cursor.fetchone()
            estadisticas['pagos_obra'] = {
                'total_pagos': resultado[0] if resultado[0] else 0,
                'monto_total': float(resultado[1]) if resultado[1] else 0.0
            }

            # Total pagos de materiales
            cursor.execute(f"""
                SELECT COUNT(*), SUM(total), SUM(pagado), SUM(pendiente)
                FROM {self.tabla_pagos_materiales}
            """)
            resultado = cursor.fetchone()
            estadisticas['pagos_materiales'] = {
                'total_compras': resultado[0] if resultado[0] else 0,
                'monto_total': float(resultado[1]) if resultado[1] else 0.0,
                'total_pagado': float(resultado[2]) if resultado[2] else 0.0,
                'total_pendiente': float(resultado[3]) if resultado[3] else 0.0
            }

            return estadisticas

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_balance_general(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene el balance general para un período.

        Args:
            fecha_desde (date): Fecha desde
            fecha_hasta (date): Fecha hasta

        Returns:
            Dict: Balance general
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            
            conditions = ["estado = 'ACTIVO'"]
            params = []

            if fecha_desde:
                conditions.append("fecha_asiento >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("fecha_asiento <= ?")
                params.append(fecha_hasta)

            query = f"""
                SELECT 
                    tipo_asiento,
                    SUM(debe) as total_debe,
                    SUM(haber) as total_haber,
                    SUM(saldo) as saldo_neto
                FROM {self.tabla_libro_contable}
                WHERE {" AND ".join(conditions)}
                GROUP BY tipo_asiento
            """

            cursor.execute(query, params)
            resultados = cursor.fetchall()

            balance = {}
            for resultado in resultados:
                balance[resultado[0]] = {
                    'debe': float(resultado[1]),
                    'haber': float(resultado[2]),
                    'saldo': float(resultado[3])
                }

            return balance

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo balance: {e}")
            return {}

    def obtener_flujo_caja(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene el flujo de caja para un período.

        Args:
            fecha_desde (date): Fecha desde
            fecha_hasta (date): Fecha hasta

        Returns:
            Dict: Flujo de caja
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            flujo = {}

            conditions = []
            params = []

            if fecha_desde:
                conditions.append("fecha_emision >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("fecha_emision <= ?")
                params.append(fecha_hasta)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # Ingresos por recibos
            cursor.execute(f"""
                SELECT tipo_recibo, SUM(monto)
                FROM {self.tabla_recibos}
                {where_clause}
                GROUP BY tipo_recibo
            """, params)
            
            ingresos = dict(cursor.fetchall())
            flujo['ingresos'] = ingresos

            # Egresos por pagos de obra
            if fecha_desde and fecha_hasta:
                cursor.execute(f"""
                    SELECT categoria, SUM(monto)
                    FROM {self.tabla_pagos_obra}
                    WHERE fecha_pago >= ? AND fecha_pago <= ?
                    GROUP BY categoria
                """, (fecha_desde, fecha_hasta))
            else:
                cursor.execute(f"""
                    SELECT categoria, SUM(monto)
                    FROM {self.tabla_pagos_obra}
                    GROUP BY categoria
                """)
            
            egresos = dict(cursor.fetchall())
            flujo['egresos'] = egresos

            return flujo

        except Exception as e:
            print(f"[ERROR CONTABILIDAD] Error obteniendo flujo de caja: {e}")
            return {}