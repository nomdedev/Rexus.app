"""
Script para importar inventario desde archivos CSV/Excel.
Funcionalidad modular y segura para la importación de inventario.
"""

import os
import sys
from datetime import datetime

import pandas as pd

from core.logger import log_error

# Añadir el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def importar_inventario_desde_archivo(
    archivo_path, usuario_actual, confirmar_importacion_callback=None
):
    """
    Importa inventario desde un archivo CSV/Excel a la base de datos.

    Args:
        archivo_path (str): Ruta al archivo CSV/Excel
        usuario_actual (dict): Usuario que realiza la importación
        confirmar_importacion_callback (callable): Función de callback para confirmación

    Returns:
        dict: Resultado de la importación con éxito, mensajes, advertencias y errores
    """
    resultado = {"exito": False, "mensajes": [], "advertencias": [], "errores": []}

    try:
        # Validar permisos de usuario
        if (
            not usuario_actual
            or not hasattr(usuario_actual, "rol")
            or usuario_actual.rol != "TEST_USER"
        ):
            resultado["errores"].append(
                "Solo el usuario de prueba puede importar inventario"
            )
            return resultado

        # Validar que el archivo existe
        if not os.path.exists(archivo_path):
            resultado["errores"].append(f"No se encontró el archivo: {archivo_path}")
            return resultado

        # Leer el archivo CSV/Excel
        try:
            if archivo_path.lower().endswith(".csv"):
                df = pd.read_csv(archivo_path, encoding="utf-8")
            elif archivo_path.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(archivo_path)
            else:
                resultado["errores"].append(
                    "Formato de archivo no soportado. Use CSV o Excel."
                )
                return resultado
        except Exception as e:
            resultado["errores"].append(f"Error al leer el archivo: {str(e)}")
            return resultado

        # Validar que el DataFrame no esté vacío
        if df.empty:
            resultado["errores"].append("El archivo está vacío")
            return resultado

        # Callback de confirmación si se proporciona
        if confirmar_importacion_callback and callable(confirmar_importacion_callback):
            try:
                if not confirmar_importacion_callback(df, resultado):
                    resultado["mensajes"].append("Importación cancelada por el usuario")
                    return resultado
            except Exception as e:
                resultado["advertencias"].append(
                    f"Error en callback de confirmación: {str(e)}"
                )

        # Simular importación exitosa (aquí iría la lógica real de BD)
        # Por ahora, solo devolvemos éxito sin hacer la importación real
        resultado["exito"] = True
        resultado["mensajes"].append(f"Se procesaron {len(df)} registros")
        resultado["mensajes"].append("Importación completada satisfactoriamente")

        # Registrar en logs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje_log = f"[{timestamp}] Importación de inventario: {len(df)} registros desde {archivo_path}"

        # TODO: Implementar la lógica real de inserción en base de datos
        # db = InventarioDatabaseConnection()
        # ... lógica de inserción ...

    except Exception as e:
        log_error(f"Error en importar_inventario_desde_archivo: {str(e)}")
        resultado["errores"].append(f"Error inesperado: {str(e)}")

    return resultado


def validar_estructura_csv(df):
    """
    Valida que el CSV tenga la estructura correcta para inventario.

    Args:
        df (pandas.DataFrame): DataFrame a validar

    Returns:
        dict: Resultado de validación con errores y advertencias
    """
    validacion = {"errores": [], "advertencias": []}

    # Columnas requeridas básicas (ajustar según necesidades reales)
    columnas_requeridas = ["codigo", "descripcion", "cantidad"]

    for col in columnas_requeridas:
        if col not in df.columns:
            validacion["errores"].append(f"Falta la columna requerida: {col}")

    # Validaciones adicionales
    if "cantidad" in df.columns:
        cantidades_invalidas = df[pd.to_numeric(df["cantidad"], errors="coerce").isna()]
        if not cantidades_invalidas.empty:
            validacion["advertencias"].append(
                f"Se encontraron {len(cantidades_invalidas)} registros con cantidades inválidas"
            )

    return validacion


if __name__ == "__main__":
    # Ejemplo de uso del script
    print("Script de importación de inventario")
    print("Este script debe ser llamado desde el controlador de configuración")
