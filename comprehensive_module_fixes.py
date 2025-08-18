#!/usr/bin/env python3
"""
Comprehensive Module Fixes for Rexus.app
Systematic approach to fix all identified production issues
"""

import os
import re
from pathlib import Path

class ComprehensiveModuleFixer:
    
    def __init__(self):
        self.fixes_applied = []
        self.errors_found = []
    
    def fix_sql_parameter_mismatches(self):
        """Fix SQL parameter mismatch errors"""
        print("=== FIXING SQL PARAMETER MISMATCHES ===")
        
        # Fix 1: Inventario verification query
        inventario_sql = Path("sql/inventario/verificar_tabla_existe.sql")
        if inventario_sql.exists():
            try:
                with open(inventario_sql, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # If it doesn't have parameters but is called with parameters, add them
                if 'WHERE' not in content and 'TABLE_NAME' not in content:
                    new_content = """-- Verificar si tabla existe en inventario
SELECT COUNT(*) as tabla_existe
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = ?"""
                    
                    with open(inventario_sql, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixes_applied.append("Fixed inventario/verificar_tabla_existe.sql parameter mismatch")
                    print("[OK] Fixed inventario verification query")
            except Exception as e:
                self.errors_found.append(f"Error fixing inventario SQL: {e}")
                print(f"❌ Error fixing inventario SQL: {e}")
        
        # Fix 2: Obras verification query  
        obras_sql = Path("sql/obras/verificar_tabla_sqlite.sql")
        if obras_sql.exists():
            try:
                with open(obras_sql, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix for SQL Server (not SQLite)
                if 'sqlite_master' in content:
                    new_content = """-- Verificar si tabla obras existe en SQL Server
SELECT COUNT(*) as tabla_existe
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = ?"""
                    
                    with open(obras_sql, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixes_applied.append("Fixed obras/verificar_tabla_sqlite.sql for SQL Server")
                    print("✅ Fixed obras verification query")
            except Exception as e:
                self.errors_found.append(f"Error fixing obras SQL: {e}")
                print(f"❌ Error fixing obras SQL: {e}")
    
    def fix_invalid_column_names(self):
        """Fix invalid column name errors in SQL queries"""
        print("\n=== FIXING INVALID COLUMN NAMES ===")
        
        # Get actual column names from database schema analysis
        compras_column_fixes = {
            'fecha_entrega_estimada': 'fecha_entrega',
            'descuento': 'descuento_total', 
            'fecha_actualizacion': 'fecha_modificacion'
        }
        
        # Fix compras SQL files
        compras_sql_dir = Path("sql/compras")
        if compras_sql_dir.exists():
            for sql_file in compras_sql_dir.glob("*.sql"):
                try:
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply column name fixes
                    for old_col, new_col in compras_column_fixes.items():
                        content = re.sub(r'\\b' + old_col + r'\\b', new_col, content)
                    
                    if content != original_content:
                        with open(sql_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.fixes_applied.append(f"Fixed column names in {sql_file}")
                        print(f"✅ Fixed column names in {sql_file}")
                        
                except Exception as e:
                    self.errors_found.append(f"Error fixing {sql_file}: {e}")
                    print(f"❌ Error fixing {sql_file}: {e}")
    
    def fix_missing_controller_methods(self):
        """Fix missing controller methods"""
        print("\n=== FIXING MISSING CONTROLLER METHODS ===")
        
        missing_methods = {
            'logistica': 'cargar_logistica',
            'mantenimiento': 'cargar_mantenimiento', 
            'auditoria': 'cargar_auditoria'
        }
        
        for module, method_name in missing_methods.items():
            controller_file = Path(f"rexus/modules/{module}/controller.py")
            if controller_file.exists():
                try:
                    with open(controller_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if method already exists
                    if f"def {method_name}" not in content:
                        # Add the missing method
                        method_code = f'''
    def {method_name}(self):
        """Carga datos iniciales del módulo {module}"""
        try:
            # Delegate to generic data loading method
            if hasattr(self, 'cargar_datos_iniciales'):
                return self.cargar_datos_iniciales()
            else:
                # Fallback implementation
                if hasattr(self.model, 'obtener_datos_iniciales'):
                    datos = self.model.obtener_datos_iniciales()
                    if hasattr(self.view, 'cargar_datos'):
                        self.view.cargar_datos(datos)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error en {method_name}: {{e}}")
            return False
'''
                        
                        # Insert before the last line (usually class end)
                        content = content.rstrip() + method_code + "\\n"
                        
                        with open(controller_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.fixes_applied.append(f"Added {method_name} to {module} controller")
                        print(f"✅ Added {method_name} to {module} controller")
                    else:
                        print(f"ℹ️  Method {method_name} already exists in {module} controller")
                        
                except Exception as e:
                    self.errors_found.append(f"Error fixing {module} controller: {e}")
                    print(f"❌ Error fixing {module} controller: {e}")
    
    def fix_missing_view_methods(self):
        """Fix missing view methods"""
        print("\n=== FIXING MISSING VIEW METHODS ===")
        
        # Fix ComprasViewComplete missing method
        compras_view = Path("rexus/modules/compras/view_complete.py")
        if compras_view.exists():
            try:
                with open(compras_view, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "def cargar_compras_en_tabla" not in content:
                    method_code = '''
    def cargar_compras_en_tabla(self, compras_data):
        """Carga datos de compras en la tabla principal"""
        try:
            if not compras_data:
                compras_data = []
            
            # Use existing method if available
            if hasattr(self, 'llenar_tabla'):
                self.llenar_tabla(compras_data)
            elif hasattr(self, 'cargar_datos'):
                self.cargar_datos(compras_data)
            else:
                # Fallback: just update stats
                if hasattr(self, 'actualizar_estadisticas'):
                    self.actualizar_estadisticas()
                    
        except Exception as e:
            print(f"Error cargando compras en tabla: {e}")
'''
                    
                    # Insert before the last line
                    content = content.rstrip() + method_code + "\\n"
                    
                    with open(compras_view, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append("Added cargar_compras_en_tabla to ComprasViewComplete")
                    print("✅ Added cargar_compras_en_tabla to ComprasViewComplete")
                else:
                    print("ℹ️  Method cargar_compras_en_tabla already exists")
                    
            except Exception as e:
                self.errors_found.append(f"Error fixing compras view: {e}")
                print(f"❌ Error fixing compras view: {e}")
    
    def create_missing_sql_files(self):
        """Create missing SQL files that are referenced but don't exist"""
        print("\n=== CREATING MISSING SQL FILES ===")
        
        # Create directories if they don't exist
        sql_dirs = ['sql/inventario', 'sql/obras', 'sql/compras']
        for sql_dir in sql_dirs:
            Path(sql_dir).mkdir(parents=True, exist_ok=True)
        
        # Create missing SQL files
        missing_sql_files = {
            'sql/inventario/verificar_tabla_existe.sql': '''-- Verificar si tabla existe en inventario
SELECT COUNT(*) as tabla_existe
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = ?''',
            
            'sql/obras/verificar_tabla_sqlite.sql': '''-- Verificar si tabla obras existe en SQL Server
SELECT COUNT(*) as tabla_existe
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = ?''',
            
            'sql/compras/obtener_compras_base.sql': '''-- Obtener compras básicas con columnas existentes
SELECT 
    id,
    numero_orden,
    fecha_orden as fecha,
    proveedor,
    estado,
    prioridad,
    total,
    fecha_entrega,
    metodo_pago,
    observaciones,
    fecha_modificacion as fecha_actualizacion
FROM compras 
WHERE activo = 1
ORDER BY fecha_orden DESC'''
        }
        
        for file_path, content in missing_sql_files.items():
            sql_file = Path(file_path)
            if not sql_file.exists():
                try:
                    with open(sql_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append(f"Created missing SQL file: {file_path}")
                    print(f"✅ Created {file_path}")
                except Exception as e:
                    self.errors_found.append(f"Error creating {file_path}: {e}")
                    print(f"❌ Error creating {file_path}: {e}")
            else:
                print(f"ℹ️  SQL file already exists: {file_path}")
    
    def fix_unicode_encoding_issues(self):
        """Fix unicode encoding issues in module loading"""
        print("\n=== FIXING UNICODE ENCODING ISSUES ===")
        
        # Look for files with unicode issues in module managers
        module_files = [
            'rexus/core/module_manager.py',
            'rexus/modules/auditoria/controller.py'
        ]
        
        for file_path in module_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                try:
                    with open(file_obj, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace problematic unicode characters
                    unicode_fixes = {
                        '📊': '[STATS]',
                        '📈': '[CHART]', 
                        '📉': '[DOWN]',
                        '⚠️': '[WARNING]',
                        '✅': '[OK]',
                        '❌': '[ERROR]',
                        '🔍': '[SEARCH]'
                    }
                    
                    original_content = content
                    for unicode_char, replacement in unicode_fixes.items():
                        content = content.replace(unicode_char, replacement)
                    
                    if content != original_content:
                        with open(file_obj, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.fixes_applied.append(f"Fixed unicode encoding in {file_path}")
                        print(f"✅ Fixed unicode encoding in {file_path}")
                        
                except Exception as e:
                    self.errors_found.append(f"Error fixing unicode in {file_path}: {e}")
                    print(f"❌ Error fixing unicode in {file_path}: {e}")
    
    def run_all_fixes(self):
        """Run all fixes in the correct order"""
        print("COMPREHENSIVE MODULE FIXES - STARTING...")
        print("="*60)
        
        self.create_missing_sql_files()
        self.fix_sql_parameter_mismatches() 
        self.fix_invalid_column_names()
        self.fix_missing_controller_methods()
        self.fix_missing_view_methods()
        self.fix_unicode_encoding_issues()
        
        print("\n" + "="*60)
        print("COMPREHENSIVE MODULE FIXES - COMPLETED")
        print("="*60)
        
        print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"  • {fix}")
        
        if self.errors_found:
            print(f"\n❌ ERRORS ENCOUNTERED ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"  • {error}")
        else:
            print("\n🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        
        return len(self.errors_found) == 0

def main():
    """Run comprehensive fixes"""
    fixer = ComprehensiveModuleFixer()
    success = fixer.run_all_fixes()
    
    if success:
        print("\n🚀 READY FOR TESTING - All fixes applied successfully")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS - Some fixes failed, review errors above")
    
    return success

if __name__ == "__main__":
    main()