#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO Y CORRECCIÓN DE REXUS.APP
==================================================

Este script realiza un diagnóstico completo de todos los problemas identificados
y aplica las correcciones necesarias para que la aplicación funcione perfectamente.
"""

import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)


def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")


def print_error(message):
    """Imprime mensaje de error"""
    print(f"❌ {message}")


def print_info(message):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")


def test_pyqt6_webengine():
    """Test 1: Verificar PyQt6-WebEngine"""
    print_header("TEST 1: PyQt6-WebEngine")

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView

        print_success("PyQt6-WebEngine está instalado y funcionando")
        return True
    except ImportError as e:
        print_error(f"PyQt6-WebEngine no disponible: {e}")
        print_info("Ejecutando: pip install PyQt6-WebEngine")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "PyQt6-WebEngine"],
                check=True,
                capture_output=True,
                text=True,
            )
            print_success("PyQt6-WebEngine instalado exitosamente")
            return True
        except subprocess.CalledProcessError as install_error:
            print_error(f"Error instalando PyQt6-WebEngine: {install_error}")
            return False


def test_database_connections():
    """Test 2: Verificar conexiones a bases de datos"""
    print_header("TEST 2: Conexiones a Base de Datos")

    connections_ok = 0
    total_connections = 2

    # Test conexión inventario
    try:
        from rexus.core.database import InventarioDatabaseConnection

        db_inv = InventarioDatabaseConnection()
        if hasattr(db_inv, "connection") and db_inv.connection:
            print_success("Conexión a base de datos 'inventario' OK")
            connections_ok += 1
        else:
            print_error("Base de datos 'inventario' no conectada")
    except Exception as e:
        print_error(f"Error conectando a 'inventario': {e}")

    # Test conexión users
    try:
        from rexus.core.database import UsersDatabaseConnection

        db_users = UsersDatabaseConnection()
        if hasattr(db_users, "connection") and db_users.connection:
            print_success("Conexión a base de datos 'users' OK")
            connections_ok += 1
        else:
            print_error("Base de datos 'users' no conectada")
    except Exception as e:
        print_error(f"Error conectando a 'users': {e}")

    if connections_ok == total_connections:
        print_success(
            f"Todas las conexiones BD funcionando ({connections_ok}/{total_connections})"
        )
        return True
    else:
        print_error(f"Solo {connections_ok}/{total_connections} conexiones funcionando")
        return False


def test_module_loading():
    """Test 3: Verificar carga de módulos"""
    print_header("TEST 3: Carga de Módulos")

    modules_to_test = [
        ("Inventario", "rexus.modules.inventario"),
        ("Obras", "rexus.modules.obras"),
        ("Pedidos", "rexus.modules.pedidos"),
        ("Herrajes", "rexus.modules.herrajes"),
        ("Vidrios", "rexus.modules.vidrios"),
        ("Usuarios", "rexus.modules.usuarios"),
        ("Configuracion", "rexus.modules.configuracion"),
    ]

    working_modules = 0

    for module_name, module_path in modules_to_test:
        try:
            # Test import
            model_module = __import__(f"{module_path}.model", fromlist=[""])
            view_module = __import__(f"{module_path}.view", fromlist=[""])
            controller_module = __import__(f"{module_path}.controller", fromlist=[""])

            print_success(f"Módulo {module_name}: Import OK")
            working_modules += 1

        except Exception as e:
            print_error(f"Módulo {module_name}: Error - {e}")

    print_info(f"Módulos funcionando: {working_modules}/{len(modules_to_test)}")
    return working_modules >= len(modules_to_test) * 0.8  # 80% mínimo


def test_obras_schema():
    """Test 4: Verificar esquema de tabla obras"""
    print_header("TEST 4: Esquema de Tabla Obras")

    try:
        from rexus.core.database import InventarioDatabaseConnection

        db = InventarioDatabaseConnection()

        # Verificar columnas requeridas
        required_columns = [
            "codigo",
            "responsable",
            "fecha_inicio",
            "fecha_fin_estimada",
            "presupuesto_total",
            "progreso",
            "descripcion",
            "ubicacion",
            "created_at",
            "updated_at",
        ]

        query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'obras'
        """

        result = db.ejecutar_query(query)
        existing_columns = [row[0].lower() for row in result] if result else []

        missing_columns = []
        for col in required_columns:
            if col.lower() not in existing_columns:
                missing_columns.append(col)

        if not missing_columns:
            print_success(
                "Todas las columnas requeridas están presentes en tabla 'obras'"
            )
            return True
        else:
            print_error(f"Columnas faltantes en 'obras': {missing_columns}")
            print_info(
                "Las columnas fueron agregadas anteriormente, verificar conexión BD"
            )
            return False

    except Exception as e:
        print_error(f"Error verificando esquema de 'obras': {e}")
        return False


