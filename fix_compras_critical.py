#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix crítico para hacer compilable el archivo compras/controller.py
"""

def fix_critical_indentation():
    """Fix mínimo para que el archivo compile."""
    
    with open('rexus/modules/compras/controller.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fixes críticos para compilación
    fixes = [
        # Fix docstring de método conectar_senales
        ('    def conectar_senales(self):\n    """Conecta las señales',
         '    def conectar_senales(self):\n        """Conecta las señales'),
        
        # Fix bloques try mal indentados
        ('        try:\n        if self.view',
         '        try:\n            if self.view'),
        
        # Fix líneas de código mal indentadas en métodos
        ('        if self.view and hasattr(self.view, \'crear_orden_signal\'):\n            self.view.crear_orden_signal.connect',
         '            if self.view and hasattr(self.view, \'crear_orden_signal\'):\n                self.view.crear_orden_signal.connect'),
        
        # Fix docstrings mal indentados
        ('    def cargar_datos_iniciales(self):\n    """Carga datos iniciales',
         '    def cargar_datos_iniciales(self):\n        """Carga datos iniciales'),
        
        ('    def cargar_ordenes_compra(self, filtros: Optional[Dict[str, Any]] = None):\n    """',
         '    def cargar_ordenes_compra(self, filtros: Optional[Dict[str, Any]] = None):\n        """'),
        
        # Fix return statements mal indentados
        ('        return\n\n        # Obtener órdenes del modelo',
         '            return\n\n        # Obtener órdenes del modelo'),
        
        # Fix líneas de código en métodos
        ('        if not self.model or not self.view:\n            return\n\n        # Obtener órdenes del modelo\n        if filtros:',
         '        if not self.model or not self.view:\n            return\n\n        # Obtener órdenes del modelo\n        if filtros:'),
    ]
    
    # Aplicar fixes
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Fix general para docstrings mal indentados
    lines = content.split('\n')
    fixed_lines = []
    in_method = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and line.startswith('    def '):
            in_method = True
            fixed_lines.append(line)
        elif in_method and line.strip().startswith('"""') and not line.startswith('        """'):
            # Fix docstring indentation
            fixed_lines.append('        ' + line.strip())
        elif in_method and line.strip() and not line.startswith('    ') and not line.startswith('        '):
            # Fix method body indentation
            fixed_lines.append('        ' + line.strip())
        elif line.strip().startswith('def ') and line.startswith('def '):
            # Method without proper class indentation
            fixed_lines.append('    ' + line.strip())
            in_method = True
        else:
            fixed_lines.append(line)
    
    # Escribir archivo
    with open('rexus/modules/compras/controller.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Fix crítico aplicado a compras/controller.py")

if __name__ == "__main__":
    fix_critical_indentation()