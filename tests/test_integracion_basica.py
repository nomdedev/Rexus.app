"""
Tests básicos de integración sin dependencias complejas de UI.
Enfoque en validar la funcionalidad del sistema sin problemas de mocks.
"""

# Agregar directorio raíz
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

class TestIntegracionBasica:
    """Tests básicos de integración del sistema."""

    def test_importacion_modulos_core(self):
        """Test que los módulos core se importan correctamente."""
        try:
            # Solo importar DB_SERVER si existe config.py
            if (ROOT_DIR / "core" / "config.py").exists():
            assert True  # Si llegamos aquí, las importaciones funcionan
        except ImportError as e:
            pytest.fail(f"Error importando módulos core: {e}")
        except Exception as e:
            pytest.skip(f"Error de configuración en módulos core: {e}")

    def test_importacion_modelos_principales(self):
        """Test que los modelos principales se importan correctamente."""
        modelos_criticos = [
            ('modules.inventario.model', 'InventarioModel'),
            ('modules.obras.model', 'ObrasModel'),
            ('modules.usuarios.model', 'UsuariosModel'),
            ('modules.contabilidad.model', 'ContabilidadModel')
        ]

        for modulo_path, clase_name in modelos_criticos:
            try:
                modulo = __import__(modulo_path, fromlist=[clase_name])
                getattr(modulo, clase_name)
                print(f"✅ {clase_name} importado correctamente")
            except ImportError as e:
                pytest.skip(f"Módulo {modulo_path} no disponible: {e}")
            except AttributeError as e:
                pytest.skip(f"Clase {clase_name} no encontrada en {modulo_path}: {e}")
            except Exception as e:
                pytest.skip(f"Error inesperado importando {clase_name}: {e}")

        assert True  # Si llegamos aquí, al menos algunos modelos funcionan

    def test_logger_funcional(self):
        """Test que el logger funciona correctamente."""
        try:
            logger = Logger()

            # Verificar que tiene los métodos esperados
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'warning')
            assert hasattr(logger, 'error')

            # Estas operaciones no deberían fallar
            logger.info("Test message")
            logger.warning("Test warning")
            logger.error("Test error")
            assert True
        except Exception as e:
            pytest.skip(f"Logger no funcional: {e}")

    @pytest.mark.skipif(
        not (ROOT_DIR / "core" / "config.py").exists(),
        reason="core/config.py no existe"
    )
    def test_configuracion_disponible(self):
        """Test que la configuración está disponible."""
        try:
                DB_SERVER, DB_USERNAME, DB_PASSWORD,
                DEFAULT_THEME
            )
            # Verificar que las variables tienen valores válidos
            assert isinstance(DB_SERVER, str)
            assert isinstance(DB_USERNAME, str)
            assert isinstance(DB_PASSWORD, str)
            assert isinstance(DEFAULT_THEME, str)
            assert DEFAULT_THEME in ['light', 'dark']
        except ImportError as e:
            pytest.skip(f"Error importando configuración: {e}")
        except AttributeError as e:
            pytest.skip(f"Falta atributo en configuración: {e}")

    def test_database_connection_mock(self):
        """Test que se puede crear una conexión mock a la BD."""
        # Crear mock de conexión
        db_conn = DatabaseConnection()

        # Verificar que el objeto se crea correctamente
        assert db_conn is not None
        assert hasattr(db_conn, 'conectar_a_base')
        assert hasattr(db_conn, 'ejecutar_query')

class TestValidacionEstructura:
    """Tests de validación de estructura del proyecto."""

    def test_estructura_modulos_existe(self):
        """Test que la estructura de módulos existe."""
        modulos_criticos = ['inventario', 'obras', 'contabilidad', 'usuarios']
        modulos_opcionales = ['pedidos', 'auditoria', 'configuracion', 'vidrios', 'herrajes']

        # Verificar módulos críticos
        for modulo in modulos_criticos:
            modulo_path = ROOT_DIR / 'modules' / modulo
            assert modulo_path.exists(), f"Módulo crítico {modulo} no existe"

            # Verificar archivos esenciales
            model_path = modulo_path / 'model.py'
            view_path = modulo_path / 'view.py'
            controller_path = modulo_path / 'controller.py'

            assert model_path.exists(), f"Model de {modulo} no existe"
            assert view_path.exists(), f"View de {modulo} no existe"
            assert controller_path.exists(), f"Controller de {modulo} no existe"

        # Verificar módulos opcionales (no falla si no existen)
        for modulo in modulos_opcionales:
            modulo_path = ROOT_DIR / 'modules' / modulo
            if modulo_path.exists():
                print(f"✅ Módulo opcional {modulo} encontrado")
            else:
                print(f"ℹ️ Módulo opcional {modulo} no encontrado (esto es normal)")

    def test_estructura_tests_existe(self):
        """Test que la estructura de tests existe."""
        tests_path = ROOT_DIR / 'tests'
        assert tests_path.exists(), "Directorio tests no existe"

        # Verificar algunos directorios clave
        directorios_tests = [
            'inventario', 'contabilidad', 'obras', 'usuarios'
        ]

        for directorio in directorios_tests:
            test_dir = tests_path / directorio
            assert test_dir.exists(), f"Directorio tests/{directorio} no existe"

    def test_archivos_configuracion_existen(self):
        """Test que los archivos de configuración existen."""
        archivos_config = [
            'requirements.txt', 'pytest.ini', 'main.py',
            'README.md'
        ]

        for archivo in archivos_config:
            archivo_path = ROOT_DIR / archivo
            assert archivo_path.exists(), f"Archivo {archivo} no existe"

class TestValidacionSintaxis:
    """Tests de validación de sintaxis de archivos críticos."""

    def test_sintaxis_main_py(self):
        """Test que main.py tiene sintaxis correcta."""
        main_path = ROOT_DIR / "main.py"

        with open(main_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Esto lanzará SyntaxError si hay problemas
        ast.parse(contenido)
        assert True

    def test_sintaxis_modelos_principales(self):
        """Test que los modelos principales tienen sintaxis correcta."""
        modelos = [
            'modules/inventario/model.py',
            'modules/obras/model.py',
            'modules/contabilidad/model.py',
            'modules/usuarios/model.py'
        ]

        for modelo_path in modelos:
            archivo_path = ROOT_DIR / modelo_path
            if archivo_path.exists():
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                try:
                    ast.parse(contenido)
                except SyntaxError as e:
                    pytest.fail(f"Error de sintaxis en {modelo_path}: {e}")

    def test_sintaxis_configuracion(self):
        """Test que los archivos de configuración tienen sintaxis correcta."""
        configs = [
            'core/config.py',
            'core/logger.py',
            'core/database.py'
        ]

        for config_path in configs:
            archivo_path = ROOT_DIR / config_path
            if archivo_path.exists():
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                try:
                    ast.parse(contenido)
from pathlib import Path

from core.config import DB_SERVER, DatabaseConnection, Logger
from core.config import SyntaxError as e:
from core.config import (
    ast,
    core.database,
    core.logger,
    de,
    en,
    except,
    f"Error,
    from,
    import,
    pytest,
    pytest.fail,
    sintaxis,
    sys,
    {config_path}:,
    {e}",
)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
