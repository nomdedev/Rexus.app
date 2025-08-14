#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Analizador de conexiones de señales PyQt6 para detectar problemas comunes
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any


class SignalAnalyzer(ast.NodeVisitor):
    """Analizador AST para conexiones de señales PyQt6."""

    def __init__(self, filename: str):
        self.filename = filename
        self.signals_connected = []  # (línea, señal, slot, método)
        self.signals_disconnected = []  # (línea, señal, slot, método)
        self.signals_emitted = []  # (línea, señal)
        self.signal_definitions = []  # (línea, nombre_señal)
        self.potential_issues = []
        self.class_methods = set()
        self.current_class = None
        self.imports = set()

    def visit_Import(self, node):
        """Recolectar imports."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Recolectar imports from."""
        if node.module:
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visitar definición de clase."""
        self.current_class = node.name
        # Recolectar métodos de la clase
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.class_methods.add(item.name)
        self.generic_visit(node)
        self.current_class = None

    def visit_Assign(self, node):
        """Detectar definiciones de señales."""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == 'pyqtSignal':
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.signal_definitions.append((
                                node.lineno,
                                target.id,
                                self.current_class or "global"
                            ))
        self.generic_visit(node)

    def visit_Call(self, node):
        """Detectar conexiones y emisiones de señales."""
        # Detectar conexiones: signal.connect(slot)
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr == 'connect' and
            len(node.args) >= 1):

            signal_name = self._extract_signal_name(node.func.value)
            slot_name = self._extract_slot_name(node.args[0])

            self.signals_connected.append((
                node.lineno,
                signal_name,
                slot_name,
                'connect'
            ))

            # Verificar si el slot existe como método
            if slot_name and slot_name not in self.class_methods and '.' not in slot_name:
                self.potential_issues.append({
                    'type': 'missing_slot',
                    'line': node.lineno,
                    'signal': signal_name,
                    'slot': slot_name,
                    'message': f"Slot '{slot_name}' no encontrado en la clase"
                })

        # Detectar desconexiones: signal.disconnect()
        elif (isinstance(node.func, ast.Attribute) and
              node.func.attr == 'disconnect'):

            signal_name = self._extract_signal_name(node.func.value)
            slot_name = None
            if node.args:
                slot_name = self._extract_slot_name(node.args[0])

            self.signals_disconnected.append((
                node.lineno,
                signal_name,
                slot_name,
                'disconnect'
            ))

        # Detectar emisiones: signal.emit()
        elif (isinstance(node.func, ast.Attribute) and
              node.func.attr == 'emit'):

            signal_name = self._extract_signal_name(node.func.value)
            self.signals_emitted.append((node.lineno, signal_name))

        self.generic_visit(node)

    def _extract_signal_name(self, node) -> str:
        """Extraer nombre de señal de un nodo AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            elif isinstance(node.value, ast.Attribute):
                return f"{self._extract_signal_name(node.value)}.{node.attr}"
        return "unknown_signal"

    def _extract_slot_name(self, node) -> str:
        """Extraer nombre de slot de un nodo AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            else:
                return f"object.{node.attr}"
        elif isinstance(node, ast.Lambda):
            return "lambda"
        return "unknown_slot"

    def analyze_signal_balance(self):
        """Analizar balance entre conexiones y desconexiones."""
        connected_signals = {}
        for line, signal, slot, _ in self.signals_connected:
            key = f"{signal}->{slot}"
            if key not in connected_signals:
                connected_signals[key] = []
            connected_signals[key].append(line)

        disconnected_signals = {}
        for line, signal, slot, _ in self.signals_disconnected:
            key = f"{signal}->{slot}" if slot else f"{signal}->*"
            if key not in disconnected_signals:
                disconnected_signals[key] = []
            disconnected_signals[key].append(line)

        # Detectar conexiones sin desconexión correspondiente
        for connection, connect_lines in connected_signals.items():
            if connection not in disconnected_signals:
                signal, slot = connection.split('->')
                # Solo advertir para conexiones que deberían desconectarse
                if self._should_warn_missing_disconnect(signal, slot):
                    self.potential_issues.append({
                        'type': 'missing_disconnect',
                        'line': connect_lines[0],
                        'signal': signal,
                        'slot': slot,
                        'message': f"Conexión '{connection}' sin desconexión correspondiente"
                    })

        # Detectar múltiples conexiones de la misma señal
        for connection, connect_lines in connected_signals.items():
            if len(connect_lines) > 1:
                self.potential_issues.append({
                    'type': 'multiple_connections',
                    'line': connect_lines[0],
                    'signal': connection.split('->')[0],
                    'slot': connection.split('->')[1],
                    'message': f"Múltiples conexiones de '{connection}' en líneas: {connect_lines}"
                })

    def _should_warn_missing_disconnect(self, signal: str, slot: str) -> bool:
        """Determinar si debería advertir sobre desconexión faltante."""
        # No advertir para conexiones típicas que no necesitan desconexión
        permanent_connections = [
            'clicked', 'triggered', 'toggled', 'returnPressed',
            'textChanged', 'currentTextChanged', 'itemClicked'
        ]

        # No advertir si la señal es de un botón o control que típicamente no se desconecta
        if any(perm in signal.lower() for perm in permanent_connections):
            return False

        # No advertir para lambdas (se desconectan automáticamente)
        if slot == 'lambda':
            return False

        return True

    def detect_signal_leaks(self):
        """Detectar potenciales memory leaks de señales."""
        # Buscar patrones problemáticos
        for line, signal, slot, _ in self.signals_connected:
            # Conexión a objetos que podrían ser eliminados
            if 'dialog' in signal.lower() or 'window' in signal.lower():
                if 'close' not in slot.lower() and \
                    'destroy' not in slot.lower():
                    self.potential_issues.append({
                        'type': 'potential_leak',
                        'line': line,
                        'signal': signal,
                        'slot': slot,
                        'message': f"Posible memory leak: conexión a objeto temporal '{signal}'"
                    })


def analyze_file_signals(file_path: Path) -> Dict[str, Any]:
    """
    Analiza las conexiones de señales en un archivo Python.

    Args:
        file_path: Ruta al archivo Python

    Returns:
        Dict con resultados del análisis
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parsear AST
        tree = ast.parse(content)

        # Analizar
        analyzer = SignalAnalyzer(file_path.name)
        analyzer.visit(tree)
        analyzer.analyze_signal_balance()
        analyzer.detect_signal_leaks()

        return {
            'file': str(file_path),
            'success': True,
            'signal_definitions': analyzer.signal_definitions,
            'signals_connected': analyzer.signals_connected,
            'signals_disconnected': analyzer.signals_disconnected,
            'signals_emitted': analyzer.signals_emitted,
            'potential_issues': analyzer.potential_issues,
            'class_methods': list(analyzer.class_methods),
            'imports': list(analyzer.imports)
        }

    except SyntaxError as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': f"Error de sintaxis: {e}",
            'potential_issues': []
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': f"Error procesando archivo: {e}",
            'potential_issues': []
        }


