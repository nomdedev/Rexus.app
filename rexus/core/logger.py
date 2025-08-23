"""
Sistema de logging avanzado para Rexus
Versión: 2.0.0 - Producción Ready
"""

import logging
import logging.handlers
import sys
import json
                logging.getLogger("PyQt6").setLevel(logging.WARNING)

    # Configurar otros loggers problemáticos
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Alias para compatibilidad
default_logger = logger
Logger = logger

# Configurar automáticamente al importar
configure_third_party_logging()
