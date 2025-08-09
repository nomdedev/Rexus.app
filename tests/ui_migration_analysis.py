#!/usr/bin/env python3
"""
Análisis completo de migración UI/UX - Detección de componentes no migrados
"""

import os
import re
import glob

def find_unmigrated_components():
    """Busca componentes QTableWidget y QLabel que no están migrados"""
    base_path = os.path.join(os.getcwd(), "rexus", "modules")
    view_files = glob.glob(os.path.join(base_path, "**/view.py"), recursive=True)
    
    problems = {
        'qtablewidget_usage': [],
        'qlabel_usage': [],
        'qtablewidgetitem_usage': [],
        'missing_migrations': []
    }
    
    for file_path in view_files:
        rel_path = os.path.relpath(file_path, os.getcwd())
        module_name = file_path.split(os.sep)[-2]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        # Verificar si tiene migración de componentes (patrón: QLabel = RexusLabel)
        has_qlabel_migration = bool(re.search(r'^QLabel\s*=\s*RexusLabel', content, re.MULTILINE))
        has_qtablewidget_migration = bool(re.search(r'from rexus\.ui.*RexusTable', content, re.MULTILINE))
        
        # Buscar uso directo de QLabel()
        qlabel_matches = []
        for i, line in enumerate(lines, 1):
            if 'QLabel(' in line and not line.strip().startswith('#') and 'QLabel = RexusLabel' not in line:
                qlabel_matches.append((i, line.strip()))
        
        if qlabel_matches:
            problems['qlabel_usage'].append({
                'file': rel_path,
                'module': module_name,
                'has_migration': has_qlabel_migration,
                'instances': qlabel_matches
            })
        
        # Buscar uso directo de QTableWidget()
        qtablewidget_matches = []
        for i, line in enumerate(lines, 1):
            if re.search(r'QTableWidget\s*\(', line) and not line.strip().startswith('#'):
                qtablewidget_matches.append((i, line.strip()))
        
        if qtablewidget_matches:
            problems['qtablewidget_usage'].append({
                'file': rel_path,
                'module': module_name,
                'has_migration': has_qtablewidget_migration,
                'instances': qtablewidget_matches
            })
        
        # Buscar uso de QTableWidgetItem
        qtablewidgetitem_matches = []
        for i, line in enumerate(lines, 1):
            if 'QTableWidgetItem(' in line and not line.strip().startswith('#'):
                qtablewidgetitem_matches.append((i, line.strip()))
        
        if qtablewidgetitem_matches:
            problems['qtablewidgetitem_usage'].append({
                'file': rel_path,
                'module': module_name,
                'instances': qtablewidgetitem_matches
            })
        
        # Detectar archivos sin migración completa
        if not has_qlabel_migration and not has_qtablewidget_migration:
            # Verificar si usa componentes Qt directamente
            uses_qt_components = bool(re.search(r'from PyQt6\.QtWidgets import.*\b(QLabel|QTableWidget)\b', content))
            if uses_qt_components:
                problems['missing_migrations'].append({
                    'file': rel_path,
                    'module': module_name,
                    'reason': 'Sin migración detectada pero usa componentes Qt'
                })
    
    return problems

