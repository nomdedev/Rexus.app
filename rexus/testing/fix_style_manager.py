#!/usr/bin/env python3
"""
Script to fix style_manager.colors references
"""

import re
from pathlib import Path

def fix_style_manager_references():
    """Replace style_manager.colors with direct color values"""
    
    # Color mappings
    color_mappings = {
        'style_manager.colors.BACKGROUND': '#f8fafc',
        'style_manager.colors.TEXT_PRIMARY': '#1f2937',
        'style_manager.colors.BORDER': '#d1d5db',
        'style_manager.colors.PRIMARY': '#3b82f6',
        'style_manager.colors.PRIMARY_HOVER': '#2563eb',
        'style_manager.colors.SELECTION': '#dbeafe',
        'style_manager.colors.ALTERNATE_ROW': '#f9fafb'
    }
    
    # Find all Python files in compras module
    compras_path = Path("rexus/modules/compras")
    python_files = list(compras_path.rglob("*.py"))
    
    fixed_files = []
    
    for file_path in python_files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track if changes were made
            original_content = content
            
            # Apply color replacements
            for old_ref, new_value in color_mappings.items():
                # Replace f-string references
                pattern = r'f"""[^"]*\{' + re.escape(old_ref) + r'\}[^"]*"""'
                content = re.sub(pattern, lambda m: m.group(0).replace(f'{{{old_ref}}}', new_value), content, flags=re.DOTALL)
                
                # Replace direct references
                content = content.replace(f'{{{old_ref}}}', new_value)
            
            # If changes were made, write back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(file_path))
                print(f"Fixed style_manager references in: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\\nFixed style_manager references in {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")
    
    return fixed_files

if __name__ == "__main__":
    fixed_files = fix_style_manager_references()
    print(f"\\nStyle manager fix completed - {len(fixed_files)} files updated")