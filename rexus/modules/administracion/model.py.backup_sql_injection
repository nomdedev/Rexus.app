"""
Modelo de Contabilidad

Sistema completo de contabilidad para Stock.App v1.1.3
Incluye: libro contable, recibos, pagos, estadísticas, control de roles
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

# Importar utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import validate_table_name, SQLSecurityError
    SQL_SECURITY_AVAILABLE = True
except ImportError:
    print("[WARNING] SQL security utilities not available in administracion")
    SQL_SECURITY_AVAILABLE = False


class ContabilidadModel:
    """Modelo completo de contabilidad con control de roles y auditoría."""

    def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual
        self.tabla_libro_contable = "libro_contable"
        self.tabla_recibos = "recibos"
        self.tabla_pagos_obras = "pagos_obras"
        self.tabla_pagos_materiales = "pagos_materiales"
        self.tabla_empleados = "empleados"
        self.tabla_departamentos = "departamentos"
        self.tabla_auditoria = "auditoria_contable"

        # Crear tablas si no existen
        self.crear_tablas()
    
    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.
        
        Args:
            table_name: Nombre de tabla a validar
            
        Returns:
            Nombre de tabla validado
        """
        if SQL_SECURITY_AVAILABLE:
            try:
                from rexus.utils.sql_security import sql_validator
                # Agregar tablas de administración a lista blanca si no existen
                admin_tables = {
                    'libro_contable', 'recibos', 'pagos_obras', 'pagos_materiales',
                    'empleados', 'departamentos', 'auditoria_contable'
                }
                for table in admin_tables:
                    if table not in sql_validator.ALLOWED_TABLES:
                        sql_validator.add_allowed_table(table)
                
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                print(f"[SECURITY ERROR] Tabla no válida: {e}")
                raise
        else:
            # Validación básica como fallback
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
                raise ValueError(f"Nombre de tabla inválido: {table_name}")
            return table_name

    def crear_tablas(self):
        """Crea las tablas necesarias para el módulo de contabilidad."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Tabla de departamentos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='departamentos' AND xtype='U')
                CREATE TABLE departamentos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(20) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    responsable VARCHAR(100),
                    presupuesto_mensual DECIMAL(15,2) DEFAULT 0,
                    estado VARCHAR(20) DEFAULT 'ACTIVO',
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100)
                )
            """)

            # Tabla de empleados
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='empleados' AND xtype='U')
                CREATE TABLE empleados (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(20) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    documento VARCHAR(20) UNIQUE,
                    email VARCHAR(100),
                    telefono VARCHAR(20),
                    departamento_id INT,
                    cargo VARCHAR(50),
                    salario DECIMAL(12,2),
                    fecha_ingreso DATE,
                    estado VARCHAR(20) DEFAULT 'ACTIVO',
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100),
                    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
                )
            """)

            # Tabla de libro contable
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='libro_contable' AND xtype='U')
                CREATE TABLE libro_contable (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    numero_asiento VARCHAR(20) NOT NULL UNIQUE,
                    fecha_asiento DATE NOT NULL,
                    tipo_asiento VARCHAR(20) NOT NULL,
                    concepto VARCHAR(200) NOT NULL,
                    referencia VARCHAR(100),
                    obra_id INT,
                    proveedor_id INT,
                    empleado_id INT,
                    departamento_id INT,
                    cuenta_contable VARCHAR(20),
                    debe DECIMAL(15,2) DEFAULT 0,
                    haber DECIMAL(15,2) DEFAULT 0,
                    saldo DECIMAL(15,2),
                    estado VARCHAR(20) DEFAULT 'ACTIVO',
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100)
                )
            """)

            # Tabla de recibos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='recibos' AND xtype='U')
                CREATE TABLE recibos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    numero_recibo VARCHAR(20) NOT NULL UNIQUE,
                    fecha_emision DATE NOT NULL,
                    tipo_recibo VARCHAR(20) NOT NULL,
                    concepto VARCHAR(200) NOT NULL,
                    beneficiario VARCHAR(100),
                    obra_id INT,
                    proveedor_id INT,
                    empleado_id INT,
                    monto DECIMAL(15,2) NOT NULL,
                    moneda VARCHAR(10) DEFAULT 'ARS',
                    metodo_pago VARCHAR(20),
                    numero_comprobante VARCHAR(50),
                    estado VARCHAR(20) DEFAULT 'EMITIDO',
                    impreso BIT DEFAULT 0,
                    archivo_pdf VARCHAR(255),
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100)
                )
            """)

            # Tabla de pagos por obra
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obras' AND xtype='U')
                CREATE TABLE pagos_obras (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    obra_id INT NOT NULL,
                    concepto VARCHAR(200) NOT NULL,
                    categoria VARCHAR(50),
                    monto DECIMAL(15,2) NOT NULL,
                    fecha_pago DATE NOT NULL,
                    proveedor_id INT,
                    empleado_id INT,
                    recibo_id INT,
                    asiento_contable_id INT,
                    metodo_pago VARCHAR(20),
                    numero_comprobante VARCHAR(50),
                    estado VARCHAR(20) DEFAULT 'PAGADO',
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100)
                )
            """)

            # Tabla de pagos por materiales
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pagos_materiales' AND xtype='U')
                CREATE TABLE pagos_materiales (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    producto_id INT NOT NULL,
                    proveedor_id INT NOT NULL,
                    obra_id INT,
                    cantidad DECIMAL(10,2) NOT NULL,
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    total DECIMAL(15,2) NOT NULL,
                    fecha_compra DATE NOT NULL,
                    fecha_pago DATE,
                    estado_pago VARCHAR(20) DEFAULT 'PENDIENTE',
                    monto_pagado DECIMAL(15,2) DEFAULT 0,
                    saldo_pendiente DECIMAL(15,2),
                    recibo_id INT,
                    asiento_contable_id INT,
                    numero_factura VARCHAR(50),
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    usuario_creacion VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    usuario_actualizacion VARCHAR(100)
                )
            """)

            # Tabla de auditoría contable
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='auditoria_contable' AND xtype='U')
                CREATE TABLE auditoria_contable (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    tabla_afectada VARCHAR(50) NOT NULL,
                    registro_id INT NOT NULL,
                    accion VARCHAR(20) NOT NULL,
                    datos_anteriores TEXT,
                    datos_nuevos TEXT,
                    usuario VARCHAR(100) NOT NULL,
                    fecha_accion DATETIME DEFAULT GETDATE(),
                    ip_address VARCHAR(45),
                    observaciones TEXT
                )
            """)

            self.db_connection.commit()
            print("✅ Tablas de contabilidad creadas exitosamente")

        except Exception as e:
            print(f"❌ Error creando tablas de contabilidad: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def registrar_auditoria(
        self,
        tabla,
        registro_id,
        accion,
        datos_anteriores=None,
        datos_nuevos=None,
        observaciones=None,
    ):
        """Registra una acción en la auditoría contable."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_auditoria)}]_contable
                (tabla_afectada, registro_id, accion, datos_anteriores, datos_nuevos, usuario, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
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
            print(f"Error registrando auditoría: {e}")

    # GESTIÓN DE DEPARTAMENTOS
    def crear_departamento(
        self, codigo, nombre, descripcion="", responsable="", presupuesto_mensual=0
    ):
        """Crea un nuevo departamento."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_departamentos)}]
                (codigo, nombre, descripcion, responsable, presupuesto_mensual, usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    codigo,
                    nombre,
                    descripcion,
                    responsable,
                    presupuesto_mensual,
                    self.usuario_actual,
                    self.usuario_actual,
                ),
            )

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
            print(f"Error creando departamento: {e}")
            self.db_connection.rollback()
            return None

    def obtener_departamentos(self, activos_solo=True):
        """Obtiene la lista de departamentos."""
        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT id, codigo, nombre, descripcion, responsable, presupuesto_mensual,
                       estado, fecha_creacion, usuario_creacion
                FROM departamentos
            """

            if activos_solo:
                query += " WHERE estado = 'ACTIVO'"

            query += " ORDER BY nombre"

            cursor.execute(query)

            departamentos = []
            for row in cursor.fetchall():
                departamentos.append(
                    {
                        "id": row[0],
                        "codigo": row[1],
                        "nombre": row[2],
                        "descripcion": row[3],
                        "responsable": row[4],
                        "presupuesto_mensual": float(row[5]),
                        "estado": row[6],
                        "fecha_creacion": row[7],
                        "usuario_creacion": row[8],
                    }
                )

            return departamentos

        except Exception as e:
            print(f"Error obteniendo departamentos: {e}")
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

            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_empleados)}]
                (codigo, nombre, apellido, documento, email, telefono, departamento_id,
                 cargo, salario, fecha_ingreso, usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
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
                ),
            )

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
            print(f"Error creando empleado: {e}")
            self.db_connection.rollback()
            return None

    def obtener_empleados(self, departamento_id=None, activos_solo=True):
        """Obtiene la lista de empleados."""
        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT e.id, e.codigo, e.nombre, e.apellido, e.documento, e.email,
                       e.telefono, e.departamento_id, d.nombre as departamento,
                       e.cargo, e.salario, e.fecha_ingreso, e.estado
                FROM empleados e
                LEFT JOIN departamentos d ON e.departamento_id = d.id
            """

            conditions = []
            params = []

            if activos_solo:
                conditions.append("e.estado = 'ACTIVO'")

            if departamento_id:
                conditions.append("e.departamento_id = ?")
                params.append(departamento_id)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY e.nombre, e.apellido"

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
            print(f"Error obteniendo empleados: {e}")
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

            # Generar número de asiento
            cursor.execute("""
                SELECT ISNULL(MAX(CAST(SUBSTRING(numero_asiento, 4, 10) AS INT)), 0) + 1
                FROM libro_contable
                WHERE numero_asiento LIKE 'AS-%'
            """)
            numero = cursor.fetchone()[0]
            numero_asiento = f"AS-{numero:06d}"

            # Calcular saldo
            saldo = debe - haber

            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_libro_contable)}]
                (numero_asiento, fecha_asiento, tipo_asiento, concepto, referencia,
                 obra_id, proveedor_id, empleado_id, departamento_id, cuenta_contable,
                 debe, haber, saldo, observaciones, usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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
            print(f"Error creando asiento contable: {e}")
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

            query = """
                SELECT lc.id, lc.numero_asiento, lc.fecha_asiento, lc.tipo_asiento,
                       lc.concepto, lc.referencia, lc.obra_id, lc.proveedor_id,
                       lc.empleado_id, lc.departamento_id, d.nombre as departamento,
                       lc.cuenta_contable, lc.debe, lc.haber, lc.saldo, lc.estado,
                       lc.observaciones, lc.fecha_creacion, lc.usuario_creacion
                FROM libro_contable lc
                LEFT JOIN departamentos d ON lc.departamento_id = d.id
            """

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

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY lc.fecha_asiento DESC, lc.numero_asiento DESC"

            if limite:
                query += f" OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

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
            print(f"Error obteniendo libro contable: {e}")
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
            cursor.execute("""
                SELECT ISNULL(MAX(CAST(SUBSTRING(numero_recibo, 4, 10) AS INT)), 0) + 1
                FROM recibos
                WHERE numero_recibo LIKE 'REC-%'
            """)
            numero = cursor.fetchone()[0]
            numero_recibo = f"REC-{numero:06d}"

            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_recibos)}]
                (numero_recibo, fecha_emision, tipo_recibo, concepto, beneficiario,
                 obra_id, proveedor_id, empleado_id, monto, moneda, metodo_pago,
                 numero_comprobante, observaciones, usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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
            print(f"Error creando recibo: {e}")
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

            query = """
                SELECT r.id, r.numero_recibo, r.fecha_emision, r.tipo_recibo,
                       r.concepto, r.beneficiario, r.obra_id, r.proveedor_id,
                       r.empleado_id, r.monto, r.moneda, r.metodo_pago,
                       r.numero_comprobante, r.estado, r.impreso, r.archivo_pdf,
                       r.observaciones, r.fecha_creacion, r.usuario_creacion
                FROM recibos r
            """

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

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY r.fecha_emision DESC, r.numero_recibo DESC"

            if limite:
                query += f" OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

            cursor.execute(query, params)

            recibos = []
            for row in cursor.fetchall():
                recibos.append(
                    {
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
                    }
                )

            return recibos

        except Exception as e:
            print(f"Error obteniendo recibos: {e}")
            return []

    def marcar_recibo_impreso(self, recibo_id, archivo_pdf=None):
        """Marca un recibo como impreso."""
        try:
            cursor = self.db_connection.cursor()

            cursor.execute(
                """
                UPDATE [{self._validate_table_name(self.tabla_recibos)}]
                SET impreso = 1, archivo_pdf = ?, fecha_actualizacion = GETDATE(),
                    usuario_actualizacion = ?
                WHERE id = ?
            """,
                (archivo_pdf, self.usuario_actual, recibo_id),
            )

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
            print(f"Error marcando recibo como impreso: {e}")
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

            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_pagos_obras)}]
                (obra_id, concepto, categoria, monto, fecha_pago, proveedor_id,
                 empleado_id, metodo_pago, numero_comprobante, observaciones,
                 usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
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
                ),
            )

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
            print(f"Error registrando pago de obra: {e}")
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

            query = """
                SELECT po.id, po.obra_id, po.concepto, po.categoria, po.monto,
                       po.fecha_pago, po.proveedor_id, po.empleado_id, po.recibo_id,
                       po.metodo_pago, po.numero_comprobante, po.estado, po.observaciones,
                       po.fecha_creacion, po.usuario_creacion
                FROM pagos_obras po
            """

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
                query += f" OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

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
            print(f"Error obteniendo pagos de obra: {e}")
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

            cursor.execute(
                """
                INSERT INTO [{self._validate_table_name(self.tabla_pagos_materiales)}]
                (producto_id, proveedor_id, obra_id, cantidad, precio_unitario, total,
                 fecha_compra, saldo_pendiente, numero_factura, observaciones,
                 usuario_creacion, usuario_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
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
                ),
            )

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
            print(f"Error registrando compra de material: {e}")
            self.db_connection.rollback()
            return None

    def registrar_pago_material(self, compra_id, monto_pago, fecha_pago):
        """Registra un pago de material."""
        try:
            cursor = self.db_connection.cursor()

            # Obtener información de la compra
            cursor.execute(
                """
                SELECT total, monto_pagado, saldo_pendiente
                FROM pagos_materiales
                WHERE id = ?
            """,
                (compra_id,),
            )

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

            cursor.execute(
                """
                UPDATE pagos_materiales
                SET monto_pagado = ?, saldo_pendiente = ?, estado_pago = ?,
                    fecha_pago = ?, fecha_actualizacion = GETDATE(),
                    usuario_actualizacion = ?
                WHERE id = ?
            """,
                (
                    nuevo_monto_pagado,
                    nuevo_saldo_pendiente,
                    nuevo_estado,
                    fecha_pago,
                    self.usuario_actual,
                    compra_id,
                ),
            )

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
            print(f"Error registrando pago de material: {e}")
            self.db_connection.rollback()
            return False

    # MÉTODOS DE ESTADÍSTICAS Y REPORTES
    def obtener_resumen_contable(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene resumen contable del período."""
        try:
            cursor = self.db_connection.cursor()

            # Resumen del libro contable
            query_libro = """
                SELECT
                    SUM(debe) as total_debe,
                    SUM(haber) as total_haber,
                    SUM(saldo) as saldo_total,
                    COUNT(*) as total_asientos
                FROM libro_contable
                WHERE estado = 'ACTIVO'
            """

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
            query_recibos = """
                SELECT
                    COUNT(*) as total_recibos,
                    SUM(monto) as total_monto,
                    SUM(CASE WHEN impreso = 1 THEN 1 ELSE 0 END) as recibos_impresos
                FROM recibos
                WHERE estado = 'EMITIDO'
            """

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
            query_pagos_obra = """
                SELECT
                    COUNT(*) as total_pagos,
                    SUM(monto) as total_monto,
                    COUNT(DISTINCT obra_id) as obras_con_pagos
                FROM pagos_obras
                WHERE estado = 'PAGADO'
            """

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
            query_pagos_material = """
                SELECT
                    COUNT(*) as total_compras,
                    SUM(total) as total_compras_monto,
                    SUM(monto_pagado) as total_pagado,
                    SUM(saldo_pendiente) as total_pendiente
                FROM pagos_materiales
            """

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
            print(f"Error obteniendo resumen contable: {e}")
            return None

    def obtener_estadisticas_departamento(
        self, departamento_id, fecha_desde=None, fecha_hasta=None
    ):
        """Obtiene estadísticas por departamento."""
        try:
            cursor = self.db_connection.cursor()

            # Gastos por departamento
            query_gastos = """
                SELECT
                    COUNT(*) as total_gastos,
                    SUM(haber) as total_monto
                FROM libro_contable
                WHERE departamento_id = ? AND estado = 'ACTIVO'
            """

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
            cursor.execute(
                """
                SELECT COUNT(*) as total_empleados, SUM(salario) as total_salarios
                FROM empleados
                WHERE departamento_id = ? AND estado = 'ACTIVO'
            """,
                (departamento_id,),
            )

            empleados_row = cursor.fetchone()

            # Presupuesto del departamento
            cursor.execute(
                """
                SELECT presupuesto_mensual FROM departamentos WHERE id = ?
            """,
                (departamento_id,),
            )

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
            print(f"Error obteniendo estadísticas de departamento: {e}")
            return None

    def obtener_auditoria(
        self, tabla=None, fecha_desde=None, fecha_hasta=None, usuario=None, limite=100
    ):
        """Obtiene registros de auditoría."""
        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT id, tabla_afectada, registro_id, accion, datos_anteriores,
                       datos_nuevos, usuario, fecha_accion, ip_address, observaciones
                FROM auditoria_contable
            """

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
                query += f" OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

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
            print(f"Error obteniendo auditoría: {e}")
            return []
