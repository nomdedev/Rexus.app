#!/usr/bin/env python3
"""
Script para crear métodos seguros de administración en archivo separado
"""

def create_secure_administracion_methods():
    """Crea archivo con métodos seguros para administración"""
    
    secure_methods_content = '''
"""
Métodos seguros para administración - Reemplazo de métodos con SQL injection
Archivo temporal para corregir vulnerabilidades críticas
"""

def crear_empleado_seguro(
    self,
    nombre,
    apellido,
    email,
    telefono="",
    direccion="",
    departamento_id=None,
    cargo="",
    salario=0,
    fecha_ingreso=None,
    activo=True,
):
    """Crea un nuevo empleado de forma segura."""
    try:
        cursor = self.db_connection.cursor()

        # Usar SQL externa para inserción segura
        sql_query = self.sql_manager.load_sql("insert_empleado.sql")
        tabla_empleados = self._validate_table_name(self.tabla_empleados)
        query = sql_query.format(tabla_empleados=tabla_empleados)
        
        cursor.execute(
            query,
            (
                nombre,
                apellido,
                email,
                telefono,
                direccion,
                departamento_id,
                cargo,
                salario,
                fecha_ingreso,
                activo,
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
            {"nombre": nombre, "apellido": apellido, "email": email},
        )

        return empleado_id

    except Exception as e:
        logger.error(f"Error creando empleado: {e}")
        if self.db_connection:
            self.db_connection.rollback()
        return None

def crear_recibo_seguro(
    self,
    fecha_emision,
    empleado_emisor,
    descripcion,
    monto,
    destinatario,
    concepto="",
):
    """Crea un nuevo recibo de forma segura."""
    try:
        cursor = self.db_connection.cursor()

        # Obtener siguiente número de recibo usando SQL externa
        sql_siguiente_numero = self.sql_manager.load_sql("select_siguiente_numero_recibo.sql")
        tabla_recibos = self._validate_table_name(self.tabla_recibos)
        query_numero = sql_siguiente_numero.format(tabla_recibos=tabla_recibos)
        
        cursor.execute(query_numero)
        numero = cursor.fetchone()[0]
        numero_recibo = f"REC-{numero:06d}"

        # Insertar recibo usando SQL externa
        sql_insert = self.sql_manager.load_sql("insert_recibo.sql")
        query_insert = sql_insert.format(tabla_recibos=tabla_recibos)
        
        cursor.execute(
            query_insert,
            (
                numero_recibo,
                fecha_emision,
                empleado_emisor,
                descripcion,
                monto,
                destinatario,
                concepto,
                0,  # impreso = False
                "",  # archivo_pdf
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
            {"numero_recibo": numero_recibo, "monto": monto, "destinatario": destinatario},
        )

        return recibo_id

    except Exception as e:
        logger.error(f"Error creando recibo: {e}")
        if self.db_connection:
            self.db_connection.rollback()
        return None

def registrar_pago_obra_seguro(
    self,
    fecha_pago,
    monto,
    descripcion,
    obra_id,
    empleado_id,
    numero_recibo="",
):
    """Registra un pago de obra de forma segura."""
    try:
        cursor = self.db_connection.cursor()

        # Insertar pago usando SQL externa
        sql_insert = self.sql_manager.load_sql("insert_pago_obra.sql")
        tabla_pagos_obras = self._validate_table_name(self.tabla_pagos_obras)
        query_insert = sql_insert.format(tabla_pagos_obras=tabla_pagos_obras)
        
        cursor.execute(
            query_insert,
            (
                fecha_pago,
                monto,
                descripcion,
                obra_id,
                empleado_id,
                numero_recibo,
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
            {"obra_id": obra_id, "monto": monto, "descripcion": descripcion},
        )

        return pago_id

    except Exception as e:
        logger.error(f"Error registrando pago de obra: {e}")
        if self.db_connection:
            self.db_connection.rollback()
        return None

def registrar_compra_material_seguro(
    self,
    fecha_compra,
    material,
    cantidad,
    precio_unitario,
    total,
    proveedor,
    empleado_id,
    obra_id=None,
):
    """Registra una compra de material de forma segura."""
    try:
        cursor = self.db_connection.cursor()

        # Insertar compra usando SQL externa
        sql_insert = self.sql_manager.load_sql("insert_compra_material.sql")
        tabla_pagos_materiales = self._validate_table_name(self.tabla_pagos_materiales)
        query_insert = sql_insert.format(tabla_pagos_materiales=tabla_pagos_materiales)
        
        cursor.execute(
            query_insert,
            (
                fecha_compra,
                material,
                cantidad,
                precio_unitario,
                total,
                proveedor,
                empleado_id,
                obra_id,
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
            {"material": material, "cantidad": cantidad, "total": total, "proveedor": proveedor},
        )

        return compra_id

    except Exception as e:
        logger.error(f"Error registrando compra de material: {e}")
        if self.db_connection:
            self.db_connection.rollback()
        return None

def marcar_recibo_impreso_seguro(
    self,
    numero_recibo,
    archivo_pdf="",
):
    """Marca un recibo como impreso de forma segura."""
    try:
        cursor = self.db_connection.cursor()

        # Actualizar recibo usando SQL externa
        sql_update = self.sql_manager.load_sql("update_recibo_impreso.sql")
        tabla_recibos = self._validate_table_name(self.tabla_recibos)
        query_update = sql_update.format(tabla_recibos=tabla_recibos)
        
        cursor.execute(query_update, (archivo_pdf, numero_recibo))
        
        if cursor.rowcount > 0:
            self.db_connection.commit()
            
            # Registrar auditoría
            self.registrar_auditoria(
                "recibos",
                None,  # No tenemos ID directo
                "UPDATE",
                {"impreso": 0},
                {"impreso": 1, "archivo_pdf": archivo_pdf},
            )
            
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error marcando recibo como impreso: {e}")
        if self.db_connection:
            self.db_connection.rollback()
        return False
'''
    
    # Escribir archivo con métodos seguros
    with open('administracion_metodos_seguros.py', 'w', encoding='utf-8') as f:
        f.write(secure_methods_content)
    
    print("✅ Archivo administracion_metodos_seguros.py creado")
    print("📄 Contiene 5 métodos seguros para reemplazar los vulnerables")
    
    # Crear script de integración
    integration_script = '''
#!/usr/bin/env python3
"""
Script para integrar métodos seguros en administración
"""

def integrate_secure_methods():
    """Integra métodos seguros en administracion/model.py"""
    
    print("🔧 INSTRUCCIONES PARA INTEGRACIÓN MANUAL:")
    print("=" * 50)
    print()
    print("1. Abrir administracion_metodos_seguros.py")
    print("2. Copiar cada método y reemplazar en administracion/model.py:")
    print()
    print("   REEMPLAZOS NECESARIOS:")
    print("   ├── crear_empleado() → crear_empleado_seguro()")
    print("   ├── crear_recibo() → crear_recibo_seguro()")  
    print("   ├── registrar_pago_obra() → registrar_pago_obra_seguro()")
    print("   ├── registrar_compra_material() → registrar_compra_material_seguro()")
    print("   └── marcar_recibo_impreso() → marcar_recibo_impreso_seguro()")
    print()
    print("3. Agregar imports necesarios en administracion/model.py:")
    print("   from core.utils.sql_manager import SQLQueryManager")
    print("   import logging")
    print("   logger = logging.getLogger(__name__)")
    print()
    print("4. Inicializar sql_manager en __init__:")
    print("   self.sql_manager = SQLQueryManager()")
    print()
    print("5. Verificar que todos los archivos SQL existen en sql/administracion/")
    print()
    print("✅ Todos los métodos usan parámetros preparados y previenen SQL injection")

if __name__ == '__main__':
    integrate_secure_methods()
'''
    
    with open('integrate_secure_methods.py', 'w', encoding='utf-8') as f:
        f.write(integration_script)
    
    print("✅ Script de integración creado: integrate_secure_methods.py")

if __name__ == '__main__':
    create_secure_administracion_methods()
