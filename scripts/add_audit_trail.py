#!/usr/bin/env python3
"""
Script para agregar funcionalidad de audit trail a tablas existentes
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.database import DatabaseConnection
from src.core.audit_trail import AuditTrail, AuditableModel


def add_audit_trail_to_tables():
    """Agrega audit trail a todas las tablas principales"""
    
    # Tablas principales que requieren auditoría
    tables_to_audit = [
        'obras',
        'inventario',
        'herrajes',
        'vidrios',
        'pedidos',
        'compras',
        'proveedores',
        'empleados',
        'equipos',
        'materiales',
        'usuarios',
        'configuracion'
    ]
    
    print("🔧 Agregando audit trail a las tablas...")
    print("=" * 50)
    
    try:
        # Crear conexión a la base de datos
        db_connection = DatabaseConnection('audit_setup')
        audit_trail = AuditTrail(db_connection)
        
        # Crear tabla de auditoría
        print("📋 Creando tabla de auditoría...")
        audit_trail._create_audit_table_if_not_exists()
        print("✅ Tabla de auditoría creada")
        
        # Procesar cada tabla
        success_count = 0
        error_count = 0
        
        for table_name in tables_to_audit:
            try:
                print(f"\n🔍 Procesando tabla: {table_name}")
                
                # Verificar si la tabla existe
                cursor = db_connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = ?
                """, (table_name,))
                
                if cursor.fetchone()[0] == 0:
                    print(f"⚠️ Tabla {table_name} no existe, saltando...")
                    continue
                
                # Crear modelo auditable
                auditable_model = AuditableModel(table_name, audit_trail)
                
                # Agregar columnas de timestamp
                auditable_model.add_timestamp_columns()
                
                # Verificar que se agregaron correctamente
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = ? AND COLUMN_NAME IN ('fecha_creacion', 'fecha_actualizacion')
                """, (table_name,))
                
                timestamp_columns = cursor.fetchone()[0]
                
                if timestamp_columns >= 2:
                    print(f"✅ Audit trail agregado a {table_name}")
                    success_count += 1
                else:
                    print(f"⚠️ Audit trail parcialmente agregado a {table_name}")
                    error_count += 1
                
            except Exception as e:
                print(f"❌ Error procesando {table_name}: {e}")
                error_count += 1
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE AUDIT TRAIL:")
        print(f"✅ Tablas procesadas exitosamente: {success_count}")
        print(f"❌ Tablas con errores: {error_count}")
        print(f"📊 Total: {success_count + error_count}")
        
        if success_count > 0:
            print("\n🎉 Audit trail configurado exitosamente!")
            print("\nFuncionalidades agregadas:")
            print("• Tracking de cambios en tiempo real")
            print("• Timestamps de creación y actualización")
            print("• Historial completo de modificaciones")
            print("• Identificación de usuarios que realizan cambios")
            print("• Registro de IP y módulo de origen")
        
        return success_count > 0
        
    except Exception as e:
        print(f"💥 Error fatal configurando audit trail: {e}")
        return False


def test_audit_trail():
    """Prueba el funcionamiento del audit trail"""
    
    print("\n🧪 Probando funcionalidad de audit trail...")
    print("=" * 50)
    
    try:
        # Crear audit trail
        audit_trail = AuditTrail()
        audit_trail.set_current_user(1, "admin")
        
        # Probar logging manual
        print("📝 Probando logging manual...")
        success = audit_trail.log_change(
            tabla='test_table',
            accion='TEST',
            registro_id=999,
            datos_nuevos={'test': 'data'},
            modulo='test_module',
            detalles='Test de funcionamiento'
        )
        
        if success:
            print("✅ Logging manual exitoso")
        else:
            print("❌ Error en logging manual")
        
        # Probar consulta de logs
        print("\n🔍 Probando consulta de logs...")
        logs = audit_trail.get_audit_log(limit=5)
        
        if logs:
            print(f"✅ Consulta exitosa: {len(logs)} registros encontrados")
            for log in logs[:3]:  # Mostrar solo los primeros 3
                print(f"  • {log['fecha_cambio']} - {log['accion']} en {log['tabla']}")
        else:
            print("⚠️ No se encontraron logs")
        
        # Probar modelo auditable
        print("\n🔧 Probando modelo auditable...")
        
        # Verificar si existe la tabla 'usuarios' para probar
        db_connection = DatabaseConnection('test')
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'usuarios'
        """)
        
        if cursor.fetchone()[0] > 0:
            auditable_model = AuditableModel('usuarios', audit_trail)
            print("✅ Modelo auditable creado exitosamente")
        else:
            print("⚠️ Tabla 'usuarios' no encontrada para prueba")
        
        print("\n✅ Todas las pruebas de audit trail completadas")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas de audit trail: {e}")
        return False