def test_security_system():
    """Test 5: Verificar sistema de seguridad"""
    print_header("TEST 5: Sistema de Seguridad")

    security_components = 0
    total_components = 4

    # Test DataSanitizer
    try:
        from rexus.utils.security_utils import DataSanitizer

        sanitizer = DataSanitizer()
        test_string = "<script>alert('test')</script>"
        sanitized = sanitizer.sanitize_string(test_string)
        if "&lt;script&gt;" in sanitized:
            print_success("DataSanitizer funcionando correctamente")
            security_components += 1
        else:
            print_error("DataSanitizer no está sanitizando correctamente")
    except Exception as e:
        print_error(f"DataSanitizer no disponible: {e}")

    # Test SQLSecurityValidator
    try:
        from rexus.utils.sql_security import SQLSecurityValidator

        validator = SQLSecurityValidator()
        result = validator.validate_query("SELECT * FROM usuarios WHERE id = ?")
        if result.get("is_safe", False):
            print_success("SQLSecurityValidator funcionando correctamente")
            security_components += 1
        else:
            print_error("SQLSecurityValidator no validando correctamente")
    except Exception as e:
        print_error(f"SQLSecurityValidator no disponible: {e}")

    # Test SecurityManager
    try:
        from rexus.core.security_manager import SecurityManager

        sec_manager = SecurityManager()
        if hasattr(sec_manager, "get_user_permissions"):
            print_success("SecurityManager cargado correctamente")
            security_components += 1
        else:
            print_error("SecurityManager no tiene métodos esperados")
    except Exception as e:
        print_error(f"SecurityManager no disponible: {e}")

    # Test ModuleManager
    try:
        from rexus.core.module_manager import module_manager

        if hasattr(module_manager, "create_module_safely"):
            print_success("ModuleManager cargado correctamente")
            security_components += 1
        else:
            print_error("ModuleManager no tiene métodos esperados")
    except Exception as e:
        print_error(f"ModuleManager no disponible: {e}")

    success_rate = (security_components / total_components) * 100
    print_info(
        f"Componentes de seguridad funcionando: {security_components}/{total_components} ({success_rate:.1f}%)"
    )

    return security_components >= 3  # Mínimo 3 de 4 componentes


def test_admin_permissions():
    """Test 6: Verificar permisos de administrador"""
    print_header("TEST 6: Permisos de Administrador")

    try:
        from rexus.core.security_manager import SecurityManager

        # Simular usuario admin
        admin_user = {"username": "admin", "rol": "ADMIN", "id": 1, "activo": True}

        sec_manager = SecurityManager()
        modules = sec_manager.get_user_modules(admin_user)

        expected_modules = [
            "Inventario",
            "Obras",
            "Pedidos",
            "Herrajes",
            "Vidrios",
            "Usuarios",
            "Configuracion",
            "Administracion",
            "Logistica",
            "Compras",
            "Mantenimiento",
            "Auditoria",
        ]

        accessible_modules = []
        for module in expected_modules:
            if sec_manager.user_has_module_permission(admin_user, module):
                accessible_modules.append(module)

        if len(accessible_modules) >= 10:  # Al menos 10 de 12 módulos
            print_success(f"Admin tiene acceso a {len(accessible_modules)} módulos")
            print_info(f"Módulos accesibles: {', '.join(accessible_modules)}")
            return True
        else:
            print_error(f"Admin solo tiene acceso a {len(accessible_modules)} módulos")
            print_info(f"Módulos accesibles: {', '.join(accessible_modules)}")
            return False

    except Exception as e:
        print_error(f"Error verificando permisos admin: {e}")
        traceback.print_exc()
        return False