def scan_signal_connections(root_path: Path) -> Dict[str, Any]:
    """
    Escanea conexiones de señales en todo el proyecto.

    Args:
        root_path: Directorio raíz para escanear

    Returns:
        Dict con estadísticas globales
    """
    stats = {
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_issues': 0,
        'total_connections': 0,
        'total_disconnections': 0,
        'total_emissions': 0,
        'issues_by_type': {},
        'files_with_signals': [],
        'errors': []
    }

    python_files = list(root_path.rglob('*.py'))

    # Filtrar archivos que no necesitamos analizar
    excluded_patterns = ['backup', '__pycache__', '.git', 'venv', 'env']
    filtered_files = []

    for file_path in python_files:
        if not any(pattern in str(file_path).lower() for pattern in excluded_patterns):
            # Solo analizar archivos que probablemente tengan señales PyQt
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if ('pyqtSignal' in content or '.connect(' in content or
                        '.disconnect(' in content or '.emit(' in content or
                        'PyQt6' in content):
                        filtered_files.append(file_path)
            except:
                continue

    print(f"Analizando {len(filtered_files)} archivos con señales PyQt6...")

    for file_path in filtered_files:
        stats['files_scanned'] += 1
        result = analyze_file_signals(file_path)

        if not result['success']:
            stats['errors'].append(result)
            print(f"ERROR {file_path.name}: {result['error']}")
            continue

        # Recopilar estadísticas
        stats['total_connections'] += len(result['signals_connected'])
        stats['total_disconnections'] += len(result['signals_disconnected'])
        stats['total_emissions'] += len(result['signals_emitted'])

        if result['potential_issues']:
            stats['files_with_issues'] += 1
            stats['total_issues'] += len(result['potential_issues'])

            # Categorizar problemas
            for issue in result['potential_issues']:
                issue_type = issue['type']
                if issue_type not in stats['issues_by_type']:
                    stats['issues_by_type'][issue_type] = 0
                stats['issues_by_type'][issue_type] += 1

            print(f"ISSUES {file_path.name}: {len(result['potential_issues'])} problemas encontrados")

        # Guardar archivos con señales
        if (result['signals_connected'] or result['signals_disconnected'] or
            result['signals_emitted'] or result['signal_definitions']):
            stats['files_with_signals'].append(result)

    return stats


