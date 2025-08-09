#!/usr/bin/env python3
"""
🔍 AUDITORÍA COMPLETA DEL MÓDULO INVENTARIO
Análisis exhaustivo de todos los aspectos del módulo inventario
"""

import os
import sys
from pathlib import Path
import traceback

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def auditoria_estructura():
    """Auditar estructura del módulo inventario"""
    print("=" * 60)
    print("🏗️  AUDITORÍA DE ESTRUCTURA")
    print("=" * 60)
    
    inventario_path = Path("rexus/modules/inventario")
    
    # Verificar existencia de archivos core
    archivos_core = {
        "__init__.py": "Inicialización del módulo",
        "model.py": "Modelo de datos",
        "view.py": "Vista/interfaz",
        "controller.py": "Controlador lógica"
    }
    
    problemas_estructura = []
    
    for archivo, descripcion in archivos_core.items():
        archivo_path = inventario_path / archivo
        if archivo_path.exists():
            print(f"   [CHECK] {archivo} - {descripcion}")
        else:
            print(f"   [ERROR] {archivo} - {descripcion} (FALTA)")
            problemas_estructura.append(f"Falta {archivo}")
    
    # Verificar subdirectorios
    subdirs = ["submodules"]
    for subdir in subdirs:
        subdir_path = inventario_path / subdir
        if subdir_path.exists():
            print(f"   [CHECK] {subdir}/ - Submódulos")
            # Listar archivos en submódulos
            for archivo in subdir_path.glob("*.py"):
                print(f"      📄 {archivo.name}")
        else:
            print(f"   [ERROR] {subdir}/ - Submódulos (FALTA)")
            problemas_estructura.append(f"Falta directorio {subdir}")
    
    # Verificar archivos backup
    backups = list(inventario_path.glob("*.backup*"))
    if backups:
        print(f"   [WARN]  {len(backups)} archivos backup encontrados:")
        for backup in backups:
            print(f"      📄 {backup.name}")
    
    return problemas_estructura

def auditoria_imports():
    """Auditar imports y dependencias"""
    print("=" * 60)
    print("📦 AUDITORÍA DE IMPORTS Y DEPENDENCIAS")
    print("=" * 60)
    
    problemas_imports = []
    
    try:
        # Test imports críticos
        print("Probando imports del modelo...")
        from rexus.modules.inventario.model import InventarioModel
        print("   [CHECK] InventarioModel importado correctamente")
        
        print("Probando imports de la vista...")
        from rexus.modules.inventario.view import InventarioView
        print("   [CHECK] InventarioView importado correctamente")
        
        print("Probando imports del controlador...")
        from rexus.modules.inventario.controller import InventarioController
        print("   [CHECK] InventarioController importado correctamente")
        
        # Test diálogo de obras asociadas
        try:
            from rexus.modules.inventario.obras_asociadas_dialog import ObrasAsociadasDialog
            print("   [CHECK] ObrasAsociadasDialog importado correctamente")
        except ImportError as e:
            print(f"   [ERROR] ObrasAsociadasDialog no disponible: {e}")
            problemas_imports.append("Falta ObrasAsociadasDialog")
        
        # Test dependencias de seguridad
        try:
            from rexus.utils.data_sanitizer import DataSanitizer
            print("   [CHECK] DataSanitizer disponible")
        except ImportError:
            print("   [WARN]  DataSanitizer no disponible")
        
        try:
            from rexus.core.auth_decorators import auth_required
            print("   [CHECK] Auth decorators disponibles")
        except ImportError:
            print("   [WARN]  Auth decorators no disponibles")
            
    except Exception as e:
        print(f"   [ERROR] Error crítico en imports: {e}")
        problemas_imports.append(f"Error crítico: {e}")
        traceback.print_exc()
    
    return problemas_imports

