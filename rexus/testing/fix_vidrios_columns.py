"""
Script para corregir todas las referencias a columnas inexistentes en el modelo de vidrios
"""

import re

def fix_vidrios_model():
    file_path = "rexus/modules/vidrios/model.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Columnas que existen realmente en la tabla
    real_columns = [
        'id', 'tipo', 'espesor', 'color', 'precio_m2', 'proveedor',
        'especificaciones', 'propiedades', 'activo', 'fecha_creacion',
        'fecha_actualizacion', 'dimensiones', 'color_acabado', 'stock', 'estado'
    ]
    
    # Reemplazos de columnas
    replacements = {
        'codigo': 'tipo',  # Usar tipo como identificador
        'descripcion': 'especificaciones',  # Usar especificaciones como descripción
        'ubicacion': 'dimensiones',  # Usar dimensiones como ubicación
        'observaciones': 'propiedades',  # Usar propiedades como observaciones
        'fecha_modificacion': 'fecha_actualizacion',
        'tratamiento': 'propiedades'
    }
    
    # Aplicar reemplazos
    for old_col, new_col in replacements.items():
        # Reemplazar en SELECT statements
        content = re.sub(
            f'(SELECT.*?){old_col}(.*?FROM)',
            f'\\1{new_col} as {old_col}\\2',
            content,
            flags=re.DOTALL
        )
        
        # Reemplazar referencias directas a columnas
        content = re.sub(f'\\b{old_col}\\b(?=\\s*(LIKE|=|\\.|,|\\s))', new_col, content)
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Archivo vidrios/model.py corregido")

if __name__ == "__main__":
    fix_vidrios_model()