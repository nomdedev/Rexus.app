#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Agregar MIT License Headers a Archivos Restantes
===============================================

Script para identificar y agregar headers MIT License a archivos
view.py, dialog.py y otros archivos de interfaz que aún no los tienen.

Este script:
1. Escanea archivos de interfaz (view.py, *dialog*.py, etc.)
2. Verifica si tienen header MIT License
3. Agrega el header estándar MIT si falta
4. Mantiene el contenido original intacto
5. Genera reporte de archivos procesados

Uso:
python tools/maintenance/agregar_mit_headers.py
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

class MITHeaderAdder:
    """Agregador de headers MIT License"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.results = {
            "processed": [],
            "already_has_header": [],
            "errors": [],
            "added": []
        }

        # Template estándar MIT License para Rexus.app
        self.mit_header = '''"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""'''

    def tiene_mit_header(self, file_path: Path) -> bool:
        """Verifica si un archivo ya tiene header MIT License"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # Solo leer primeras 500 caracteres

            # Buscar indicadores de MIT License
            mit_indicators = [
                "MIT License",
                "Copyright (c)",
                "Permission is hereby granted",
                "THE SOFTWARE IS PROVIDED"
            ]

            return any(indicator in content for indicator in mit_indicators)

        except Exception as e:
            print(f"[ERROR] Error leyendo {file_path}: {e}")
            return False

    def agregar_mit_header(self, file_path: Path) -> bool:
        """Agrega header MIT License a un archivo"""

        try:
            # Leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Verificar si ya tiene header
            if self.tiene_mit_header(file_path):
                self.results["already_has_header"].append(str(file_path))
                return True

            # Buscar punto de inserción (después del shebang si existe)
            lines = original_content.split('\n')
            insert_index = 0

            # Si hay shebang, insertar después
            if lines and lines[0].startswith('#!'):
                insert_index = 1

            # Si hay encoding comment, insertar después
            for i, line in enumerate(lines[:3]):
                if 'coding:' in line or 'encoding:' in line:
                    insert_index = i + 1
                    break

            # Crear nuevo contenido con header MIT
            new_lines = lines[:insert_index]
            new_lines.append(self.mit_header)

            # Si había contenido original, agregarlo
            if insert_index < len(lines):
                # Agregar línea en blanco si es necesario
                if lines[insert_index].strip():
                    new_lines.append('')
                new_lines.extend(lines[insert_index:])

            new_content = '\n'.join(new_lines)

            # Escribir archivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"  [OK] Header MIT agregado a {file_path.name}")
            self.results["added"].append(str(file_path))
            return True

        except Exception as e:
            print(f"  [ERROR] Error procesando {file_path}: {e}")
            self.results["errors"].append(f"{file_path}: {e}")
            return False

    def encontrar_archivos_objetivo(self) -> List[Path]:
        """Encuentra archivos que pueden necesitar header MIT"""

        archivos_objetivo = []

        # Patrones de archivos a procesar
        patterns = [
            "rexus/modules/**/view*.py",
            "rexus/modules/**/*dialog*.py",
            "rexus/core/login_dialog.py",
            "rexus/utils/*dialog*.py",
            "rexus/ui/*.py"
        ]

        for pattern in patterns:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file() and \
                    not file_path.name.startswith('__'):
                    archivos_objetivo.append(file_path)

        # Buscar archivos específicos adicionales
        additional_files = [
            "rexus/main/app.py",
            "rexus/core/login_dialog.py"
        ]

        for file_rel_path in additional_files:
            file_path = self.base_dir / file_rel_path
            if file_path.exists():
                archivos_objetivo.append(file_path)

        # Remover duplicados y ordenar
        archivos_objetivo = list(set(archivos_objetivo))
        archivos_objetivo.sort()

        return archivos_objetivo

    def procesar_archivo(self, file_path: Path):
        """Procesa un archivo individual"""

        print(f"\n[PROCESANDO] {file_path.relative_to(self.base_dir)}")

        try:
            self.results["processed"].append(str(file_path))

            # Verificar si necesita header
            if self.tiene_mit_header(file_path):
                print(f"  [SKIP] Ya tiene header MIT License")
                self.results["already_has_header"].append(str(file_path))
                return

            # Agregar header MIT
            if self.agregar_mit_header(file_path):
                print(f"  [SUCCESS] Header MIT agregado exitosamente")
            else:
                print(f"  [FAILED] Error agregando header MIT")

        except Exception as e:
            print(f"  [ERROR] Error procesando archivo: {e}")
            self.results["errors"].append(f"{file_path}: {e}")

    def ejecutar_agregado(self):
        """Ejecuta el proceso completo de agregar headers MIT"""

        print("[MIT HEADERS] Agregando MIT License headers a archivos restantes")
        print("=" * 65)

        # Encontrar archivos objetivo
        archivos_objetivo = self.encontrar_archivos_objetivo()
        print(f"[INFO] Encontrados {len(archivos_objetivo)} archivos para revisar")

        if not archivos_objetivo:
            print("[INFO] No se encontraron archivos para procesar")
            return

        # Procesar cada archivo
        for archivo in archivos_objetivo:
            self.procesar_archivo(archivo)

        # Mostrar resumen
        self._mostrar_resumen()

    def _mostrar_resumen(self):
        """Muestra resumen de la operación"""

        print("\n" + "=" * 65)
        print("[REPORT] RESUMEN DE AGREGADO MIT HEADERS")
        print("=" * 65)

        print(f"[TOTAL] Archivos procesados: {len(self.results['processed'])}")
        print(f"[ADDED] Headers MIT agregados: {len(self.results['added'])}")
        print(f"[SKIP] Ya tenían header: {len(self.results['already_has_header'])}")
        print(f"[ERROR] Errores: {len(self.results['errors'])}")

        if self.results['added']:
            print(f"\n[SUCCESS] HEADERS MIT AGREGADOS:")
            for archivo in self.results['added']:
                file_path = Path(archivo)
                print(f"  + {file_path.relative_to(self.base_dir)}")

        if self.results['errors']:
            print(f"\n[ERRORS] ERRORES:")
            for error in self.results['errors']:
                print(f"  - {error}")

        # Estadísticas finales
        total_con_header = len(self.results['added']) + len(self.results['already_has_header'])
        total_procesados = len(self.results['processed'])

        if total_procesados > 0:
            cobertura = (total_con_header / total_procesados) * 100
            print(f"\n[RESULT] Cobertura MIT License: {cobertura:.1f}%")

        if len(self.results['errors']) == 0:
            print("[SUCCESS] HEADERS MIT AGREGADOS EXITOSAMENTE")
        else:
            print("[WARNING] Headers agregados con algunos errores")

def main():
    """Función principal"""

    # Verificar directorio
    root_dir = Path('.')
    if not (root_dir / "rexus").exists():
        print("[ERROR] No se encuentra el directorio 'rexus'. Ejecutar desde la raíz del proyecto.")
        return

    try:
        # Crear y ejecutar agregador
        header_adder = MITHeaderAdder(root_dir)
        header_adder.ejecutar_agregado()

        print(f"\n[INFO] Operación completada")

    except Exception as e:
        print(f"[ERROR] Error ejecutando script: {e}")

if __name__ == "__main__":
    main()
