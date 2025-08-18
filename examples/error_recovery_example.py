"""
Ejemplo práctico del sistema de recuperación de errores de Rexus.app
Este archivo muestra cómo integrar el sistema de recuperación en módulos reales
"""

from rexus.utils.error_recovery import (
    with_error_recovery, 
    database_operation_recovery,
    get_error_recovery_manager,
    RecoveryConfig,
    RecoveryStrategy
)
from rexus.utils.app_logger import get_logger

logger = get_logger(__name__)

class ExampleUserManager:
    """Ejemplo de gestor de usuarios con recuperación automática"""
    
    def __init__(self):
        self.db_connection = None
        self.recovery_manager = get_error_recovery_manager()
    
    @database_operation_recovery('obtener_usuario_por_id')
    def obtener_usuario(self, user_id: int):
        """Obtiene usuario con recuperación automática"""
        if not self.db_connection:
            raise ConnectionError("No database connection available")
        
        # Simular consulta SQL
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"Usuario {user_id} no encontrado")
        
        return {
            'id': result[0],
            'username': result[1], 
            'email': result[2],
            'activo': result[3]
        }
    
    @with_error_recovery('autenticar_usuario', max_retries=2, enable_cache=True)
    def autenticar_usuario(self, username: str, password: str):
        """Autentica usuario con recuperación y cache"""
        
        # Simular posibles errores de red/BD
        import random
        if random.random() < 0.3:  # 30% probabilidad de error
            raise ConnectionError("Error de conexión simulado")
        
        # Lógica de autenticación
        if username == "admin" and password == "password123":
            return {
                'success': True,
                'user_id': 1,
                'role': 'administrator'
            }
        
        return {'success': False, 'message': 'Credenciales inválidas'}
    
    @with_error_recovery('sincronizar_datos', max_retries=5, enable_cache=False)
    def sincronizar_datos_remotos(self, endpoint_url: str):
        """Sincroniza datos con servidor remoto con múltiples reintentos"""
        import requests
        import time
        
        # Simular timeout ocasional
        if 'timeout' in endpoint_url:
            time.sleep(2)
            raise TimeoutError("Request timeout")
        
        # Simular llamada HTTP exitosa
        return {
            'status': 'success',
            'records_updated': 150,
            'timestamp': time.time()
        }

def ejemplo_uso_avanzado():
    """Demuestra uso avanzado del sistema de recuperación"""
    
    user_manager = ExampleUserManager()
    recovery_manager = get_error_recovery_manager()
    
    print("=== EJEMPLO USO AVANZADO RECUPERACIÓN ===")
    
    # Configuración personalizada para operaciones críticas
    config_critica = RecoveryConfig(
        max_retries=5,
        base_delay=0.5,
        backoff_factor=1.5,
        enable_cache=True,
        cache_duration=600,  # 10 minutos
        enable_offline_mode=True
    )
    
    @recovery_manager.with_recovery(config_critica, 'operacion_critica')
    def operacion_critica():
        import random
        if random.random() < 0.8:  # 80% probabilidad de error
            raise RuntimeError("Falla simulada en operación crítica")
        return "Operación crítica exitosa"
    
    try:
        resultado = operacion_critica()
        print(f"Resultado: {resultado}")
    except Exception as e:
        print(f"Operación falló definitivamente: {e}")
    
    # Mostrar estadísticas
    stats = recovery_manager.get_recovery_statistics()
    print(f"Tasa de éxito: {stats['success_rate']:.1f}%")
    print(f"Tiempo promedio de recuperación: {stats['avg_recovery_time']:.2f}s")
    
    # Exportar log para análisis
    recovery_manager.export_recovery_log("recovery_log.csv")
    print("Log de recuperación exportado")

if __name__ == "__main__":
    # Ejecutar ejemplo
    try:
        user_manager = ExampleUserManager()
        
        # Test autenticación con recuperación
        print("Probando autenticación con recuperación...")
        for i in range(3):
            try:
                auth_result = user_manager.autenticar_usuario("admin", "password123")
                print(f"Intento {i+1}: {auth_result}")
                break
            except Exception as e:
                print(f"Intento {i+1} falló: {e}")
        
        # Test sincronización con reintentos
        print("\\nProbando sincronización con reintentos...")
        sync_result = user_manager.sincronizar_datos_remotos("https://api.example.com/sync")
        print(f"Sincronización: {sync_result}")
        
        # Ejecutar ejemplo avanzado
        ejemplo_uso_avanzado()
        
    except Exception as e:
        logger.error(f"Error en ejemplo: {e}")
        print(f"Error: {e}")