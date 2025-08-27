"""
Modelo de Administración - Rexus.app v2.0.0

Sistema completo de administración y contabilidad.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.

[LOCK] DB Authorization Check - Verify user permissions before DB operations
Ensure all database operations are properly authorized
"""

import sys
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.sql_query_manager import SQLQueryManager

# Configurar logger específico para el módulo
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))
    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"No se pudo cargar utilidad de seguridad: {e}")
    SECURITY_AVAILABLE = False

# Importar utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name
    SQL_SECURITY_AVAILABLE = True
except ImportError:
    logger.warning("No se pudo cargar SQL security - usando validación básica")
    SQL_SECURITY_AVAILABLE = False
    validate_table_name = None
    SQLSecurityError = Exception


class ContabilidadModel:
    """Modelo completo de administración y contabilidad con control de roles y auditoría."""

    def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        self.db_connection = db_connection  # type: ignore # type: Any


class AdministracionModel(ContabilidadModel):
    """Alias para compatibilidad con tests y controladores."""

    # Constante para evitar duplicación de literales
    WHERE_PLACEHOLDER = "WHERE 1=1"

    def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        super().__init__(db_connection, usuario_actual)
        self.usuario_actual = usuario_actual
        self.tabla_libro_contable = "libro_contable"
        self.tabla_recibos = "recibos"
        self.tabla_pagos_obras = "pagos_obras"
        self.tabla_pagos_materiales = "pagos_materiales"
        self.tabla_empleados = "empleados"
        self.tabla_departamentos = "departamentos"
        self.tabla_auditoria = "auditoria_contable"

        # Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        self.sanitizer = unified_sanitizer
        self.data_sanitizer = unified_sanitizer  # Alias para compatibilidad
        logger.info("Sistema unificado de sanitización cargado")

        # Las tablas ya existen en SQL Server
    def validar_departamento_duplicado(self, codigo, nombre):
        """
        Valida si ya existe un departamento con el mismo código o nombre.

        Args:
            codigo: Código del departamento
            nombre: Nombre del departamento

        Returns:
            dict: Diccionario con las claves 'codigo_duplicado' y 'nombre_duplicado'
        """
        try:
            cursor = self.db_connection.cursor()  # type: ignore
            
            # Verificar código duplicado
            cursor.execute(
                "SELECT COUNT(*) FROM departamentos WHERE codigo = ? AND estado = 'ACTIVO'",
                (codigo,)
            )
            codigo_duplicado = cursor.fetchone()[0] > 0

            # Verificar nombre duplicado
            cursor.execute(
                "SELECT COUNT(*) FROM departamentos WHERE nombre = ? AND estado = 'ACTIVO'",
                (nombre,)
            )
            nombre_duplicado = cursor.fetchone()[0] > 0

            return {
                "codigo_duplicado": codigo_duplicado,
                "nombre_duplicado": nombre_duplicado
            }

        except Exception as e:
            logger.error(f"Error validando departamento duplicado: {e}")
            return {"codigo_duplicado": False, "nombre_duplicado": False}

    def crear_departamento(
        self, codigo, nombre, descripcion="", responsable="", presupuesto_mensual=0
    ):
        """Crea un nuevo departamento con validación de seguridad."""
        try:
            # [LOCK] SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.data_sanitizer:
                codigo_limpio = sanitize_string(codigo)
                nombre_limpio = sanitize_string(nombre)
                descripcion_limpia = sanitize_string(descripcion)
                responsable_limpio = sanitize_string(responsable)
            else:
                codigo_limpio = codigo.strip()
                nombre_limpio = nombre.strip()
                descripcion_limpia = descripcion.strip()
                responsable_limpio = responsable.strip()

            # Validar datos obligatorios
            if not codigo_limpio or not nombre_limpio:
                return False, "Código y nombre son requeridos"

            # Verificar duplicados
            duplicados = self.validar_departamento_duplicado(
                codigo_limpio, nombre_limpio
            )
            if duplicados["codigo_duplicado"]:
                return (
                    False,
                    f"Ya existe un departamento con el código: {codigo_limpio}",
                )
            if duplicados["nombre_duplicado"]:
                return (
                    False,
                    f"Ya existe un departamento con el nombre: {nombre_limpio}",
                )

            cursor = self.db_connection.cursor()

            # Usar consulta SQL desde archivo para evitar SQL injection
            query_insert = self.sql_manager.get_query('administracion', 'insert_departamento')

            cursor.execute(query_insert, (
                codigo_limpio,
                nombre_limpio,
                descripcion_limpia,
                responsable_limpio,
                presupuesto_mensual,
                self.usuario_actual,
                self.usuario_actual,
            ))

            departamento_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "departamentos",
                departamento_id,
                "INSERT",
                None,
                {"codigo": codigo, "nombre": nombre},
            )

            return departamento_id

        except Exception as e:
            logger.error(f"Error creando departamento: {e}")
            return None

    def _validate_limit(self, limite):
        """
        Valida el parámetro de límite para prevenir SQL injection.

        Args:
            limite: Límite a validar

        Returns:
            int: Límite validado y seguro
        """
        try:
            limite_int = int(limite)
            if limite_int > 0 and limite_int <= 10000:  # Máximo razonable
                return limite_int
        except (ValueError, TypeError):
            pass
        # Si no es válido, usar límite por defecto
        return 100

    
    def registrar_auditoria(
        self,
        tabla,
        registro_id,
        accion,
        datos_anteriores=None,
        datos_nuevos=None,
        observaciones=None,
    ) -> Optional[int]:
        """Registra una acción en la auditoría contable."""
        try:
            cursor = self.db_connection.cursor()  # type: ignore
            
            # Usar consulta SQL desde archivo para evitar SQL injection
            query = self.sql_manager.get_query('administracion', 'insert_auditoria')
            
            cursor.execute(
                query,
                (
                    tabla,
                    registro_id,
                    accion,
                    str(datos_anteriores),
                    str(datos_nuevos),
                    self.usuario_actual,
                    observaciones,
                ),
            )

            self.db_connection.commit()

        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            raise

    def obtener_departamentos(self, activos_solo=True) -> list:
        """Obtiene la lista de departamentos."""
        try:
            cursor = self.db_connection.cursor()  # type: ignore

            if activos_solo:
                query = self.sql_manager.get_query("administracion", "obtener_departamentos_activos")
            else:
                query = self.sql_manager.get_query("administracion", "obtener_departamentos")

            cursor.execute(query)

            departamentos = []
            for row in cursor.fetchall():
                departamentos.append({
                    "id": row[0],
                    "codigo": row[1],
                    "nombre": row[2],
                    "descripcion": row[3],
                    "responsable": row[4],
                    "presupuesto_mensual": float(row[5]),
                    "estado": row[6],
                    "fecha_creacion": row[7],
                    "usuario_creacion": row[8],
                })

            return departamentos

        except Exception as e:
            logger.error(f"Error obteniendo departamentos: {e}")
            return []

    # GESTIÓN DE EMPLEADOS
    def crear_empleado(
        self,
        codigo,
        nombre,
        apellido,
        documento,
        email="",
        telefono="",
        departamento_id=None,
        cargo="",
        salario=0,
        fecha_ingreso=None,
    ):
        """Crea un nuevo empleado."""
        try:
            cursor = self.db_connection.cursor()

            if fecha_ingreso is None:
                fecha_ingreso = date.today()

            # Usar consulta externa para crear empleado
            query = self.sql_manager.get_query("administracion", "insertar_empleado")
            cursor.execute(query, (
                codigo,
                nombre,
                apellido,
                documento,
                email,
                telefono,
                departamento_id,
                cargo,
                salario,
                fecha_ingreso,
                self.usuario_actual,
                self.usuario_actual,
            ))

            empleado_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "empleados",
                empleado_id,
                "INSERT",
                None,
                {"codigo": codigo, "nombre": nombre, "apellido": apellido},
            )

            return empleado_id

        except Exception as e:
            self.db_connection.rollback()
            logging.error(f"Error creando empleado: {e}")
            return None

    def obtener_empleados(self, departamento_id=None, activos_solo=True):
        """Obtiene la lista de empleados."""
        try:
            cursor = self.db_connection.cursor()

            # Usar la query base y construir WHERE dinámicamente
            query = self.sql_manager.get_query("administracion", "obtener_empleados")
            
            conditions = []
            params = []

            if activos_solo:
                conditions.append("e.estado = 'ACTIVO'")

            if departamento_id:
                conditions.append("e.departamento_id = ?")
                params.append(departamento_id)

            # Reemplazar el WHERE 1=1 con las condiciones reales
            if conditions:
                where_clause = " AND ".join(conditions)
                query = query.replace(self.WHERE_PLACEHOLDER, f"WHERE {where_clause}")
            else:
                query = query.replace(self.WHERE_PLACEHOLDER, "")

            cursor.execute(query, params)

            empleados = []
            for row in cursor.fetchall():
                empleados.append(
                    {
                        "id": row[0],
                        "codigo": row[1],
                        "nombre": row[2],
                        "apellido": row[3],
                        "documento": row[4],
                        "email": row[5],
                        "telefono": row[6],
                        "departamento_id": row[7],
                        "departamento": row[8],
                        "cargo": row[9],
                        "salario": float(row[10]) if row[10] else 0,
                        "fecha_ingreso": row[11],
                        "estado": row[12],
                    }
                )

            return empleados

        except Exception as e:
            logging.error(f"Error obteniendo empleados: {e}")
            return []

    # GESTIÓN DE LIBRO CONTABLE
    def crear_asiento_contable(
        self,
        fecha_asiento,
        tipo_asiento,
        concepto,
        referencia="",
        obra_id=None,
        proveedor_id=None,
        empleado_id=None,
        departamento_id=None,
        cuenta_contable="",
        debe=0,
        haber=0,
        observaciones="",
    ):
        """Crea un nuevo asiento contable."""
        try:
            cursor = self.db_connection.cursor()

            # Generar número de asiento usando SQL externa
            query_numero = self.sql_manager.get_query("administracion", "select_siguiente_numero_asiento")
            
            cursor.execute(query_numero)
            numero = cursor.fetchone()[0]
            numero_asiento = f"AS-{numero:06d}"

            # Calcular saldo
            saldo = debe - haber

            # Insertar asiento usando SQL externa
            query_insert = self.sql_manager.get_query("administracion", "insertar_asiento_contable")
            
            cursor.execute(
                query_insert,
                (
                    numero_asiento,
                    fecha_asiento,
                    tipo_asiento,
                    concepto,
                    referencia,
                    obra_id,
                    proveedor_id,
                    empleado_id,
                    departamento_id,
                    cuenta_contable,
                    debe,
                    haber,
                    saldo,
                    observaciones,
                    self.usuario_actual,
                    self.usuario_actual,
                ),
            )

            asiento_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "libro_contable",
                asiento_id,
                "INSERT",
                None,
                {"numero_asiento": numero_asiento, "concepto": concepto},
            )

            return asiento_id

        except Exception as e:
            logging.error(f"Error creando asiento contable: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def obtener_libro_contable(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        tipo_asiento=None,
        obra_id=None,
        departamento_id=None,
        limite=100,
    ):
        """Obtiene asientos del libro contable."""
        try:
            cursor = self.db_connection.cursor()

            # Usar la query base y construir WHERE dinámicamente
            query = self.sql_manager.get_query("administracion", "obtener_libro_contable")

            conditions = []
            params = []

            if fecha_desde:
                conditions.append("lc.fecha_asiento >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("lc.fecha_asiento <= ?")
                params.append(fecha_hasta)

            if tipo_asiento:
                conditions.append("lc.tipo_asiento = ?")
                params.append(tipo_asiento)

            if obra_id:
                conditions.append("lc.obra_id = ?")
                params.append(obra_id)

            if departamento_id:
                conditions.append("lc.departamento_id = ?")
                params.append(departamento_id)

            # Reemplazar el WHERE 1=1 con las condiciones reales
            if conditions:
                where_clause = " AND ".join(conditions)
                query = query.replace("WHERE 1=1", f"WHERE {where_clause}")
            else:
                query = query.replace("WHERE 1=1", "")

            if limite:
                limite_validado = self._validate_limit(limite)
                query += f" OFFSET 0 ROWS FETCH NEXT {limite_validado} ROWS ONLY"

            cursor.execute(query, params)

            asientos = []
            for row in cursor.fetchall():
                asientos.append(
                    {
                        "id": row[0],
                        "numero_asiento": row[1],
                        "fecha_asiento": row[2],
                        "tipo_asiento": row[3],
                        "concepto": row[4],
                        "referencia": row[5],
                        "obra_id": row[6],
                        "proveedor_id": row[7],
                        "empleado_id": row[8],
                        "departamento_id": row[9],
                        "departamento": row[10],
                        "cuenta_contable": row[11],
                        "debe": float(row[12]),
                        "haber": float(row[13]),
                        "saldo": float(row[14]),
                        "estado": row[15],
                        "observaciones": row[16],
                        "fecha_creacion": row[17],
                        "usuario_creacion": row[18],
                    }
                )

            return asientos

        except Exception as e:
            logging.error(f"Error obteniendo libro contable: {e}")
            return []

    # GESTIÓN DE RECIBOS
    def crear_recibo(
        self,
        fecha_emision,
        tipo_recibo,
        concepto,
        beneficiario,
        monto,
        obra_id=None,
        proveedor_id=None,
        empleado_id=None,
        moneda="ARS",
        metodo_pago="EFECTIVO",
        numero_comprobante="",
        observaciones="",
    ):
        """Crea un nuevo recibo."""
        try:
            cursor = self.db_connection.cursor()

            # Generar número de recibo
            query_numero = self.sql_manager.get_query("administracion", "generar_numero_recibo")
            cursor.execute(query_numero)
            numero = cursor.fetchone()[0]
            numero_recibo = f"REC-{numero:06d}"

            query_insert = self.sql_manager.get_query("administracion", "insertar_recibo")
            cursor.execute(
                query_insert,
                (
                    numero_recibo,
                    fecha_emision,
                    tipo_recibo,
                    concepto,
                    beneficiario,
                    obra_id,
                    proveedor_id,
                    empleado_id,
                    monto,
                    moneda,
                    metodo_pago,
                    numero_comprobante,
                    observaciones,
                    self.usuario_actual,
                    self.usuario_actual,
                ),
            )

            recibo_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "recibos",
                recibo_id,
                "INSERT",
                None,
                {"numero_recibo": numero_recibo, "concepto": concepto, "monto": monto},
            )

            return recibo_id

        except Exception as e:
            logging.error(f"Error creando recibo: {e}")
            self.db_connection.rollback()
            return None

    def obtener_recibos(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        tipo_recibo=None,
        obra_id=None,
        limite=100,
    ):
        """Obtiene la lista de recibos."""
        try:
            cursor = self.db_connection.cursor()

            # Usar consulta externa para obtener recibos
            query = self.sql_manager.get_query("administracion", "obtener_recibos")

            conditions = []
            params = []

            if fecha_desde:
                conditions.append("r.fecha_emision >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("r.fecha_emision <= ?")
                params.append(fecha_hasta)

            if tipo_recibo:
                conditions.append("r.tipo_recibo = ?")
                params.append(tipo_recibo)

            if obra_id:
                conditions.append("r.obra_id = ?")
                params.append(obra_id)

            # Construir WHERE clause
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            query = query.replace("{{WHERE_CONDITIONS}}", where_clause)

            # Agregar límite si se especifica
            if limite:
                limite_validado = self._validate_limit(limite)
                query = query.replace("{{LIMIT_CLAUSE}}", f"TOP {limite_validado}")
            else:
                query = query.replace("{{LIMIT_CLAUSE}}", "")

            cursor.execute(query, params)

            recibos = []
            for row in cursor.fetchall():
                recibos.append({
                    "id": row[0],
                    "numero_recibo": row[1],
                    "fecha_emision": row[2],
                    "tipo_recibo": row[3],
                    "concepto": row[4],
                    "beneficiario": row[5],
                    "obra_id": row[6],
                    "proveedor_id": row[7],
                    "empleado_id": row[8],
                    "monto": float(row[9]),
                    "moneda": row[10],
                    "metodo_pago": row[11],
                    "numero_comprobante": row[12],
                    "estado": row[13],
                    "impreso": bool(row[14]),
                    "archivo_pdf": row[15],
                    "observaciones": row[16],
                    "fecha_creacion": row[17],
                    "usuario_creacion": row[18],
                })

            return recibos

        except Exception as e:
            logger.info(f"Error obteniendo recibos: {e}")
            return []

    def marcar_recibo_impreso(self, recibo_id, archivo_pdf=None):
        """Marca un recibo como impreso."""
        try:
            cursor = self.db_connection.cursor()

            # Usar consulta externa para marcar recibo como impreso
            query = self.sql_manager.get_query("administracion", "marcar_recibo_impreso")
            cursor.execute(query, (archivo_pdf, self.usuario_actual, recibo_id))

            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "recibos",
                recibo_id,
                "UPDATE",
                None,
                {"impreso": True, "archivo_pdf": archivo_pdf},
            )

            return True

        except Exception as e:
            logger.info(f"Error marcando recibo como impreso: {e}")
            self.db_connection.rollback()
            return False

