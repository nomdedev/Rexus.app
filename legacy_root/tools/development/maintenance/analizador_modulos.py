"""
Analizador de estructura de módulos para verificación de calidad y funcionamiento.
Este script examina cada módulo del proyecto para verificar:
1. Estructura de archivos
2. Patrones de carga de datos
3. Implementación de feedback visual
4. Cobertura de tests
5. Identificación de edge cases potenciales
"""

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

class AnalizadorModulo:
    """Clase para analizar un módulo específico del proyecto."""

    def __init__(self, ruta_modulo):
        """
        Inicializa el analizador para un módulo específico.

        Args:
            ruta_modulo (str): Ruta al directorio del módulo
        """
        self.ruta_modulo = Path(ruta_modulo)
        self.nombre_modulo = self.ruta_modulo.name
        self.archivos_encontrados = {}
        self.analisis = {
            'estructura': {},
            'carga_datos': {},
            'feedback_visual': {},
            'tests': {},
            'edge_cases': [],
            'sugerencias': []
        }

    def analizar_estructura(self):
        """Analiza la estructura de archivos del módulo."""
        archivos_esperados = ['model.py', 'controller.py', 'view.py', '__init__.py']
        archivos_opcionales = ['forms.py', 'utils.py', 'constants.py', 'exceptions.py']

        estructura = {
            'archivos_core': {},
            'archivos_opcionales': {},
            'otros_archivos': [],
            'directorios': []
        }

        # Verificar archivos existentes
        for archivo in os.listdir(self.ruta_modulo):
            ruta_archivo = self.ruta_modulo / archivo

            if os.path.isfile(ruta_archivo):
                if archivo in archivos_esperados:
                    estructura['archivos_core'][archivo] = {
                        'existe': True,
                        'tamaño': os.path.getsize(ruta_archivo),
                        'lineas': self._contar_lineas(ruta_archivo)
                    }
                    self.archivos_encontrados[archivo] = ruta_archivo
                elif archivo in archivos_opcionales:
                    estructura['archivos_opcionales'][archivo] = {
                        'existe': True,
                        'tamaño': os.path.getsize(ruta_archivo),
                        'lineas': self._contar_lineas(ruta_archivo)
                    }
                    self.archivos_encontrados[archivo] = ruta_archivo
                else:
                    estructura['otros_archivos'].append(archivo)
            elif os.path.isdir(ruta_archivo):
                estructura['directorios'].append(archivo)

        # Verificar archivos faltantes
        for archivo in archivos_esperados:
            if archivo not in estructura['archivos_core']:
                estructura['archivos_core'][archivo] = {'existe': False}

        self.analisis['estructura'] = estructura
        return estructura

    def analizar_carga_datos(self):
        """Analiza los patrones de carga de datos en el módulo."""
        carga_datos = {
            'model_methods': [],
            'database_connections': [],
            'query_patterns': [],
            'data_validation': [],
            'error_handling': []
        }

        # Analizar model.py si existe
        if 'model.py' in self.archivos_encontrados:
            model_analysis = self._analizar_archivo_python(self.archivos_encontrados['model.py'])
            carga_datos['model_methods'] = self._extraer_metodos_modelo(model_analysis)
            carga_datos['database_connections'] = self._buscar_conexiones_bd(model_analysis)
            carga_datos['query_patterns'] = self._analizar_patrones_consulta(model_analysis)

        # Analizar controller.py si existe
        if 'controller.py' in self.archivos_encontrados:
            controller_analysis = self._analizar_archivo_python(self.archivos_encontrados['controller.py'])
            carga_datos['data_validation'] = self._buscar_validaciones(controller_analysis)
            carga_datos['error_handling'] = self._buscar_manejo_errores(controller_analysis)

        self.analisis['carga_datos'] = carga_datos
        return carga_datos

    def analizar_feedback_visual(self):
        """Analiza la implementación de feedback visual al usuario."""
        feedback = {
            'loading_indicators': [],
            'error_messages': [],
            'success_messages': [],
            'progress_bars': [],
            'ui_updates': []
        }

        # Buscar patrones de feedback en todos los archivos Python
        for archivo, ruta in self.archivos_encontrados.items():
            if archivo.endswith('.py'):
                contenido = self._leer_archivo(ruta)

                # Buscar indicadores de carga
                feedback['loading_indicators'].extend(
                    self._buscar_patrones(contenido, [
                        r'loading', r'spinner', r'progress', r'wait',
                        r'setCursor.*Qt\.WaitCursor', r'QProgressBar'
                    ])
                )

                # Buscar mensajes de error
                feedback['error_messages'].extend(
                    self._buscar_patrones(contenido, [
                        r'QMessageBox.*warning', r'QMessageBox.*critical',
                        r'mostrar_error', r'error_message', r'show_error'
                    ])
                )

                # Buscar mensajes de éxito
                feedback['success_messages'].extend(
                    self._buscar_patrones(contenido, [
                        r'QMessageBox.*information', r'mostrar_exito',
                        r'success_message', r'show_success'
                    ])
                )

                # Buscar actualizaciones de UI
                feedback['ui_updates'].extend(
                    self._buscar_patrones(contenido, [
                        r'refresh', r'update', r'reload', r'actualizar',
                        r'cargar_tabla', r'populate'
                    ])
                )

        self.analisis['feedback_visual'] = feedback
        return feedback

    def analizar_tests(self):
        """Analiza los tests existentes para el módulo."""
        tests = {
            'archivos_test': [],
            'cobertura_estimada': 0,
            'tipos_test': [],
            'edge_cases_cubiertos': [],
            'edge_cases_faltantes': []
        }

        # Buscar archivos de test para este módulo
        tests_dir = ROOT_DIR / 'tests'
        if tests_dir.exists():
            for test_file in tests_dir.rglob(f'*{self.nombre_modulo}*.py'):
                tests['archivos_test'].append(str(test_file))

                # Analizar contenido del test
                contenido = self._leer_archivo(test_file)
                tests['tipos_test'].extend(self._identificar_tipos_test(contenido))
                tests['edge_cases_cubiertos'].extend(self._identificar_edge_cases(contenido))

        # Estimar cobertura basada en métodos encontrados vs tests
        if 'model.py' in self.archivos_encontrados:
            metodos_modelo = len(self.analisis['carga_datos'].get('model_methods', []))
            tests_encontrados = len(tests['archivos_test'])
            if metodos_modelo > 0:
                tests['cobertura_estimada'] = min(100, (tests_encontrados * 20))

        # Identificar edge cases potenciales faltantes
        tests['edge_cases_faltantes'] = self._sugerir_edge_cases()

        self.analisis['tests'] = tests
        return tests

    def generar_sugerencias(self):
        """Genera sugerencias de mejora basadas en el análisis."""
        sugerencias = []

        # Sugerencias basadas en estructura
        estructura = self.analisis['estructura']
        if not estructura['archivos_core'].get('model.py', {}).get('existe', False):
            sugerencias.append({
                'categoria': 'estructura',
                'prioridad': 'alta',
                'descripcion': 'Falta archivo model.py - es esencial para la lógica de datos'
            })

        if not estructura['archivos_core'].get('controller.py', {}).get('existe', False):
            sugerencias.append({
                'categoria': 'estructura',
                'prioridad': 'alta',
                'descripcion': 'Falta archivo controller.py - es esencial para la lógica de negocio'
            })

        # Sugerencias basadas en carga de datos
        carga_datos = self.analisis['carga_datos']
        if not carga_datos.get('error_handling'):
            sugerencias.append({
                'categoria': 'robustez',
                'prioridad': 'media',
                'descripcion': 'Implementar manejo de errores en operaciones de base de datos'
            })

        if not carga_datos.get('data_validation'):
            sugerencias.append({
                'categoria': 'seguridad',
                'prioridad': 'alta',
                'descripcion': 'Implementar validación de datos de entrada'
            })

        # Sugerencias basadas en feedback visual
        feedback = self.analisis['feedback_visual']
        if not feedback.get('loading_indicators'):
            sugerencias.append({
                'categoria': 'ux',
                'prioridad': 'media',
                'descripcion': 'Agregar indicadores de carga para operaciones lentas'
            })

        if not feedback.get('error_messages'):
            sugerencias.append({
                'categoria': 'ux',
                'prioridad': 'alta',
                'descripcion': 'Implementar mensajes de error claros para el usuario'
            })

        # Sugerencias basadas en tests
        tests = self.analisis['tests']
        if tests['cobertura_estimada'] < 50:
            sugerencias.append({
                'categoria': 'calidad',
                'prioridad': 'alta',
                'descripcion': f'Cobertura de tests baja ({tests["cobertura_estimada"]}%) - agregar más pruebas'
            })

        if tests['edge_cases_faltantes']:
            sugerencias.append({
                'categoria': 'robustez',
                'prioridad': 'media',
                'descripcion': 'Agregar tests para edge cases identificados'
            })

        self.analisis['sugerencias'] = sugerencias
        return sugerencias

    def generar_informe_html(self):
        """Genera un informe HTML del análisis del módulo."""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis del Módulo {self.nombre_modulo}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #444; }}
        .header {{ background-color: #f8f8f8; padding: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .ok {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .error {{ color: #F44336; }}
        .info {{ color: #2196F3; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .priority-alta {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
        .priority-media {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
        .priority-baja {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
        .suggestion {{ margin: 10px 0; padding: 10px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Análisis del Módulo: {self.nombre_modulo}</h1>
        <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Resumen Ejecutivo</h2>
        <p>Este informe analiza la estructura, funcionalidad y calidad del módulo {self.nombre_modulo}.</p>
    </div>
"""

        # Sección de estructura
        html += self._generar_seccion_estructura()

        # Sección de carga de datos
        html += self._generar_seccion_carga_datos()

        # Sección de feedback visual
        html += self._generar_seccion_feedback()

        # Sección de tests
        html += self._generar_seccion_tests()

        # Sección de sugerencias
        html += self._generar_seccion_sugerencias()

        html += """
</body>
</html>
"""
        return html

    def _contar_lineas(self, ruta_archivo):
        """Cuenta las líneas de un archivo."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0

    def _leer_archivo(self, ruta_archivo):
        """Lee el contenido de un archivo."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

    def _analizar_archivo_python(self, ruta_archivo):
        """Analiza un archivo Python usando AST."""
        try:
            contenido = self._leer_archivo(ruta_archivo)
            return ast.parse(contenido)
        except:
            return None

    def _extraer_metodos_modelo(self, ast_tree):
        """Extrae métodos del modelo."""
        if not ast_tree:
            return []

        metodos = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                metodos.append(node.name)

        return metodos

    def _buscar_conexiones_bd(self, ast_tree):
        """Busca patrones de conexión a base de datos."""
        if not ast_tree:
            return []

        conexiones = []
        contenido = ast.unparse(ast_tree) if hasattr(ast, 'unparse') else ""

        patrones = [
            r'DatabaseConnection', r'conectar\(\)', r'cursor',
            r'execute', r'fetchall', r'commit'
        ]

        for patron in patrones:
            if re.search(patron, contenido, re.IGNORECASE):
                conexiones.append(patron)

        return conexiones

    def _analizar_patrones_consulta(self, ast_tree):
        """Analiza patrones de consulta SQL."""
        if not ast_tree:
            return []

        patrones = []
        contenido = ast.unparse(ast_tree) if hasattr(ast, 'unparse') else ""

        # Buscar consultas SQL
        sql_patterns = re.findall(r'(SELECT|INSERT|UPDATE|DELETE).*?(?="|\')', contenido, re.IGNORECASE)
        return sql_patterns[:10]  # Limitar a 10 ejemplos

    def _buscar_validaciones(self, ast_tree):
        """Busca patrones de validación de datos."""
        if not ast_tree:
            return []

        validaciones = []
        contenido = ast.unparse(ast_tree) if hasattr(ast, 'unparse') else ""

        patrones = [
            r'validar', r'validate', r'check', r'verify',
            r'isinstance', r'len\(.*\) >', r'if.*not'
        ]

        for patron in patrones:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            validaciones.extend(matches[:3])  # Limitar ejemplos

        return validaciones

    def _buscar_manejo_errores(self, ast_tree):
        """Busca patrones de manejo de errores."""
        if not ast_tree:
            return []

        errores = []
        contenido = ast.unparse(ast_tree) if hasattr(ast, 'unparse') else ""

        patrones = [
            r'try:', r'except', r'raise', r'Exception',
            r'error', r'Error', r'finally:'
        ]

        for patron in patrones:
            if re.search(patron, contenido):
                errores.append(patron)

        return list(set(errores))

    def _buscar_patrones(self, contenido, patrones):
        """Busca patrones específicos en el contenido."""
        encontrados = []
        for patron in patrones:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            encontrados.extend(matches)
        return encontrados

    def _identificar_tipos_test(self, contenido):
        """Identifica tipos de tests en el archivo."""
        tipos = []

        if 'unittest' in contenido:
            tipos.append('unittest')
        if 'pytest' in contenido:
            tipos.append('pytest')
        if 'mock' in contenido:
            tipos.append('mocking')
        if 'setUp' in contenido:
            tipos.append('setup/teardown')

        return tipos

    def _identificar_edge_cases(self, contenido):
        """Identifica edge cases ya cubiertos en tests."""
        edge_cases = []

        patrones = [
            r'empty', r'null', r'None', r'zero', r'negative',
            r'large', r'invalid', r'boundary', r'edge'
        ]

        for patron in patrones:
            if re.search(patron, contenido, re.IGNORECASE):
                edge_cases.append(patron)

        return edge_cases

    def _sugerir_edge_cases(self):
        """Sugiere edge cases que deberían probarse."""
        return [
            'Datos vacíos o nulos',
            'Strings muy largos',
            'Números negativos',
            'Valores límite',
            'Caracteres especiales',
            'Inyección SQL',
            'XSS en campos de texto',
            'Conexión de BD fallida',
            'Timeout de operaciones',
            'Memoria insuficiente'
        ]

    def _generar_seccion_estructura(self):
        """Genera la sección HTML de estructura."""
        estructura = self.analisis['estructura']

        html = """
    <div class="section">
        <h2>Estructura del Módulo</h2>
        <h3>Archivos Core</h3>
        <table>
            <tr><th>Archivo</th><th>Estado</th><th>Líneas</th><th>Tamaño</th></tr>
"""

        for archivo, info in estructura['archivos_core'].items():
            estado = "[CHECK] Existe" if info.get('existe') else "[ERROR] Faltante"
            lineas = info.get('lineas', 'N/A')
            tamaño = f"{info.get('tamaño', 0)} bytes" if info.get('existe') else 'N/A'

            html += f"""
            <tr>
                <td>{archivo}</td>
                <td class="{'ok' if info.get('existe') else 'error'}">{estado}</td>
                <td>{lineas}</td>
                <td>{tamaño}</td>
            </tr>"""

        html += """
        </table>
    </div>
"""
        return html

    def _generar_seccion_carga_datos(self):
        """Genera la sección HTML de carga de datos."""
        carga = self.analisis['carga_datos']

        html = """
    <div class="section">
        <h2>Carga y Manejo de Datos</h2>
"""

        if carga.get('model_methods'):
            html += "<h3>Métodos del Modelo</h3><ul>"
            for metodo in carga['model_methods'][:10]:
                html += f"<li>{metodo}</li>"
            html += "</ul>"

        if carga.get('database_connections'):
            html += "<h3>Conexiones a Base de Datos</h3><ul>"
            for conexion in carga['database_connections']:
                html += f"<li>{conexion}</li>"
            html += "</ul>"

        html += "</div>"
        return html

    def _generar_seccion_feedback(self):
        """Genera la sección HTML de feedback visual."""
        feedback = self.analisis['feedback_visual']

        html = """
    <div class="section">
        <h2>Feedback Visual</h2>
"""

        categorias = [
            ('loading_indicators', 'Indicadores de Carga'),
            ('error_messages', 'Mensajes de Error'),
            ('success_messages', 'Mensajes de Éxito'),
            ('ui_updates', 'Actualizaciones de UI')
        ]

        for key, titulo in categorias:
            items = feedback.get(key, [])
            estado = "[CHECK]" if items else "[WARN]"
            html += f"<p>{estado} <strong>{titulo}:</strong> {len(items)} implementaciones encontradas</p>"

        html += "</div>"
        return html

    def _generar_seccion_tests(self):
        """Genera la sección HTML de tests."""
        tests = self.analisis['tests']

        html = f"""
    <div class="section">
        <h2>Análisis de Tests</h2>
        <p><strong>Cobertura estimada:</strong> {tests['cobertura_estimada']}%</p>
        <p><strong>Archivos de test:</strong> {len(tests['archivos_test'])}</p>

        <h3>Edge Cases Sugeridos</h3>
        <ul>
"""

        for edge_case in tests.get('edge_cases_faltantes', []):
            html += f"<li>{edge_case}</li>"

        html += """
        </ul>
    </div>
"""
        return html

    def _generar_seccion_sugerencias(self):
        """Genera la sección HTML de sugerencias."""
        sugerencias = self.analisis['sugerencias']

        html = """
    <div class="section">
        <h2>Sugerencias de Mejora</h2>
"""

        for sugerencia in sugerencias:
            prioridad = sugerencia.get('prioridad', 'baja')
            html += f"""
        <div class="suggestion priority-{prioridad}">
            <strong>{sugerencia['categoria'].upper()}</strong> - Prioridad: {prioridad}<br>
            {sugerencia['descripcion']}
        </div>
"""

        html += "</div>"
        return html

    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo del módulo."""
        print(f"Analizando módulo: {self.nombre_modulo}")

        self.analizar_estructura()
        self.analizar_carga_datos()
        self.analizar_feedback_visual()
        self.analizar_tests()
        self.generar_sugerencias()

        return self.analisis

    def guardar_informe(self, directorio_salida):
        """Guarda el informe en archivos HTML y JSON."""
        os.makedirs(directorio_salida, exist_ok=True)

        # Guardar HTML
        html_path = Path(directorio_salida) / f"analisis_{self.nombre_modulo}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.generar_informe_html())

        # Guardar JSON
        json_path = Path(directorio_salida) / f"analisis_{self.nombre_modulo}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analisis, f, indent=2, ensure_ascii=False)

        return str(html_path), str(json_path)


def main():
    """Función principal para ejecutar el análisis desde línea de comandos."""
    parser = argparse.ArgumentParser(description='Analizador de módulos del proyecto')
    parser.add_argument('--modulo', '-m', help='Nombre específico del módulo a analizar')
    parser.add_argument('--todos',
'-t',
        action='store_true',
        help='Analizar todos los módulos')
    parser.add_argument('--output',
'-o',
        default='informes_modulos',
        help='Directorio de salida')

    args = parser.parse_args()

    modules_dir = ROOT_DIR / 'modules'
import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

    if args.modulo:
        # Analizar módulo específico
        ruta_modulo = modules_dir / args.modulo
        if ruta_modulo.exists():
            analizador = AnalizadorModulo(ruta_modulo)
            analizador.ejecutar_analisis_completo()
            html_path, json_path = analizador.guardar_informe(args.output)
            print(f"Informe generado: {html_path}")
        else:
            print(f"Módulo {args.modulo} no encontrado")

    elif args.todos:
        # Analizar todos los módulos
        for modulo_dir in modules_dir.iterdir():
            if modulo_dir.is_dir() and not modulo_dir.name.startswith('.'):
                print(f"\nAnalizando: {modulo_dir.name}")
                analizador = AnalizadorModulo(modulo_dir)
                analizador.ejecutar_analisis_completo()
                html_path, json_path = analizador.guardar_informe(args.output)
                print(f"Informe generado: {html_path}")

    else:
        print("Especifica --modulo <nombre> o --todos para analizar módulos")


if __name__ == "__main__":
    main()
