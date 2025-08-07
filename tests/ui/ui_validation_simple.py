#!/usr/bin/env python3
"""
UI Consistency Validator Simple - Rexus.app v2.0.0

Valida la consistencia UI sin caracteres especiales.
"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def validate_ui_consistency():
    """Valida consistencia UI de forma simplificada"""
    
    print("UI CONSISTENCY VALIDATION - REXUS.APP")
    print("=" * 50)
    
    # Buscar archivos view.py
    modules_dir = project_root / "rexus" / "modules"
    view_files = list(modules_dir.rglob("view.py"))
    
    print(f"\nArchivos view.py encontrados: {len(view_files)}")
    
    # Validar componentes
    standard_components = {
        'QPushButton': 'RexusButton',
        'QLabel': 'RexusLabel', 
        'QLineEdit': 'RexusLineEdit',
        'QComboBox': 'RexusComboBox',
        'QTableWidget': 'RexusTable'
    }
    
    inconsistencies = []
    style_violations = []
    
    for view_file in view_files:
        try:
            content = view_file.read_text(encoding='utf-8')
            
            # Verificar componentes
            for qt_comp, rexus_comp in standard_components.items():
                if qt_comp in content and rexus_comp not in content:
                    inconsistencies.append({
                        'file': view_file.name,
                        'component': qt_comp,
                        'suggested': rexus_comp
                    })
            
            # Verificar estilos inline
            style_patterns = [r'setStyleSheet\(["\'].*["\']']
            for pattern in style_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    style_violations.append({
                        'file': view_file.name,
                        'violations': len(matches)
                    })
                    
        except Exception as e:
            print(f"Error leyendo {view_file.name}: {e}")
    
    # Resultados
    print(f"\n--- RESULTADOS ---")
    print(f"Componentes inconsistentes: {len(inconsistencies)}")
    print(f"Archivos con estilos inline: {len(style_violations)}")
    
    if inconsistencies:
        print(f"\n--- COMPONENTES A MIGRAR ---")
        for inc in inconsistencies[:5]:  # Mostrar primeros 5
            print(f"  {inc['file']}: {inc['component']} -> {inc['suggested']}")
    
    if style_violations:
        print(f"\n--- ESTILOS INLINE ENCONTRADOS ---")
        for viol in style_violations[:5]:
            print(f"  {viol['file']}: {viol['violations']} violaciones")
    
    # Estado general
    total_issues = len(inconsistencies) + len(style_violations)
    
    if total_issues == 0:
        print(f"\nESTADO: EXCELENTE - UI Completamente Consistente")
        return 0
    elif total_issues <= 10:
        print(f"\nESTADO: BUENO - Pocas inconsistencias ({total_issues} problemas)")
        return 1
    else:
        print(f"\nESTADO: NECESITA MEJORAS - {total_issues} problemas encontrados")
        return 2


if __name__ == "__main__":
    sys.exit(validate_ui_consistency())