#!/usr/bin/env python3
"""
Dry-run para migrar print() a logging: no modifica archivos, solo muestra diffs propuestos.
Usa las mismas reglas que `migrate_prints_to_logging.py` pero en memoria.
"""

import re
from pathlib import Path
import difflib

REPLACEMENTS = [
    (re.compile(r'print\(f?"\[ERROR[^\"]*\]\S*{[^}]+}[^\"]*"\)'), lambda s: s.replace('print(f"', 'logger.error(f"').replace('print("', 'logger.error("')),
    (re.compile(r'print\(f?"\[WARNING[^\"]*\]'), lambda s: s.replace('print(f"', 'logger.warning(f"').replace('print("', 'logger.warning("')),
    (re.compile(r'print\(f"\[[A-Z_]+ CONTROLLER\]'), lambda s: s.replace('print(f"', 'logger.info(f"').replace('print("', 'logger.info("')),
    (re.compile(r'print\(f"[^\"]*{[^}]+}[^\"]*"\)'), lambda s: s.replace('print(f"', 'logger.debug(f"')),
    (re.compile(r'print\("([^\"]+)"\)'), lambda s, m: f'logger.info("{m.group(1)}")')
]

TARGETS = [
    'rexus/modules/auditoria/controller.py',
    'rexus/modules/configuracion/controller.py',
    'rexus/modules/mantenimiento/controller.py',
    'rexus/modules/notificaciones/controller.py',
    'rexus/modules/administracion/controller.py',
]

base = Path('.')

def migrate_content(content, file_path):
    new_content = content
    # add import block if missing
    if 'from rexus.utils.app_logger import get_logger' not in new_content:
        insert_point = 0
        lines = new_content.splitlines()
        # try to insert after first import block
        for i, line in enumerate(lines[:50]):
            if line.startswith('from') or line.startswith('import'):
                insert_point = i+1
        logger_block = ("\n# Importar logging centralizado\ntry:\n    from rexus.utils.app_logger import get_logger\n    logger = get_logger(\"PLACEHOLDER_MODULE\")\nexcept ImportError:\n    class DummyLogger:\n        def info(self, msg): print(f\"[INFO] {msg}\")\n        def warning(self, msg): print(f\"[WARNING] {msg}\")\n        def error(self, msg): print(f\"[ERROR] {msg}\")\n        def debug(self, msg): print(f\"[DEBUG] {msg}\")\n    logger = DummyLogger()\n\n")
        lines.insert(insert_point, logger_block)
        new_content = '\n'.join(lines)

    # apply replacements
    for pattern, repl in REPLACEMENTS:
        def _repl(m):
            if callable(repl):
                try:
                    return repl(m.group(0))
                except TypeError:
                    return repl(m.group(0), m)
            return repl
        new_content = pattern.sub(_repl, new_content)

    # update module name
    module_name = Path(file_path).parent.name
    new_content = new_content.replace('get_logger("PLACEHOLDER_MODULE")', f'get_logger("{module_name}.controller")')

    return new_content


def show_diff(orig, new, path):
    diff = difflib.unified_diff(
        orig.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=str(path) + ' (orig)',
        tofile=str(path) + ' (proposed)',
    )
    out = ''.join(diff)
    if out.strip():
        print(out)
    else:
        print(f'No changes for {path}')


if __name__ == '__main__':
    for rel in TARGETS:
        p = base / rel
        if not p.exists():
            print(f'File not found: {p}')
            continue
        content = p.read_text(encoding='utf-8')
        new = migrate_content(content, p)
        show_diff(content, new, p)
