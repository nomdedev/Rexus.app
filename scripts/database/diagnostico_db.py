"""
Script para realizar un diagnóstico completo de la base de datos.
Genera un reporte detallado de la estructura, relaciones y estadísticas.
"""

# Agregar el directorio raíz al path de Python
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

def generar_reporte_diagnostico(formato='html', tablas_especificas=None, ruta_salida=None):
    """
    Genera un reporte de diagnóstico de la base de datos.

    Args:
        formato (str): Formato del reporte ('html' o 'json')
        tablas_especificas (list): Lista opcional de tablas específicas a analizar
        ruta_salida (str): Ruta donde guardar el reporte. Si no se proporciona,
                          se guardará en la carpeta logs/ con un nombre basado en la fecha actual.

    Returns:
        str: Ruta del archivo generado
    """
    logger = Logger()
    logger.info(f"Iniciando diagnóstico de base de datos ({formato})")

import argparse
import datetime
import sys
from pathlib import Path

from core.database import ObrasDatabaseConnection
from core.exceptions import ConnectionError, QueryError
from core.logger import Logger
from utils.analizador_db import AnalizadorDB

    try:
        # Crear la conexión y el analizador
        db = ObrasDatabaseConnection()
        analizador = AnalizadorDB(db)

        # Generar nombre de archivo si no se proporcionó
        if not ruta_salida:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"diagnostico_db_{timestamp}.{formato.lower()}"
            ruta_salida = str(ROOT_DIR / "logs" / nombre_archivo)

        # Generar y guardar el reporte
        ruta_completa = analizador.guardar_reporte(
            ruta_salida,
            tablas=tablas_especificas,
            formato=formato
        )

        logger.info(f"Reporte de diagnóstico generado exitosamente: {ruta_completa}")
        print(f"\n✅ Reporte generado en: {ruta_completa}")

        return ruta_completa

    except ConnectionError as e:
        logger.error(f"Error de conexión durante el diagnóstico: {e}")
        print(f"\n❌ Error de conexión: {e}")
        raise
    except Exception as e:
        logger.error(f"Error durante el diagnóstico: {e}")
        print(f"\n❌ Error durante el diagnóstico: {e}")
        raise

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Generar diagnóstico de la base de datos.')
    parser.add_argument('--formato', choices=['html', 'json'], default='html',
                        help='Formato del reporte (html o json)')
    parser.add_argument('--tablas', nargs='*',
                        help='Nombres de tablas específicas a analizar (opcional)')
    parser.add_argument('--salida', type=str,
                        help='Ruta donde guardar el reporte (opcional)')
    args = parser.parse_args()

    try:
        generar_reporte_diagnostico(
            formato=args.formato,
            tablas_especificas=args.tablas,
            ruta_salida=args.salida
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
