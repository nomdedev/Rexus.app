
#!/usr/bin/env python3
"""
Punto de entrada principal para Rexus.app
"""

import sys
import os
from pathlib import Path

def setup_environment():
	"""Configura el entorno de la aplicación."""
	root_dir = Path(__file__).parent
	os.chdir(root_dir)
	sys.path.insert(0, str(root_dir))

	# Detectar modo desarrollo
	is_dev_mode = (
		'--dev' in sys.argv or
		os.getenv('REXUS_ENV') == 'development' or
		os.getenv('HOTRELOAD_ENABLED', '').lower() == 'true'
	)

	# Cargar variables de entorno
	try:
		from dotenv import load_dotenv

		if is_dev_mode:
			# Cargar configuración de desarrollo
			dev_env_file = root_dir / '.env.development'
			if dev_env_file.exists():
				load_dotenv(dev_env_file)
				print(f"[DEV] Configuracion de desarrollo cargada desde {dev_env_file}")
			else:
				# Configurar credenciales por defecto para desarrollo
				os.environ.setdefault('REXUS_DEV_USER', 'admin')
				os.environ.setdefault('REXUS_DEV_PASSWORD', 'admin')
				os.environ.setdefault('REXUS_DEV_AUTO_LOGIN', 'true')
				print("[DEV] Usando credenciales por defecto: admin/admin")
		else:
			# Cargar configuración normal
			load_dotenv()

	except ImportError:
		if is_dev_mode:
			print("[DEV] python-dotenv no disponible, usando variables del sistema")

	return True

def main():
	"""Función principal."""
	if not setup_environment():
		sys.exit(1)
	try:
		from rexus.main.app import main as app_main
		app_main()
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)

if __name__ == "__main__":
	main()
