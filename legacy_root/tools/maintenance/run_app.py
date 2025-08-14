#!/usr/bin/env python3
"""
Script de inicio para Rexus.app
"""

import sys
import os
from pathlib import Path

# Establecer el directorio actual
current_dir = Path(__file__).parent
os.chdir(current_dir)
sys.path.insert(0, str(current_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables .env cargadas")
except:
    print("[WARNING] No se pudo cargar .env")

# Verificar variables críticas
db_server = os.getenv('DB_SERVER')
if db_server:
    print(f"[OK] DB configurada: {db_server}")
else:
    print("[ERROR] Variables de BD no configuradas")

# Importar y ejecutar aplicación
try:
    from src.main.app import main
    main()
except Exception as e:
    print(f"[ERROR] Error iniciando aplicación: {e}")
    import traceback
    traceback.print_exc()
