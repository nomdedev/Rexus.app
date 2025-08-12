"""
SQL Script Updater for Consolidated Database Structure - Rexus.app v2.0.0

Updates existing SQL scripts to use the new consolidated table structure.
Creates updated versions of scripts while preserving originals.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class SQLScriptUpdater:
    """Updates SQL scripts to use consolidated table structure."""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "scripts" / "sql" / "legacy_backup"
        self.updated_dir = self.project_root / "scripts" / "sql" / "consolidated"
        
        # Table mapping: legacy -> consolidated
        self.table_mappings = {
            # Product tables consolidation
            "inventario_perfiles": "productos",
            "herrajes": "productos", 
            "vidrios": "productos",
            "materiales": "productos",
            
            # Movement tables consolidation
            "movimientos_stock": "movimientos_inventario",
            "historial_herrajes": "movimientos_inventario",
            "movimientos_vidrios": "movimientos_inventario",
            
            # Order tables consolidation
            "pedidos": "pedidos_consolidado",
            "pedidos_detalle": "pedidos_detalle_consolidado",
            "pedidos_herrajes": "pedidos_consolidado",
            "pedidos_vidrios": "pedidos_consolidado",
            
            # Assignment tables consolidation
            "herrajes_obra": "productos_obra",
            "vidrios_obra": "productos_obra", 
            "materiales_por_obra": "productos_obra",
            
            # Inventory tables consolidation
            "herrajes_inventario": "productos",
            "vidrios_inventario": "productos",
            "inventario_items": "productos"
        }
        
        # Column mappings for specific tables
        self.column_mappings = {
            "productos": {
                # From inventario_perfiles
                "tipo": "categoria",
                "acabado": "subcategoria", 
                
                # From herrajes  
                "categoria": "subcategoria",
                
                # From vidrios
                "tipo": "subcategoria",
                "precio_m2": "precio_unitario",
                "espesor": "JSON_VALUE(propiedades_especiales, '$.espesor')",
                
                # Common mappings
                "stock": "stock_actual",
                "precio": "precio_unitario"
            },
            
            "productos_obra": {
                # From herrajes_obra
                "herraje_id": "producto_id",
                "cantidad_requerida": "cantidad_requerida",
                "cantidad_pedida": "cantidad_asignada",
                
                # From vidrios_obra  
                "vidrio_id": "producto_id",
                "metros_cuadrados_requeridos": "cantidad_requerida",
                "metros_cuadrados_pedidos": "cantidad_asignada",
                
                # From materiales_por_obra
                "material_id": "producto_id"
            },
            
            "pedidos_consolidado": {
                # From pedidos_herrajes
                "herraje_cantidad": "cantidad_solicitada",
                
                # From pedidos_vidrios
                "metros_cuadrados": "cantidad_solicitada"
            }
        }
        
        # Additional WHERE clauses for category filtering
        self.category_filters = {
            "productos": {
                "herrajes_context": "AND categoria = 'HERRAJE'",
                "vidrios_context": "AND categoria = 'VIDRIO'", 
                "perfiles_context": "AND categoria = 'PERFIL'",
                "materiales_context": "AND categoria = 'MATERIAL'"
            }
        }
        
    def create_directories(self):
        """Create necessary directories for backup and updated scripts."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.updated_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Created directories:")
        print(f"  - Backup: {self.backup_dir}")
        print(f"  - Updated: {self.updated_dir}")
        
    def find_sql_scripts(self):
        """Find all SQL scripts in the project."""
        sql_files = []
        
        # Search in common SQL directories
        search_dirs = [
            self.project_root / "scripts" / "sql",
            self.project_root / "src" / "modules",
            self.project_root / "database"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                sql_files.extend(search_dir.rglob("*.sql"))
                
        return sql_files
        
    def backup_script(self, sql_file):
        """Create backup of original SQL script."""
        relative_path = sql_file.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(sql_file, backup_path)
        return backup_path
        
    def update_table_names(self, sql_content):
        """Update table names in SQL content."""
        updated_content = sql_content
        
        for legacy_table, consolidated_table in self.table_mappings.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(legacy_table) + r'\b'
            updated_content = re.sub(pattern, consolidated_table, updated_content, flags=re.IGNORECASE)
            
        return updated_content
        
    def update_column_names(self, sql_content, context_table=None):
        """Update column names based on table context."""
        updated_content = sql_content
        
        if context_table and context_table in self.column_mappings:
            mappings = self.column_mappings[context_table]
            
            for old_column, new_column in mappings.items():
                # Update column references
                pattern = r'\b' + re.escape(old_column) + r'\b'
                updated_content = re.sub(pattern, new_column, updated_content, flags=re.IGNORECASE)
                
        return updated_content
        
    def add_category_filters(self, sql_content):
        """Add category filters where appropriate."""
        updated_content = sql_content
        
        # Detect context and add appropriate filters
        if re.search(r'\bherrajes?\b', sql_content, re.IGNORECASE):
            # Add HERRAJE category filter
            if 'WHERE' in updated_content.upper():
                updated_content = re.sub(
                    r'(WHERE.*?)(\s+ORDER\s+BY|\s+GROUP\s+BY|\s*$)', 
                    r'\1 AND categoria = \'HERRAJE\'\2',
                    updated_content, 
                    flags=re.IGNORECASE | re.DOTALL
                )
            else:
                updated_content = re.sub(
                    r'(FROM\s+productos\s*)', 
                    r'\1WHERE categoria = \'HERRAJE\' ',
                    updated_content,
                    flags=re.IGNORECASE
                )
                
        elif re.search(r'\bvidrios?\b', sql_content, re.IGNORECASE):
            # Add VIDRIO category filter  
            if 'WHERE' in updated_content.upper():
                updated_content = re.sub(
                    r'(WHERE.*?)(\s+ORDER\s+BY|\s+GROUP\s+BY|\s*$)',
                    r'\1 AND categoria = \'VIDRIO\'\2', 
                    updated_content,
                    flags=re.IGNORECASE | re.DOTALL
                )
            else:
                updated_content = re.sub(
                    r'(FROM\s+productos\s*)',
                    r'\1WHERE categoria = \'VIDRIO\' ',
                    updated_content, 
                    flags=re.IGNORECASE
                )
                
        return updated_content
        
    def add_consolidation_header(self, sql_content, original_file):
        """Add header indicating script has been updated for consolidation."""
        header = f"""-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: {original_file.name}
-- Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- 
-- CAMBIOS REALIZADOS:
-- - Tablas actualizadas a estructura consolidada
-- - Columnas mapeadas a nuevos nombres
-- - Filtros de categoría agregados donde corresponde
-- 
-- TABLAS CONSOLIDADAS UTILIZADAS:
-- - productos (reemplaza inventario_perfiles, herrajes, vidrios, materiales)
-- - movimientos_inventario (reemplaza movimientos_stock, historial_*)
-- - pedidos_consolidado (reemplaza pedidos, pedidos_herrajes, pedidos_vidrios)
-- - productos_obra (reemplaza *_obra tables)
-- =====================================================

"""
        return header + sql_content
        
    def update_script(self, sql_file):
        """Update a single SQL script."""
        try:
            # Read original content
            with open(sql_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # Skip if already consolidated
            if 'SCRIPT CONSOLIDADO' in original_content:
                print(f"  [SKIP] {sql_file.name} - Already consolidated")
                return None, "Already consolidated"
                
            # Create backup
            backup_path = self.backup_script(sql_file)
            
            # Update content
            updated_content = original_content
            
            # 1. Update table names
            updated_content = self.update_table_names(updated_content)
            
            # 2. Update column names (detect main table context)
            main_table = self.detect_main_table(updated_content)
            if main_table:
                updated_content = self.update_column_names(updated_content, main_table)
                
            # 3. Add category filters
            updated_content = self.add_category_filters(updated_content)
            
            # 4. Add consolidation header
            updated_content = self.add_consolidation_header(updated_content, sql_file)
            
            # Save updated script
            relative_path = sql_file.relative_to(self.project_root)
            updated_path = self.updated_dir / relative_path
            updated_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(updated_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            return updated_path, "Updated successfully"
            
        except Exception as e:
            return None, f"Error: {str(e)}"
            
    def detect_main_table(self, sql_content):
        """Detect the main table being used in the SQL script."""
        # Look for FROM clauses to determine main table
        for table_name in ["productos", "productos_obra", "pedidos_consolidado", "movimientos_inventario"]:
            if re.search(rf'\bFROM\s+{table_name}\b', sql_content, re.IGNORECASE):
                return table_name
        return None
        
    def process_all_scripts(self):
        """Process all SQL scripts in the project."""
        print("[INFO] Starting SQL script consolidation update...")
        
        # Create directories
        self.create_directories()
        
        # Find all SQL scripts
        sql_files = self.find_sql_scripts()
        print(f"[INFO] Found {len(sql_files)} SQL scripts to process")
        
        if not sql_files:
            print("[WARNING] No SQL scripts found to process")
            return
            
        # Process each script
        results = []
        for sql_file in sql_files:
            print(f"\n[PROCESSING] {sql_file.relative_to(self.project_root)}")
            updated_path, status = self.update_script(sql_file)
            
            results.append({
                'original': sql_file,
                'updated': updated_path,
                'status': status
            })
            
            print(f"  [RESULT] {status}")
            
        # Generate summary
        self.generate_summary(results)
        
    def generate_summary(self, results):
        """Generate summary report of script updates."""
        print("\n" + "="*70)
        print("SQL SCRIPT UPDATE SUMMARY")
        print("="*70)
        
        successful = [r for r in results if r['updated'] is not None]
        skipped = [r for r in results if r['status'] == 'Already consolidated']
        failed = [r for r in results if r['updated'] is None and r['status'] != 'Already consolidated']
        
        print(f"Total scripts processed: {len(results)}")
        print(f"Successfully updated: {len(successful)}")
        print(f"Skipped (already consolidated): {len(skipped)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            print(f"\n[SUCCESS] Updated scripts saved to: {self.updated_dir}")
            
        if failed:
            print("\n[FAILURES]")
            for result in failed:
                print(f"  - {result['original'].name}: {result['status']}")
                
        # Create summary file
        summary_file = self.updated_dir / "UPDATE_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"""# SQL Script Update Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total scripts processed: {len(results)}
- Successfully updated: {len(successful)}
- Skipped (already consolidated): {len(skipped)}
- Failed: {len(failed)}

## Updated Scripts
""")
            for result in successful:
                f.write(f"- {result['original'].name} → {result['updated'].name}\n")
                
            if failed:
                f.write(f"\n## Failed Scripts\n")
                for result in failed:
                    f.write(f"- {result['original'].name}: {result['status']}\n")
                    
        print(f"\n[INFO] Summary report saved to: {summary_file}")
        print("\n[RECOMMENDATION] Review updated scripts before deploying to production")


def main():
    """Main execution."""
    print("SQL Script Updater for Consolidated Database Structure")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    print(f"Project root: {project_root}")
    
    # Initialize updater
    updater = SQLScriptUpdater(project_root)
    
    # Process all scripts
    updater.process_all_scripts()
    
    print("\n[COMPLETED] SQL script update process finished")


if __name__ == "__main__":
    main()