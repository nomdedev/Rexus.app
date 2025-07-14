"""
Script para verificar rápidamente las tablas existentes en la base de datos.
Utiliza la capa de conexión del sistema, manejo de excepciones personalizadas
y validación de entrada para incrementar la seguridad.
"""
# Agregar el directorio raíz al path de Python
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importar componentes del sistema
# Lista blanca de tablas conocidas en el sistema
TABLAS_CONOCIDAS = [
    'users', 'obras', 'Inventario', 'vidrios_por_obra', 'herrajes_por_obra',
    'pedidos_material', 'pedidos_herrajes', 'pagos_pedidos', 'auditoria',
    'materiales_por_obra', 'cronograma_obras', 'auditorias_sistema',
    'clientes', 'proveedores', 'configuracion'
import argparse
import sys
from pathlib import Path

from core.database import ObrasDatabaseConnection
from core.exceptions import ConnectionError, QueryError
from core.logger import Logger

]

def validar_lista_blanca(valor, lista_permitida):
    """
    Valida que un valor esté dentro de una lista blanca de valores permitidos.

    Args:
        valor: El valor a validar
        lista_permitida: Lista de valores permitidos

    Returns:
        bool: True si el valor está en la lista blanca, False en caso contrario
    """
    return valor in lista_permitida