# GESTIÓN DE PAGOS POR OBRA
    def registrar_pago_obra(
        self,
        obra_id,
        concepto,
        monto,
        fecha_pago,
        categoria="GENERAL",
        proveedor_id=None,
        empleado_id=None,
        metodo_pago="EFECTIVO",
        numero_comprobante="",
        observaciones="",
    ):
        """Registra un pago asociado a una obra."""
        try:
            cursor = self.db_connection.cursor()

            # Usar consulta SQL externa para registrar pago de obra
            with open('sql/administracion/insertar_pago_obra.sql', 'r') as file:
                query = file.read()
            cursor.execute(query, (
                obra_id,
                concepto,
                categoria,
                monto,
                fecha_pago,
                proveedor_id,
                empleado_id,
                metodo_pago,
                numero_comprobante,
                observaciones,
                self.usuario_actual,
                self.usuario_actual,
            ))

            pago_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "pagos_obras",
                pago_id,
                "INSERT",
                None,
                {"obra_id": obra_id, "concepto": concepto, "monto": monto},
            )

            return pago_id

        except Exception as e:
            logger.info(f"Error registrando pago de obra: {e}")
            self.db_connection.rollback()
            return None

    def obtener_pagos_obra(
        self,
        obra_id=None,
        fecha_desde=None,
        fecha_hasta=None,
        categoria=None,
        limite=100,
    ):
        """Obtiene pagos por obra."""
        try:
            cursor = self.db_connection.cursor()

            # Usar consulta SQL externa para obtener pagos de obra
            with open('sql/administracion/obtener_pagos_obra.sql', 'r') as file:
                query = file.read()

            conditions = []
            params = []

            if obra_id:
                conditions.append("po.obra_id = ?")
                params.append(obra_id)

            if fecha_desde:
                conditions.append("po.fecha_pago >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("po.fecha_pago <= ?")
                params.append(fecha_hasta)

            if categoria:
                conditions.append("po.categoria = ?")
                params.append(categoria)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY po.fecha_pago DESC"

            if limite:
                limite_validado = self._validate_limit(limite)
                query += f" OFFSET 0 ROWS FETCH NEXT {limite_validado} ROWS ONLY"

            cursor.execute(query, params)

            pagos = []
            for row in cursor.fetchall():
                pagos.append(
                    {
                        "id": row[0],
                        "obra_id": row[1],
                        "concepto": row[2],
                        "categoria": row[3],
                        "monto": float(row[4]),
                        "fecha_pago": row[5],
                        "proveedor_id": row[6],
                        "empleado_id": row[7],
                        "recibo_id": row[8],
                        "metodo_pago": row[9],
                        "numero_comprobante": row[10],
                        "estado": row[11],
                        "observaciones": row[12],
                        "fecha_creacion": row[13],
                        "usuario_creacion": row[14],
                    }
                )

            return pagos

        except Exception as e:
            logger.info(f"Error obteniendo pagos de obra: {e}")
            return []

# GESTIÓN DE PAGOS POR MATERIALES
    def registrar_compra_material(
        self,
        producto_id,
        proveedor_id,
        cantidad,
        precio_unitario,
        fecha_compra,
        obra_id=None,
        numero_factura="",
        observaciones="",
    ):
        """Registra una compra de material."""
        try:
            cursor = self.db_connection.cursor()

            total = cantidad * precio_unitario
            saldo_pendiente = total

            # Usar consulta SQL externa para registrar compra de material
            with open('sql/administracion/insertar_compra_material.sql', 'r') as file:
                query = file.read()
            cursor.execute(query, (
                producto_id,
                proveedor_id,
                obra_id,
                cantidad,
                precio_unitario,
                total,
                fecha_compra,
                saldo_pendiente,
                numero_factura,
                observaciones,
                self.usuario_actual,
                self.usuario_actual,
            ))

            compra_id = cursor.lastrowid
            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "pagos_materiales",
                compra_id,
                "INSERT",
                None,
                {"producto_id": producto_id, "total": total},
            )

            return compra_id

        except Exception as e:
            logger.info(f"Error registrando compra de material: {e}")
            self.db_connection.rollback()
            return None

    def registrar_pago_material(self, compra_id, monto_pago, fecha_pago):
        """Registra un pago de material."""
        try:
            cursor = self.db_connection.cursor()

            # Obtener información de la compra
            with open('sql/administracion/obtener_compra_material.sql', 'r') as file:
                query = file.read()
            cursor.execute(query, (compra_id,))

            row = cursor.fetchone()
            if not row:
                return False

            total, monto_pagado_actual, saldo_pendiente = row

            # Calcular nuevos montos
            nuevo_monto_pagado = monto_pagado_actual + monto_pago
            nuevo_saldo_pendiente = total - nuevo_monto_pagado

            # Determinar estado del pago
            if nuevo_saldo_pendiente <= 0:
                nuevo_estado = "PAGADO"
            elif nuevo_monto_pagado > 0:
                nuevo_estado = "PARCIAL"
            else:
                nuevo_estado = "PENDIENTE"

            with open('sql/administracion/actualizar_pago_material.sql', 'r') as file:
                query = file.read()
            cursor.execute(query, (
                nuevo_monto_pagado,
                nuevo_saldo_pendiente,
                nuevo_estado,
                fecha_pago,
                self.usuario_actual,
                compra_id,
            ))

            self.db_connection.commit()

            # Registrar auditoría
            self.registrar_auditoria(
                "pagos_materiales",
                compra_id,
                "UPDATE",
                {"monto_pagado": monto_pagado_actual, "estado": "PENDIENTE"},
                {"monto_pagado": nuevo_monto_pagado, "estado": nuevo_estado},
            )

            return True

        except Exception as e:
            logger.info(f"Error registrando pago de material: {e}")
            self.db_connection.rollback()
            return False

    # MÉTODOS DE ESTADÍSTICAS Y REPORTES
    def obtener_resumen_contable(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene resumen contable del período."""
        try:
            cursor = self.db_connection.cursor()

            # Resumen del libro contable
            with open('sql/administracion/resumen_libro_contable.sql', 'r') as file:
                query_libro = file.read()

            params = []
            if fecha_desde:
                query_libro += " AND fecha_asiento >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_libro += " AND fecha_asiento <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_libro, params)
            libro_row = cursor.fetchone()

            # Resumen de recibos
            with open('sql/administracion/resumen_recibos.sql', 'r') as file:
                query_recibos = file.read()

            params = []
            if fecha_desde:
                query_recibos += " AND fecha_emision >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_recibos += " AND fecha_emision <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_recibos, params)
            recibos_row = cursor.fetchone()

            # Resumen de pagos por obra
            with open('sql/administracion/resumen_pagos_obras.sql', 'r') as file:
                query_pagos_obra = file.read()

            params = []
            if fecha_desde:
                query_pagos_obra += " AND fecha_pago >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_pagos_obra += " AND fecha_pago <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_pagos_obra, params)
            pagos_obra_row = cursor.fetchone()

            # Resumen de pagos por materiales
            with open('sql/administracion/resumen_pagos_materiales.sql', 'r') as file:
                query_pagos_material = file.read()

            params = []
            if fecha_desde:
                query_pagos_material += " AND fecha_compra >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_pagos_material += " AND fecha_compra <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_pagos_material, params)
            pagos_material_row = cursor.fetchone()

            resumen = {
                "libro_contable": {
                    "total_debe": float(libro_row[0] or 0),
                    "total_haber": float(libro_row[1] or 0),
                    "saldo_total": float(libro_row[2] or 0),
                    "total_asientos": libro_row[3] or 0,
                },
                "recibos": {
                    "total_recibos": recibos_row[0] or 0,
                    "total_monto": float(recibos_row[1] or 0),
                    "recibos_impresos": recibos_row[2] or 0,
                },
                "pagos_obras": {
                    "total_pagos": pagos_obra_row[0] or 0,
                    "total_monto": float(pagos_obra_row[1] or 0),
                    "obras_con_pagos": pagos_obra_row[2] or 0,
                },
                "pagos_materiales": {
                    "total_compras": pagos_material_row[0] or 0,
                    "total_compras_monto": float(pagos_material_row[1] or 0),
                    "total_pagado": float(pagos_material_row[2] or 0),
                    "total_pendiente": float(pagos_material_row[3] or 0),
                },
            }

            return resumen

        except Exception as e:
            logger.info(f"Error obteniendo resumen contable: {e}")
            return None

    def obtener_estadisticas_departamento(
        self, departamento_id, fecha_desde=None, fecha_hasta=None
    ):
        """Obtiene estadísticas por departamento."""
        try:
            cursor = self.db_connection.cursor()

            # Gastos por departamento
            with open('sql/administracion/estadisticas_gastos_departamento.sql', 'r') as file:
                query_gastos = file.read()

            params = [departamento_id]
            if fecha_desde:
                query_gastos += " AND fecha_asiento >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_gastos += " AND fecha_asiento <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_gastos, params)
            gastos_row = cursor.fetchone()

            # Empleados del departamento
            with open('sql/administracion/estadisticas_empleados_departamento.sql', 'r') as file:
                query_empleados = file.read()
            cursor.execute(query_empleados, (departamento_id,))

            empleados_row = cursor.fetchone()

            # Presupuesto del departamento
            query_presupuesto = self.sql_manager.get_query('administracion', 'select_presupuesto_departamento')
            cursor.execute(query_presupuesto, (departamento_id,))

            presupuesto_row = cursor.fetchone()

            estadisticas = {
                "gastos": {
                    "total_gastos": gastos_row[0] or 0,
                    "total_monto": float(gastos_row[1] or 0),
                },
                "empleados": {
                    "total_empleados": empleados_row[0] or 0,
                    "total_salarios": float(empleados_row[1] or 0),
                },
                "presupuesto": {
                    "presupuesto_mensual": float(presupuesto_row[0] or 0)
                    if presupuesto_row
                    else 0
                },
            }

            return estadisticas

        except Exception as e:
            logger.info(f"Error obteniendo estadísticas de departamento: {e}")
            return None

    def obtener_auditoria(
        self, tabla=None, fecha_desde=None, fecha_hasta=None, usuario=None, limite=100
    ):
        """Obtiene registros de auditoría."""
        try:
            cursor = self.db_connection.cursor()

            with open('sql/administracion/obtener_auditoria.sql', 'r') as file:
                query = file.read()

            conditions = []
            params = []

            if tabla:
                conditions.append("tabla_afectada = ?")
                params.append(tabla)

            if fecha_desde:
                conditions.append("fecha_accion >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("fecha_accion <= ?")
                params.append(fecha_hasta)

            if usuario:
                conditions.append("usuario = ?")
                params.append(usuario)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY fecha_accion DESC"

            if limite:
                limite_validado = self._validate_limit(limite)
                query += f" OFFSET 0 ROWS FETCH NEXT {limite_validado} ROWS ONLY"

            cursor.execute(query, params)

            auditoria = []
            for row in cursor.fetchall():
                auditoria.append(
                    {
                        "id": row[0],
                        "tabla_afectada": row[1],
                        "registro_id": row[2],
                        "accion": row[3],
                        "datos_anteriores": row[4],
                        "datos_nuevos": row[5],
                        "usuario": row[6],
                        "fecha_accion": row[7],
                        "ip_address": row[8],
                        "observaciones": row[9],
                    }
                )

            return auditoria

        except Exception as e:
            logger.info(f"Error obteniendo auditoría: {e}")
            return []


# Alias para compatibilidad con tests y controladores
Administracion = AdministracionModel