def main():
    """Función principal."""
    print("=" * 80)
    print("ANALIZADOR DE CONEXIONES DE SENALES PYQT6 - REXUS.APP")
    print("=" * 80)

    # Obtener directorio raíz del proyecto
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    rexus_path = project_root / 'rexus'

    print(f"Directorio del proyecto: {project_root}")
    print(f"Directorio rexus: {rexus_path}")

    if not rexus_path.exists():
        print(f"ERROR: Directorio rexus no encontrado en {rexus_path}")
        return 1

    # Ejecutar análisis
    print("\nAnalizando conexiones de señales...")
    stats = scan_signal_connections(rexus_path)

    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESUMEN DE ANALISIS DE SENALES")
    print("=" * 50)

    print(f"Archivos analizados: {stats['files_scanned']}")
    print(f"Archivos con problemas: {stats['files_with_issues']}")
    print(f"Total problemas encontrados: {stats['total_issues']}")
    print(f"Total conexiones: {stats['total_connections']}")
    print(f"Total desconexiones: {stats['total_disconnections']}")
    print(f"Total emisiones: {stats['total_emissions']}")

    if stats['issues_by_type']:
        print("\nTIPOS DE PROBLEMAS:")
        for issue_type, count in stats['issues_by_type'].items():
            issue_names = {
                'missing_slot': 'Slots faltantes',
                'missing_disconnect': 'Desconexiones faltantes',
                'multiple_connections': 'Conexiones múltiples',
                'potential_leak': 'Posibles memory leaks'
            }
            print(f"  {issue_names.get(issue_type, issue_type)}: {count}")

    if stats['files_with_issues'] > 0:
        print(f"\nDETALLE DE PROBLEMAS:")
        for file_result in stats['files_with_signals']:
            if file_result['potential_issues']:
                filename = Path(file_result['file']).name
                print(f"\n  {filename}:")
                for issue in file_result['potential_issues']:
                    print(f"    Linea {issue['line']}: {issue['message']}")

    if stats['errors']:
        print("\nERRORES ENCONTRADOS:")
        for error in stats['errors']:
            filename = Path(error['file']).name
            print(f"  {filename}: {error['error']}")

    print("\n" + "=" * 50)

    if stats['total_issues'] == 0:
        print("EXCELENTE: No se encontraron problemas de conexiones de senales.")
        print("Las conexiones de senales estan bien gestionadas.")
    else:
        print("RECOMENDACIONES:")
        print("1. Revisar slots faltantes y agregar metodos correspondientes")
        print("2. Considerar desconectar senales en destructores si es necesario")
        print("3. Evitar conexiones multiples de la misma senal")
        print("4. Revisar posibles memory leaks en objetos temporales")

    return 0 if stats['total_issues'] == 0 else 1


if __name__ == "__main__":
    exit(main())
