"""
Ejemplo del sistema de backup y recuperación automático
Demuestra el uso del BackupRecoveryManager
"""

from rexus.utils.backup_recovery import (
    get_backup_recovery_manager,
    create_emergency_backup,
    get_backup_health_report,
    BackupConfig
)
from rexus.utils.app_logger import get_logger

logger = get_logger(__name__)

def ejemplo_backup_basico():
    """Ejemplo básico de uso del sistema de backup"""
    
    print("=== EJEMPLO SISTEMA DE BACKUP Y RECUPERACIÓN ===")
    
    # Obtener manager de backup
    backup_manager = get_backup_recovery_manager()
    
    # Crear backup completo
    print("1. Creando backup completo...")
    backup_info = backup_manager.create_full_backup()
    
    if backup_info:
        print(f"   ✅ Backup creado: {backup_info.backup_id}")
        print(f"   📁 Tamaño: {backup_info.size_bytes / 1024 / 1024:.2f} MB")
        print(f"   📊 Archivos: {backup_info.files_count}")
        print(f"   💾 Base de datos incluida: {backup_info.database_included}")
    else:
        print("   ❌ Error creando backup")
    
    # Obtener estado del sistema
    print("\n2. Estado del sistema de backup:")
    status = backup_manager.get_backup_status()
    print(f"   📈 Backups totales: {status['total_backups']}")
    print(f"   ✅ Exitosos: {status['successful_backups']}")
    print(f"   ❌ Fallidos: {status['failed_backups']}")
    print(f"   📊 Tasa de éxito: {status['success_rate']:.1f}%")
    print(f"   💾 Tamaño total: {status['total_size_mb']:.2f} MB")
    
    # Listar backups disponibles
    print("\n3. Backups disponibles:")
    backups = backup_manager.list_available_backups()
    for backup in backups:
        print(f"   🗂️ {backup['id']} - {backup['type']} - {backup['size_mb']:.2f} MB")
    
    # Verificar integridad
    if backup_info:
        print(f"\n4. Verificando integridad de {backup_info.backup_id}...")
        is_valid = backup_manager.verify_backup_integrity(backup_info.backup_id)
        print(f"   {'✅ Íntegro' if is_valid else '❌ Corrupto'}")
    
    print("\n✅ Ejemplo completado exitosamente")

def ejemplo_configuracion_avanzada():
    """Ejemplo de configuración personalizada"""
    
    print("\n=== CONFIGURACIÓN AVANZADA ===")
    
    # Configuración personalizada
    custom_config = BackupConfig(
        backup_directory="backups_custom",
        max_backups=10,
        full_backup_interval=3,  # Cada 3 días
        incremental_backup_interval=1,  # Diario
        compress_backups=True,
        verify_integrity=True,
        schedule_enabled=False,  # Manual por ahora
        include_logs=True,
        include_config=True,
        include_sql_files=True
    )
    
    # Crear manager con configuración personalizada
    custom_manager = BackupRecoveryManager(custom_config)
    
    print(f"📁 Directorio personalizado: {custom_config.backup_directory}")
    print(f"🔄 Backup completo cada: {custom_config.full_backup_interval} días")
    print(f"📊 Máximo de backups: {custom_config.max_backups}")
    print(f"🗜️ Compresión: {'Habilitada' if custom_config.compress_backups else 'Deshabilitada'}")
    print(f"✅ Verificación: {'Habilitada' if custom_config.verify_integrity else 'Deshabilitada'}")

def ejemplo_recuperacion():
    """Ejemplo de recuperación desde backup"""
    
    print("\n=== EJEMPLO DE RECUPERACIÓN ===")
    
    backup_manager = get_backup_recovery_manager()
    
    # Listar backups disponibles
    backups = backup_manager.list_available_backups()
    if not backups:
        print("❌ No hay backups disponibles para recuperación")
        return
    
    # Usar el backup más reciente
    latest_backup = backups[0]
    print(f"📥 Recuperando desde: {latest_backup['id']}")
    print(f"📅 Fecha: {latest_backup['timestamp']}")
    print(f"📊 Tipo: {latest_backup['type']}")
    
    # Simular recuperación (sin sobrescribir archivos reales)
    print("⚠️ SIMULACIÓN - No se sobrescriben archivos reales")
    # success = backup_manager.restore_from_backup(latest_backup['id'], "temp_restore")
    # print(f"{'✅ Recuperación exitosa' if success else '❌ Error en recuperación'}")

def ejemplo_reporte_salud():
    """Ejemplo de reporte de salud del sistema"""
    
    print("\n=== REPORTE DE SALUD DEL SISTEMA ===")
    
    health_report = get_backup_health_report()
    
    print(f"🏥 Estado general: {health_report['health_status'].upper()}")
    print(f"📊 Tasa de éxito: {health_report['success_rate']:.1f}%")
    print(f"📅 Antigüedad último backup: {health_report.get('last_backup_age_days', 'N/A')} días")
    print(f"📈 Total de backups: {health_report['total_backups']}")
    print(f"💾 Espacio utilizado: {health_report['total_size_mb']:.2f} MB")
    print(f"🤖 Backup automático: {'Activo' if health_report['automated_backup_enabled'] else 'Inactivo'}")
    
    # Recomendaciones basadas en el estado
    if health_report['success_rate'] < 90:
        print("⚠️ RECOMENDACIÓN: Revisar configuración - tasa de éxito baja")
    
    if health_report.get('last_backup_age_days', 0) > 7:
        print("⚠️ RECOMENDACIÓN: Crear backup - último backup muy antiguo")

def ejemplo_backup_emergencia():
    """Ejemplo de backup de emergencia"""
    
    print("\n=== BACKUP DE EMERGENCIA ===")
    
    print("🚨 Creando backup de emergencia inmediato...")
    emergency_backup = create_emergency_backup()
    
    if emergency_backup:
        print(f"✅ Backup de emergencia creado: {emergency_backup.backup_id}")
        print(f"📁 Tamaño: {emergency_backup.size_bytes / 1024 / 1024:.2f} MB")
        print(f"⏱️ Creado: {emergency_backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Error creando backup de emergencia")

if __name__ == "__main__":
    try:
        # Ejecutar ejemplos
        ejemplo_backup_basico()
        ejemplo_configuracion_avanzada()
        ejemplo_recuperacion()
        ejemplo_reporte_salud()
        ejemplo_backup_emergencia()
        
        print("\n🎉 TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE")
        
    except Exception as e:
        logger.error(f"Error en ejemplo de backup: {e}")
        print(f"❌ Error: {e}")