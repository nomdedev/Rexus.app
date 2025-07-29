"""
Herramienta para el análisis estático de código en busca de consultas SQL inseguras.
Este módulo permite escanear archivos Python en busca de consultas SQL potencialmente
vulnerables a inyección SQL y otros problemas de seguridad.
"""

# Asegurar que podemos importar desde el directorio raíz
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Patrones adicionales para detectar consultas SQL en código Python
PATRONES_DETECCION_SQL = [
    # Consultas directas en ejecutar_query
    r'ejecutar_query\s*\(\s*["\'](.+?)["\']\s*(?:,|\))',
    # Consultas en variables
    r'(?:query|sql|consulta)\s*=\s*["\'](.+?)["\']',
    # Construcciones con f-strings (peligrosas)
    r'(?:query|sql|consulta)\s*=\s*f["\'](.+?)["\']',
import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

from utils.sanitizador_sql import detectar_vulnerabilidades_consulta

    # Construcciones con format (peligrosas)
    r'(?:query|sql|consulta)\s*=\s*["\'](.+?)["\']\s*\.format\(',
    # Construcciones con concatenación de strings (peligrosas)
    r'(?:query|sql|consulta)\s*=\s*["\'](.*?)["\']\s*\+\s*',
    # Construcción de SQL con varios elementos concatenados
    r'(?:query|sql|consulta)\s*\+?=\s*["\'](.*)["\']'
]

# Compilar patrones
PATRONES_SQL_COMPILADOS = [re.compile(patron, re.IGNORECASE | re.DOTALL) for patron in PATRONES_DETECCION_SQL]

