"""
Script específico para corregir consultas_manager.py
"""

def fix_consultas_manager():
    file_path = "rexus/modules/02_inventario/submodules/consultas_manager.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        in_try_block = False
        
        for i, line in enumerate(lines):
            # Corregir indentación específica
            if line.strip().startswith('params = []') and not line.startswith('            '):
                fixed_lines.append('            params = []')
                continue
                
            # Corregir if statements mal indentados
            if line.strip().startswith('if ') and not line.startswith('        '):
                if 'filtros' in line or 'categoria' in line:
                    fixed_lines.append('            ' + line.strip())
                    continue
            
            # Corregir líneas mal indentadas después de if
            if line.strip() and not line.startswith(' ') and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line.endswith(':') and ('if ' in prev_line or 'else' in prev_line):
                    fixed_lines.append('                ' + line.strip())
                    continue
            
            # Agregar except blocks faltantes
            if line.strip().startswith('def ') and in_try_block:
                # Agregamos except antes del nuevo método
                fixed_lines.append('        except Exception as e:')
                fixed_lines.append('            logger.error(f"Error en consulta: {str(e)}")')
                fixed_lines.append('            return []')
                fixed_lines.append('')
                in_try_block = False
            
            if line.strip() == 'try:':
                in_try_block = True
            
            fixed_lines.append(line)
        
        # Si todavía hay un try abierto al final
        if in_try_block:
            fixed_lines.append('        except Exception as e:')
            fixed_lines.append('            logger.error(f"Error en consulta: {str(e)}")')
            fixed_lines.append('            return []')
        
        fixed_content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("consultas_manager.py corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"Error corrigiendo consultas_manager.py: {e}")
        return False

if __name__ == "__main__":
    fix_consultas_manager()