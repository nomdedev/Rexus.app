# Script para corregir reportes_manager.py

import re

# Leer el archivo
with open('rexus/modules/inventario/submodules/reportes_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Patrones para corregir los errores de return mal formateados
# Buscar patrones como: except Exception as e:\n                'success': False,
pattern1 = r'except Exception as e:\s*\n\s+\'success\': False,'
replacement1 = 'except Exception as e:\n            return {\n                \'success\': False,'

# Buscar patrones donde falta 'return {' después de except
pattern2 = r'(except Exception as e:)\s*\n(\s+)(\'success\': False,)'
replacement2 = r'\1\n\2return {\n\2    \3'

# Aplicar correcciones
content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

# Corregir bloques de error mal formateados específicos
content = re.sub(
    r'except Exception as e:\s*\n\s+\'error\': f\"Error interno: \{str\(e\)\}\"\s*\n\s*\}',
    'except Exception as e:\n            return {\n                \'success\': False,\n                \'error\': f\"Error interno: {str(e)}\"\n            }',
    content,
    flags=re.MULTILINE
)

# Escribir el archivo corregido
with open('rexus/modules/inventario/submodules/reportes_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Archivo reportes_manager.py corregido')
