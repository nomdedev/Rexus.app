"""
Escáner completo de vulnerabilidades y problemas de seguridad para la aplicación.
Este script ejecuta múltiples análisis:
1. Escaneo de vulnerabilidades SQL en el código
2. Diagnóstico de seguridad de la BD
3. Verificación de archivos sensibles (claves, configuraciones)
4. Análisis de dependencias con problemas de seguridad
"""

# Agregar el directorio raíz al path de Python
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importar módulos del proyecto
try:
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

# ------------------ Funciones de análisis ------------------

def escanear_vulnerabilidades_sql(directorio_base, directorio_salida):
    """
    Ejecuta el analizador de seguridad SQL en el código.
from pathlib import Path
from scripts.verificacion.analizar_seguridad_sql_codigo import AnalizadorCodigoSQL
import argparse
import datetime
import json
import os
import shutil
import sys

import subprocess

    Args:
        directorio_base (str): Directorio raíz a analizar
        directorio_salida (str): Directorio donde guardar el informe

    Returns:
        str: Ruta al informe generado
    """
    print("\n[*] Iniciando escaneo de vulnerabilidades SQL en código fuente...")

    # Crear analizador
    analizador = AnalizadorCodigoSQL()

    # Directorios a excluir
    exclusiones = ['venv', '__pycache__', '.git', 'node_modules', '.pytest_cache']

    # Analizar directorio
    problemas = analizador.analizar_directorio(
        directorio_base,
        extensiones=['.py'],
        exclusiones=exclusiones
    )

    # Guardar informe
    ruta_informe = os.path.join(directorio_salida, 'informe_seguridad_sql.html')
    ruta_guardada = analizador.guardar_reporte(ruta_informe, 'html')

    # También guardar versión JSON para procesamiento automatizado
    analizador.guardar_reporte(os.path.join(directorio_salida, 'informe_seguridad_sql.json'), 'json')

    # Mostrar resumen
    print(f"  ✅ Escaneo SQL completado:")
    print(f"    - Archivos analizados: {analizador.archivos_analizados}")
    print(f"    - Líneas revisadas: {analizador.lineas_analizadas}")
    print(f"    - Vulnerabilidades encontradas: {len(problemas)}")
    print(f"    - Informe guardado en: {ruta_guardada}")

    return ruta_guardada

