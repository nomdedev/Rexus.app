#!/usr/bin/env python3
"""
AUDITORÍA COMPLETA DE ARCHIVOS DUPLICADOS - Rexus.app
Detecta, analiza y limpia archivos duplicados identificados
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict

class DuplicateFileAnalyzer:
    """Analizador y limpiador de archivos duplicados."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.duplicates_found = []
        self.to_delete = []
        
    def get_file_hash(self, file_path):
        """Obtiene hash MD5 de un archivo."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def analyze_duplicates(self):
        """Analiza archivos duplicados específicos identificados."""
        
        print("🔍 ANÁLISIS DE ARCHIVOS DUPLICADOS DETECTADOS")
        print("=" * 60)
        
        # Archivos duplicados críticos identificados
        critical_duplicates = [
            # main.py duplicados
            {
                'files': ['main.py', 'main_clean.py'],
                'keep': 'main.py',
                'reason': 'main.py es el punto de entrada principal'
            },
            
            # Scripts en tools/ y scripts/tools/
            {
                'files': ['tools/cleanup_duplicates.py', 'scripts/tools/cleanup_duplicates.py'],
                'keep': 'scripts/tools/cleanup_duplicates.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/aplicar_estilos_premium.py', 'scripts/tools/aplicar_estilos_premium.py'],
                'keep': 'scripts/tools/aplicar_estilos_premium.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/expert_audit.py', 'scripts/tools/expert_audit.py'],
                'keep': 'scripts/tools/expert_audit.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/fix_code_quality.py', 'scripts/tools/fix_code_quality.py'],
                'keep': 'scripts/tools/fix_code_quality.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/fix_syntax_errors.py', 'scripts/tools/fix_syntax_errors.py'],
                'keep': 'scripts/tools/fix_syntax_errors.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/limpiar_emojis_unicode.py', 'scripts/tools/limpiar_emojis_unicode.py'],
                'keep': 'scripts/tools/limpiar_emojis_unicode.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/migrate_prints_batch.py', 'scripts/tools/migrate_prints_batch.py'],
                'keep': 'scripts/tools/migrate_prints_batch.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/quick_audit.py', 'scripts/tools/quick_audit.py'],
                'keep': 'scripts/tools/quick_audit.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/reporte_optimizacion_completa.py', 'scripts/tools/reporte_optimizacion_completa.py'],
                'keep': 'scripts/tools/reporte_optimizacion_completa.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            {
                'files': ['tools/verify_fixes.py', 'scripts/tools/verify_fixes.py'],
                'keep': 'scripts/tools/verify_fixes.py',
                'reason': 'scripts/tools es la ubicación estándar'
            },
            
            # Duplicados core vs utils
            {
                'files': ['rexus/core/cache_manager.py', 'rexus/utils/cache_manager.py'],
                'keep': 'rexus/utils/cache_manager.py',
                'reason': 'utils es la ubicación correcta para herramientas'
            },
            {
                'files': ['rexus/core/query_optimizer.py', 'rexus/utils/query_optimizer.py'],
                'keep': 'rexus/utils/query_optimizer.py',
                'reason': 'utils es la ubicación correcta para optimizadores'
            },
            {
                'files': ['rexus/core/security.py', 'rexus/utils/security.py'],
                'keep': 'rexus/utils/security.py',
                'reason': 'utils es la ubicación correcta para utilidades de seguridad'
            },
            {
                'files': ['rexus/core/sql_query_manager.py', 'rexus/utils/sql_query_manager.py'],
                'keep': 'rexus/utils/sql_query_manager.py',
                'reason': 'utils es la ubicación correcta para managers'
            },
        ]
        
        return self.process_critical_duplicates(critical_duplicates)
    
    def process_critical_duplicates(self, critical_duplicates):
        """Procesa duplicados críticos identificados."""
        
        for duplicate_group in critical_duplicates:
            files = duplicate_group['files']
            keep_file = duplicate_group['keep']
            reason = duplicate_group['reason']
            
            print(f"\\n📁 Grupo: {', '.join(files)}")
            print(f"✅ Mantener: {keep_file}")
            print(f"📝 Razón: {reason}")
            
            # Verificar que los archivos existen
            existing_files = []
            for file_path in files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    existing_files.append(file_path)
            
            if len(existing_files) > 1:
                # Comparar contenido de archivos si existen múltiples
                hashes = {}
                for file_path in existing_files:
                    full_path = self.project_root / file_path
                    file_hash = self.get_file_hash(full_path)
                    hashes[file_path] = file_hash
                
                # Determinar archivos a eliminar
                for file_path in existing_files:
                    if file_path != keep_file:
                        full_path = self.project_root / file_path
                        
                        # Verificar si son idénticos o diferentes
                        keep_hash = hashes.get(keep_file)
                        current_hash = hashes.get(file_path)
                        
                        if keep_hash == current_hash:
                            print(f"🗑️ Eliminar: {file_path} (idéntico)")
                            self.to_delete.append(full_path)
                        else:
                            print(f"⚠️ Diferente: {file_path} (revisar manualmente)")
                            
            elif len(existing_files) == 1:
                print(f"ℹ️ Solo existe: {existing_files[0]}")
            else:
                print(f"❌ Ningún archivo existe")
                
        return len(self.to_delete)
    
    def execute_cleanup(self, dry_run=True):
        """Ejecuta la limpieza de archivos duplicados."""
        
        if not self.to_delete:
            print("\\n✅ No hay archivos para eliminar")
            return
            
        print(f"\\n🗑️ ARCHIVOS A ELIMINAR ({len(self.to_delete)}):")
        print("-" * 40)
        
        for file_path in self.to_delete:
            print(f"  - {file_path}")
            
        if dry_run:
            print(f"\\n⚠️ MODO DRY-RUN: No se eliminaron archivos")
            print("Para ejecutar la limpieza real, usar: python cleanup_duplicates.py --execute")
        else:
            print(f"\\n🔥 EJECUTANDO LIMPIEZA...")
            deleted_count = 0
            
            for file_path in self.to_delete:
                try:
                    file_path.unlink()
                    print(f"✅ Eliminado: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Error eliminando {file_path}: {e}")
            
            print(f"\\n🎉 Limpieza completada: {deleted_count} archivos eliminados")

def main():
    """Función principal."""
    import sys
    
    analyzer = DuplicateFileAnalyzer()
    
    print("🧹 LIMPIEZA DE ARCHIVOS DUPLICADOS - REXUS.APP")
    print("=" * 60)
    
    # Analizar duplicados
    duplicates_count = analyzer.analyze_duplicates()
    
    # Determinar modo de ejecución
    execute_mode = '--execute' in sys.argv
    
    # Ejecutar limpieza
    analyzer.execute_cleanup(dry_run=not execute_mode)
    
    print(f"\\n📊 RESUMEN:")
    print(f"  - Duplicados detectados: {duplicates_count}")
    print(f"  - Modo: {'EJECUCIÓN' if execute_mode else 'DRY-RUN'}")

if __name__ == '__main__':
    main()
