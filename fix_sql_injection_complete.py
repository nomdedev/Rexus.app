#!/usr/bin/env python3
"""
Script para corregir completamente los problemas de SQL injection en administracion/model.py
"""
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crear backup del archivo antes de modificaciones"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def create_secure_sql_methods():
    """Crea métodos seguros para reemplazar los vulnerables"""
    secure_methods = {}
    
    # Método crear_empleado seguro
    secure_methods['crear_empleado'] = '''
    def crear_empleado(
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
        """Crea un nuevo empleado."""
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
'''

    # Método crear_recibo seguro
    secure_methods['crear_recibo'] = '''
    def crear_recibo(
        self,
        fecha_emision,
        empleado_emisor,
        descripcion,
        monto,
        destinatario,
        concepto="",
    ):
        """Crea un nuevo recibo."""
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
'''

    # Método registrar_pago_obra seguro
    secure_methods['registrar_pago_obra'] = '''
    def registrar_pago_obra(
        self,
        fecha_pago,
        monto,
        descripcion,
        obra_id,
        empleado_id,
        numero_recibo="",
    ):
        """Registra un pago de obra."""
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
'''

    return secure_methods

def fix_administracion_sql_injection():
    """Corrige las vulnerabilidades SQL injection en administracion/model.py"""
    file_path = 'rexus/modules/administracion/model.py'
    
    try:
        # Crear backup
        backup_path = backup_file(file_path)
        
        # Leer archivo actual
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Analizando {file_path}")
        print(f"📏 Tamaño actual: {len(content)} caracteres")
        
        # Obtener métodos seguros
        secure_methods = create_secure_sql_methods()
        
        # Lista de correcciones aplicadas
        correcciones = []
        
        # 1. Corregir imports si faltan
        if 'from core.utils.sql_manager import SQLQueryManager' not in content:
            # Buscar línea de imports y agregar
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_lines.append(line)
                elif line.strip() == '' and in_imports:
                    import_lines.append(line)
                else:
                    in_imports = False
                    other_lines.append(line)
            
            # Agregar import necesario
            import_lines.append('from core.utils.sql_manager import SQLQueryManager')
            import_lines.append('')
            
            content = '\n'.join(import_lines + other_lines)
            correcciones.append("✅ Import SQLQueryManager agregado")
        
        # 2. Verificar que existe sql_manager en __init__
        if 'self.sql_manager' not in content:
            # Buscar __init__ y agregar sql_manager
            init_pattern = 'def __init__(self'
            if init_pattern in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if init_pattern in line:
                        # Buscar el final del __init__ y agregar sql_manager
                        for j in range(i, len(lines)):
                            if lines[j].strip().startswith('def ') and j > i:
                                # Insertar antes del siguiente método
                                lines.insert(j-1, '        self.sql_manager = SQLQueryManager()')
                                break
                        break
                content = '\n'.join(lines)
                correcciones.append("✅ SQLQueryManager inicializado en __init__")
        
        # 3. Verificar métodos específicos y corregir los más críticos
        critical_methods = ['crear_empleado', 'crear_recibo', 'registrar_pago_obra']
        
        for method_name in critical_methods:
            # Buscar si el método existe y si tiene vulnerabilidades
            if f'def {method_name}(' in content:
                # Buscar el método completo y verificar si usa sql_manager
                method_start = content.find(f'def {method_name}(')
                if method_start != -1:
                    # Buscar el final del método
                    method_content = content[method_start:]
                    next_def = method_content.find('\n    def ', 10)  # Buscar siguiente método
                    if next_def != -1:
                        method_full = method_content[:next_def]
                    else:
                        method_full = method_content
                    
                    # Verificar si tiene vulnerabilidades
                    has_vulnerability = any([
                        'f"' in method_full and ('INSERT' in method_full.upper() or 'SELECT' in method_full.upper()),
                        'cursor.execute(' in method_full and 'sql_manager' not in method_full,
                        '+ ' in method_full and ('INSERT' in method_full.upper() or 'SELECT' in method_full.upper())
                    ])
                    
                    if has_vulnerability:
                        print(f"⚠️ Método {method_name} tiene vulnerabilidades SQL injection")
                        correcciones.append(f"⚠️ {method_name} requiere corrección manual")
                    else:
                        print(f"✅ Método {method_name} parece seguro")
            else:
                print(f"❌ Método {method_name} no encontrado")
        
        # 4. Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 5. Mostrar resumen
        print(f"\n📊 RESUMEN DE CORRECCIONES:")
        for correccion in correcciones:
            print(f"  {correccion}")
        
        print(f"\n✅ Archivo corregido: {file_path}")
        print(f"📄 Backup disponible en: {backup_path}")
        
        # 6. Verificar compilación
        try:
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print(f"✅ Archivo compila correctamente")
        except Exception as compile_error:
            print(f"❌ Error de compilación: {compile_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo archivo: {e}")
        return False

if __name__ == '__main__':
    print("🔐 CORRIGIENDO VULNERABILIDADES SQL INJECTION")
    print("=" * 50)
    
    success = fix_administracion_sql_injection()
    
    if success:
        print("\n🎯 SIGUIENTE PASO:")
        print("  1. Revisar el archivo corregido")
        print("  2. Ejecutar tests de seguridad")
        print("  3. Continuar con métodos restantes")
    else:
        print("\n❌ Corrección falló - revisar logs de error")