def verificar_archivos_sensibles(directorio_base, directorio_salida):
    """
    Busca archivos sensibles como configuraciones, claves y credenciales.

    Args:
        directorio_base (str): Directorio raíz a analizar
        directorio_salida (str): Directorio donde guardar el informe

    Returns:
        str: Ruta al informe generado
    """
    print("\n[*] Verificando archivos sensibles y posibles fugas de información...")

    # Patrones para buscar archivos sensibles
    patrones_sensibles = [
        '*.key',
        '*.pem',
        '*.env',
        '*password*',
        '*secret*',
        'config*.py',
        '*credentials*',
        '.env*',
        'config*.json'
    ]

    # Patrones para buscar contenido sensible
    patrones_contenido = [
        'password',
        'secret',
        'api_key',
        'apikey',
        'token',
        'passwd',
        'contraseña',
        'clave',
        'DATABASE_URL'
    ]

    resultados = {
        'archivos_sensibles': [],
        'contenido_sospechoso': [],
        'estadisticas': {
            'total_archivos_revisados': 0,
            'archivos_sensibles': 0,
            'archivos_con_contenido_sospechoso': 0
        }
    }

    # Rutas a excluir
    exclusiones = [
        '.git',
        '__pycache__',
        'venv',
        'node_modules',
        '.pytest_cache'
    ]

    # Función para verificar si una ruta debe ser excluida
    def debe_excluir(ruta):
        for exclusion in exclusiones:
            if exclusion in ruta:
                return True
        return False

    # Recorrer el sistema de archivos
    for root, dirs, files in os.walk(directorio_base):
        # No procesar directorios excluidos
        dirs[:] = [d for d in dirs if not debe_excluir(os.path.join(root, d))]

        for file in files:
            resultados['estadisticas']['total_archivos_revisados'] += 1
            ruta_completa = os.path.join(root, file)

            # Verificar si el nombre de archivo coincide con patrones sensibles
            if any(Path(ruta_completa).match(patron) for patron in patrones_sensibles):
                resultados['estadisticas']['archivos_sensibles'] += 1
                resultados['archivos_sensibles'].append({
                    'ruta': os.path.relpath(ruta_completa, directorio_base),
                    'tipo': 'Archivo potencialmente sensible por nombre',
                    'fecha_modificacion': datetime.datetime.fromtimestamp(
                        os.path.getmtime(ruta_completa)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                })

            # Verificar contenido solo en tipos de archivo de texto
            if file.endswith(('.py', '.txt', '.json', '.yaml', '.yml', '.env', '.ini', '.cfg', '.conf')):
                try:
                    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()

                        # Buscar patrones en contenido
                        for patron in patrones_contenido:
                            if patron in contenido.lower():
                                resultados['estadisticas']['archivos_con_contenido_sospechoso'] += 1
                                resultados['contenido_sospechoso'].append({
                                    'ruta': os.path.relpath(ruta_completa, directorio_base),
                                    'patron': patron,
                                    'tipo': 'Posible información sensible en contenido'
                                })
                                # Solo registrar una vez por archivo
                                break
                except Exception as e:
                    print(f"  Error al leer {ruta_completa}: {e}")

    # Guardar informe JSON
    ruta_json = os.path.join(directorio_salida, 'archivos_sensibles.json')
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    # Crear informe HTML
    ruta_html = os.path.join(directorio_salida, 'archivos_sensibles.html')

    # Generar HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Archivos Sensibles</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #444; }}
        .header {{ background-color: #f8f8f8; padding: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .summary {{ background-color: #f1f1f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; padding: 15px; }}
        .warning {{ color: #f57c00; }}
        .danger {{ color: #d32f2f; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #777; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Informe de Archivos Sensibles</h1>
        <p>Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Resumen</h2>
        <p>Total archivos revisados: {resultados['estadisticas']['total_archivos_revisados']}</p>
        <p>Archivos sensibles detectados: {resultados['estadisticas']['archivos_sensibles']}</p>
        <p>Archivos con contenido sospechoso: {resultados['estadisticas']['archivos_con_contenido_sospechoso']}</p>
    </div>
"""

    # Sección de archivos sensibles
    html += """
    <div class="section">
        <h2 class="warning">Archivos Potencialmente Sensibles</h2>
"""

    if resultados['archivos_sensibles']:
        html += """
        <table>
            <thead>
                <tr>
                    <th>Archivo</th>
                    <th>Tipo</th>
                    <th>Última Modificación</th>
                </tr>
            </thead>
            <tbody>
"""

        for archivo in resultados['archivos_sensibles']:
            html += f"""
                <tr>
                    <td>{archivo['ruta']}</td>
                    <td>{archivo['tipo']}</td>
                    <td>{archivo['fecha_modificacion']}</td>
                </tr>"""

        html += """
            </tbody>
        </table>
"""
    else:
        html += """
        <p>No se encontraron archivos con nombres sensibles.</p>
"""

    html += """
    </div>
"""

    # Sección de contenido sospechoso
    html += """
    <div class="section">
        <h2 class="danger">Contenido Potencialmente Sensible</h2>
"""

    if resultados['contenido_sospechoso']:
        html += """
        <table>
            <thead>
                <tr>
                    <th>Archivo</th>
                    <th>Patrón Detectado</th>
                    <th>Tipo</th>
                </tr>
            </thead>
            <tbody>
"""

        for contenido in resultados['contenido_sospechoso']:
            html += f"""
                <tr>
                    <td>{contenido['ruta']}</td>
                    <td>{contenido['patron']}</td>
                    <td>{contenido['tipo']}</td>
                </tr>"""

        html += """
            </tbody>
        </table>
"""
    else:
        html += """
        <p>No se encontró contenido sospechoso en los archivos.</p>
"""

    html += """
    </div>

    <div class="section">
        <h2>Recomendaciones</h2>
        <ul>
            <li>Revisar y asegurar que archivos con información sensible como credenciales estén excluidos del control de versiones.</li>
            <li>Considerar el uso de variables de entorno o almacenes seguros para credenciales.</li>
            <li>Verificar que los archivos de configuración no contengan claves en texto plano.</li>
            <li>Para configuraciones sensibles, utilizar archivos .env excluidos del repositorio.</li>
        </ul>
    </div>

    <div class="footer">
        <p>Generado por Scanner de Seguridad</p>
    </div>
</body>
</html>
"""

    # Guardar HTML
    with open(ruta_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✅ Verificación de archivos sensibles completada:")
    print(f"    - Total archivos revisados: {resultados['estadisticas']['total_archivos_revisados']}")
    print(f"    - Archivos con nombres sensibles: {resultados['estadisticas']['archivos_sensibles']}")
    print(f"    - Archivos con contenido sospechoso: {resultados['estadisticas']['archivos_con_contenido_sospechoso']}")
    print(f"    - Informe guardado en: {ruta_html}")

    return ruta_html

def verificar_dependencias_seguridad(directorio_base, directorio_salida):
    """
    Verifica si hay dependencias con problemas de seguridad conocidos.

    Args:
        directorio_base (str): Directorio raíz a analizar
        directorio_salida (str): Directorio donde guardar el informe

    Returns:
        str: Ruta al informe generado
    """
    print("\n[*] Analizando dependencias en busca de vulnerabilidades conocidas...")

    requirements_paths = []

    # Buscar todos los archivos requirements.txt
    for root, dirs, files in os.walk(directorio_base):
        if 'requirements.txt' in files:
            requirements_paths.append(os.path.join(root, 'requirements.txt'))

    if not requirements_paths:
        print("  ⚠️ No se encontraron archivos requirements.txt")
        return None

    # Crear archivo para informe
    ruta_informe = os.path.join(directorio_salida, 'informe_dependencias.txt')

    # Intentar usar safety para analizar dependencias si está disponible
    try:
        # Primero, intentar analizarlos con safety
        for requirements_path in requirements_paths:
            print(f"  📝 Analizando {requirements_path}")

            # Crear un requirements.txt temporal con las dependencias
            temp_requirements = os.path.join(directorio_salida, 'temp_requirements.txt')
            shutil.copy(requirements_path, temp_requirements)

            try:
                # Intentar ejecutar safety check (asume que safety está instalado)
                result = subprocess.run(
                    ['safety', 'check', '-r', temp_requirements, '--output', 'text'],
                    capture_output=True,
                    text=True
                )

                # Guardar la salida en el informe
                with open(ruta_informe, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n=== Análisis de seguridad para {requirements_path} ===\n\n")
                    f.write(result.stdout)
                    if result.stderr:
                        f.write(f"\nErrores:\n{result.stderr}")
            except Exception as e:
                print(f"  ❌ Error al ejecutar safety: {e}")
                with open(ruta_informe, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n=== Análisis de seguridad para {requirements_path} ===\n\n")
                    f.write(f"Error al ejecutar safety: {e}\n")
                    f.write("Recomendación: Instalar safety con 'pip install safety' para análisis de seguridad.\n")
            finally:
                # Eliminar el archivo temporal
                if os.path.exists(temp_requirements):
                    os.remove(temp_requirements)
    except Exception as e:
        print(f"  ⚠️ No se pudo analizar dependencias con safety: {e}")
        # Simplemente listar las dependencias
        with open(ruta_informe, 'w', encoding='utf-8') as f:
            f.write("# ANÁLISIS DE DEPENDENCIAS\n\n")
            f.write("No se pudo usar 'safety' para verificar vulnerabilidades.\n")
            f.write("Se recomienda instalar safety con 'pip install safety'.\n\n")

            f.write("## Dependencias encontradas:\n\n")
            for requirements_path in requirements_paths:
                f.write(f"\n### Archivo: {requirements_path}\n\n")
                try:
                    with open(requirements_path, 'r', encoding='utf-8') as req_file:
                        f.write(req_file.read())
                except Exception as e:
                    f.write(f"Error al leer {requirements_path}: {e}\n")

    print(f"  ✅ Análisis de dependencias completado")
    print(f"    - Informe guardado en: {ruta_informe}")

    return ruta_informe

def generar_indice(reportes, directorio_salida):
    """
    Genera un archivo HTML con los enlaces a todos los informes.

    Args:
        reportes (dict): Diccionario con tipo de reporte y ruta
        directorio_salida (str): Directorio donde guardar el índice

    Returns:
        str: Ruta al archivo de índice
    """
    ruta_indice = os.path.join(directorio_salida, 'index.html')

    # Crear HTML del índice
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice de Informes de Seguridad</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #444; }}
        .header {{ background-color: #f8f8f8; padding: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .report-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .report-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; transition: all 0.3s ease; }}
        .report-card:hover {{ box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .report-card h3 {{ margin-top: 0; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
        .report-card p {{ color: #666; }}
        .report-card a {{ display: inline-block; margin-top: 10px; background: #4CAF50; color: white; padding: 8px 12px;
                           text-decoration: none; border-radius: 4px; }}
        .report-card a:hover {{ background: #388E3C; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #777; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Informes de Seguridad</h1>
        <p>Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Este documento contiene enlaces a todos los informes de seguridad generados.</p>
    </div>

    <h2>Informes Disponibles</h2>
    <div class="report-list">
"""

    # Añadir tarjetas para cada informe
    for titulo, info in reportes.items():
        if not info['ruta']:
            continue

        # Obtener ruta relativa para el enlace
        ruta_rel = os.path.relpath(info['ruta'], directorio_salida)

        html += f"""
        <div class="report-card">
            <h3>{titulo}</h3>
            <p>{info['descripcion']}</p>
            <a href="{ruta_rel}" target="_blank">Ver Informe</a>
        </div>
"""

    html += """
    </div>

    <div class="footer">
        <p>Generado por el Escáner de Vulnerabilidades</p>
    </div>
</body>
</html>
"""

    # Guardar archivo
    with open(ruta_indice, 'w', encoding='utf-8') as f:
        f.write(html)

    return ruta_indice

def main():
    """Función principal para ejecutar el escáner de vulnerabilidades."""
    parser = argparse.ArgumentParser(description='Escáner completo de vulnerabilidades')
    parser.add_argument('--dir', '-d', default=str(ROOT_DIR), help='Directorio a analizar')
    parser.add_argument('--output', '-o', default=os.path.join(str(ROOT_DIR), 'informes_seguridad'),
                        help='Directorio donde guardar los informes')
    parser.add_argument('--skip-sql', action='store_true', help='Omitir análisis de código SQL')
    parser.add_argument('--skip-bd', action='store_true', help='Omitir diagnóstico de BD')
    parser.add_argument('--skip-files', action='store_true', help='Omitir verificación de archivos sensibles')
    parser.add_argument('--skip-deps', action='store_true', help='Omitir verificación de dependencias')

    args = parser.parse_args()

    # Banner inicial
    print("\n" + "=" * 80)
    print(" "*25 + "ESCÁNER DE VULNERABILIDADES")
    print(" "*32 + "Versión 1.0.0")
    print(" "*24 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 80 + "\n")

    # Crear directorio de salida si no existe
    directorio_salida = args.output
    os.makedirs(directorio_salida, exist_ok=True)

    print(f"[*] Iniciando escaneo completo en {args.dir}")
    print(f"[*] Los informes se guardarán en {directorio_salida}")

    # Recolectar todos los informes generados
    informes = {
        "Vulnerabilidades SQL": {
            "ruta": None,
            "descripcion": "Análisis de vulnerabilidades SQL en el código fuente"
        },
        "Diagnóstico de BD": {
            "ruta": None,
            "descripcion": "Diagnóstico de seguridad de la base de datos"
        },
        "Archivos Sensibles": {
            "ruta": None,
            "descripcion": "Detección de archivos con información potencialmente sensible"
        },
        "Análisis de Dependencias": {
            "ruta": None,
            "descripcion": "Verificación de dependencias con vulnerabilidades conocidas"
        }
    }

    # 1. Escanear vulnerabilidades SQL en código
    if not args.skip_sql:
        try:
            ruta_sql = escanear_vulnerabilidades_sql(args.dir, directorio_salida)
            informes["Vulnerabilidades SQL"]["ruta"] = ruta_sql
        except Exception as e:
            print(f"  ❌ Error durante el escaneo SQL: {e}")
    else:
        print("\n[*] Escaneo de vulnerabilidades SQL omitido por el usuario")

    # 2. Verificar archivos sensibles
    if not args.skip_files:
        try:
            ruta_archivos = verificar_archivos_sensibles(args.dir, directorio_salida)
            informes["Archivos Sensibles"]["ruta"] = ruta_archivos
        except Exception as e:
            print(f"  ❌ Error durante la verificación de archivos sensibles: {e}")
    else:
        print("\n[*] Verificación de archivos sensibles omitida por el usuario")

    # 3. Verificar dependencias
    if not args.skip_deps:
        try:
            ruta_deps = verificar_dependencias_seguridad(args.dir, directorio_salida)
            informes["Análisis de Dependencias"]["ruta"] = ruta_deps
        except Exception as e:
            print(f"  ❌ Error durante la verificación de dependencias: {e}")
    else:
        print("\n[*] Verificación de dependencias omitida por el usuario")

    # 4. Generar índice de informes
    try:
        ruta_indice = generar_indice(informes, directorio_salida)
        print(f"\n[*] Índice de informes generado en {ruta_indice}")
    except Exception as e:
        print(f"  ❌ Error al generar índice de informes: {e}")

    print("\n[*] Escaneo de vulnerabilidades completado")
    print("=" * 80)


if __name__ == "__main__":
    main()
