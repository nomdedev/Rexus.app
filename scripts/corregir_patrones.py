#!/usr/bin/env python3
"""
Script de Corrección Automática de Patrones Comunes
USAR CON PRECAUCIÓN - Crear backup antes de ejecutar
"""

import re
import os
import shutil
from datetime import datetime

def crear_backup(archivo):
    """Crea backup del archivo antes de modificar."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{archivo}.backup_{timestamp}"
    shutil.copy2(archivo, backup_file)
    return backup_file

def corregir_docstrings_mal_indentados(archivo):
    """Corrige docstrings con patrón ):""" incorrectos."""
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # Patrón 1: ):"""""" → ):\n        """"""""
    patron1 = r'(\):)("""[^"]*""")'
    reemplazo1 = r'\1\n        \2'
    contenido = re.sub(patron1, reemplazo1, contenido)
    
    # Patrón 2: Indentación incorrecta después de métodos
    patron2 = r'(def \w+\([^)]*\):)(""")'
    reemplazo2 = r'\1\n        \2'
    contenido = re.sub(patron2, reemplazo2, contenido)
    
    if contenido != contenido_original:
        # Crear backup
        backup = crear_backup(archivo)
        print(f"📄 Backup creado: {backup}")
        
        # Escribir contenido corregido
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True
    
    return False

# Lista de archivos a corregir
archivos_a_corregir = [
    "rexus/modules/inventario/controller.py",
    "rexus/modules/obras/controller.py",
    "rexus/modules/administracion/controller.py",
    # Agregar más según necesidad
]

if __name__ == "__main__":
    print("🔧 CORRECTOR AUTOMÁTICO DE PATRONES")
    print("⚠️  ESTO MODIFICARÁ LOS ARCHIVOS - Se crearán backups")
    
    respuesta = input("¿Continuar? (s/N): ")
    if respuesta.lower() != 's':
        print("Operación cancelada")
        exit()
    
    for archivo in archivos_a_corregir:
        if os.path.exists(archivo):
            if corregir_docstrings_mal_indentados(archivo):
                print(f"✅ Corregido: {archivo}")
            else:
                print(f"ℹ️  Sin cambios: {archivo}")
        else:
            print(f"❌ No encontrado: {archivo}")