def verificar_tablas(tablas_especificas=None):
    """
    Verifica las tablas existentes en la base de datos.

    Args:
        tablas_especificas: Lista opcional de nombres de tablas específicas a verificar.
                           Si es None, se verifican todas las tablas en la lista blanca.

    Returns:
        tuple: (tablas_encontradas, resultados_verificacion) donde:
               - tablas_encontradas es una lista de nombres de tablas
               - resultados_verificacion es un diccionario con información de cada tabla verificada
    """
    logger = Logger()
    db = ObrasDatabaseConnection()
    tablas_encontradas = []
    resultados = {}

    try:
        # Conectar a la base de datos
        db.conectar()
        print("✅ Conectado a la base de datos")

        # Obtener lista de tablas
        query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        result = db.ejecutar_query(query)

        if result:
            tablas_encontradas = [row[0] for row in result]
            print(f"\n📋 Tablas encontradas ({len(tablas_encontradas)}):")
            for tabla in tablas_encontradas:
                print(f"  - {tabla}")
        else:
            print("⚠️ No se encontraron tablas en la base de datos")

        # Determinar qué tablas verificar
        if tablas_especificas:
            # Validar que las tablas especificadas estén en la lista blanca
            tablas_a_verificar = [t for t in tablas_especificas if validar_lista_blanca(t, TABLAS_CONOCIDAS)]
            if len(tablas_a_verificar) < len(tablas_especificas):
                print("\n⚠️ Algunas tablas especificadas no están en la lista blanca y serán ignoradas")
        else:
            # Por defecto verificar todas las tablas conocidas
            tablas_a_verificar = TABLAS_CONOCIDAS

        # Verificar tablas
        print(f"\n🔍 Verificación de tablas:")
        for tabla in tablas_a_verificar:
            try:
                # Validar que el nombre de la tabla esté en la lista blanca
                if validar_lista_blanca(tabla, TABLAS_CONOCIDAS):
                    # Usar consultas parametrizadas para mayor seguridad
                    count_query = f"SELECT COUNT(*) FROM [{tabla}]"
                    count_result = db.ejecutar_query(count_query)
                    count = count_result[0][0] if count_result else 0

                    # Verificar estructura de la tabla
                    columns_query = f"""
                        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION
                    """
                    columns_result = db.ejecutar_query(columns_query, (tabla,))

                    # Almacenar los resultados
                    resultados[tabla] = {
                        'registros': count,
                        'existe': tabla in tablas_encontradas,
                        'columnas': [
                            {
                                'nombre': col[0],
                                'tipo': col[1],
                                'longitud': col[2]
                            } for col in columns_result
                        ] if columns_result else []
                    }

                    # Mostrar resumen
                    estado = "✅" if tabla in tablas_encontradas else "❌"
                    print(f"  {estado} {tabla}: {count} registros, {len(resultados[tabla]['columnas'])} columnas")
                else:
                    print(f"  ⚠️ {tabla}: No está en la lista de tablas permitidas")
            except Exception as e:
                logger.error(f"Error al verificar tabla {tabla}: {e}")
                print(f"  ❌ {tabla}: Error - {e}")
                resultados[tabla] = {
                    'error': str(e),
                    'existe': False,
                    'registros': 0,
                    'columnas': []
                }

    except ConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        print(f"❌ Error de conexión: {e}")
        raise
    except QueryError as e:
        logger.error(f"Error en consulta: {e}")
        print(f"❌ Error en consulta: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"❌ Error inesperado: {e}")
        raise
    finally:
        db.cerrar_conexion()

    return tablas_encontradas, resultados

def generar_reporte_html(tablas_encontradas, resultados):
    """
    Genera un reporte HTML con los resultados de la verificación.

    Args:
        tablas_encontradas: Lista de nombres de tablas encontradas
        resultados: Diccionario con información de cada tabla verificada

    Returns:
        str: Contenido del reporte HTML
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Reporte de Verificación de Tablas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333366; }
            .summary { background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .error { color: red; }
            .missing { background-color: #ffcccc; }
            .exists { background-color: #ccffcc; }
        </style>
    </head>
    <body>
        <h1>Reporte de Verificación de Tablas</h1>
        <div class="summary">
            <h2>Resumen</h2>
            <p>Total de tablas encontradas: """ + str(len(tablas_encontradas)) + """</p>
            <p>Total de tablas verificadas: """ + str(len(resultados)) + """</p>
        </div>

        <h2>Tablas Encontradas</h2>
        <table>
            <tr>
                <th>Nombre de Tabla</th>
                <th>Número de Registros</th>
                <th>Número de Columnas</th>
                <th>Estado</th>
            </tr>
    """

    # Agregar filas para cada tabla verificada
    for tabla, info in resultados.items():
        estado_css = "exists" if info['existe'] else "missing"
        estado_texto = "Existente" if info['existe'] else "No encontrada"
        if 'error' in info:
            estado_css = "error"
            estado_texto = f"Error: {info['error']}"

        html += f"""
        <tr class="{estado_css}">
            <td>{tabla}</td>
            <td>{info['registros']}</td>
            <td>{len(info['columnas'])}</td>
            <td>{estado_texto}</td>
        </tr>
        """

    html += """
        </table>

        <h2>Detalles de Estructura</h2>
    """

    # Agregar detalles de columnas para cada tabla
    for tabla, info in resultados.items():
        if info['existe'] and info['columnas']:
            html += f"""
            <h3>Tabla: {tabla}</h3>
            <table>
                <tr>
                    <th>Columna</th>
                    <th>Tipo de Dato</th>
                    <th>Longitud Máxima</th>
                </tr>
            """

            for columna in info['columnas']:
                longitud = columna['longitud'] if columna['longitud'] is not None else 'N/A'
                html += f"""
                <tr>
                    <td>{columna['nombre']}</td>
                    <td>{columna['tipo']}</td>
                    <td>{longitud}</td>
                </tr>
                """

            html += """
            </table>
            """

    html += """
    </body>
    </html>
    """

    return html

def main():
    """Función principal del script."""
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Verificar tablas en la base de datos.')
    parser.add_argument('--tablas', nargs='*', help='Nombres de tablas específicas a verificar (opcional)')
    parser.add_argument('--reporte', type=str, help='Nombre del archivo para guardar reporte HTML (opcional)')
    args = parser.parse_args()

    try:
        # Ejecutar la verificación
        tablas_encontradas, resultados = verificar_tablas(args.tablas)

        # Generar reporte si se solicita
        if args.reporte:
            reporte_html = generar_reporte_html(tablas_encontradas, resultados)
            with open(args.reporte, 'w', encoding='utf-8') as f:
                f.write(reporte_html)
            print(f"\n💾 Reporte guardado en: {args.reporte}")

        print("\n✅ Verificación completada")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
