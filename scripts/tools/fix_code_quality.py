#!/usr/bin/env python3
"""
Script automático para corregir problemas de calidad de código detectados por flake8
Corrige: imports no usados, espacios en blanco, líneas muy largas, variables no usadas
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Set, Dict, List, Tuple


class CodeQualityFixer:
    """Corrector automático de problemas de calidad de código"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixed_files = 0
        self.issues_fixed = 0

    def fix_all_issues(self):
        """Corrige todos los problemas de calidad detectados"""
        print("=== INICIANDO CORRECCIÓN AUTOMÁTICA DE CÓDIGO ===\n")

        # 1. Corregir espacios en blanco (más fácil y seguro)
        self.fix_whitespace_issues()

        # 2. Corregir imports no usados
        self.fix_unused_imports()

        # 3. Corregir líneas largas (parcial)
        self.fix_long_lines()

        # 4. Corregir variables no usadas
        self.fix_unused_variables()

        print("\n=== RESUMEN ===")
        print(f"Archivos procesados: {self.fixed_files}")
        print(f"Problemas corregidos: {self.issues_fixed}")

    def fix_whitespace_issues(self):
        """Corrige problemas de espacios en blanco"""
        print("🔧 Corrigiendo espacios en blanco...")

        python_files = self._find_python_files()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                original_lines = len(lines)
                new_lines = []
                file_fixes = 0

                for line in lines:
                    # Eliminar espacios al final de línea
                    stripped = line.rstrip()
                    if stripped != line.rstrip('\n'):
                        file_fixes += 1

                    # Agregar nueva línea si no existe
                    if not stripped.endswith('\n') and stripped:
                        stripped += '\n'

                    new_lines.append(stripped)

                # Eliminar líneas vacías al final
                while new_lines and new_lines[-1].strip() == '':
                    new_lines.pop()
                    file_fixes += 1

                if file_fixes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    self.fixed_files += 1
                    self.issues_fixed += file_fixes
                    print(f"  ✓ {file_path.name}: {file_fixes} correcciones")

            except Exception as e:
                print(f"  ✗ Error en {file_path.name}: {str(e)}")

    def fix_unused_imports(self):
        """Corrige imports no usados"""
        print("🔧 Corrigiendo imports no usados...")

        python_files = self._find_python_files()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                analyzer = ImportAnalyzer()
                analyzer.visit(tree)

                unused_imports = analyzer.get_unused_imports()

                if unused_imports:
                    new_content = self._remove_unused_imports(content, unused_imports)

                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

                        self.fixed_files += 1
                        self.issues_fixed += len(unused_imports)
                        print(f"  ✓ {file_path.name}: {len(unused_imports)} imports removidos")

            except Exception as e:
                print(f"  ✗ Error en {file_path.name}: {str(e)}")

    def fix_long_lines(self):
        """Corrige líneas muy largas (implementación básica)"""
        print("🔧 Corrigiendo líneas largas...")

        python_files = self._find_python_files()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                new_lines = []
                file_fixes = 0

                for line in lines:
                    if len(line) > 79 and len(line) < 120:  # Solo líneas moderadamente largas
                        # Casos simples de división
                        if ' and ' in line and line.count(' and ') == 1:
                            # Partir en 'and'
                            parts = line.split(' and ')
                            if len(parts) == 2:
                                indent = len(line) - len(line.lstrip())
                                new_line = f"{parts[0].rstrip()} and \\\n                                    {' ' * (indent + 4)}{parts[1].lstrip()}"
                                new_lines.append(new_line)
                                file_fixes += 1
                                continue
                        elif ', ' in line and line.count(', ') >= 3:
                            # Partir listas/parámetros largos
                            indent = len(line) - len(line.lstrip())
                            if '(' in line and ')' in line:
                                # Función con muchos parámetros
                                parts = line.split(', ')
                                if len(parts) >= 4:
                                    new_line = parts[0] + ',\\\n' + '\\\n'.join([f"{' ' * (indent + 4)}{p.strip()}" for p in parts[1:-1]]) + f",\\\n{' ' * (indent + 4)}{parts[-1]}"
                                    new_lines.append(new_line)
                                    file_fixes += 1
                                    continue

                    new_lines.append(line)

                if file_fixes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    self.fixed_files += 1
                    self.issues_fixed += file_fixes
                    print(f"  ✓ {file_path.name}: {file_fixes} líneas corregidas")

            except Exception as e:
                print(f"  ✗ Error en {file_path.name}: {str(e)}")

    def fix_unused_variables(self):
        """Corrige variables no usadas (implementación básica)"""
        print("🔧 Corrigiendo variables no usadas...")

        python_files = self._find_python_files()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                analyzer = VariableAnalyzer()
                analyzer.visit(tree)

                unused_vars = analyzer.get_unused_variables()

                if unused_vars:
                    new_content = self._remove_unused_variables(content, unused_vars)

                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

                        self.fixed_files += 1
                        self.issues_fixed += len(unused_vars)
                        print(f"  ✓ {file_path.name}: {len(unused_vars)} variables removidas")

            except Exception as e:
                print(f"  ✗ Error en {file_path.name}: {str(e)}")

    def _find_python_files(self) -> List[Path]:
        """Encuentra todos los archivos Python en el proyecto"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Excluir directorios
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def _remove_unused_imports(self, content: str, unused_imports: Set[str]) -> str:
        """Remueve imports no usados del contenido"""
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Verificar si es un import no usado
            is_unused = False
            for unused in unused_imports:
                if f"import {unused}" in line_stripped or f"from {unused}" in line_stripped:
                    is_unused = True
                    break

            if not is_unused:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def _remove_unused_variables(self, content: str, unused_vars: Set[str]) -> str:
        """Remueve variables no usadas del contenido (implementación básica)"""
        # Esta es una implementación simplificada
        # En un caso real, se necesitaría un análisis más sofisticado
        return content


class ImportAnalyzer(ast.NodeVisitor):
    """Analiza imports en código Python"""

    def __init__(self):
        self.imports = set()
        self.used_names = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def get_unused_imports(self) -> Set[str]:
        return self.imports - self.used_names


class VariableAnalyzer(ast.NodeVisitor):
    """Analiza variables en código Python"""

    def __init__(self):
        self.variables = set()
        self.used_vars = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)

    def get_unused_variables(self) -> Set[str]:
        return self.variables - self.used_vars


def main():
    """Función principal"""
    print("=== CORRECTOR AUTOMÁTICO DE CALIDAD DE CÓDIGO ===")
    print("Versión: scripts/tools/fix_code_quality.py")
    print()

    fixer = CodeQualityFixer()
    fixer.fix_all_issues()

    print("\n=== VALIDACIÓN FINAL ===")
    try:
        # Ejecutar flake8 para verificar
        result = subprocess.run([
            'python', '-m', 'flake8', '--count', '--select=E9,F63,F7,F82',
            '--show-source', '--statistics', '.'
        ], capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            print("✅ No se encontraron errores críticos de sintaxis")
        else:
            print("⚠️  Aún quedan algunos problemas:")
            print(result.stdout[-500:])

    except Exception as e:
        print(f"Error ejecutando validación: {e}")


if __name__ == '__main__':
    main()