def auditoria_base_datos():
    """Auditar conexión y estructura de base de datos"""
    print("=" * 60)
    print("🗄️  AUDITORÍA DE BASE DE DATOS")
    print("=" * 60)
    
    problemas_bd = []
    
    try:
        from rexus.core.database import get_inventario_connection
        
        print("Probando conexión a la base de datos...")
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        # Verificar tablas principales
        tablas_requeridas = [
            "inventario_perfiles",
            "obras", 
            "detalles_obra",
            "historial",
            "reserva_materiales"
        ]
        
        print("Verificando tablas requeridas:")
        for tabla in tablas_requeridas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   [CHECK] {tabla}: {count} registros")
            except Exception as e:
                print(f"   [ERROR] {tabla}: ERROR - {e}")
                problemas_bd.append(f"Tabla {tabla} no accesible")
        
        # Verificar columnas críticas en inventario_perfiles
        print("\nVerificando estructura de inventario_perfiles:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventario_perfiles'
            ORDER BY ORDINAL_POSITION
        """)
        
        columnas = cursor.fetchall()
        columnas_requeridas = ['codigo', 'descripcion', 'categoria', 'stock_actual', 'precio_unitario']
        
        columnas_existentes = [col[0] for col in columnas]
        for col_req in columnas_requeridas:
            if col_req in columnas_existentes:
                print(f"   [CHECK] Columna {col_req} existe")
            else:
                print(f"   [ERROR] Columna {col_req} FALTA")
                problemas_bd.append(f"Falta columna {col_req}")
        
        print(f"\nTotal columnas en inventario_perfiles: {len(columnas)}")
        
        # Verificar relación inventario-obras
        print("\nVerificando relación inventario-obras:")
        cursor.execute("""
            SELECT COUNT(*) FROM detalles_obra 
            WHERE codigo_inventario IS NOT NULL
        """)
        
        relaciones = cursor.fetchone()[0]
        print(f"   [CHECK] {relaciones} relaciones inventario-obras encontradas")
        
        conn.close()
        
    except Exception as e:
        print(f"   [ERROR] Error conectando a BD: {e}")
        problemas_bd.append(f"Error de conexión: {e}")
        traceback.print_exc()
    
    return problemas_bd

def auditoria_interfaz():
    """Auditar interfaz de usuario"""
    print("=" * 60)
    print("🖥️  AUDITORÍA DE INTERFAZ DE USUARIO")
    print("=" * 60)
    
    problemas_ui = []
    
    try:
        from PyQt6.QtWidgets import QApplication
        from rexus.modules.inventario.view import InventarioView
        
        # Crear aplicación Qt si no existe
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        print("Creando vista de inventario...")
        vista = InventarioView()
        
        # Verificar componentes críticos
        componentes_requeridos = [
            'tabla_inventario',
            'tab_widget', 
            'busqueda_input',
            'btn_buscar',
            'btn_nuevo_producto',
            'btn_editar',
            'btn_eliminar'
        ]
        
        print("Verificando componentes de la interfaz:")
        for componente in componentes_requeridos:
            if hasattr(vista, componente):
                print(f"   [CHECK] {componente} existe")
            else:
                print(f"   [ERROR] {componente} FALTA")
                problemas_ui.append(f"Falta componente {componente}")
        
        # Verificar estilos
        print("\nVerificando estilos aplicados:")
        if vista.styleSheet():
            print("   [CHECK] Estilos CSS aplicados")
            # Verificar estilos de alto contraste
            styles = vista.styleSheet()
            if "background-color: #ffffff" in styles and "color: #000000" in styles:
                print("   [CHECK] Estilos de alto contraste aplicados")
            else:
                print("   [WARN]  Estilos de alto contraste incompletos")
                problemas_ui.append("Estilos de alto contraste incompletos")
        else:
            print("   [ERROR] No hay estilos aplicados")
            problemas_ui.append("Faltan estilos CSS")
        
        # Verificar señales conectadas
        print("\nVerificando señales de la vista:")
        if hasattr(vista, 'datos_actualizados'):
            print("   [CHECK] Señal datos_actualizados existe")
        
        if hasattr(vista, 'solicitar_busqueda'):
            print("   [CHECK] Señal solicitar_busqueda existe")
        
        # Test doble click en tabla
        if hasattr(vista, 'tabla_inventario') and vista.tabla_inventario:
            print("   [CHECK] Tabla de inventario inicializada")
            # Verificar si hay conexión de doble click
            try:
                # Esto es un hack para verificar si hay conexiones
                receivers = vista.tabla_inventario.receivers(vista.tabla_inventario.itemDoubleClicked)
                if receivers > 0:
                    print("   [CHECK] Doble click conectado")
                else:
                    print("   [WARN]  Doble click no conectado")
                    problemas_ui.append("Doble click no conectado")
            except:
                print("   [WARN]  No se pudo verificar doble click")
        
    except Exception as e:
        print(f"   [ERROR] Error en auditoría de interfaz: {e}")
        problemas_ui.append(f"Error de interfaz: {e}")
        traceback.print_exc()
    
    return problemas_ui

def auditoria_funcionalidad():
    """Auditar funcionalidades específicas del módulo"""
    print("=" * 60)
    print("⚙️  AUDITORÍA DE FUNCIONALIDADES")
    print("=" * 60)
    
    problemas_func = []
    
    try:
        from rexus.modules.inventario.model import InventarioModel
        from rexus.modules.inventario.controller import InventarioController
        
        print("Probando instanciación del modelo...")
        modelo = InventarioModel()
        print("   [CHECK] Modelo instanciado correctamente")
        
        # Verificar métodos críticos del modelo
        metodos_modelo = [
            'obtener_inventario',
            'buscar_productos', 
            'crear_producto',
            'actualizar_producto',
            'eliminar_producto',
            'obtener_estadisticas'
        ]
        
        print("\nVerificando métodos del modelo:")
        for metodo in metodos_modelo:
            if hasattr(modelo, metodo):
                print(f"   [CHECK] {metodo} existe")
            else:
                print(f"   [ERROR] {metodo} FALTA")
                problemas_func.append(f"Falta método {metodo}")
        
        print("\nProbando instanciación del controlador...")
        controlador = InventarioController(model=modelo)
        print("   [CHECK] Controlador instanciado correctamente")
        
        # Verificar métodos críticos del controlador
        metodos_controlador = [
            'cargar_inventario',
            'buscar_productos',
            'nuevo_producto',
            'editar_producto',
            'eliminar_producto'
        ]
        
        print("\nVerificando métodos del controlador:")
        for metodo in metodos_controlador:
            if hasattr(controlador, metodo):
                print(f"   [CHECK] {metodo} existe")
            else:
                print(f"   [ERROR] {metodo} FALTA")
                problemas_func.append(f"Falta método controlador {metodo}")
        
        # Test funcionalidad de obras asociadas
        print("\nVerificando funcionalidad de obras asociadas:")
        try:
            from rexus.modules.inventario.obras_asociadas_dialog import ObrasAsociadasDialog
            
            # Test datos del diálogo
            datos_test = {
                'codigo': 'TEST001',
                'descripcion': 'Material de prueba',
                'categoria': 'Test',
                'stock_actual': 100
            }
            
            dialogo = ObrasAsociadasDialog(datos_test)
            print("   [CHECK] Diálogo de obras asociadas funcional")
            
            if hasattr(dialogo, 'cargar_obras_asociadas'):
                print("   [CHECK] Método cargar_obras_asociadas existe")
            else:
                print("   [ERROR] Método cargar_obras_asociadas FALTA")
                problemas_func.append("Falta método cargar_obras_asociadas")
            
        except Exception as e:
            print(f"   [ERROR] Error en obras asociadas: {e}")
            problemas_func.append(f"Error en obras asociadas: {e}")
        
    except Exception as e:
        print(f"   [ERROR] Error en auditoría de funcionalidades: {e}")
        problemas_func.append(f"Error funcional: {e}")
        traceback.print_exc()
    
    return problemas_func

def auditoria_seguridad():
    """Auditar aspectos de seguridad"""
    print("=" * 60)
    print("[LOCK] AUDITORÍA DE SEGURIDAD")
    print("=" * 60)
    
    problemas_seg = []
    
    try:
        from rexus.modules.inventario.model import InventarioModel
        
        modelo = InventarioModel()
        
        # Verificar sanitización de datos
        print("Verificando utilidades de seguridad:")
        if hasattr(modelo, 'data_sanitizer') and modelo.data_sanitizer:
            print("   [CHECK] DataSanitizer disponible")
        else:
            print("   [WARN]  DataSanitizer no disponible")
            problemas_seg.append("DataSanitizer no disponible")
        
        if hasattr(modelo, 'sql_validator') and modelo.sql_validator:
            print("   [CHECK] SQL Validator disponible")
        else:
            print("   [WARN]  SQL Validator no disponible") 
            problemas_seg.append("SQL Validator no disponible")
        
        # Verificar decoradores de autenticación
        print("\nVerificando decoradores de seguridad:")
        try:
            from rexus.core.auth_decorators import auth_required, admin_required
            print("   [CHECK] Decoradores de autenticación disponibles")
        except ImportError:
            print("   [WARN]  Decoradores de autenticación no disponibles")
            problemas_seg.append("Decoradores de auth no disponibles")
        
        # Verificar protección XSS
        print("\nVerificando protección XSS:")
        try:
            from rexus.utils.xss_protection import FormProtector
            print("   [CHECK] FormProtector disponible")
        except ImportError:
            print("   [WARN]  FormProtector no disponible")
            problemas_seg.append("FormProtector no disponible")
        
    except Exception as e:
        print(f"   [ERROR] Error en auditoría de seguridad: {e}")
        problemas_seg.append(f"Error de seguridad: {e}")
    
    return problemas_seg

def auditoria_tests():
    """Auditar tests existentes"""
    print("=" * 60)
    print("🧪 AUDITORÍA DE TESTS")
    print("=" * 60)
    
    problemas_tests = []
    
    # Buscar archivos de test
    test_files = []
    
    # Buscar en directorio tests
    tests_dir = Path("tests")
    if tests_dir.exists():
        test_files.extend(tests_dir.glob("**/test_inventario*.py"))
        test_files.extend(tests_dir.glob("**/inventario*.py"))
    
    # Buscar en raíz del proyecto
    root_tests = list(Path(".").glob("test_inventario*.py"))
    test_files.extend(root_tests)
    
    print(f"Archivos de test encontrados: {len(test_files)}")
    
    if test_files:
        for test_file in test_files:
            print(f"   📄 {test_file}")
    else:
        print("   [WARN]  No se encontraron tests específicos de inventario")
        problemas_tests.append("Faltan tests específicos")
    
    # Verificar tests críticos
    tests_requeridos = [
        "test_inventario_model",
        "test_inventario_view", 
        "test_inventario_controller",
        "test_obras_asociadas"
    ]
    
    print("\nTests requeridos:")
    for test in tests_requeridos:
        encontrado = any(test in str(tf) for tf in test_files)
        if encontrado:
            print(f"   [CHECK] {test}")
        else:
            print(f"   [ERROR] {test} FALTA")
            problemas_tests.append(f"Falta test {test}")
    
    return problemas_tests

def auditoria_performance():
    """Auditar aspectos de performance"""
    print("=" * 60)
    print("⚡ AUDITORÍA DE PERFORMANCE")
    print("=" * 60)
    
    problemas_perf = []
    
    try:
        from rexus.modules.inventario.model import InventarioModel
        
        modelo = InventarioModel()
        
        # Verificar paginación
        print("Verificando utilidades de performance:")
        if hasattr(modelo, 'paginate_query'):
            print("   [CHECK] Paginación disponible")
        else:
            print("   [WARN]  Paginación no implementada")
            problemas_perf.append("Falta paginación")
        
        # Verificar cache
        if hasattr(modelo, 'cache_manager'):
            print("   [CHECK] Cache manager disponible")
        else:
            print("   [WARN]  Cache manager no disponible")
            problemas_perf.append("Falta cache manager")
        
        # Verificar conexión a BD
        if hasattr(modelo, 'db_connection'):
            print("   [CHECK] Conexión BD configurada")
        else:
            print("   [WARN]  Conexión BD no configurada")
            problemas_perf.append("Conexión BD no configurada")
        
    except Exception as e:
        print(f"   [ERROR] Error en auditoría de performance: {e}")
        problemas_perf.append(f"Error de performance: {e}")
    
    return problemas_perf

def generar_reporte_final(todos_problemas):
    """Generar reporte final de la auditoría"""
    print("\n" + "=" * 80)
    print("📋 REPORTE FINAL DE AUDITORÍA DEL MÓDULO INVENTARIO")
    print("=" * 80)
    
    total_problemas = sum(len(problemas) for problemas in todos_problemas.values())
    
    if total_problemas == 0:
        print("🎉 ¡EXCELENTE! No se encontraron problemas críticos.")
        print("   El módulo inventario está en buen estado.")
    else:
        print(f"[WARN]  Se encontraron {total_problemas} problemas que requieren atención:")
        
        for categoria, problemas in todos_problemas.items():
            if problemas:
                print(f"\n🔸 {categoria.upper()}:")
                for i, problema in enumerate(problemas, 1):
                    print(f"   {i}. {problema}")
    
    # Priorización de problemas
    print("\n🎯 PRIORIZACIÓN DE CORRECCIONES:")
    
    problemas_criticos = []
    problemas_importantes = []
    problemas_menores = []
    
    # Clasificar problemas
    for categoria, problemas in todos_problemas.items():
        for problema in problemas:
            if any(word in problema.lower() for word in ['error crítico', 'falta', 'no disponible']):
                if categoria in ['estructura', 'imports', 'base_datos']:
                    problemas_criticos.append(f"{categoria}: {problema}")
                else:
                    problemas_importantes.append(f"{categoria}: {problema}")
            else:
                problemas_menores.append(f"{categoria}: {problema}")
    
    if problemas_criticos:
        print("\n🚨 CRÍTICOS (Corregir inmediatamente):")
        for p in problemas_criticos:
            print(f"   • {p}")
    
    if problemas_importantes:
        print("\n[WARN]  IMPORTANTES (Corregir pronto):")
        for p in problemas_importantes:
            print(f"   • {p}")
    
    if problemas_menores:
        print("\n📝 MENORES (Mejorar cuando sea posible):")
        for p in problemas_menores:
            print(f"   • {p}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    print("   1. Priorizar correcciones críticas antes de continuar desarrollo")
    print("   2. Implementar tests faltantes para mayor robustez")
    print("   3. Mejorar documentación del código")
    print("   4. Considerar refactorización si hay muchos problemas estructurales")
    
    return total_problemas

def main():
    """Función principal de auditoría"""
    print("🔍 INICIANDO AUDITORÍA COMPLETA DEL MÓDULO INVENTARIO")
    print("=" * 80)
    
    # Ejecutar todas las auditorías
    problemas = {
        'estructura': auditoria_estructura(),
        'imports': auditoria_imports(),
        'base_datos': auditoria_base_datos(),
        'interfaz': auditoria_interfaz(),
        'funcionalidad': auditoria_funcionalidad(),
        'seguridad': auditoria_seguridad(),
        'tests': auditoria_tests(),
        'performance': auditoria_performance()
    }
    
    # Generar reporte final
    total_problemas = generar_reporte_final(problemas)
    
    print(f"\n🏁 AUDITORÍA COMPLETADA")
    print(f"   Problemas encontrados: {total_problemas}")
    print(f"   Tiempo de ejecución: ⏱️")
    
    return total_problemas == 0

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n🛑 Auditoría interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado en auditoría: {e}")
        traceback.print_exc()
        sys.exit(1)
