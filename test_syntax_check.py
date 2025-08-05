import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Verifica la sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    modules_dir = Path("rexus/modules")
    
    print("Verificando sintaxis de archivos view.py:")
    print("="*50)
    
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir():
            view_file = module_dir / "view.py"
            if view_file.exists():
                is_valid, error = check_syntax(view_file)
                status = "[OK]" if is_valid else "[SYNTAX ERROR]"
                print(f"{module_dir.name:15} | {status}")
                if error:
                    print(f"                 | {error}")

if __name__ == "__main__":
    main()