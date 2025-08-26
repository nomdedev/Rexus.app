#!/usr/bin/env python3
"""
Script para analizar queries embebidas en el código
"""

import os
import re
from collections import defaultdict

def find_embedded_queries(directory):
    """Encuentra queries SQL embebidas en archivos Python"""
    issues = {}
    
    # Patrones para encontrar queries SQL embebidas
    patterns = [
        # cursor.execute("SELECT ...")
        re.compile(r'\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']', re.IGNORECASE | re.DOTALL),
        # execute("SELECT ...")
        re.compile(r'execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']', re.IGNORECASE | re.DOTALL),
        # Queries en strings multilinea
        re.compile(r'["\'"]{3}([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'"]{3}', re.IGNORECASE | re.DOTALL),
        # Variables con queries
        re.compile(r'=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']', re.IGNORECASE | re.DOTALL)
    ]
    
    for root, dirs, files in os.walk(directory):
        # Saltar directorios de cache y tests
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Buscar queries con todos los patrones
                    total_matches = 0
                    query_examples = []
                    
                    for pattern in patterns:
                        matches = pattern.findall(content)
                        for match in matches:
                            # Filtrar falsos positivos (comentarios, documentación)
                            if not any(exclude in match.lower() for exclude in ['example', 'ejemplo', 'documentation', 'comment']):
                                total_matches += 1
                                if len(query_examples) < 3:  # Guardar algunos ejemplos
                                    query_examples.append(match[:100] + '...' if len(match) > 100 else match)
                    
                    if total_matches > 0:
                        relative_path = os.path.relpath(filepath, directory)
                        issues[relative_path] = {'count': total_matches, 'examples': query_examples}
                        
                except Exception as e:
                    print(f"Error leyendo {filepath}: {e}")
                    
    return issues

def analyze_by_module(issues):
    """Agrupa los problemas por módulo"""
    by_module = defaultdict(list)
    
    for file, data in issues.items():
        if '/' in file or '\\' in file:
            module = file.split(os.sep)[0]
        else:
            module = 'root'
        by_module[module].append((file, data['count'], data['examples']))
    
    return by_module

def main():
    print("=== ANÁLISIS DE QUERIES EMBEBIDAS ===\n")
    
    # Analizar directorio rexus
    issues = find_embedded_queries('rexus')
    
    if not issues:
        print("✅ ¡No se encontraron queries embebidas!")
        return
    
    # Agrupar por módulo
    by_module = analyze_by_module(issues)
    
    print("📊 ARCHIVOS CON QUERIES EMBEBIDAS:\n")
    
    total_files = len(issues)
    total_queries = sum(data['count'] for data in issues.values())
    
    # Mostrar por módulo
    for module, files in sorted(by_module.items(), key=lambda x: sum(f[1] for f in x[1]), reverse=True):
        module_queries = sum(f[1] for f in files)
        print(f"🔴 {module}/ ({module_queries} queries):")
        for file, count, examples in sorted(files, key=lambda x: x[1], reverse=True):
            print(f"  - {file}: {count} queries")
            if examples:
                print(f"    Ejemplos: {examples[0]}")
        print()
    
    print("📈 RESUMEN:")
    print(f"  • Archivos problemáticos: {total_files}")
    print(f"  • Total queries embebidas: {total_queries}")
    print(f"  • Módulos afectados: {len(by_module)}")
    
    # Top 5 archivos más problemáticos
    print("\n🚨 TOP 5 ARCHIVOS MÁS PROBLEMÁTICOS:")
    top_files = sorted(issues.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
    for i, (file, data) in enumerate(top_files, 1):
        print(f"  {i}. {file}: {data['count']} queries")
        if data['examples']:
            print(f"     Ejemplo: {data['examples'][0]}")

if __name__ == "__main__":
    main()
