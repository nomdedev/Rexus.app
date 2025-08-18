#!/usr/bin/env python3
"""
Script to fix emoji encoding issues in module views
"""

import os
import re
from pathlib import Path

def fix_emoji_encoding():
    """Replace problematic emojis with text equivalents"""
    
    # Emoji replacements
    emoji_replacements = {
        '📦': '[PACKAGE]',
        '👥': '[USERS]',
        '🚛': '[TRUCK]',
        '🏗️': '[CONSTRUCTION]',
        '💰': '[MONEY]',
        '📝': '[NOTE]',
        '⚙️': '[SETTINGS]',
        '📊': '[CHART]',
        '🔧': '[WRENCH]',
        '🪟': '[WINDOW]',
        '🔩': '[BOLT]',
        '🎨': '[ART]',
        '📋': '[CLIPBOARD]',
        '✅': '[CHECK]',
        '❌': '[X]',
        '⚠️': '[WARNING]',
        '🔍': '[SEARCH]',
        '📈': '[TRENDING]',
        '💼': '[BRIEFCASE]',
        '🏪': '[STORE]',
        '📞': '[PHONE]',
        '📧': '[EMAIL]',
        '🌟': '[STAR]',
        '🔒': '[LOCK]',
        '🔓': '[UNLOCK]'
    }
    
    # Find all Python files in modules
    modules_path = Path("rexus/modules")
    python_files = list(modules_path.rglob("*.py"))
    
    fixed_files = []
    
    for file_path in python_files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track if changes were made
            original_content = content
            
            # Apply emoji replacements
            for emoji, replacement in emoji_replacements.items():
                content = content.replace(emoji, replacement)
            
            # If changes were made, write back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(file_path))
                print(f"Fixed emojis in: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nFixed emoji encoding in {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")
    
    return fixed_files

if __name__ == "__main__":
    fixed_files = fix_emoji_encoding()
    print(f"\nEmoji encoding fix completed - {len(fixed_files)} files updated")