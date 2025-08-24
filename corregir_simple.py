#!/usr/bin/env python3
"""
Script simple para corrección final de todos los atributos None restantes.
"""

import os
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_default_value(metodo, caso=1):
    metodo_lower = metodo.lower()
    if any(word in metodo_lower for word in ['obtener', 'get', 'buscar', 'find']):
        if 'todos' in metodo_lower or metodo.endswith('s'):
            return '[]'
        elif 'estadistica' in metodo_lower:
            return '{}'
        else:
            return 'None'
    elif 'contador' in metodo_lower:
        return '0'
    elif caso == 2 and any(word in metodo_lower for word in ['existe', 'validar']):
        return 'False'
    else:
        return 'None'

def handle_return_case(linea, i, lineas, filepath):
    indent = len(linea) - len(linea.lstrip())
    espacios = ' ' * indent
    match = re.search(r'return\s+(self\.model\.\w+\([^)]*\))', linea)
    if match:
        llamada = match.group(1)
        metodo = llamada.split('.')[2].split('(')[0]
        default = get_default_value(metodo)
        lineas[i] = f"{espacios}if self.model:\n{espacios}    return {llamada}\n{espacios}return {default}"
        logger.info(f"Corregido return {llamada} en {filepath}")
        return True
    return False

def handle_assignment_case(linea, i, lineas, filepath):
    match = re.search(r'(\s*)(\w+)\s*=\s*(self\.model\.\w+\([^)]*\))', linea)
    if match:
        indent = match.group(1)
        variable = match.group(2)
        llamada = match.group(3)
        metodo = llamada.split('.')[2].split('(')[0]
        default = get_default_value(metodo, caso=2)
        lineas[i] = f"{indent}if self.model:\n{indent}    {variable} = {llamada}\n{indent}else:\n{indent}    {variable} = {default}"
        logger.info(f"Corregida asignación {variable} = {llamada} en {filepath}")
        return True
    return False

def handle_direct_call_case(linea, i, lineas, filepath):
    indent = len(linea) - len(linea.lstrip())
    espacios = ' ' * indent
    llamada = linea.strip()
    lineas[i] = f"{espacios}if self.model:\n{espacios}    {llamada}"
    logger.info(f"Corregida llamada directa {llamada} en {filepath}")
    return True

def corregir_archivo_simple(filepath):
    """Corrige un archivo específico agregando verificaciones None de forma simple."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()

        lineas = contenido.split('\n')
        modificado =
def main():
    """Función principal."""
    logger.info("Iniciando corrección final simple de atributos None...")
    
    # Lista de archivos con problemas conocidos
    archivos_problematicos = [
        'rexus/modules/administracion/controller.py',
        'rexus/modules/administracion/contabilidad/controller.py',
        'rexus/modules/administracion/recursos_humanos/controller.py',
        'rexus/modules/auditoria/controller.py',
        'rexus/modules/compras/controller.py',
        'rexus/modules/compras/pedidos/controller.py',
        'rexus/modules/configuracion/controller.py',
        'rexus/modules/inventario/controller.py',
        'rexus/modules/logistica/controller.py',
        'rexus/modules/mantenimiento/controller.py',
        'rexus/modules/usuarios/controller.py'
    ]
    
    archivos_corregidos = 0
    
    for archivo in archivos_problematicos:
        filepath = archivo.replace('/', os.sep)
        if os.path.exists(filepath):
            if corregir_archivo_simple(filepath):
                archivos_corregidos += 1
        else:
            logger.warning(f"Archivo no encontrado: {filepath}")
    
    logger.info(f"Corrección completada. {archivos_corregidos} archivos modificados.")

if __name__ == "__main__":
    main()
