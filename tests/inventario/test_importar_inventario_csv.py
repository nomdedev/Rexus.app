sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
def test_importar_csv_y_consultar():
    # Ejecutar el script de importación
    resultado = os.system('python scripts/importar_inventario_csv.py')
    assert resultado == 0, "El script de importación falló"

    # Usar directamente la configuración del sistema
import os
import sys

import pandas as pd
import pyodbc

from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE
from core.logger import log_error
    server = DB_SERVER
    database = DB_DEFAULT_DATABASE
    username = DB_USERNAME
    password = DB_PASSWORD
    driver = "ODBC Driver 17 for SQL Server"

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD=***;"  # No mostrar password
        f"TrustServerCertificate=yes;"
    )
    try:
        real_connection_string = connection_string.replace("PWD=***;", f"PWD={password};")
        with pyodbc.connect(real_connection_string, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventario_perfiles")
            row = cursor.fetchone()
            assert row is not None, "La consulta COUNT(*) no devolvió resultados; ¿existe la tabla inventario_perfiles?"
            total = row[0]
            assert total > 0, "La tabla inventario_perfiles está vacía tras la importación"
            cursor.execute("SELECT TOP 5 codigo, descripcion, stock, pedido FROM inventario_perfiles")
            filas = cursor.fetchall()
            assert len(filas) > 0, "No se obtuvieron registros tras la importación"
            for fila in filas:
                assert fila[0] is not None, "El campo 'codigo' no debe ser None"
                assert fila[1] is not None, "El campo 'descripcion' no debe ser None"
        print("Test de importación y consulta de inventario_perfiles: OK")
    except Exception as e:
        log_error(f"Error en test_importar_csv_y_consultar: {str(e)}")
        assert False, f"Error en test_importar_csv_y_consultar: {str(e)}"

def test_coincidencia_columnas_csv_sql():
    # Leer el CSV y verificar que las columnas requeridas existen
    csv_path = os.path.join('data_inventario', 'INVENTARIO_COMPLETO_REHAU_LIMPIO.csv')
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        df.columns = [col.lower() for col in df.columns]
    except FileNotFoundError:
        assert False, f"No se encontró el archivo de prueba: {csv_path}"
    columnas_requeridas = [
        'codigo', 'nombre', 'tipo_material', 'unidad', 'stock_actual', 'stock_minimo', 'ubicacion', 'descripcion', 'qr', 'imagen'
    ]
    for col in columnas_requeridas:
        assert col in df.columns, f"Falta la columna requerida: {col}"
    print("Test de columnas del CSV: OK")

if __name__ == "__main__":
    test_coincidencia_columnas_csv_sql()
    test_importar_csv_y_consultar()
