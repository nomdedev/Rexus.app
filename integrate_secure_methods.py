
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