def show_audit_trail_usage():
    """Muestra ejemplos de uso del audit trail"""
    
    print("\n📖 EJEMPLOS DE USO DEL AUDIT TRAIL:")
    print("=" * 50)
    
    usage_examples = """
# 1. Configurar usuario actual para auditoría
from src.core.audit_trail import set_audit_user
set_audit_user(user_id=1, username="admin")

# 2. Usar modelo auditable para operaciones CRUD
from src.core.audit_trail import AuditableModel

# Crear modelo
obras_model = AuditableModel('obras')

# Insertar con auditoría
nueva_obra = {
    'nombre': 'Obra Test',
    'cliente': 'Cliente Test',
    'estado': 'Activa'
}
obra_id = obras_model.insert_with_audit(nueva_obra, modulo='obras')

# Actualizar con auditoría
cambios = {'estado': 'Completada'}
obras_model.update_with_audit(obra_id, cambios, modulo='obras')

# 3. Consultar historial de cambios
from src.core.audit_trail import get_audit_trail

audit_trail = get_audit_trail()

# Historial de una tabla específica
historial_obras = audit_trail.get_table_activity('obras', limit=10)

# Historial de un registro específico
historial_obra = audit_trail.get_record_history('obras', obra_id)

# Actividad de un usuario
actividad_usuario = audit_trail.get_user_activity(user_id=1, limit=20)

# 4. Consultar logs con filtros
from datetime import datetime, timedelta

# Logs de los últimos 7 días
fecha_inicio = datetime.now() - timedelta(days=7)
logs_recientes = audit_trail.get_audit_log(
    fecha_inicio=fecha_inicio,
    limit=50
)

# Logs de una tabla específica
logs_inventario = audit_trail.get_audit_log(
    tabla='inventario',
    limit=100
)
"""
    
    print(usage_examples)
    
    print("\n🔧 FUNCIONALIDADES DISPONIBLES:")
    print("• Tracking automático de INSERT, UPDATE, DELETE")
    print("• Timestamps de creación y actualización")
    print("• Identificación de usuario que realiza cambios")
    print("• Registro de IP y módulo de origen")
    print("• Historial completo por registro")
    print("• Consultas filtradas por fecha, usuario, tabla")
    print("• Limpieza automática de logs antiguos")
    
    print("\n📊 COLUMNAS DE AUDIT TRAIL:")
    print("• id: ID único del registro de auditoría")
    print("• tabla: Nombre de la tabla afectada")
    print("• accion: Tipo de acción (INSERT, UPDATE, DELETE)")
    print("• registro_id: ID del registro afectado")
    print("• usuario_id: ID del usuario que realizó el cambio")
    print("• usuario_nombre: Nombre del usuario")
    print("• datos_anteriores: Datos antes del cambio")
    print("• datos_nuevos: Datos después del cambio")
    print("• modulo: Módulo que realizó el cambio")
    print("• detalles: Detalles adicionales")
    print("• fecha_cambio: Timestamp del cambio")
    print("• ip_address: IP del cliente")


def main():
    """Función principal"""
    
    print("🚀 CONFIGURACIÓN DE AUDIT TRAIL - Rexus.app")
    print("=" * 60)
    
    # Agregar audit trail a tablas
    print("Paso 1: Agregando audit trail a tablas existentes...")
    setup_success = add_audit_trail_to_tables()
    
    if setup_success:
        # Probar funcionalidad
        print("\nPaso 2: Probando funcionalidad...")
        test_success = test_audit_trail()
        
        if test_success:
            # Mostrar ejemplos de uso
            show_audit_trail_usage()
            
            print("\n🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("\nEl sistema de audit trail está listo para usar.")
            print("Todos los cambios en la base de datos serán registrados automáticamente.")
            
            return 0
        else:
            print("\n⚠️ Configuración completada pero las pruebas fallaron.")
            return 1
    else:
        print("\n❌ Error en la configuración del audit trail.")
        return 1


if __name__ == "__main__":
    sys.exit(main())