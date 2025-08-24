#!/usr/bin/env python3
"""
Script para corrección final de todos los atributos None restantes.
Se enfoca en casos específicos que no fueron corregidos automáticamente.
"""

import os
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def corregir_archivo(filepath):
    """Corrige un archivo específico agregando verificaciones None."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        modificado = False
        
        # Patrón 1: return self.model.metodo() -> return self.model.metodo() if self.model else None/[]/{}/False
        patron_return_model = r'return\s+self\.model\.(\w+)\([^)]*\)'
        matches = re.findall(patron_return_model, contenido)
        
        for match in matches:
            metodo = match
            # Determinar el tipo de retorno basado en el nombre del método
            if any(word in metodo.lower() for word in ['obtener', 'get', 'buscar', 'find']):
                if 'todos' in metodo.lower() or 'lista' in metodo.lower() or metodo.endswith('s'):
                    default_return = '[]'
                elif 'estadistica' in metodo.lower() or 'contador' in metodo.lower():
                    default_return = '{}'
                else:
                    default_return = 'None'
            elif any(word in metodo.lower() for word in ['crear', 'crear', 'actualizar', 'eliminar', 'guardar']):
                default_return = 'False'
            elif any(word in metodo.lower() for word in ['existe', 'validar', 'verificar']):
                default_return = 'False'
            else:
                default_return = 'None'
            
            # Buscar y reemplazar la línea completa
            patron_linea = r'(\s*)return\s+self\.model\.' + metodo + r'\([^)]*\)'
            reemplazo = r'\1if self.model:\n\1    return self.model.' + metodo + r'(\g<2>)\n\1return ' + default_return
            
            nuevo_contenido = re.sub(patron_linea, reemplazo, contenido)
            if nuevo_contenido != contenido:
                contenido = nuevo_contenido
                modificado = True
                logger.info(f"Corregido return self.model.{metodo}() en {filepath}")
        
        # Patrón 2: variable = self.model.metodo() -> if self.model: variable = self.model.metodo() else: variable = default
        patron_asignacion_model = r'(\s*)(\w+)\s*=\s*self\.model\.(\w+)\([^)]*\)'
        
        def reemplazar_asignacion(match):
            indent = match.group(1)
            variable = match.group(2)
            metodo = match.group(3)
            llamada = match.group(0).strip()
            
            # Determinar valor por defecto
            if any(word in metodo.lower() for word in ['obtener', 'get', 'buscar', 'find']):
                if 'todos' in metodo.lower() or 'lista' in metodo.lower() or metodo.endswith('s'):
                    default_val = '[]'
                elif 'estadistica' in metodo.lower() or 'contador' in metodo.lower():
                    default_val = '{}'
                else:
                    default_val = 'None'
            elif any(word in metodo.lower() for word in ['existe', 'validar', 'verificar']):
                default_val = 'False'
            elif 'contador' in metodo.lower():
                default_val = '0'
            else:
                default_val = 'None'
            
            return f"{indent}if self.model:\n{indent}    {llamada}\n{indent}else:\n{indent}    {variable} = {default_val}"
        
        nuevo_contenido = re.sub(patron_asignacion_model, reemplazar_asignacion, contenido)
        if nuevo_contenido != contenido:
            contenido = nuevo_contenido
            modificado = True
            logger.info(f"Corregidas asignaciones de self.model en {filepath}")
        
        # Solo aplicar si no está precedido por 'return' o asignación
        lineas = contenido.split('\n')
        for i, linea in enumerate(lineas):
            if re.search(r'^\s*self\.model\.\w+\([^)]*\)$', linea) and not re.search(r'return|=', linea):
                match = re.match(r'^(\s*)', linea)
                if match:
                    indent = match.group(1)
                    llamada = linea.strip()
                    lineas[i] = f"{indent}if self.model:\n{indent}    {llamada}"
                    modificado = True
                    logger.info(f"Corregida llamada directa {llamada} en {filepath}")
        
        contenido = '\n'.join(lineas)
        
        # Patrón 4: Accesos a self.view sin verificación
        patron_return_view = r'return\s+self\.view\.(\w+)\([^)]*\)'
        matches = re.findall(patron_return_view, contenido)
        
        for match in matches:
            metodo = match
            # Para views, generalmente retornamos None o False
            default_return = 'None' if 'obtener' in metodo.lower() or 'get' in metodo.lower() else 'False'
            
            patron_linea = r'(\s*)return\s+self\.view\.' + metodo + r'\([^)]*\)'
            reemplazo = r'\1if self.view:\n\1    return self.view.' + metodo + r'(\g<2>)\n\1return ' + default_return
            
            nuevo_contenido = re.sub(patron_linea, reemplazo, contenido)
            if nuevo_contenido != contenido:
                contenido = nuevo_contenido
                modificado = True
                logger.info(f"Corregido return self.view.{metodo}() en {filepath}")
        
        # Guardar si se modificó
        if modificado:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contenido)
            logger.info(f"Archivo corregido: {filepath}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error procesando {filepath}: {e}")
        return False

def main():
    """Función principal."""
    logger.info("Iniciando corrección final de atributos None...")
    
    # Leer el archivo de análisis para obtener los archivos problemáticos
    archivos_problematicos = set()
    
    try:
        with open('ANALISIS_ATRIBUTOS_NONE.md', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Extraer nombres de archivos
        lineas = contenido.split('\n')
        for linea in lineas:
            if 'rexus/modules' in linea and '.py:' in linea:
                # Extraer path del archivo
                match = re.search(r'(rexus/modules[^:]+\.py)', linea)
                if match:
                    archivo = match.group(1).replace('/', os.sep)
                    archivos_problematicos.add(archivo)
    
    except Exception as e:
        logger.error(f"Error leyendo análisis: {e}")
        return
    
    archivos_corregidos = 0
    
    for archivo in archivos_problematicos:
        filepath = os.path.join('.', archivo)
        if os.path.exists(filepath):
            if corregir_archivo(filepath):
                archivos_corregidos += 1
        else:
            logger.warning(f"Archivo no encontrado: {filepath}")
    
    logger.info(f"Corrección completada. {archivos_corregidos} archivos modificados.")

if __name__ == "__main__":
    main()
