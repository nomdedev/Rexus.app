"""
Script para corregir automáticamente problemas de atributos None
"""

import os
import re
from typing import List, Tuple

def corregir_accesos_model_view():
    """Corrige accesos directos a self.model y self.view sin verificación None."""
    
    archivos_corregidos = []
    
    # Recorrer todos los archivos Python en rexus/modules
    for root, dirs, files in os.walk('rexus/modules'):
        for file in files:
            if file.endswith('.py') and file in ['controller.py', 'view.py']:
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Patrones para corregir accesos directos
                    
                    # 1. self.model.metodo() -> if self.model and hasattr(self.model, 'metodo'): self.model.metodo()
                    # Pero solo si no hay verificación previa
                    lines = content.split('\n')
                    corrected_lines = []
                    
                    for i, line in enumerate(lines):
                        # Buscar accesos directos a self.model o self.view
                        model_match = re.search(r'(\s*)(\w+ = )?self\.model\.(\w+)\((.*?)\)', line)
                        view_match = re.search(r'(\s*)(\w+ = )?self\.view\.(\w+)\((.*?)\)', line)
                        
                        if model_match or view_match:
                            # Verificar contexto previo
                            context_start = max(0, i-5)
                            context_lines = lines[context_start:i]
                            context = ' '.join(context_lines).lower()
                            
                            # Si ya hay verificación, no modificar
                            if ('if self.model' in context or 'hasattr(self.model' in context or 
                                'if self.view' in context or 'hasattr(self.view' in context):
                                corrected_lines.append(line)
                                continue
                            
                            # Si es en un try/except, no modificar
                            if any('try:' in prev_line or 'except' in prev_line for prev_line in context_lines):
                                corrected_lines.append(line)
                                continue
                            
                            # Corregir el acceso
                            if model_match:
                                indent, assignment, method, params = model_match.groups()
                                assignment = assignment or ""
                                
                                # Crear líneas corregidas
                                corrected_lines.append(f"{indent}if self.model and hasattr(self.model, '{method}'):")
                                corrected_lines.append(f"{indent}    {assignment}self.model.{method}({params})")
                                if assignment:
                                    corrected_lines.append(f"{indent}else:")
                                    corrected_lines.append(f"{indent}    {assignment.split('=')[0].strip()} = None")
                                
                            elif view_match:
                                indent, assignment, method, params = view_match.groups()
                                assignment = assignment or ""
                                
                                # Crear líneas corregidas
                                corrected_lines.append(f"{indent}if self.view and hasattr(self.view, '{method}'):")
                                corrected_lines.append(f"{indent}    {assignment}self.view.{method}({params})")
                                if assignment:
                                    corrected_lines.append(f"{indent}else:")
                                    corrected_lines.append(f"{indent}    {assignment.split('=')[0].strip()} = None")
                        else:
                            corrected_lines.append(line)
                    
                    new_content = '\n'.join(corrected_lines)
                    
                    # Solo escribir si hubo cambios
                    if new_content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        archivos_corregidos.append(filepath)
                        print(f"Corregido: {filepath}")
                
                except Exception as e:
                    print(f"Error procesando {filepath}: {e}")
    
    return archivos_corregidos

def corregir_hasattr_sin_none():
    """Corrige hasattr() sin verificación previa de None."""
    
    archivos_corregidos = []
    
    for root, dirs, files in os.walk('rexus/modules'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Corregir hasattr(self.model, ...) -> if self.model and hasattr(self.model, ...)
                    content = re.sub(
                        r'(\s*)if hasattr\(self\.model,',
                        r'\1if self.model and hasattr(self.model,',
                        content
                    )
                    
                    # Corregir hasattr(self.view, ...) -> if self.view and hasattr(self.view, ...)
                    content = re.sub(
                        r'(\s*)if hasattr\(self\.view,',
                        r'\1if self.view and hasattr(self.view,',
                        content
                    )
                    
                    # Solo escribir si hubo cambios
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        archivos_corregidos.append(filepath)
                        print(f"Corregido hasattr: {filepath}")
                
                except Exception as e:
                    print(f"Error procesando {filepath}: {e}")
    
    return archivos_corregidos

# Ejecutar correcciones
if __name__ == "__main__":
    print("Iniciando corrección de problemas de atributos None...")
    
    print("\n1. Corrigiendo accesos directos a model/view...")
    archivos_model_view = corregir_accesos_model_view()
    
    print("\n2. Corrigiendo hasattr sin verificación None...")
    archivos_hasattr = corregir_hasattr_sin_none()
    
    total_archivos = set(archivos_model_view + archivos_hasattr)
    
    print(f"\n✅ Corrección completada!")
    print(f"📁 Archivos modificados: {len(total_archivos)}")
    
    if total_archivos:
        print("\nArchivos corregidos:")
        for archivo in sorted(total_archivos):
            print(f"  - {archivo}")
    
    print("\n🔍 Ejecuta nuevamente el análisis para verificar las correcciones.")