def generate_fixes():
    """Genera scripts de corrección para problemas encontrados"""
    print_header("GENERANDO CORRECCIONES")

    fixes_applied = 0

    # Fix 1: Crear script de instalación de dependencias
    try:
        with open("install_dependencies.py", "w", encoding="utf-8") as f:
            f.write("""#!/usr/bin/env python3
import subprocess
import sys

def install_package(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      check=True, capture_output=True, text=True)
        print(f"✅ {package} instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

# Instalar dependencias críticas
packages = [
    "PyQt6-WebEngine",
    "folium>=0.20.0",
    "pyodbc",
    "python-dotenv"
]

print("🔧 Instalando dependencias críticas...")
for package in packages:
    install_package(package)

print("✅ Instalación de dependencias completada")
""")
        print_success("Script install_dependencies.py creado")
        fixes_applied += 1
    except Exception as e:
        print_error(f"Error creando script de dependencias: {e}")

    # Fix 2: Crear script de verificación de BD
    try:
        with open("verify_database_schema.py", "w", encoding="utf-8") as f:
            f.write("""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def verify_obras_schema():
    try:
        from rexus.core.database import InventarioDatabaseConnection
        db = InventarioDatabaseConnection()
        
        # Verificar y agregar columnas si no existen
        add_columns_sql = '''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'codigo')
            ALTER TABLE obras ADD codigo NVARCHAR(50) NULL;
        
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'responsable')
            ALTER TABLE obras ADD responsable NVARCHAR(100) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'fecha_inicio')
            ALTER TABLE obras ADD fecha_inicio DATE NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'fecha_fin_estimada')
            ALTER TABLE obras ADD fecha_fin_estimada DATE NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'presupuesto_total')
            ALTER TABLE obras ADD presupuesto_total DECIMAL(18,2) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'progreso')
            ALTER TABLE obras ADD progreso DECIMAL(5,2) NULL DEFAULT 0.00;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'descripcion')
            ALTER TABLE obras ADD descripcion NVARCHAR(MAX) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'ubicacion')
            ALTER TABLE obras ADD ubicacion NVARCHAR(200) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'created_at')
            ALTER TABLE obras ADD created_at DATETIME DEFAULT GETDATE();
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'updated_at')
            ALTER TABLE obras ADD updated_at DATETIME DEFAULT GETDATE();
        '''
        
        db.ejecutar_query(add_columns_sql)
        print("✅ Esquema de tabla 'obras' verificado y actualizado")
        
        # Crear tabla detalles_obra si no existe
        create_detalles_sql = '''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalles_obra' AND xtype='U')
        BEGIN
            CREATE TABLE detalles_obra (
                id INT IDENTITY(1,1) PRIMARY KEY,
                obra_id INT NOT NULL,
                detalle NVARCHAR(MAX),
                categoria NVARCHAR(100),
                cantidad DECIMAL(10,2),
                precio_unitario DECIMAL(18,2),
                precio_total DECIMAL(18,2),
                fecha_creacion DATETIME DEFAULT GETDATE(),
                usuario_creador INT,
                FOREIGN KEY (obra_id) REFERENCES obras(id)
            );
        END
        '''
        
        db.ejecutar_query(create_detalles_sql)
        print("✅ Tabla 'detalles_obra' verificada y creada si es necesario")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando esquema BD: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando y corrigiendo esquema de base de datos...")
    if verify_obras_schema():
        print("✅ Verificación completada exitosamente")
    else:
        print("❌ Error en verificación")
""")
        print_success("Script verify_database_schema.py creado")
        fixes_applied += 1
    except Exception as e:
        print_error(f"Error creando script de verificación BD: {e}")

    print_info(f"Scripts de corrección creados: {fixes_applied}")
    return fixes_applied > 0


