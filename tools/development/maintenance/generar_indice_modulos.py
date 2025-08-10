"""
Generador de índice para los informes de análisis de módulos.
Este script crea un archivo HTML que agrupa todos los informes de módulos
y proporciona un resumen ejecutivo del estado del proyecto.
"""

def generar_indice_informes(directorio_informes):
    """
    Genera un índice HTML con todos los informes de módulos.

    Args:
        directorio_informes (str): Directorio donde están los informes
    """

    # Buscar todos los archivos JSON de análisis
    patron = os.path.join(directorio_informes, "analisis_*.json")
    archivos_json = glob.glob(patron)

    # Leer datos de todos los módulos
    modulos_data = []
    for archivo_json in archivos_json:
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nombre_modulo = Path(archivo_json).stem.replace('analisis_', '')
                modulos_data.append({
                    'nombre': nombre_modulo,
                    'data': data,
                    'archivo_html': f"analisis_{nombre_modulo}.html"
                })
        except Exception as e:
            print(f"Error leyendo {archivo_json}: {e}")

    # Generar estadísticas generales
    stats = calcular_estadisticas_generales(modulos_data)

    # Generar HTML
    html = generar_html_indice(modulos_data, stats)

    # Guardar archivo
    ruta_indice = os.path.join(directorio_informes, "00_indice_analisis_modulos.html")
    with open(ruta_indice, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Índice generado: {ruta_indice}")
    return ruta_indice

def calcular_estadisticas_generales(modulos_data):
    """Calcula estadísticas generales del proyecto."""
    stats = {
        'total_modulos': len(modulos_data),
        'modulos_con_model': 0,
        'modulos_con_controller': 0,
        'modulos_con_view': 0,
        'modulos_con_tests': 0,
        'total_sugerencias': 0,
        'sugerencias_alta_prioridad': 0,
        'cobertura_promedio': 0,
        'archivos_totales': 0,
        'lineas_totales': 0
    }

    cobertura_total = 0
    for modulo in modulos_data:
        data = modulo['data']

        # Estadísticas de estructura
        estructura = data.get('estructura', {})
        archivos_core = estructura.get('archivos_core', {})

        if archivos_core.get('model.py', {}).get('existe', False):
            stats['modulos_con_model'] += 1
        if archivos_core.get('controller.py', {}).get('existe', False):
            stats['modulos_con_controller'] += 1
        if archivos_core.get('view.py', {}).get('existe', False):
            stats['modulos_con_view'] += 1

        # Contar archivos y líneas
        for archivo, info in archivos_core.items():
            if info.get('existe', False):
                stats['archivos_totales'] += 1
                stats['lineas_totales'] += info.get('lineas', 0)

        # Estadísticas de tests
        tests = data.get('tests', {})
        if tests.get('archivos_test'):
            stats['modulos_con_tests'] += 1

        cobertura = tests.get('cobertura_estimada', 0)
        cobertura_total += cobertura

        # Estadísticas de sugerencias
        sugerencias = data.get('sugerencias', [])
        stats['total_sugerencias'] += len(sugerencias)

        for sugerencia in sugerencias:
            if sugerencia.get('prioridad') == 'alta':
                stats['sugerencias_alta_prioridad'] += 1

    # Calcular promedios
    if stats['total_modulos'] > 0:
        stats['cobertura_promedio'] = cobertura_total / stats['total_modulos']

    return stats

def generar_html_indice(modulos_data, stats):
    """Genera el HTML del índice."""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice de Análisis de Módulos</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #444; }}
        .header {{ background-color: #f8f8f8; padding: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #4CAF50; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .stat-label {{ font-size: 0.9em; color: #666; }}
        .modules-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .module-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: white; }}
        .module-card h3 {{ margin-top: 0; color: #333; }}
        .module-status {{ display: flex; gap: 10px; margin: 10px 0; }}
        .status-item {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }}
        .status-ok {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .suggestions {{ margin: 10px 0; }}
        .suggestion {{ font-size: 0.9em; margin: 5px 0; padding: 5px; border-radius: 3px; }}
        .priority-alta {{ background: #ffebee; border-left: 3px solid #f44336; }}
        .priority-media {{ background: #fff3e0; border-left: 3px solid #ff9800; }}
        .priority-baja {{ background: #e8f5e8; border-left: 3px solid #4caf50; }}
        .module-link {{ display: inline-block; margin-top: 10px; background: #4CAF50; color: white;
                        padding: 8px 12px; text-decoration: none; border-radius: 4px; }}
        .module-link:hover {{ background: #388E3C; }}
        .summary {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Análisis de Módulos del Proyecto</h1>
        <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Resumen ejecutivo del estado de todos los módulos del sistema.</p>
    </div>

    <div class="summary">
        <h2>Resumen Ejecutivo</h2>
        <p>Este informe presenta el análisis automatizado de {stats['total_modulos']} módulos del sistema,
        evaluando estructura, funcionalidad, tests y calidad del código.</p>
    </div>

    <h2>Estadísticas Generales</h2>
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{stats['total_modulos']}</div>
            <div class="stat-label">Módulos Analizados</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['modulos_con_model']}</div>
            <div class="stat-label">Con Model.py</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['modulos_con_controller']}</div>
            <div class="stat-label">Con Controller.py</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['modulos_con_tests']}</div>
            <div class="stat-label">Con Tests</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['cobertura_promedio']:.1f}%</div>
            <div class="stat-label">Cobertura Promedio</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['total_sugerencias']}</div>
            <div class="stat-label">Total Sugerencias</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['sugerencias_alta_prioridad']}</div>
            <div class="stat-label">Alta Prioridad</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['lineas_totales']:,}</div>
            <div class="stat-label">Líneas de Código</div>
        </div>
    </div>

    <h2>Análisis por Módulo</h2>
    <div class="modules-grid">
"""

    # Agregar tarjeta para cada módulo
    for modulo in sorted(modulos_data, key=lambda x: x['nombre']):
        html += generar_tarjeta_modulo(modulo)

    html += """
    </div>

    <div style="margin-top: 40px; text-align: center; color: #666; font-size: 0.9em;">
        <p>Generado automáticamente por el Analizador de Módulos</p>
    </div>
</body>
</html>
"""

    return html

def generar_tarjeta_modulo(modulo):
    """Genera la tarjeta HTML para un módulo específico."""
    data = modulo['data']
    nombre = modulo['nombre']
    archivo_html = modulo['archivo_html']

    # Determinar estado general del módulo
    estructura = data.get('estructura', {})
    archivos_core = estructura.get('archivos_core', {})

    tiene_model = archivos_core.get('model.py', {}).get('existe', False)
    tiene_controller = archivos_core.get('controller.py', {}).get('existe', False)

    tests = data.get('tests', {})
    cobertura = tests.get('cobertura_estimada', 0)

    sugerencias = data.get('sugerencias', [])
    sugerencias_alta = [s for s in sugerencias if s.get('prioridad') == 'alta']

    # HTML de la tarjeta
    html = f"""
        <div class="module-card">
            <h3>{nombre.title()}</h3>

            <div class="module-status">
"""

    # Estados de archivos
    if tiene_model:
        html += '<span class="status-item status-ok">[OK] Model</span>'
    else:
        html += '<span class="status-item status-error">✗ Model</span>'

    if tiene_controller:
        html += '<span class="status-item status-ok">[OK] Controller</span>'
    else:
        html += '<span class="status-item status-error">✗ Controller</span>'

    # Estado de tests
    if cobertura >= 70:
        html += f'<span class="status-item status-ok">Tests {cobertura}%</span>'
    elif cobertura >= 30:
        html += f'<span class="status-item status-warning">Tests {cobertura}%</span>'
    else:
        html += f'<span class="status-item status-error">Tests {cobertura}%</span>'

    html += """
            </div>

            <div class="suggestions">
"""

    # Mostrar sugerencias principales
    if sugerencias_alta:
        html += f"<strong>Sugerencias críticas ({len(sugerencias_alta)}):</strong><br>"
        for sugerencia in sugerencias_alta[:3]:  # Mostrar máximo 3
            html += f'<div class="suggestion priority-alta">{sugerencia.get("descripcion", "")}</div>'

        if len(sugerencias_alta) > 3:
            html += f"<div class='suggestion'>... y {len(sugerencias_alta) - 3} más</div>"
    elif sugerencias:
        html += f"<strong>Sugerencias ({len(sugerencias)}):</strong><br>"
        for sugerencia in sugerencias[:2]:  # Mostrar máximo 2
            prioridad = sugerencia.get('prioridad', 'baja')
            html += f'<div class="suggestion priority-{prioridad}">{sugerencia.get("descripcion", "")}</div>'
    else:
        html += '<div class="suggestion status-ok">[OK] Sin sugerencias críticas</div>'

    html += f"""
            </div>

            <a href="{archivo_html}" class="module-link" target="_blank">Ver Análisis Detallado</a>
        </div>
"""

    return html

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Generador de índice de análisis de módulos')
    parser.add_argument('--dir', '-d', default='informes_modulos',
                        help='Directorio donde están los informes')

    args = parser.parse_args()

import argparse
import glob
import json
import os
from datetime import datetime
from pathlib import Path

    if not os.path.exists(args.dir):
        print(f"Directorio {args.dir} no existe. Ejecuta primero el analizador de módulos.")
        return

    generar_indice_informes(args.dir)

if __name__ == "__main__":
    main()
