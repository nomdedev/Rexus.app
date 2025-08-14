#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Script para limpiar imports no utilizados
"""

import ast
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple


class ImportAnalyzer(ast.NodeVisitor):
    """Analizador de imports y uso de variables/funciones."""

    def __init__(self):
        self.imports = {}  # nombre -> nodo import
        self.from_imports = {}  # nombre -> nodo from import
        self.used_names = set()
        self.import_lines = {}  # línea -> nodo

    def visit_Import(self, node):
        """Visita declaraciones import."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node
            self.import_lines[node.lineno] = node
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visita declaraciones from import."""
        if node.names[0].name == '*':
            # from module import * - no podemos analizar, marcar como usado
            self.used_names.add('*')
            return

        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.from_imports[name] = node
            self.import_lines[node.lineno] = node
        self.generic_visit(node)

    def visit_Name(self, node):
        """Visita uso de nombres."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Visita acceso a atributos (ej: module.function)."""
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        """Visita llamadas a funciones."""
        if isinstance(node.func, ast.Name):
            self.used_names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and \
            isinstance(node.func.value, ast.Name):
            self.used_names.add(node.func.value.id)
        self.generic_visit(node)


def analyze_file(file_path: Path) -> Dict:
    """
    Analiza un archivo Python para encontrar imports no utilizados.

    Args:
        file_path: Ruta al archivo Python

    Returns:
        Dict con información de análisis
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()

        # Parsear AST
        tree = ast.parse(content)

        # Analizar imports y uso
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)

        # Encontrar imports no utilizados
        unused_imports = []
        all_imported_names = {**analyzer.imports, **analyzer.from_imports}

        for name in all_imported_names:
            if name not in analyzer.used_names:
                node = all_imported_names[name]
                line_content = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                unused_imports.append({
                    'name': name,
                    'line': node.lineno,
                    'content': line_content,
                    'type': 'import' if name in analyzer.imports else 'from_import'
                })

        return {
            'file': str(file_path),
            'success': True,
            'unused_imports': unused_imports,
            'total_imports': len(all_imported_names),
            'used_imports': len(all_imported_names) - len(unused_imports)
        }

    except SyntaxError as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': f"Error de sintaxis: {e}",
            'unused_imports': []
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': f"Error procesando archivo: {e}",
            'unused_imports': []
        }


def remove_unused_imports(file_path: Path, unused_imports: List[Dict]) -> bool:
    """
    Remueve imports no utilizados de un archivo.

    Args:
        file_path: Ruta al archivo
        unused_imports: Lista de imports no utilizados

    Returns:
        True si se realizaron cambios, False caso contrario
    """
    if not unused_imports:
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Marcar líneas a eliminar (en orden inverso para mantener índices)
        lines_to_remove = sorted([imp['line'] - 1 for imp in unused_imports], reverse=True)

        modified = False
        for line_idx in lines_to_remove:
            if 0 <= line_idx < len(lines):
                # Verificar que realmente es un import
                line = lines[line_idx].strip()
                if line.startswith(('import ', 'from ')) and \
                    not line.endswith('# keep'):
                    lines.pop(line_idx)
                    modified = True

        if modified:
            # Limpiar líneas vacías consecutivas dejadas por los imports eliminados
            cleaned_lines = []
            prev_empty = False

            for line in lines:
                if line.strip() == '':
                    if not prev_empty:
                        cleaned_lines.append(line)
                    prev_empty = True
                else:
                    cleaned_lines.append(line)
                    prev_empty = False

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)

        return modified

    except Exception as e:
        print(f"Error removiendo imports de {file_path}: {e}")
        return False


def is_potentially_used_import(import_name: str, file_content: str) -> bool:
    """
    Verifica si un import podría estar siendo usado de formas que el AST no detecta.

    Args:
        import_name: Nombre del import
        file_content: Contenido del archivo

    Returns:
        True si podría estar siendo usado
    """
    # Patrones que indican uso potencial
    patterns = [
        rf'\b{re.escape(import_name)}\b',  # Uso directo
        rf'__import__.*{re.escape(import_name)}',  # Import dinámico
        rf'getattr.*{re.escape(import_name)}',  # Acceso dinámico a atributos
        rf'hasattr.*{re.escape(import_name)}',  # Verificación de atributos
        rf'isinstance.*{re.escape(import_name)}',  # Verificaciones de tipo
        rf'setattr.*{re.escape(import_name)}',  # Asignación dinámica
    ]

    # También verificar en strings y comentarios por si es usado en docstrings
    for pattern in patterns:
        if re.search(pattern, file_content, re.IGNORECASE):
            return True

    return False


def scan_unused_imports(root_path: Path, auto_remove: bool = False) -> Dict:
    """
    Escanea imports no utilizados en archivos Python.

    Args:
        root_path: Directorio raíz para escanear
        auto_remove: Si remover automáticamente imports no utilizados

    Returns:
        Dict con estadísticas
    """
    stats = {
        'files_scanned': 0,
        'files_with_unused': 0,
        'total_unused': 0,
        'files_modified': 0,
        'errors': [],
        'unused_by_file': []
    }

    python_files = list(root_path.rglob('*.py'))

    # Filtrar archivos que no queremos procesar
    excluded_patterns = [
        'backup',
        '__pycache__',
        '.git',
        'venv',
        'env',
        'migrations',
        'tests',  # Los tests pueden tener imports que solo se usan implícitamente
    ]

    filtered_files = []
    for file_path in python_files:
        if not any(pattern in str(file_path).lower() for pattern in excluded_patterns):
            filtered_files.append(file_path)

    print(f"Analizando {len(filtered_files)} archivos Python...")

    for file_path in filtered_files:
        stats['files_scanned'] += 1
        result = analyze_file(file_path)

        if not result['success']:
            stats['errors'].append(result)
            print(f"ERROR {file_path.name}: {result['error']}")
            continue

        if result['unused_imports']:
            # Filtrar imports que podrían estar siendo usados dinámicamente
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                truly_unused = []
                for unused_import in result['unused_imports']:
                    if not is_potentially_used_import(unused_import['name'], file_content):
                        truly_unused.append(unused_import)

                if truly_unused:
                    stats['files_with_unused'] += 1
                    stats['total_unused'] += len(truly_unused)
                    stats['unused_by_file'].append({
                        'file': str(file_path),
                        'unused': truly_unused
                    })

                    print(f"UNUSED {file_path.name}: {len(truly_unused)} imports no utilizados")

                    if auto_remove:
                        if remove_unused_imports(file_path, truly_unused):
                            stats['files_modified'] += 1
                            print(f"  -> Limpiado automáticamente")

            except Exception as e:
                print(f"ERROR procesando {file_path.name}: {e}")

    return stats


def main():
    """Función principal."""
    print("=" * 80)
    print("LIMPIADOR DE IMPORTS NO UTILIZADOS - REXUS.APP")
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

    # Ejecutar análisis (sin auto-remover por seguridad)
    print("\nAnalizando imports no utilizados...")
    stats = scan_unused_imports(rexus_path, auto_remove=False)

    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESUMEN DE ANÁLISIS")
    print("=" * 50)

    print(f"Archivos analizados: {stats['files_scanned']}")
    print(f"Archivos con imports no utilizados: {stats['files_with_unused']}")
    print(f"Total imports no utilizados: {stats['total_unused']}")

    if stats['unused_by_file']:
        print("\nDETALLE POR ARCHIVO:")
        for file_info in stats['unused_by_file']:
            filename = Path(file_info['file']).name
            print(f"\n  {filename}:")
            for unused in file_info['unused']:
                print(f"    Línea {unused['line']}: {unused['content']}")

    if stats['errors']:
        print("\nERRORES ENCONTRADOS:")
        for error in stats['errors']:
            filename = Path(error['file']).name
            print(f"  {filename}: {error['error']}")

    print("\n" + "=" * 50)

    if stats['total_unused'] > 0:
        print("RECOMENDACIÓN:")
        print(f"Se encontraron {stats['total_unused']} imports no utilizados.")
        print("Revise manualmente cada uno antes de eliminarlos.")
        print("Algunos pueden ser necesarios para funcionalidad dinámica.")
        print("\nPara limpiar automáticamente (con precaución):")
        print("  python tools/maintenance/clean_unused_imports.py --auto-clean")
    else:
        print("EXCELENTE: No se encontraron imports no utilizados.")
        print("El código está limpio de imports innecesarios.")

    return 0 if not stats['errors'] else 1


if __name__ == "__main__":
    import sys

    # Verificar si se solicita limpieza automática
    if '--auto-clean' in sys.argv:
        print("MODO AUTO-CLEAN ACTIVADO")
        print("Los imports no utilizados serán eliminados automáticamente.")
        input("Presione Enter para continuar o Ctrl+C para cancelar...")
        # Aquí se podría modificar para usar auto_remove=True

    exit(main())