class AnalizadorCodigoSQL:
    """
    Clase para analizar código fuente en busca de consultas SQL inseguras.
    """

    def __init__(self):
        """
        Inicializa el analizador de código.
        """
        self.archivos_analizados = 0
        self.lineas_analizadas = 0
        self.problemas_encontrados = []

    def analizar_archivo(self, ruta_archivo):
        """
        Analiza un archivo Python en busca de consultas SQL inseguras.

        Args:
            ruta_archivo (str): Ruta al archivo Python a analizar

        Returns:
            list: Lista de problemas encontrados en el archivo
        """
        problemas = []

        try:
            # Leer el contenido del archivo
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
                lineas = codigo.split('\n')
                self.lineas_analizadas += len(lineas)

            # Buscar fragmentos que parezcan consultas SQL
            for patron_idx, patron in enumerate(PATRONES_SQL_COMPILADOS):
                for match in patron.finditer(codigo):
                    # Obtener la consulta SQL detectada
                    consulta = match.group(1) if match.groups() else match.group(0)

                    # Obtener número de línea aproximado
                    linea_numero = codigo[:match.start()].count('\n') + 1

                    # Extraer la línea completa donde se encontró
                    linea_completa = lineas[linea_numero - 1] if linea_numero <= len(lineas) else ""

                    # Detectar vulnerabilidades en la consulta SQL
                    vulnerabilidades = detectar_vulnerabilidades_consulta(consulta)

                    if vulnerabilidades:
                        for vuln in vulnerabilidades:
                            problemas.append({
                                'archivo': ruta_archivo,
                                'linea': linea_numero,
                                'fragmento': linea_completa.strip(),
                                'consulta': consulta,
                                'tipo': vuln['tipo'],
                                'descripcion': vuln['descripcion'],
                                'detalles': vuln
                            })

                    # Verificar si usa parámetros o concatenación directa (riegos)
                    if 'f"' in linea_completa or "f'" in linea_completa:
                        problemas.append({
                            'archivo': ruta_archivo,
                            'linea': linea_numero,
                            'fragmento': linea_completa.strip(),
                            'consulta': consulta,
                            'tipo': 'construccion_insegura',
                            'descripcion': 'Uso de f-string para construir SQL. Riesgo de inyección.',
                            'detalles': {'recomendacion': 'Use consultas parametrizadas con marcadores ?'}
                        })
                    elif '+' in linea_completa and ('query' in linea_completa.lower() or 'sql' in linea_completa.lower()):
                        problemas.append({
                            'archivo': ruta_archivo,
                            'linea': linea_numero,
                            'fragmento': linea_completa.strip(),
                            'consulta': consulta,
                            'tipo': 'construccion_insegura',
                            'descripcion': 'Concatenación de strings en SQL. Riesgo de inyección.',
                            'detalles': {'recomendacion': 'Use consultas parametrizadas con marcadores ?'}
                        })
                    elif '.format(' in linea_completa:
                        problemas.append({
                            'archivo': ruta_archivo,
                            'linea': linea_numero,
                            'fragmento': linea_completa.strip(),
                            'consulta': consulta,
                            'tipo': 'construccion_insegura',
                            'descripcion': 'Uso de format() para construir SQL. Riesgo de inyección.',
                            'detalles': {'recomendacion': 'Use consultas parametrizadas con marcadores ?'}
                        })

            # Añadir estadísticas
            self.archivos_analizados += 1

            return problemas

        except Exception as e:
            print(f"Error al analizar archivo {ruta_archivo}: {e}")
            return []

    def analizar_directorio(self, directorio, extensiones=['.py'], exclusiones=[]):
        """
        Analiza recursivamente los archivos en un directorio.

        Args:
            directorio (str): Directorio a analizar
            extensiones (list): Lista de extensiones de archivo a incluir
            exclusiones (list): Lista de patrones de ruta a excluir

        Returns:
            list: Lista de todos los problemas encontrados
        """
        problemas_totales = []

        for root, dirs, files in os.walk(directorio):
            # Omitir directorios excluidos
            dirs[:] = [d for d in dirs if not any(e in os.path.join(root, d) for e in exclusiones)]

            for file in files:
                if any(file.endswith(ext) for ext in extensiones):
                    ruta_completa = os.path.join(root, file)

                    # Omitir archivos excluidos
                    if any(e in ruta_completa for e in exclusiones):
                        continue

                    # Analizar archivo
                    problemas = self.analizar_archivo(ruta_completa)
                    if problemas:
                        problemas_totales.extend(problemas)

        self.problemas_encontrados = problemas_totales
        return problemas_totales

    def generar_reporte_html(self, problemas=None):
        """
        Genera un reporte HTML con los problemas de seguridad SQL encontrados.

        Args:
            problemas (list, optional): Lista de problemas a incluir en el reporte.
                                       Si es None, usa los problemas encontrados.

        Returns:
            str: Contenido HTML del reporte
        """
        if problemas is None:
            problemas = self.problemas_encontrados

        # Agrupar problemas por archivo
        problemas_por_archivo = {}
        for problema in problemas:
            archivo = problema['archivo']
            if archivo not in problemas_por_archivo:
                problemas_por_archivo[archivo] = []
            problemas_por_archivo[archivo].append(problema)

        # Crear HTML
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Seguridad SQL</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #444; }}
        .header {{ background-color: #f8f8f8; padding: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .summary {{ background-color: #f1f1f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .file-section {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }}
        .file-header {{ background-color: #eee; padding: 10px; border-bottom: 1px solid #ddd; }}
        .problem {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .problem:last-child {{ border-bottom: none; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .info {{ color: #0288d1; }}
        .code {{ font-family: monospace; background-color: #f7f7f7; padding: 8px; border-radius: 4px; overflow-x: auto; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #777; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Informe de Seguridad SQL</h1>
        <p>Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Resumen</h2>
        <p>Archivos analizados: {self.archivos_analizados}</p>
        <p>Líneas de código revisadas: {self.lineas_analizadas}</p>
        <p>Problemas encontrados: {len(problemas)}</p>
    </div>
"""

        if not problemas:
            html += """
    <div>
        <h2>No se encontraron problemas</h2>
        <p>¡Enhorabuena! No se han detectado problemas de seguridad SQL en el código analizado.</p>
    </div>
"""
        else:
            # Mostrar problemas por archivo
            for archivo, lista_problemas in problemas_por_archivo.items():
                # Obtener ruta relativa para mejor visualización
                if str(ROOT_DIR) in archivo:
                    archivo_rel = os.path.relpath(archivo, str(ROOT_DIR))
                else:
                    archivo_rel = archivo

                html += f"""
    <div class="file-section">
        <div class="file-header">
            <h2>{archivo_rel}</h2>
            <p>Problemas encontrados: {len(lista_problemas)}</p>
        </div>
"""

                for i, problema in enumerate(lista_problemas, 1):
                    tipo_class = "error" if problema['tipo'] == 'patron_peligroso' else "warning"

                    html += f"""
        <div class="problem">
            <h3 class="{tipo_class}">Problema #{i}: {problema['tipo']}</h3>
            <p><strong>Línea:</strong> {problema['linea']}</p>
            <p><strong>Descripción:</strong> {problema['descripcion']}</p>
            <div class="code">{problema['fragmento']}</div>
"""

                    if 'detalles' in problema and 'recomendacion' in problema['detalles']:
                        html += f"""
            <p><strong>Recomendación:</strong> {problema['detalles']['recomendacion']}</p>
"""

                    html += """
        </div>
"""

                html += """
    </div>
"""

        html += """
    <div class="footer">
        <p>Generado por Analizador de Seguridad SQL</p>
    </div>
</body>
</html>
"""

        return html

    def guardar_reporte(self, ruta_archivo, formato='html'):
        """
        Guarda un reporte con los resultados del análisis.

        Args:
            ruta_archivo (str): Ruta donde guardar el reporte
            formato (str): Formato del reporte ('html' o 'json')

        Returns:
            str: Ruta del archivo guardado
        """
        # Asegurar que el directorio existe
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

        if formato.lower() == 'html':
            contenido = self.generar_reporte_html()

            # Asegurar extensión correcta
            if not ruta_archivo.lower().endswith('.html'):
                ruta_archivo += '.html'

            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)

        elif formato.lower() == 'json':
            # Asegurar extensión correcta
            if not ruta_archivo.lower().endswith('.json'):
                ruta_archivo += '.json'

            informe = {
                'fecha': datetime.datetime.now().isoformat(),
                'estadisticas': {
                    'archivos_analizados': self.archivos_analizados,
                    'lineas_analizadas': self.lineas_analizadas,
                    'total_problemas': len(self.problemas_encontrados)
                },
                'problemas': self.problemas_encontrados
            }

            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(informe, f, indent=2, ensure_ascii=False)

        return ruta_archivo


def main():
    """Función principal para ejecutar el análisis desde línea de comandos."""
    parser = argparse.ArgumentParser(description='Analizador de seguridad SQL en código Python')
    parser.add_argument('--dir', '-d', default='.', help='Directorio a analizar (por defecto: directorio actual)')
    parser.add_argument('--output', '-o', default='informe_seguridad_sql.html', help='Ruta del archivo de salida')
    parser.add_argument('--format', '-f', choices=['html', 'json'], default='html', help='Formato del informe (html o json)')
    parser.add_argument('--exclude', '-e', action='append', default=['venv', '__pycache__', '.git'], help='Patrones a excluir')

    args = parser.parse_args()

    print(f"Analizando código en '{args.dir}'...")

    # Crear analizador
    analizador = AnalizadorCodigoSQL()

    # Analizar directorio
    problemas = analizador.analizar_directorio(
        args.dir,
        extensiones=['.py'],
        exclusiones=args.exclude
    )

    # Guardar informe
    ruta_informe = analizador.guardar_reporte(args.output, args.format)

    # Mostrar resumen
    print(f"\nAnálisis completado:")
    print(f"- Archivos analizados: {analizador.archivos_analizados}")
    print(f"- Líneas de código revisadas: {analizador.lineas_analizadas}")
    print(f"- Problemas encontrados: {len(problemas)}")
    print(f"\nInforme guardado en: {ruta_informe}")


if __name__ == "__main__":
    main()
