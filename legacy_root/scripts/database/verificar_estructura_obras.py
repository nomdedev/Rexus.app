"""
Script para verificar la estructura de la tabla obras
y ajustar el modelo según la estructura real
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

def verificar_estructura_obras():
    """Verifica la estructura real de la tabla obras."""
    try:
        from rexus.core.database import get_inventario_connection

        print("[INFO] Verificando estructura de tabla 'obras'...")

        db_conn = get_inventario_connection(auto_connect=True)
        if not db_conn or not db_conn.connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False

        cursor = db_conn.connection.cursor()

        # Obtener estructura de la tabla
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'obras'
            ORDER BY ORDINAL_POSITION
        """)

        columnas = cursor.fetchall()

        if not columnas:
            print("[ERROR] La tabla 'obras' no existe o no se puede acceder")
            return False

        print(f"[SUCCESS] Tabla 'obras' encontrada con {len(columnas)} columnas:")
        print("\n[INFO] ESTRUCTURA DE LA TABLA:")
        print("-" * 80)
        print(f"{'COLUMNA':<25} {'TIPO':<15} {'NULLABLE':<10} {'DEFAULT':<20}")
        print("-" * 80)

        columnas_encontradas = {}
        for col in columnas:
            nombre, tipo, nullable, default = col
            print(f"{nombre:<25} {tipo:<15} {nullable:<10} {str(default):<20}")
            columnas_encontradas[nombre.lower()] = {
                'tipo': tipo,
                'nullable': nullable,
                'default': default
            }

        # Verificar columnas críticas esperadas
        columnas_criticas = [
            'id', 'codigo', 'nombre', 'cliente', 'responsable',
            'fecha_inicio', 'fecha_fin_estimada', 'estado',
            'presupuesto_total', 'activo', 'created_at', 'updated_at'
        ]

        print("\n[INFO] VERIFICACION DE COLUMNAS CRITICAS:")
        print("-" * 50)
        faltantes = []
        for col in columnas_criticas:
            if col.lower() in columnas_encontradas:
                print(f"[OK] {col}")
            else:
                print(f"[MISSING] {col} - FALTANTE")
                faltantes.append(col)

        if faltantes:
            print(f"\n[WARNING] COLUMNAS FALTANTES: {', '.join(faltantes)}")
            print("[INFO] Considere ejecutar migraciones de base de datos")
        else:
            print("\n[SUCCESS] Todas las columnas criticas estan presentes")

        # Verificar algunos registros de ejemplo
        cursor.execute("SELECT COUNT(*) FROM obras")
        total_obras = cursor.fetchone()[0]
        print(f"\n[INFO] Total de obras en la base: {total_obras}")

        if total_obras > 0:
            cursor.execute("SELECT TOP 3 id,
codigo,
                nombre,
                estado FROM obras ORDER BY created_at DESC")
            obras_muestra = cursor.fetchall()
            print("\n[INFO] MUESTRA DE OBRAS:")
            print("-" * 60)
            for obra in obras_muestra:
                print(f"ID: {obra[0]},
Código: {obra[1]},
                    Nombre: {obra[2][:30]}...,
                    Estado: {obra[3]}")

        cursor.close()
        return True

    except Exception as e:
        print(f"[ERROR] Error verificando estructura: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("[INFO] VERIFICADOR DE ESTRUCTURA - TABLA OBRAS")
    print("=" * 60)

    exito = verificar_estructura_obras()

    if exito:
        print("\n[SUCCESS] VERIFICACION COMPLETADA EXITOSAMENTE")
    else:
        print("\n[ERROR] VERIFICACION FALLO - REVISE LA CONFIGURACION")

    print("=" * 60)