def generate_report():
    """Genera reporte completo de migración"""
    problems = find_unmigrated_components()
    
    print("=" * 80)
    print("ANÁLISIS COMPLETO DE MIGRACIÓN UI/UX - COMPONENTES NO MIGRADOS")
    print("=" * 80)
    print()
    
    # Resumen
    total_problems = sum(len(problems[key]) for key in problems if problems[key])
    print(f"RESUMEN:")
    print(f"- Archivos con QLabel no migrado: {len(problems['qlabel_usage'])}")
    print(f"- Archivos con QTableWidget no migrado: {len(problems['qtablewidget_usage'])}")
    print(f"- Archivos con QTableWidgetItem: {len(problems['qtablewidgetitem_usage'])}")
    print(f"- Archivos sin migración completa: {len(problems['missing_migrations'])}")
    print(f"TOTAL DE PROBLEMAS: {total_problems}")
    print()
    
    # Detalle QLabel
    if problems['qlabel_usage']:
        print("PROBLEMAS CON QLabel:")
        print("-" * 50)
        for issue in problems['qlabel_usage']:
            print(f"MODULO: {issue['module']} ({issue['file']})")
            print(f"   Migracion presente: {'SI' if issue['has_migration'] else 'NO'}")
            for line_num, line_content in issue['instances']:
                print(f"   Linea {line_num}: {line_content}")
            print()
    
    # Detalle QTableWidget
    if problems['qtablewidget_usage']:
        print("PROBLEMAS CON QTableWidget:")
        print("-" * 50)
        for issue in problems['qtablewidget_usage']:
            print(f"MODULO: {issue['module']} ({issue['file']})")
            print(f"   Migracion presente: {'SI' if issue['has_migration'] else 'NO'}")
            for line_num, line_content in issue['instances']:
                print(f"   Linea {line_num}: {line_content}")
            print()
    
    # Detalle QTableWidgetItem
    if problems['qtablewidgetitem_usage']:
        print("USO DE QTableWidgetItem (puede necesitar migracion):")
        print("-" * 50)
        for issue in problems['qtablewidgetitem_usage']:
            print(f"MODULO: {issue['module']} ({issue['file']})")
            print(f"   Instancias encontradas: {len(issue['instances'])}")
            # Mostrar solo las primeras 3 para no saturar
            for line_num, line_content in issue['instances'][:3]:
                print(f"   Linea {line_num}: {line_content}")
            if len(issue['instances']) > 3:
                print(f"   ... y {len(issue['instances']) - 3} mas")
            print()
    
    # Archivos sin migración
    if problems['missing_migrations']:
        print("ARCHIVOS SIN MIGRACION COMPLETA:")
        print("-" * 50)
        for issue in problems['missing_migrations']:
            print(f"MODULO: {issue['module']} ({issue['file']})")
            print(f"   Razon: {issue['reason']}")
            print()
    
    print("=" * 80)
    
    # Generar plan de acción
    print("PLAN DE ACCIÓN RECOMENDADO:")
    print("-" * 30)
    
    action_items = []
    
    # Problemas críticos (QLabel/QTableWidget directo sin migración)
    critical_qlabel = [p for p in problems['qlabel_usage'] if not p['has_migration']]
    critical_qtable = [p for p in problems['qtablewidget_usage'] if not p['has_migration']]
    
    if critical_qlabel or critical_qtable:
        print("CRITICO - Migrar componentes sin migracion:")
        for issue in critical_qlabel:
            print(f"   - {issue['module']}: Migrar {len(issue['instances'])} instancias de QLabel")
            action_items.append(f"Migrar QLabel en {issue['module']}")
        for issue in critical_qtable:
            print(f"   - {issue['module']}: Migrar {len(issue['instances'])} instancias de QTableWidget")
            action_items.append(f"Migrar QTableWidget en {issue['module']}")
    
    # Problemas menores (componentes migrados pero con uso directo esporádico)
    minor_qlabel = [p for p in problems['qlabel_usage'] if p['has_migration']]
    if minor_qlabel:
        print("MENOR - Limpiar usos directos en archivos ya migrados:")
        for issue in minor_qlabel:
            print(f"   - {issue['module']}: Limpiar {len(issue['instances'])} usos directos de QLabel")
            action_items.append(f"Limpiar QLabel en {issue['module']}")
    
    # QTableWidgetItem
    if problems['qtablewidgetitem_usage']:
        print("EVALUAR - Revisar uso de QTableWidgetItem:")
        for issue in problems['qtablewidgetitem_usage']:
            print(f"   - {issue['module']}: {len(issue['instances'])} usos de QTableWidgetItem")
            action_items.append(f"Evaluar QTableWidgetItem en {issue['module']}")
    
    print(f"\nTOTAL DE ACCIONES: {len(action_items)}")
    return problems, action_items

if __name__ == "__main__":
    problems, actions = generate_report()