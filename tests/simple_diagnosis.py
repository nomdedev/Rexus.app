# -*- coding: utf-8 -*-
"""
Simple Diagnostic - Version simplificada sin emojis
"""

import subprocess
import sys
import os
from pathlib import Path

# Configurar encoding
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*80)
print("DIAGNOSTICO SIMPLIFICADO - TESTS REXUS.APP")
print("="*80)

os.chdir(Path(__file__).parent.parent)

# Ejecutar pytest simple
print("\n1. Ejecutando tests (sin coverage)...\n")

cmd = [
    sys.executable, '-m', 'pytest',
    'tests/unit/',
    '-v',
    '--tb=short',
    '--no-header',
    '-q'
]

print(f"Comando: {' '.join(cmd)}\n")

result = subprocess.run(cmd, capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print("\n" + "="*80)
if result.returncode == 0:
    print("RESULTADO: TESTS PASARON")
else:
    print(f"RESULTADO: TESTS FALLARON (exit code: {result.returncode})")
print("="*80)

# Contar tests existentes
print("\n2. Contando tests existentes...\n")

test_files = list(Path('tests').rglob('test_*.py'))
print(f"Total archivos de tests: {len(test_files)}")

test_count = 0
for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        test_count += content.count('def test_')
    except:
        # Intentar con latin-1
        try:
            content = test_file.read_text(encoding='latin-1')
            test_count += content.count('def test_')
        except:
            pass

print(f"Total funciones de test: {test_count}")

# Analizar modulos
print("\n3. Analizando modulos...\n")

modules_path = Path('rexus/modules')
if modules_path.exists():
    modules = [d for d in modules_path.iterdir() if d.is_dir() and not d.name.startswith('_')]
    print(f"Total modulos: {len(modules)}")

    for module in sorted(modules):
        model_file = module / 'model.py'
        test_dir = Path('tests/unit') / module.name[:2]

        has_model = model_file.exists()
        has_test = test_dir.exists() and any(test_dir.glob('test_*.py'))

        status = "OK" if has_test else "FALTA TEST"
        print(f"  {module.name:30} {status}")
else:
    print("No se encuentra directorio de modulos")

print("\n" + "="*80)
print("DIAGNOSTICO FINALIZADO")
print("="*80)

print("""
RECOMENDACIONES:
1. Ejecutar: pytest tests/unit/ -v (individual)
2. Revisar tests fallantes
3. Crear tests para modulos sin testear
4. Implementar plan 99% cobertura
""")

sys.exit(result.returncode)
