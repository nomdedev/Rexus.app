#!/usr/bin/env python3
"""
Script to fix import paths from src. to rexus.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace src. imports with rexus. imports
        original_content = content
        content = re.sub(r'from src\.', 'from rexus.', content)
        content = re.sub(r'import src\.', 'import rexus.', content)
        
        # Only write if there were changes
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all import paths"""
    project_root = Path(__file__).parent
    src_modules_dir = project_root / "src" / "modules"
    
    print("Starting import path fixes...")
    
    total_files = 0
    fixed_files = 0
    
    # Process all Python files in src/modules
    for py_file in src_modules_dir.rglob("*.py"):
        total_files += 1
        if fix_imports_in_file(py_file):
            fixed_files += 1
    
    print(f"\nSummary:")
    print(f"Total files processed: {total_files}")
    print(f"Files with fixes: {fixed_files}")
    print("Import path fixes completed!")

if __name__ == "__main__":
    main()