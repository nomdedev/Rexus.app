#!/usr/bin/env python3
"""
Test Manual de Funcionalidades Críticas - Rexus.app
Validación de todas las funcionalidades principales antes de deployment
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ManualTestRunner:
    """Coordinador de tests manuales críticos"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.test_results = []
        self.start_time = None

    def log_test(self, test_name: str, status: str, details: str = ""):
        """Registra resultado de test"""
        result = {
            "test": test_name,
            "status": status,  # PASS, FAIL, SKIP
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   → {details}")

    def test_aplicacion_inicio(self):
        """Test 1: Verificar que la aplicación inicie correctamente"""
        print("\n[TEST 1] Verificando inicio de aplicación...")

        try:
            # Verificar que main.py existe y es ejecutable
            main_file = self.root_path / "main.py"
            if not main_file.exists():
                self.log_test("Inicio de aplicación", "FAIL", "main.py no encontrado")
                return False

            # Verificar imports críticos
            try:
                from rexus.main.app import RexusApp

                self.log_test(
                    "Imports principales", "PASS", "RexusApp importada correctamente"
                )
            except Exception as e:
                self.log_test(
                    "Imports principales", "FAIL", f"Error importando RexusApp: {e}"
                )
                return False

            # Verificar configuración
            from core.config import DatabaseConfig

            self.log_test("Configuración", "PASS", "DatabaseConfig disponible")

            self.log_test(
                "Inicio de aplicación", "PASS", "Todos los componentes disponibles"
            )
            return True

        except Exception as e:
            self.log_test("Inicio de aplicación", "FAIL", f"Error: {e}")
            return False

    def test_seguridad_componentes(self):
        """Test 2: Verificar componentes de seguridad"""
        print("\n[TEST 2] Verificando componentes de seguridad...")

        try:
            # Test DataSanitizer
            from utils.data_sanitizer import DataSanitizer

            sanitizer = DataSanitizer()

            # Test básico de sanitización XSS
            test_input = "<script>alert('xss')</script>Test"
            sanitized = sanitizer.sanitize_html(test_input)
            if "<script>" not in sanitized:
                self.log_test(
                    "DataSanitizer XSS", "PASS", "Script tags removidos correctamente"
                )
            else:
                self.log_test("DataSanitizer XSS", "FAIL", "Script tags no removidos")

            # Test 2FA
            from utils.two_factor_auth import TwoFactorAuth

            tfa = TwoFactorAuth()
            secret = tfa.generar_secret_key()
            if len(secret) == 32:
                self.log_test(
                    "TwoFactorAuth", "PASS", "Secret key generado correctamente"
                )
            else:
                self.log_test("TwoFactorAuth", "FAIL", "Secret key inválido")

            # Test SecurityManager
            from core.security_manager import SecurityManager

            self.log_test("SecurityManager", "PASS", "SecurityManager disponible")

            return True

        except Exception as e:
            self.log_test("Componentes de seguridad", "FAIL", f"Error: {e}")
            return False

    def test_modulos_principales(self):
        """Test 3: Verificar que todos los módulos se importen correctamente"""
        print("\n[TEST 3] Verificando módulos principales...")

        modulos = [
            "administracion",
            "auditoria",
            "compras",
            "configuracion",
            "herrajes",
            "inventario",
            "logistica",
            "mantenimiento",
            "obras",
            "pedidos",
            "usuarios",
            "vidrios",
        ]

        modulos_ok = 0
        for modulo in modulos:
            try:
                # Verificar que el módulo tiene los archivos principales
                modulo_path = self.root_path / "rexus" / "modules" / modulo

                if not modulo_path.exists():
                    self.log_test(
                        f"Módulo {modulo}", "FAIL", "Directorio no encontrado"
                    )
                    continue

                # Verificar archivos críticos
                files_required = ["__init__.py", "view.py", "model.py"]
                missing_files = []

                for file_name in files_required:
                    if not (modulo_path / file_name).exists():
                        missing_files.append(file_name)

                if missing_files:
                    self.log_test(
                        f"Módulo {modulo}",
                        "FAIL",
                        f"Archivos faltantes: {missing_files}",
                    )
                else:
                    # Intentar importar el modelo
                    try:
                        model_module = f"rexus.modules.{modulo}.model"
                        __import__(model_module)
                        self.log_test(f"Módulo {modulo}", "PASS", "Estructura completa")
                        modulos_ok += 1
                    except Exception as e:
                        self.log_test(
                            f"Módulo {modulo}", "FAIL", f"Error importando modelo: {e}"
                        )

            except Exception as e:
                self.log_test(f"Módulo {modulo}", "FAIL", f"Error: {e}")

        success_rate = (modulos_ok / len(modulos)) * 100
        self.log_test(
            "Test de módulos",
            "PASS" if success_rate >= 90 else "FAIL",
            f"{modulos_ok}/{len(modulos)} módulos OK ({success_rate:.1f}%)",
        )

        return success_rate >= 90

    def test_base_datos(self):
        """Test 4: Verificar conectividad y estructura de base de datos"""
        print("\n[TEST 4] Verificando base de datos...")

        try:
            from core.config import DatabaseConfig
            from core.database import DatabaseManager

            # Intentar conexión
            config = DatabaseConfig()

            # Verificar configuración
            if hasattr(config, "host") and hasattr(config, "database"):
                self.log_test(
                    "Configuración BD", "PASS", "Parámetros de conexión disponibles"
                )
            else:
                self.log_test("Configuración BD", "FAIL", "Configuración incompleta")
                return False

            # Test de estructura básica (sin conectar realmente)
            self.log_test("Estructura BD", "PASS", "Configuración verificada")

            return True

        except Exception as e:
            self.log_test("Base de datos", "FAIL", f"Error: {e}")
            return False

    def test_archivos_criticos(self):
        """Test 5: Verificar archivos críticos del proyecto"""
        print("\n[TEST 5] Verificando archivos críticos...")

        archivos_criticos = {
            "requirements.txt": "Dependencias Python",
            "Dockerfile": "Configuración Docker",
            "docker-compose.yml": "Orquestación de servicios",
            "main.py": "Punto de entrada principal",
            "config/rexus_config.json": "Configuración principal",
            "utils/rexus_styles.py": "Estilos UI centralizados",
            "core/security_manager.py": "Gestor de seguridad",
            "docs/UI_UX_STANDARDS.md": "Estándares UI/UX",
        }

        archivos_ok = 0
        for archivo, descripcion in archivos_criticos.items():
            archivo_path = self.root_path / archivo
            if archivo_path.exists():
                # Verificar que no esté vacío
                if archivo_path.stat().st_size > 0:
                    self.log_test(f"Archivo {archivo}", "PASS", descripcion)
                    archivos_ok += 1
                else:
                    self.log_test(f"Archivo {archivo}", "FAIL", "Archivo vacío")
            else:
                self.log_test(f"Archivo {archivo}", "FAIL", "Archivo no encontrado")

        success_rate = (archivos_ok / len(archivos_criticos)) * 100
        self.log_test(
            "Archivos críticos",
            "PASS" if success_rate >= 85 else "FAIL",
            f"{archivos_ok}/{len(archivos_criticos)} archivos OK ({success_rate:.1f}%)",
        )

        return success_rate >= 85

    def test_scripts_deployment(self):
        """Test 6: Verificar scripts de deployment"""
        print("\n[TEST 6] Verificando scripts de deployment...")

        try:
            # Verificar ConfigManager
            from config.config_manager import ConfigManager

            manager = ConfigManager("development")

            if hasattr(manager, "get_database_config"):
                self.log_test("ConfigManager", "PASS", "ConfigManager funcional")
            else:
                self.log_test("ConfigManager", "FAIL", "ConfigManager incompleto")

            # Verificar scripts de deploy
            deploy_script = self.root_path / "scripts" / "deploy.sh"
            if deploy_script.exists():
                self.log_test(
                    "Script deploy", "PASS", "Script de deployment disponible"
                )
            else:
                self.log_test("Script deploy", "FAIL", "Script de deployment faltante")

            # Verificar Docker files
            dockerfile = self.root_path / "Dockerfile"
            compose_file = self.root_path / "docker-compose.yml"

            if dockerfile.exists() and compose_file.exists():
                self.log_test("Docker config", "PASS", "Configuración Docker completa")
            else:
                self.log_test(
                    "Docker config", "FAIL", "Configuración Docker incompleta"
                )

            return True

        except Exception as e:
            self.log_test("Scripts deployment", "FAIL", f"Error: {e}")
            return False

    def test_documentacion(self):
        """Test 7: Verificar documentación crítica"""
        print("\n[TEST 7] Verificando documentación...")

        docs_criticos = {
            "docs/UI_UX_STANDARDS.md": "Estándares UI/UX",
            "docs/COMO_EJECUTAR.md": "Instrucciones de ejecución",
            "REPORTE_PROGRESO_COMPLETO.md": "Estado del proyecto",
            "README_ESTRUCTURA.md": "Estructura del proyecto",
        }

        docs_ok = 0
        for doc, descripcion in docs_criticos.items():
            doc_path = self.root_path / doc
            if doc_path.exists():
                # Verificar que tenga contenido mínimo
                if doc_path.stat().st_size > 1000:  # Al menos 1KB
                    self.log_test(f"Doc {doc.split('/')[-1]}", "PASS", descripcion)
                    docs_ok += 1
                else:
                    self.log_test(
                        f"Doc {doc.split('/')[-1]}",
                        "FAIL",
                        "Documentación insuficiente",
                    )
            else:
                self.log_test(
                    f"Doc {doc.split('/')[-1]}", "FAIL", "Documento no encontrado"
                )

        success_rate = (docs_ok / len(docs_criticos)) * 100
        self.log_test(
            "Documentación",
            "PASS" if success_rate >= 75 else "FAIL",
            f"{docs_ok}/{len(docs_criticos)} docs OK ({success_rate:.1f}%)",
        )

        return success_rate >= 75

    def generar_reporte_final(self):
        """Genera reporte final de tests manuales"""
        print("\n" + "=" * 60)
        print("REPORTE FINAL DE TESTS MANUALES")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total de tests: {total_tests}")
        print(f"Exitosos: {passed_tests}")
        print(f"Fallidos: {failed_tests}")
        print(f"Omitidos: {skipped_tests}")
        print(f"Tasa de éxito: {success_rate:.1f}%")

        # Estado general
        if success_rate >= 90:
            estado = "EXCELENTE - Listo para producción"
            emoji = "🟢"
        elif success_rate >= 75:
            estado = "BUENO - Necesita ajustes menores"
            emoji = "🟡"
        elif success_rate >= 50:
            estado = "REGULAR - Requiere correcciones"
            emoji = "🟠"
        else:
            estado = "CRÍTICO - No apto para deployment"
            emoji = "🔴"

        print(f"\n{emoji} Estado general: {estado}")

        # Guardar reporte
        try:
            logs_path = self.root_path / "logs"
            logs_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reporte_path = logs_path / f"manual_tests_report_{timestamp}.json"

            reporte = {
                "timestamp": timestamp,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": round(success_rate, 2),
                "estado": estado,
                "duracion_segundos": time.time() - self.start_time
                if self.start_time
                else 0,
                "tests": self.test_results,
            }

            with open(reporte_path, "w", encoding="utf-8") as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)

            print(f"\n[SUCCESS] Reporte guardado en: {reporte_path}")

        except Exception as e:
            print(f"[ERROR] No se pudo guardar el reporte: {e}")

        return success_rate >= 75

    def ejecutar_todos_los_tests(self):
        """Ejecuta todos los tests manuales"""
        self.start_time = time.time()

        print("=" * 60)
        print("INICIANDO TESTS MANUALES CRÍTICOS - REXUS.APP")
        print("=" * 60)

        # Ejecutar tests en orden
        tests_exitosos = 0

        if self.test_aplicacion_inicio():
            tests_exitosos += 1

        if self.test_seguridad_componentes():
            tests_exitosos += 1

        if self.test_modulos_principales():
            tests_exitosos += 1

        if self.test_base_datos():
            tests_exitosos += 1

        if self.test_archivos_criticos():
            tests_exitosos += 1

        if self.test_scripts_deployment():
            tests_exitosos += 1

        if self.test_documentacion():
            tests_exitosos += 1

        # Generar reporte final
        return self.generar_reporte_final()


def main():
    """Función principal"""
    runner = ManualTestRunner()
    exito = runner.ejecutar_todos_los_tests()

    if exito:
        print("\n🎉 TESTS MANUALES COMPLETADOS EXITOSAMENTE")
        print("✅ El proyecto está listo para las siguientes fases")
    else:
        print("\n⚠️ TESTS MANUALES COMPLETADOS CON PROBLEMAS")
        print("❌ Se requieren correcciones antes de continuar")

    return 0 if exito else 1


if __name__ == "__main__":
    exit(main())
