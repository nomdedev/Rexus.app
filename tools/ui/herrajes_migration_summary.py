#!/usr/bin/env python3
"""
Herrajes Module UI Migration Summary Script
Validates the successful migration of Herrajes module to Rexus UI framework.
"""

import re
import os

def analyze_herrajes_migration():
    """Analyzes the Herrajes module migration status."""
    
    file_path = "rexus/modules/herrajes/view.py"
    
    if not os.path.exists(file_path):
        print("❌ ERROR: Herrajes view.py file not found!")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count legacy components
    legacy_patterns = [
        r'QPushButton\(',
        r'QLineEdit\(',
        r'QComboBox\(',
        r'QGroupBox\(',
        r'QFrame\(',
        r'QLabel\(',
        r'QWidget\(',
        r'QVBoxLayout\(',
        r'QHBoxLayout\(',
        r'setStyleSheet\s*\(',
    ]
    
    legacy_count = 0
    legacy_found = []
    
    for pattern in legacy_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        count = len(matches)
        if count > 0:
            legacy_count += count
            legacy_found.append(f"{pattern}: {count}")
    
    # Count Rexus components
    rexus_patterns = [
        r'RexusButton\(',
        r'RexusLabel\(',
        r'RexusLineEdit\(',
        r'RexusComboBox\(',
        r'RexusTable\(',
        r'RexusGroupBox\(',
        r'RexusFrame\(',
        r'RexusTabWidget\(',
        r'RexusLayoutHelper\.',
        r'StandardComponents\.',
    ]
    
    rexus_count = 0
    rexus_found = []
    
    for pattern in rexus_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        count = len(matches)
        if count > 0:
            rexus_count += count
            rexus_found.append(f"{pattern}: {count}")
    
    # Count lines of code
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    
    # Generate summary
    print("="*60)
    print("[HERRAJES] MODULE UI MIGRATION SUMMARY")
    print("="*60)
    print()
    
    print(f"[FILE] {file_path}")
    print(f"[LINES] Total: {total_lines}, Code: {code_lines}")
    print()
    
    print("[MIGRATION] STATUS:")
    if legacy_count == 0:
        print("[SUCCESS] MIGRATION COMPLETE - No legacy components found!")
        print(f"[SUCCESS] {rexus_count} Rexus components in use")
        
        if rexus_found:
            print("\n[REXUS] COMPONENTS USED:")
            for item in rexus_found[:10]:  # Show top 10
                print(f"  - {item}")
        
        print("\n[STATUS] MIGRATION SUCCESSFUL")
        return True
        
    else:
        print(f"[WARNING] MIGRATION INCOMPLETE - {legacy_count} legacy components found")
        
        if legacy_found:
            print("\n[LEGACY] COMPONENTS FOUND:")
            for item in legacy_found:
                print(f"  - {item}")
        
        print(f"\n[SUCCESS] {rexus_count} Rexus components in use")
        if rexus_found:
            print("\n[REXUS] COMPONENTS USED:")
            for item in rexus_found[:5]:  # Show top 5
                print(f"  - {item}")
        
        print("\n[STATUS] MIGRATION INCOMPLETE")
        return False

if __name__ == "__main__":
    success = analyze_herrajes_migration()
    exit(0 if success else 1)