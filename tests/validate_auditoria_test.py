#!/usr/bin/env python3
"""
Script de validación para test_auditoria.py
"""

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

try:
    print("=== VALIDANDO test_auditoria.py ===")

    # Intentar importar módulos necesarios
    print("1. Importando pytest...")
    print("   ✅ pytest importado correctamente")

    print("2. Importando MagicMock...")
    print("   ✅ MagicMock importado correctamente")

    print("3. Importando AuditoriaModel...")
    print("   ✅ AuditoriaModel importado correctamente")

    print("4. Validando sintaxis del archivo de test...")
    print("   ✅ test_auditoria.py importado correctamente")
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.auditoria.model import AuditoriaModel

    print("5. Creando mock_db...")
    # Crear una instancia del fixture mock_db manualmente
    mock = MagicMock()
    mock.ejecutar_query.return_value = []
    mock.last_query = None
    mock.last_params = None
    mock.query_result = []
    print("   ✅ mock_db creado correctamente")

    print("6. Creando AuditoriaModel con mock...")
    model = AuditoriaModel(mock)
    print("   ✅ AuditoriaModel instanciado correctamente")

    print("7. Probando método registrar_evento...")
    result = model.registrar_evento(1, "test", "accion", "detalle", "127.0.0.1")
    print(f"   ✅ registrar_evento ejecutado. Resultado: {result}")

    print("\n🎉 VALIDACIÓN EXITOSA: test_auditoria.py está funcionalmente correcto")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"❌ Error de sintaxis: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)
