#!/usr/bin/env python3
"""
Script para reparar el controlador de inventario con soporte completo de paginación
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def reparar_controlador():
    """Repara el controlador de inventario."""
    
    archivo_controller = Path("rexus/modules/inventario/controller.py")
    
    # Leer contenido actual
    with open(archivo_controller, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Encontrar el final del método _cargar_datos_inventario
    lineas = contenido.split('\n')
    nuevas_lineas = []
    
    dentro_metodo_problematico = False
    
    for linea in lineas:
        # Si encontramos el inicio del método _cargar_datos_inventario
        if 'def _cargar_datos_inventario(self):' in linea:
            nuevas_lineas.append(linea)
            nuevas_lineas.append('        """Método privado para cargar datos del inventario."""')
            nuevas_lineas.append('        # Redirigir al método de paginación')
            nuevas_lineas.append('        return self.cargar_inventario_paginado(1, 100)')
            nuevas_lineas.append('')
            dentro_metodo_problematico = True
            continue
            
        # Si estamos dentro del método problemático, buscar el siguiente método
        if dentro_metodo_problematico:
            if linea.strip().startswith('def ') and not linea.strip().startswith('def _cargar_datos_inventario'):
                # Encontramos el siguiente método, salir del modo problemático
                dentro_metodo_problematico = False
                nuevas_lineas.append(linea)
            # Mientras estemos en el método problemático, no agregamos líneas
            continue
        else:
            nuevas_lineas.append(linea)
    
    # Escribir el archivo reparado
    with open(archivo_controller, 'w', encoding='utf-8') as f:
        f.write('\n'.join(nuevas_lineas))
    
    print("✅ Controlador reparado exitosamente")

if __name__ == "__main__":
    reparar_controlador()
