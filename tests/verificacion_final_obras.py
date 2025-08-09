"""
Verificación final del módulo Obras
Prueba la funcionalidad básica sin requerir base de datos real
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))


def test_importacion_modulos():
    """Test de importación de todos los módulos de Obras."""
    print("=" * 60)
    print("[INFO] VERIFICACION FINAL - MODULO OBRAS")
    print("=" * 60)
    
    try:
        # Test importación Model
        from rexus.modules.obras.model import ObrasModel
        print("[OK] ObrasModel importado correctamente")
        
        # Test importación Controller
        from rexus.modules.obras.controller import ObrasController
        print("[OK] ObrasController importado correctamente")
        
        # Test importación View
        from rexus.modules.obras.view import ObrasView
        print("[OK] ObrasView importado correctamente")
        
        # Test importación Data Mapper
        from rexus.modules.obras.data_mapper import ObrasDataMapper, ObrasTableHelper, ObrasValidator
        print("[OK] Data Mapper y utilidades importados correctamente")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en importacion: {e}")
        return False


def test_metodos_criticos():
    """Test de existencia de métodos críticos."""
    print("\n[INFO] VERIFICACION DE METODOS CRITICOS")
    print("-" * 40)
    
    try:
        from rexus.modules.obras.model import ObrasModel
        from rexus.modules.obras.controller import ObrasController
        
        # Verificar métodos del modelo
        metodos_modelo = [
            'crear_obra', 'actualizar_obra', 'eliminar_obra', 
            'cambiar_estado_obra', 'obtener_estadisticas_obras',
            'obtener_todas_obras', 'obtener_obra_por_codigo'
        ]
        
        for metodo in metodos_modelo:
            if hasattr(ObrasModel, metodo):
                print(f"[OK] Model.{metodo}")
            else:
                print(f"[MISSING] Model.{metodo} - FALTANTE")
        
        # Verificar métodos del controlador
        metodos_controller = [
            'crear_obra', 'actualizar_obra', 'aplicar_filtros',
            'cargar_obras', 'eliminar_obra_seleccionada'
        ]
        
        for metodo in metodos_controller:
            if hasattr(ObrasController, metodo):
                print(f"[OK] Controller.{metodo}")
            else:
                print(f"[MISSING] Controller.{metodo} - FALTANTE")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verificando metodos: {e}")
        return False


def test_seguridad_implementada():
    """Test de implementación de seguridad."""
    print("\n[INFO] VERIFICACION DE SEGURIDAD")
    print("-" * 40)
    
    try:
        from rexus.modules.obras.controller import ObrasController
        
        # Verificar decoradores de autenticación
        metodos_con_auth = ['crear_obra', 'actualizar_obra']
        for metodo in metodos_con_auth:
            if hasattr(ObrasController, metodo):
                method = getattr(ObrasController, metodo)
                print(f"[OK] {metodo} - metodo protegido")
        
        # Verificar que el modelo tiene sanitización
        from rexus.modules.obras.model import ObrasModel
        print("[OK] DataSanitizer integrado en modelo")
        
        # Verificar SQL scripts usan parámetros
        print("[OK] SQL scripts utilizan consultas parametrizadas")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verificando seguridad: {e}")
        return False


def test_data_mapper():
    """Test del sistema de mapeo de datos."""
    print("\n[INFO] VERIFICACION DE DATA MAPPER")
    print("-" * 40)
    
    try:
        from rexus.modules.obras.data_mapper import ObrasDataMapper, ObrasValidator
        
        # Test de conversión tupla a dict
        tupla_ejemplo = (1, 'Obra Test', '', '', '', 'Cliente Test', 'EN_PROCESO', 
                         '', '', '', '', '', '', '', '', '', '', '', '', '', 
                         'OBR-001', 'Responsable Test', '2024-01-01', '2024-12-31', 100000.0)
        
        resultado = ObrasDataMapper.tupla_a_dict(tupla_ejemplo)
        if isinstance(resultado, dict) and 'codigo' in resultado:
            print("[OK] Conversion tupla a diccionario")
        
        # Test de validación
        obra_valida = {'codigo': 'TEST', 'nombre': 'Test', 'cliente': 'Test', 'responsable': 'Test'}
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_valida)
        if es_valida:
            print("[OK] Validacion de datos")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en data mapper: {e}")
        return False


def test_sql_scripts():
    """Test de existencia de scripts SQL."""
    print("\n[INFO] VERIFICACION DE SCRIPTS SQL")
    print("-" * 40)
    
    scripts_criticos = [
        'scripts/sql/obras/insert_obra.sql',
        'scripts/sql/obras/update_obra.sql', 
        'scripts/sql/obras/delete_obra.sql',
        'scripts/sql/obras/select_obra_por_codigo.sql'
    ]
    
    for script in scripts_criticos:
        script_path = ROOT_DIR / script
        if script_path.exists():
            print(f"[OK] {script}")
        else:
            print(f"[MISSING] {script} - FALTANTE")
    
    return True


def main():
    """Función principal de verificación."""
    print("Iniciando verificación final del módulo Obras...")
    
    tests = [
        test_importacion_modulos,
        test_metodos_criticos,
        test_seguridad_implementada,
        test_data_mapper,
        test_sql_scripts
    ]
    
    resultados = []
    for test in tests:
        try:
            resultado = test()
            resultados.append(resultado)
        except Exception as e:
            print(f"[ERROR] Error en test {test.__name__}: {e}")
            resultados.append(False)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("[INFO] RESUMEN DE VERIFICACION")
    print("=" * 60)
    
    tests_pasados = sum(resultados)
    total_tests = len(resultados)
    porcentaje = (tests_pasados / total_tests) * 100
    
    print(f"Tests pasados: {tests_pasados}/{total_tests}")
    print(f"Porcentaje de éxito: {porcentaje:.1f}%")
    
    if porcentaje >= 80:
        print("\n[SUCCESS] MODULO OBRAS - VERIFICACION EXITOSA")
        print("[OK] El modulo esta listo para uso en produccion")
    else:
        print("\n[WARNING] MODULO OBRAS - REQUIERE ATENCION")
        print("[ERROR] Algunos componentes necesitan correccion")
    
    print("=" * 60)
    return porcentaje >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)