"""
Script para detectar y analizar problemas de atributos None en el proyecto Rexus.app
"""

import os
import re
import ast
from typing import List, Dict, Any

def encontrar_problemas_none():
    """Encuentra problemas relacionados con atributos None en archivos Python."""
    
    problemas = {
        'accesos_directos_model': [],
        'accesos_directos_view': [],
        'model_none_issues': [],
        'view_none_issues': [],
        'hasattr_sin_none_check': []
    }
    
    # Patrones a buscar
    patron_model_directo = re.compile(r'self\.model\.\w+\(.*?\)')
    patron_view_directo = re.compile(r'self\.view\.\w+\(.*?\)')
    patron_hasattr_model = re.compile(r'hasattr\(self\.model,')
    patron_hasattr_view = re.compile(r'hasattr\(self\.view,')
    patron_if_model = re.compile(r'if self\.model')
    patron_if_view = re.compile(r'if self\.view')
    
    # Recorrer todos los archivos Python en rexus/modules
    for root, dirs, files in os.walk('rexus/modules'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        line_stripped = line.strip()
                        
                        # Buscar accesos directos a model sin verificaciones
                        if patron_model_directo.search(line):
                            # Verificar si en las líneas anteriores hay verificación
                            context_start = max(0, i-5)
                            context_lines = lines[context_start:i]
                            context = ' '.join(context_lines).lower()
                            
                            if 'if self.model' not in context and 'hasattr(self.model' not in context:
                                problemas['accesos_directos_model'].append({
                                    'archivo': filepath,
                                    'linea': i,
                                    'codigo': line_stripped
                                })
                        
                        # Buscar accesos directos a view sin verificaciones
                        if patron_view_directo.search(line):
                            context_start = max(0, i-5)
                            context_lines = lines[context_start:i]
                            context = ' '.join(context_lines).lower()
                            
                            if 'if self.view' not in context and 'hasattr(self.view' not in context:
                                problemas['accesos_directos_view'].append({
                                    'archivo': filepath,
                                    'linea': i,
                                    'codigo': line_stripped
                                })
                        
                        # Buscar hasattr sin verificación previa de None
                        if patron_hasattr_model.search(line):
                            context_start = max(0, i-3)
                            context_lines = lines[context_start:i]
                            context = ' '.join(context_lines).lower()
                            
                            if 'if self.model' not in context and 'self.model is not none' not in context:
                                problemas['hasattr_sin_none_check'].append({
                                    'archivo': filepath,
                                    'linea': i,
                                    'codigo': line_stripped,
                                    'tipo': 'model'
                                })
                        
                        if patron_hasattr_view.search(line):
                            context_start = max(0, i-3)
                            context_lines = lines[context_start:i]
                            context = ' '.join(context_lines).lower()
                            
                            if 'if self.view' not in context and 'self.view is not none' not in context:
                                problemas['hasattr_sin_none_check'].append({
                                    'archivo': filepath,
                                    'linea': i,
                                    'codigo': line_stripped,
                                    'tipo': 'view'
                                })
                
                except Exception as e:
                    print(f"Error procesando {filepath}: {e}")
    
    return problemas

def generar_reporte(problemas: Dict[str, List[Dict[str, Any]]]):
    """Genera un reporte detallado de los problemas encontrados."""
    
    reporte = []
    reporte.append("=" * 80)
    reporte.append("ANÁLISIS DE PROBLEMAS DE ATRIBUTOS None - REXUS.APP")
    reporte.append("=" * 80)
    reporte.append("")
    
    total_problemas = sum(len(lista) for lista in problemas.values())
    reporte.append(f"RESUMEN GENERAL: {total_problemas} problemas encontrados")
    reporte.append("")
    
    # Accesos directos a model
    if problemas['accesos_directos_model']:
        reporte.append(f"1. ACCESOS DIRECTOS A MODEL SIN VERIFICACIÓN ({len(problemas['accesos_directos_model'])} problemas)")
        reporte.append("-" * 60)
        for problema in problemas['accesos_directos_model']:
            reporte.append(f"   {problema['archivo']}:{problema['linea']}")
            reporte.append(f"   -> {problema['codigo']}")
            reporte.append("")
    
    # Accesos directos a view
    if problemas['accesos_directos_view']:
        reporte.append(f"2. ACCESOS DIRECTOS A VIEW SIN VERIFICACIÓN ({len(problemas['accesos_directos_view'])} problemas)")
        reporte.append("-" * 60)
        for problema in problemas['accesos_directos_view']:
            reporte.append(f"   {problema['archivo']}:{problema['linea']}")
            reporte.append(f"   -> {problema['codigo']}")
            reporte.append("")
    
    # hasattr sin verificación de None
    if problemas['hasattr_sin_none_check']:
        reporte.append(f"3. HASATTR SIN VERIFICACIÓN DE None ({len(problemas['hasattr_sin_none_check'])} problemas)")
        reporte.append("-" * 60)
        for problema in problemas['hasattr_sin_none_check']:
            reporte.append(f"   {problema['archivo']}:{problema['linea']} ({problema['tipo']})")
            reporte.append(f"   -> {problema['codigo']}")
            reporte.append("")
    
    # Recomendaciones
    reporte.append("RECOMENDACIONES DE CORRECCIÓN")
    reporte.append("=" * 40)
    reporte.append("")
    reporte.append("1. Para accesos directos a model:")
    reporte.append("   ANTES: self.model.metodo()")
    reporte.append("   DESPUÉS: if self.model and hasattr(self.model, 'metodo'):")
    reporte.append("              self.model.metodo()")
    reporte.append("")
    reporte.append("2. Para accesos directos a view:")
    reporte.append("   ANTES: self.view.metodo()")
    reporte.append("   DESPUÉS: if self.view and hasattr(self.view, 'metodo'):")
    reporte.append("              self.view.metodo()")
    reporte.append("")
    reporte.append("3. Para hasattr sin verificación de None:")
    reporte.append("   ANTES: if hasattr(self.model, 'metodo'):")
    reporte.append("   DESPUÉS: if self.model and hasattr(self.model, 'metodo'):")
    reporte.append("")
    
    return '\n'.join(reporte)

# Ejecutar análisis
if __name__ == "__main__":
    print("Analizando problemas de atributos None en el proyecto...")
    problemas = encontrar_problemas_none()
    reporte = generar_reporte(problemas)
    
    # Guardar reporte
    with open('ANALISIS_ATRIBUTOS_NONE.md', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("Análisis completado. Ver ANALISIS_ATRIBUTOS_NONE.md para detalles.")
    print(f"Total problemas encontrados: {sum(len(lista) for lista in problemas.values())}")
