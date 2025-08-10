#!/usr/bin/env python3
"""
Auditoría automatizada de estilos visuales en módulos Rexus
"""

print('🔍 AUDITORÍA COMPLETA DE ESTILOS VISUALES')
print('=' * 50)
print()

# Análisis de archivos de estilo
import os

modules = ['inventario', 'obras', 'herrajes', 'vidrios', 'compras', 'pedidos', 'mantenimiento', 'logistica']
results = {}

for module in modules:
    view_path = f'rexus/modules/{module}/view.py'
    if os.path.exists(view_path):
        with open(view_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Análisis de componentes
        has_rexus_components = 'RexusButton' in content or 'RexusLabel' in content
        has_qt_native = 'QLabel(' in content or 'QLineEdit(' in content or 'QPushButton(' in content
        has_tabs = 'QTabWidget' in content
        has_style_method = 'def aplicar_estilos' in content or 'setStyleSheet' in content
        has_base_module = 'BaseModuleView' in content
        
        # Conteo de líneas
        lines = len(content.split('\n'))
        
        # Puntuación de conformidad
        score = 0
        if has_rexus_components: score += 30
        if not has_qt_native: score += 25
        if has_style_method: score += 20
        if has_base_module: score += 15
        if has_tabs: score += 10
        
        results[module] = {
            'score': score,
            'lines': lines,
            'rexus': has_rexus_components,
            'qt_native': has_qt_native,
            'style_method': has_style_method,
            'base_module': has_base_module,
            'tabs': has_tabs
        }

# Mostrar resultados
for module, data in sorted(results.items(), key=lambda x: x[1]['score'], reverse=True):
    score = data['score']
    if score >= 70:
        status = '✅ BUENO'
    elif score >= 50:
        status = '🟡 MODERADO' 
    else:
        status = '🔴 CRÍTICO'
    
    print(f'{status} {module.upper()}: {score}/100 puntos ({data["lines"]} líneas)')
    print(f'  • RexusComponents: {"✅" if data["rexus"] else "❌"}')
    print(f'  • Qt Nativo: {"❌" if data["qt_native"] else "✅"}') 
    print(f'  • Método Estilos: {"✅" if data["style_method"] else "❌"}')
    print(f'  • BaseModuleView: {"✅" if data["base_module"] else "❌"}')
    print(f'  • Pestañas: {"✅" if data["tabs"] else "❌"}')
    print()

print('RESUMEN FINAL:')
critical = [m for m, d in results.items() if d['score'] < 50]
moderate = [m for m, d in results.items() if 50 <= d['score'] < 70]
good = [m for m, d in results.items() if d['score'] >= 70]

print(f'🔴 CRÍTICOS ({len(critical)}): {", ".join(critical)}')
print(f'🟡 MODERADOS ({len(moderate)}): {", ".join(moderate)}')
print(f'✅ BUENOS ({len(good)}): {", ".join(good)}')
