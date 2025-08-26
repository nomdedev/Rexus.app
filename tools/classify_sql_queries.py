#!/usr/bin/env python3
"""
Clasificador de queries SQL por criticidad y tipo
Separa queries críticas de las que son solo strings informativos
"""

import re
import json
from pathlib import Path

class SQLQueryClassifier:
    def __init__(self):
        # Patrones para queries críticas (que realmente ejecutan SQL)
        self.critical_patterns = [
            r'cursor\.execute\s*\([^)]*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            r'\.execute\s*\([^)]*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            r'execute_query\s*\([^)]*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            r'query\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\'](?=.*execute)',
            r'sql\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\'](?=.*execute)',
        ]
        
        # Patrones que son solo strings/mensajes (no críticos)
        self.non_critical_patterns = [
            r'logger\.',  # Log messages
            r'print\(',   # Print statements  
            r'\.error\(',  # Error messages
            r'\.info\(',   # Info messages
            r'\.warning\(', # Warning messages
            r'f["\'].*{.*}.*Error.*["\']', # F-string error messages
            r'\.join\(',  # String joins
            r'setText\(', # UI text setting
            r'setObjectName\(', # UI object naming
            r'setStyleSheet\(', # CSS/Styles
            r'setUrl\(', # URLs
        ]
        
        # Keywords para identificar operaciones SQL reales
        self.sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 
            'CREATE', 'DROP', 'ALTER', 'FROM', 'WHERE', 
            'JOIN', 'VALUES', 'SET'
        ]

    def is_critical_sql(self, line: str, sql_content: str) -> dict:
        """Determina si es una query SQL crítica que necesita migración"""
        
        # Check if it's obviously non-critical
        for pattern in self.non_critical_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return {'critical': False, 'reason': 'Non-critical pattern matched'}
        
        # Check if it matches critical execution patterns
        for pattern in self.critical_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Verify it has actual SQL keywords
                keyword_count = sum(1 for kw in self.sql_keywords if kw in sql_content.upper())
                if keyword_count >= 2:
                    return {'critical': True, 'reason': 'Critical execution pattern with SQL keywords', 'keywords': keyword_count}
        
        # Check for string interpolation in SQL (potential SQL injection risk)
        if any(char in sql_content for char in ['{', '%s', '%d']) and any(kw in sql_content.upper() for kw in self.sql_keywords):
            return {'critical': True, 'reason': 'SQL with string interpolation (injection risk)'}
        
        # Check for basic SQL structure
        sql_upper = sql_content.upper()
        has_sql_structure = (
            ('SELECT' in sql_upper and 'FROM' in sql_upper) or
            ('INSERT' in sql_upper and 'INTO' in sql_upper) or
            ('UPDATE' in sql_upper and 'SET' in sql_upper) or
            ('DELETE' in sql_upper and 'FROM' in sql_upper)
        )
        
        if has_sql_structure and len(sql_content) > 20:
            return {'critical': True, 'reason': 'Complete SQL statement structure'}
        
        return {'critical': False, 'reason': 'Does not match critical criteria'}

    def analyze_report(self, report_file: str) -> dict:
        """Analiza el reporte exhaustivo y clasifica queries"""
        
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        classification = {
            'critical_queries': 0,
            'non_critical_queries': 0,
            'modules': {},
            'summary': {
                'high_priority': [],  # Módulos con muchas queries críticas
                'medium_priority': [],
                'low_priority': []
            }
        }
        
        for module_name, module_data in data['modules'].items():
            module_analysis = {
                'critical_files': {},
                'critical_count': 0,
                'non_critical_count': 0,
                'total_queries': module_data['total_queries']
            }
            
            for file_path, file_data in module_data['files'].items():
                critical_queries = []
                
                for query in file_data['queries']:
                    analysis = self.is_critical_sql(query['context'], query['sql'])
                    
                    if analysis['critical']:
                        critical_queries.append({
                            'line': query['line'],
                            'sql': query['sql'],
                            'context': query['context'],
                            'reason': analysis['reason']
                        })
                        classification['critical_queries'] += 1
                        module_analysis['critical_count'] += 1
                    else:
                        classification['non_critical_queries'] += 1
                        module_analysis['non_critical_count'] += 1
                
                if critical_queries:
                    module_analysis['critical_files'][file_path] = {
                        'critical_queries': critical_queries,
                        'count': len(critical_queries)
                    }
            
            classification['modules'][module_name] = module_analysis
            
            # Classify module priority
            if module_analysis['critical_count'] > 10:
                classification['summary']['high_priority'].append(module_name)
            elif module_analysis['critical_count'] > 3:
                classification['summary']['medium_priority'].append(module_name)
            elif module_analysis['critical_count'] > 0:
                classification['summary']['low_priority'].append(module_name)
        
        return classification

    def generate_priority_report(self, classification: dict):
        """Genera reporte de prioridades para migración"""
        
        print("=== CLASIFICACIÓN DE QUERIES SQL POR CRITICIDAD ===")
        print(f"Queries críticas (requieren migración): {classification['critical_queries']}")
        print(f"Queries no críticas (strings/mensajes): {classification['non_critical_queries']}")
        
        total = classification['critical_queries'] + classification['non_critical_queries']
        critical_percent = (classification['critical_queries'] / total * 100) if total > 0 else 0
        print(f"Porcentaje crítico: {critical_percent:.1f}%")
        
        print(f"\n=== PRIORIDADES DE MIGRACIÓN ===")
        
        # High priority modules
        if classification['summary']['high_priority']:
            print(f"\n*** ALTA PRIORIDAD (>10 queries críticas) ***")
            for module in classification['summary']['high_priority']:
                module_data = classification['modules'][module]
                print(f"  - {module}: {module_data['critical_count']} queries críticas")
                
                # Show most critical files
                sorted_files = sorted(
                    module_data['critical_files'].items(), 
                    key=lambda x: x[1]['count'], 
                    reverse=True
                )
                for file_path, file_info in sorted_files[:2]:  # Top 2 files
                    print(f"    • {file_path}: {file_info['count']} queries")
        
        # Medium priority modules
        if classification['summary']['medium_priority']:
            print(f"\n*** PRIORIDAD MEDIA (3-10 queries críticas) ***")
            for module in classification['summary']['medium_priority']:
                module_data = classification['modules'][module]
                print(f"  - {module}: {module_data['critical_count']} queries críticas")
        
        # Low priority modules
        if classification['summary']['low_priority']:
            print(f"\n*** PRIORIDAD BAJA (1-3 queries críticas) ***")
            for module in classification['summary']['low_priority']:
                module_data = classification['modules'][module]
                print(f"  - {module}: {module_data['critical_count']} queries críticas")
        
        # Save detailed classification
        with open('tools/sql_classification.json', 'w', encoding='utf-8') as f:
            json.dump(classification, f, indent=2, ensure_ascii=False)
        
        print(f"\nClasificación detallada guardada en: tools/sql_classification.json")

def main():
    classifier = SQLQueryClassifier()
    
    # Analyze the exhaustive report
    classification = classifier.analyze_report('tools/exhaustive_sql_report.json')
    classifier.generate_priority_report(classification)
    
    return classification['critical_queries']

if __name__ == "__main__":
    critical_count = main()
    print(f"\n*** {critical_count} QUERIES CRÍTICAS REQUIEREN MIGRACIÓN ***")