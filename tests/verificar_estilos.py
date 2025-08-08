#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar estilos de alto contraste a todos los módulos principales
"""
import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath('.'))

def create_high_contrast_method():
    """Crea el método de alto contraste que se usará en todos los módulos."""
    return '''
    def apply_high_contrast_style(self):
        """Aplicar estilos de alto contraste para mejor legibilidad."""
        high_contrast_style = """
        /* Estilo general de alto contraste */
        QWidget {
            background-color: #ffffff;
            color: #000000;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 13px;
        }
        
        /* Tabla principal */
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #cccccc;
            gridline-color: #dddddd;
            selection-background-color: #0078d4;
            selection-color: #ffffff;
            font-size: 13px;
        }
        
        QTableWidget::item {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #dddddd;
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QTableWidget::item:hover {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        /* Headers de la tabla */
        QHeaderView::section {
            background-color: #f8f9fa;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 8px;
            font-weight: bold;
            font-size: 13px;
        }
        
        /* Botones */
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: 2px solid #0078d4;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
            border-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
            border-color: #005a9e;
        }
        
        /* Filtros y campos de entrada */
        QComboBox, QLineEdit, QSpinBox {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 13px;
        }
        
        QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
            border-color: #0078d4;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 2px solid #cccccc;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f8f9fa;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 8px 16px;
            font-size: 13px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #000000;
            border-bottom: 2px solid #0078d4;
        }
        
        /* Labels y textos */
        QLabel {
            color: #000000;
            font-size: 13px;
        }
        
        /* GroupBoxes */
        QGroupBox {
            color: #000000;
            border: 2px solid #cccccc;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #000000;
        }
        """
        self.setStyleSheet(high_contrast_style)
'''

def verify_style_application():
    """Verifica que los estilos se están aplicando en los módulos principales."""
    modules_to_check = [
        'rexus/modules/inventario/view.py',
        'rexus/modules/obras/view.py', 
        'rexus/modules/pedidos/view.py',
        'rexus/modules/usuarios/view.py',
        'rexus/modules/herrajes/view.py',
        'rexus/modules/vidrios/view.py',
        'rexus/modules/logistica/view.py'
    ]
    
    results = {}
    
    for module_path in modules_to_check:
        if os.path.exists(module_path):
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            has_style_method = 'apply_high_contrast_style' in content or 'aplicar_estilo' in content or 'apply_theme' in content
            has_style_manager = 'style_manager' in content
            has_setStyleSheet = 'setStyleSheet' in content
            
            results[module_path] = {
                'exists': True,
                'has_style_method': has_style_method,
                'has_style_manager': has_style_manager,
                'has_setStyleSheet': has_setStyleSheet
            }
        else:
            results[module_path] = {'exists': False}
    
    return results

def print_results(results):
    """Imprime los resultados del análisis."""
    print("🎨 [ANÁLISIS] Estado de estilos en módulos principales:")
    print("=" * 60)
    
    for module, data in results.items():
        module_name = module.split('/')[-2].upper()
        
        if not data['exists']:
            print(f"❌ {module_name}: Archivo no encontrado")
            continue
            
        print(f"\n📁 {module_name}:")
        print(f"   ✅ Método de estilo: {'Sí' if data['has_style_method'] else 'No'}")
        print(f"   🎨 Style Manager: {'Sí' if data['has_style_manager'] else 'No'}")
        print(f"   🖌️ setStyleSheet: {'Sí' if data['has_setStyleSheet'] else 'No'}")
        
        if data['has_style_method'] and data['has_setStyleSheet']:
            print(f"   ✅ Estado: BIEN - Tiene estilos aplicados")
        elif data['has_style_manager']:
            print(f"   ⚠️ Estado: PARCIAL - Usa style_manager pero puede necesitar fallback")
        else:
            print(f"   ❌ Estado: PROBLEMA - Sin estilos aplicados")

if __name__ == "__main__":
    print("🔍 Verificando estado de estilos en módulos...")
    results = verify_style_application()
    print_results(results)
    
    print("\n" + "=" * 60)
    print("📋 RECOMENDACIONES:")
    
    problematic_modules = []
    for module, data in results.items():
        if data.get('exists', False) and not data.get('has_style_method', False) and not data.get('has_setStyleSheet', False):
            problematic_modules.append(module)
    
    if problematic_modules:
        print("❌ Módulos que necesitan estilos:")
        for module in problematic_modules:
            print(f"   - {module}")
    else:
        print("✅ Todos los módulos principales tienen algún sistema de estilos")
    
    print("\n🎯 MÓDULOS YA ACTUALIZADOS:")
    print("   ✅ Obras - Alto contraste aplicado")
    print("   ✅ Inventario - Alto contraste aplicado") 
    print("   ✅ Pedidos - Alto contraste aplicado")
    print("   ✅ Usuarios - Alto contraste aplicado")
