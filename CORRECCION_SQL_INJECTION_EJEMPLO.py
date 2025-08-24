#!/usr/bin/env python3
"""
EJEMPLO: Método crear_departamento corregido para evitar SQL injection

ANTES (VULNERABLE):
def crear_departamento_VULNERABLE(self, codigo, nombre):
    cursor = self.db_connection.cursor()
    # ¡SQL INJECTION VULNERABILITY!
    query = f"INSERT INTO departamentos (codigo, nombre) VALUES ('{codigo}', '{nombre}')"
    cursor.execute(query)  # ¡PELIGROSO!

DESPUÉS (SEGURO):
"""

def crear_departamento_CORREGIDO(self, codigo, nombre, descripcion="", responsable="", presupuesto_mensual=0):
    """
    Crea un nuevo departamento con validación de seguridad.
    
    CORRECCIONES APLICADAS:
    1. Usar archivos SQL externos en lugar de strings concatenados
    2. Usar parámetros preparados (?) en lugar de f-strings
    3. Validación y sanitización de entrada
    4. Manejo de errores apropiado
    """
    try:
        # 1. SANITIZACIÓN Y VALIDACIÓN DE DATOS
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

        # 2. VALIDAR DATOS OBLIGATORIOS
        if not codigo_limpio or not nombre_limpio:
            return False, "Código y nombre son requeridos"

        # 3. VERIFICAR DUPLICADOS USANDO CONSULTAS SEGURAS
        cursor = self.db_connection.cursor()
        
        # Verificar código duplicado
        query_codigo = self.sql_manager.get_query('administracion', 'validate_departamento_codigo')
        cursor.execute(query_codigo, (codigo_limpio.lower(),))
        if cursor.fetchone()[0] > 0:
            return False, f"Ya existe un departamento con el código: {codigo_limpio}"
            
        # Verificar nombre duplicado  
        query_nombre = self.sql_manager.get_query('administracion', 'validate_departamento_nombre')
        cursor.execute(query_nombre, (nombre_limpio.lower(),))
        if cursor.fetchone()[0] > 0:
            return False, f"Ya existe un departamento con el nombre: {nombre_limpio}"

        # 4. INSERTAR USANDO CONSULTA SQL EXTERNA (SEGURA)
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

        # 5. REGISTRAR AUDITORÍA
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
        if self.db_connection:
            self.db_connection.rollback()
        return None


# EJEMPLO DE OTROS MÉTODOS QUE NECESITAN CORRECCIÓN:

def obtener_empleados_VULNERABLE(self, departamento_id=None):
    """EJEMPLO DE MÉTODO VULNERABLE - NO USAR"""
    # ¡SQL INJECTION VULNERABILITY!
    query = f"SELECT * FROM empleados WHERE departamento_id = {departamento_id}"
    cursor.execute(query)  # ¡PELIGROSO!

def obtener_empleados_CORREGIDO(self, departamento_id=None, activos_solo=True):
    """MÉTODO CORREGIDO - USAR ESTE PATRÓN"""
    try:
        cursor = self.db_connection.cursor()
        
        if activos_solo:
            query = self.sql_manager.get_query('administracion', 'select_empleados_activos')
            cursor.execute(query)
        else:
            query = self.sql_manager.get_query('administracion', 'select_empleados_all')  
            cursor.execute(query)
            
        # Procesar resultados...
        return empleados
        
    except Exception as e:
        logger.error(f"Error obteniendo empleados: {e}")
        return []
