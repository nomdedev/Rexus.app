#!/usr/bin/env python3
"""
Migrador inteligente de SQL que filtra falsos positivos y solo migra queries reales
Se enfoca en cursor.execute(), execute() y queries SQL reales

Fecha: 26/08/2025
"""

import os
import re
from pathlib import Path
import json

class SmartSQLMigrator:
    def __init__(self):
        # Patrones más específicos para SQL real
        self.real_sql_patterns = [
            r'cursor\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'query\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'sql\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
        ]
        
        # Excluir estos patrones (falsos positivos)
        self.exclude_patterns = [
            r'logger\.',  # Log messages
            r'print\(',   # Print statements
            r'\.error\(', # Error messages
            r'\.info\(',  # Info messages
            r'\.warning\(', # Warning messages
            r'f["\']Error.*', # Error messages with f-strings
            r'#.*',  # Comments
            r'""".*?"""',  # Docstrings
            r"'''.*?'''",  # Docstrings
            r'sql_manager\.get_query',  # Already migrated
            r'file.*\.sql',  # SQL file references
        ]
        
        self.migrations_applied = 0
        self.files_processed = 0

    def is_legitimate_sql(self, line: str, sql_content: str) -> bool:
        """Check if this is a legitimate SQL query worth migrating"""
        # Exclude obvious false positives
        for exclude in self.exclude_patterns:
            if re.search(exclude, line, re.IGNORECASE):
                return False
        
        # Check for SQL keywords - must have at least 2
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'UPDATE', 'SET', 'DELETE', 'JOIN']
        keyword_count = sum(1 for kw in sql_keywords if kw in sql_content.upper())
        
        if keyword_count < 2:
            return False
        
        # Must be longer than basic queries
        if len(sql_content.strip()) < 15:
            return False
            
        # Should not be just error messages
        if any(word in sql_content.lower() for word in ['error', 'exception', 'failed', 'problema']):
            return False
            
        return True

    def extract_legitimate_sql(self, file_path: Path) -> list:
        """Extract only legitimate SQL queries from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        legitimate_queries = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.real_sql_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    sql_content = match.group(1).strip()
                    
                    if self.is_legitimate_sql(line, sql_content):
                        legitimate_queries.append({
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'sql_content': sql_content,
                            'full_match': match.group(0)
                        })
                        print(f"  VALID SQL at line {line_num}: {sql_content[:60]}...")
        
        return legitimate_queries

    def determine_sql_filename(self, sql_content: str, module_name: str, index: int) -> str:
        """Determine appropriate filename for SQL query"""
        sql_upper = sql_content.upper()
        
        # Try to extract table name
        table_name = ""
        table_match = re.search(r'FROM\s+(\w+)', sql_upper)
        if table_match:
            table_name = f"_{table_match.group(1).lower()}"
        
        # Determine operation type
        if 'SELECT' in sql_upper:
            if 'COUNT' in sql_upper:
                return f"count{table_name}_{index}"
            elif 'JOIN' in sql_upper:
                return f"select{table_name}_with_joins_{index}"
            else:
                return f"select{table_name}_{index}"
        elif 'INSERT' in sql_upper:
            return f"insert{table_name}_{index}"
        elif 'UPDATE' in sql_upper:
            return f"update{table_name}_{index}"
        elif 'DELETE' in sql_upper:
            return f"delete{table_name}_{index}"
        else:
            return f"query{table_name}_{index}"

    def migrate_file_sql(self, file_path: Path, module_name: str) -> dict:
        """Migrate SQL from a specific file"""
        print(f"\nProcessing: {file_path.relative_to(Path('rexus'))}")
        
        queries = self.extract_legitimate_sql(file_path)
        if not queries:
            return {'queries_migrated': 0, 'files': []}
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create SQL directory
        sql_dir = Path(f'sql/{module_name}')
        sql_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        modified_content = content
        migrated_files = []
        
        # Process each query
        for i, query in enumerate(queries):
            sql_filename = self.determine_sql_filename(query['sql_content'], module_name, i + 1)
            sql_file_path = sql_dir / f"{sql_filename}.sql"
            
            # Write SQL file
            with open(sql_file_path, 'w', encoding='utf-8') as f:
                f.write(f"-- {sql_filename}.sql\n")
                f.write(f"-- Extracted from: {file_path.relative_to(Path('.'))}\n")
                f.write(f"-- Line: {query['line_number']}\n\n")
                f.write(query['sql_content'])
            
            migrated_files.append(str(sql_file_path))
            
            # Replace in code - be more careful with replacements
            old_pattern = query['full_match']
            new_code = f"self.sql_manager.ejecutar_consulta_archivo('sql/{module_name}/{sql_filename}.sql', params)"
            
            # Only replace the first occurrence to be safe
            modified_content = modified_content.replace(old_pattern, new_code, 1)
            print(f"    -> Created: {sql_filename}.sql")
        
        # Add imports if needed
        if queries and 'SQLQueryManager' not in modified_content:
            import_line = "from rexus.utils.sql_query_manager import SQLQueryManager\n"
            
            # Find a good place to add the import
            lines = modified_content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.startswith('from rexus.') and not import_added:
                    lines.insert(i + 1, import_line.strip())
                    import_added = True
                    break
            
            if not import_added:
                # Add after existing imports
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        continue
                    else:
                        lines.insert(i, import_line.strip())
                        break
            
            modified_content = '\n'.join(lines)
        
        # Add sql_manager initialization if needed
        if queries and 'self.sql_manager' not in modified_content:
            init_pattern = r'(def __init__\(self[^)]*\):[^\n]*\n)'
            if re.search(init_pattern, modified_content):
                modified_content = re.sub(
                    init_pattern,
                    r'\1        self.sql_manager = SQLQueryManager()\n',
                    modified_content, count=1
                )
        
        # Write modified file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        self.migrations_applied += len(queries)
        return {'queries_migrated': len(queries), 'files': migrated_files}

    def migrate_module(self, module_path: Path) -> dict:
        """Migrate all SQL in a module"""
        module_name = module_path.name
        print(f"\n=== MIGRATING MODULE: {module_name.upper()} ===")
        
        results = {
            'module_name': module_name,
            'total_queries': 0,
            'files_processed': 0,
            'migrated_files': []
        }
        
        # Find Python files
        for py_file in module_path.glob('**/*.py'):
            if '__pycache__' in str(py_file) or py_file.name.startswith('__'):
                continue
            
            self.files_processed += 1
            result = self.migrate_file_sql(py_file, module_name)
            
            if result['queries_migrated'] > 0:
                results['total_queries'] += result['queries_migrated']
                results['files_processed'] += 1
                results['migrated_files'].extend(result['files'])
        
        return results

    def run_migration(self):
        """Run complete migration process"""
        print("=== SMART SQL MIGRATION PROCESS ===")
        print("Only migrating legitimate SQL queries...")
        
        all_results = []
        
        # Migrate modules
        modules_path = Path('rexus/modules')
        if modules_path.exists():
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('_'):
                    result = self.migrate_module(module_dir)
                    if result['total_queries'] > 0:
                        all_results.append(result)
        
        # Migrate core and utils if needed
        for core_dir in ['rexus/core', 'rexus/utils']:
            core_path = Path(core_dir)
            if core_path.exists():
                # Treat as module for migration
                result = self.migrate_module(core_path)
                if result['total_queries'] > 0:
                    all_results.append(result)
        
        # Generate summary
        print(f"\n=== MIGRATION COMPLETE ===")
        print(f"Files processed: {self.files_processed}")
        print(f"Legitimate SQL queries migrated: {self.migrations_applied}")
        print(f"Modules affected: {len(all_results)}")
        
        for result in all_results:
            print(f"  - {result['module_name']}: {result['total_queries']} queries")
        
        # Save results
        with open('tools/migration_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: tools/migration_results.json")
        print(f"Backup files created with .backup extension")
        
        return all_results

def main():
    migrator = SmartSQLMigrator()
    results = migrator.run_migration()
    
    if migrator.migrations_applied > 0:
        print(f"\n*** MIGRATION SUCCESSFUL ***")
        print(f"Remember to test the application to ensure all queries work correctly!")
    else:
        print(f"\n*** NO LEGITIMATE SQL FOUND ***")
        print(f"All SQL queries appear to already be externalized!")

if __name__ == "__main__":
    main()