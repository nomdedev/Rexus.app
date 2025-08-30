"""
Rexus.app - Validador de Dependencias

Módulo para validar que todas las dependencias del sistema estén instaladas
y configuradas correctamente antes de iniciar la aplicación.
"""

import importlib
from typing import List, Tuple

class DependencyValidator:
    """
    Validador de dependencias del sistema.
    Verifica que todos los módulos requeridos estén disponibles.
    """

    REQUIRED_MODULES = [
        'PyQt6',
        'pyodbc',
        'dotenv',
        'cryptography',
        'bcrypt'
    ]

    OPTIONAL_MODULES = [
        'pandas',
        'numpy',
        'matplotlib'
    ]

    def __init__(self):
        self.missing_required = []
        self.missing_optional = []
        self.validation_results = {}

    def validate_all_dependencies(self) -> bool:
        """
        Valida todas las dependencias requeridas y opcionales.

        Returns:
            True si todas las dependencias requeridas están disponibles
        """
        self._validate_required_modules()
        self._validate_optional_modules()

        return len(self.missing_required) == 0

    def _validate_required_modules(self):
        """Valida los módulos requeridos."""
        for module_name in self.REQUIRED_MODULES:
            available, version = self._check_module(module_name)
            self.validation_results[module_name] = {
                'available': available,
                'version': version,
                'required': True
            }
            if not available:
                self.missing_required.append(module_name)

    def _validate_optional_modules(self):
        """Valida los módulos opcionales."""
        for module_name in self.OPTIONAL_MODULES:
            available, version = self._check_module(module_name)
            self.validation_results[module_name] = {
                'available': available,
                'version': version,
                'required': False
            }
            if not available:
                self.missing_optional.append(module_name)

    def _check_module(self, module_name: str) -> Tuple[bool, str]:
        """
        Verifica si un módulo está disponible e intenta obtener su versión.

        Args:
            module_name: Nombre del módulo a verificar

        Returns:
            Tupla (disponible, versión)
        """
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'Unknown')
            return True, str(version)
        except ImportError:
            return False, 'Not installed'

    def get_validation_report(self) -> str:
        """
        Genera un reporte detallado de la validación de dependencias.

        Returns:
            String con el reporte formateado
        """
        report_lines = ["🔍 REPORTE DE VALIDACIÓN DE DEPENDENCIAS", "="*50]

        # Dependencias requeridas
        report_lines.append("\n📦 DEPENDENCIAS REQUERIDAS:")
        for module, info in self.validation_results.items():
            if info['required']:
                status = "✅" if info['available'] else "❌"
                report_lines.append(f"  {status} {module}: {info['version']}")

        # Dependencias opcionales
        if self.missing_optional:
            report_lines.append("\n📦 DEPENDENCIAS OPCIONALES (FALTANTES):")
            for module in self.missing_optional:
                report_lines.append(f"  ⚠️  {module}: No disponible")

        # Resumen
        report_lines.append("\n📊 RESUMEN:")
        report_lines.append(f"  Requeridas faltantes: {len(self.missing_required)}")
        report_lines.append(f"  Opcionales faltantes: {len(self.missing_optional)}")

        if self.missing_required:
            report_lines.append("\n❌ DEPENDENCIAS REQUERIDAS FALTANTES:")
            for module in self.missing_required:
                report_lines.append(f"     pip install {module}")

        return "\n".join(report_lines)

    def get_missing_modules(self) -> List[str]:
        """
        Obtiene la lista de módulos faltantes (requeridos).

        Returns:
            Lista de nombres de módulos faltantes
        """
        return self.missing_required.copy()

def validate_system_dependencies() -> Tuple[bool, dict]:
    """
    Función de conveniencia para validar dependencias del sistema.

    Returns:
        Tupla con (éxito, información de dependencias)
    """
    validator = DependencyValidator()
    is_valid = validator.validate_all_dependencies()

    deps_info = {
        "status": "VALID" if is_valid else "INVALID",
        "missing_required": validator.missing_required,
        "missing_optional": validator.missing_optional,
        "validation_results": validator.validation_results
    }

    if not is_valid:
        print(validator.get_validation_report())

    return is_valid, deps_info