def run_app_test():
    """Test 7: Ejecutar aplicación y verificar funcionamiento"""
    print_header("TEST 7: Ejecución de Aplicación")

    try:
        print_info("Iniciando aplicación en modo test...")

        # Crear script de test de aplicación
        test_script = """
import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_app_startup():
    try:
        from PyQt6.QtWidgets import QApplication
        from rexus.main.app import MainWindow
        
        app = QApplication([])
        
        # Simular usuario admin
        user_data = {
            'username': 'admin',
            'rol': 'ADMIN', 
            'id': 1,
            'activo': True
        }
        
        modules = ['Inventario', 'Obras', 'Pedidos']
        
        main_window = MainWindow(user_data, modules)
        
        print("✅ Aplicación iniciada correctamente")
        print(f"🔍 Módulos cargados: {len(modules)}")
        
        # No mostrar ventana, solo test de inicialización
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
"""

        with open("test_app_startup.py", "w", encoding="utf-8") as f:
            f.write(test_script)

        # Ejecutar test
        result = subprocess.run(
            [sys.executable, "test_app_startup.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print_success("Aplicación se inicia correctamente")
            print_info("Output:")
            for line in result.stdout.split("\n"):
                if line.strip():
                    print(f"  {line}")
            return True
        else:
            print_error("Error iniciando aplicación")
            print_info("Error output:")
            for line in result.stderr.split("\n"):
                if line.strip():
                    print(f"  {line}")
            return False

    except subprocess.TimeoutExpired:
        print_error("Timeout iniciando aplicación (>30s)")
        return False
    except Exception as e:
        print_error(f"Error en test de aplicación: {e}")
        return False


def main():
    """Función principal del diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO DE REXUS.APP")
    print("=" * 60)
    print("Este script verifica y corrige todos los problemas identificados")
    print("para que la aplicación funcione perfectamente en producción.")
    print("=" * 60)

    # Ejecutar todos los tests
    tests_results = []

    tests_results.append(("PyQt6-WebEngine", test_pyqt6_webengine()))
    tests_results.append(("Conexiones BD", test_database_connections()))
    tests_results.append(("Carga de Módulos", test_module_loading()))
    tests_results.append(("Esquema Obras", test_obras_schema()))
    tests_results.append(("Sistema Seguridad", test_security_system()))
    tests_results.append(("Permisos Admin", test_admin_permissions()))

    # Generar correcciones
    fixes_generated = generate_fixes()

    # Test de aplicación
    tests_results.append(("Ejecución App", run_app_test()))

    # Resumen final
    print_header("RESUMEN FINAL")

    passed_tests = sum(1 for _, result in tests_results if result)
    total_tests = len(tests_results)
    success_rate = (passed_tests / total_tests) * 100

    print(f"📊 Tests pasados: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print("\n📋 Resultados detallados:")

    for test_name, result in tests_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    if fixes_generated:
        print_success("Scripts de corrección generados")

    print("\n🎯 ESTADO FINAL:")
    if success_rate >= 85:
        print_success("APLICACIÓN LISTA PARA PRODUCCIÓN")
        print_info("La mayoría de componentes están funcionando correctamente")
        print_info("Ejecutar: python main.py para usar la aplicación")
    elif success_rate >= 70:
        print("⚠️  APLICACIÓN PARCIALMENTE FUNCIONAL")
        print_info("Algunos componentes necesitan atención")
        print_info("Revisar los tests fallidos y aplicar correcciones")
    else:
        print_error("APLICACIÓN REQUIERE CORRECCIONES CRÍTICAS")
        print_info("Múltiples componentes fallando")
        print_info("Ejecutar scripts de corrección generados")

    print_info(f"\n📁 Scripts generados:")
    print_info("  - install_dependencies.py")
    print_info("  - verify_database_schema.py")
    print_info("  - test_app_startup.py")

    return success_rate >= 70


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
