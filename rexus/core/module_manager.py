"""
Gestor de Módulos Robusto para Rexus.app

Proporciona una solución sistemática para la carga de módulos,
manejo de errores y prevención de vulnerabilidades SQL injection.
"""

import logging
import traceback
                            ]
            )

        if "table" in error_lower:
            suggestions.extend(
                [
                    "• Verificar que las tablas existan en la base de datos",
                    "• Ejecutar scripts de creación de tablas",
                    "• Revisar estructura de la base de datos",
                ]
            )

        if "import" in error_lower:
            suggestions.extend(
                [
                    "• Verificar que todos los archivos del módulo existan",
                    "• Revisar sintaxis de los archivos Python",
                    "• Comprobar dependencias del módulo",
                ]
            )

        if not suggestions:
            suggestions.append("• Revisar logs de la aplicación para más detalles")

        return "\n".join(suggestions)

    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Obtiene el estado de un módulo."""
        return self.loaded_modules.get(module_name, {"status": "not_loaded"})

    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado de todos los módulos."""
        return self.loaded_modules.copy()


# Instancia global del gestor
module_manager = ModuleManager()
