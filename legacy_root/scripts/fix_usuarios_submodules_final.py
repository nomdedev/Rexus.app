#!/usr/bin/env python3
"""
Correcciones finales para submódulos de usuarios - Post ediciones manuales
"""

import re
from pathlib import Path
from typing import List, Tuple

class UsuariosSubmodulesFinalFixer:
    def __init__(self):
        self.fixes_applied = 0
        
    def fix_profiles_manager(self) -> int:
        """Corrige problemas específicos en profiles_manager.py"""
        file_path = Path("rexus/modules/usuarios/submodules/profiles_manager.py")
        
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            return 0
            
        print(f"🔧 Corrigiendo {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes = 0
        
        # Fix 1: Corregir tipo de retorno None -> Optional[Dict[str, Any]]
        if "from typing import Dict, List, Any, Optional" not in content:
            content = content.replace(
                "from typing import Dict, List, Any",
                "from typing import Dict, List, Any, Optional"
            )
            fixes += 1
        
        # Fix 2: Corregir funciones que retornan None pero están tipadas como Dict
        def_patterns = [
            (r'def obtener_perfil_usuario\(self, usuario_id: int\) -> Dict\[str, Any\]:',
             'def obtener_perfil_usuario(self, usuario_id: int) -> Optional[Dict[str, Any]]:'),
            (r'def obtener_usuario_por_id\(self, usuario_id: int\) -> Dict\[str, Any\]:',
             'def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:'),
            (r'def eliminar_usuario\(self, usuario_id: int\) -> Dict\[str, Any\]:',
             'def eliminar_usuario(self, usuario_id: int) -> Optional[Dict[str, Any]]:')
        ]
        
        for pattern, replacement in def_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes += 1
        
        # Fix 3: Corregir try/except/pass patterns
        try_except_patterns = [
            # Pattern 1: except Exception: return None
            (r'(\s+)except Exception:\s*\n\s+return None',
             r'\1except Exception as e:\n\1    logger.error(f"Error en operación: {e}")\n\1    return None'),
            
            # Pattern 2: except Exception: pass seguido de if cursor:
            (r'(\s+)except Exception:\s*\n\s+pass\s*\n(\s+)if cursor:',
             r'\1except Exception as e:\n\1    logger.error(f"Error en operación: {e}")\n\2if cursor:'),
        ]
        
        for pattern, replacement in try_except_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            fixes += 1
        
        # Fix 4: Corregir cursor posiblemente desvinculado
        cursor_patterns = [
            # Inicializar cursor correctamente
            (r'(\s+)cursor = None\s*\n(\s+)try:\s*\n(\s+)cursor = self\.db_connection\.cursor\(\)',
             r'\1cursor = None\n\2try:\n\3cursor = self.db_connection.cursor()'),
        ]
        
        for pattern, replacement in cursor_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            fixes += 1
        
        # Fix 5: Mejorar manejo de excepciones específicas
        # Reemplazar logger.info con f-strings seguros
        f_string_pattern = r'logger\.info\(f"Usuario eliminado: \{usuario\[\'username\'\]\} \(ID: \{usuario_id\}\)"\)'
        if re.search(f_string_pattern, content):
            content = re.sub(
                f_string_pattern,
                'logger.info("Usuario eliminado: %s (ID: %s)", usuario.get("username", "N/A"), usuario_id)',
                content
            )
            fixes += 1
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {fixes} correcciones aplicadas en profiles_manager.py")
            return fixes
        else:
            print(f"  ℹ️ No se necesitaron cambios en profiles_manager.py")
            return 0
    
    def fix_auth_manager(self) -> int:
        """Corrige problemas específicos en auth_manager.py"""
        file_path = Path("rexus/modules/usuarios/submodules/auth_manager.py")
        
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            return 0
            
        print(f"🔧 Corrigiendo {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes = 0
        
        # Fix try/except/pass en auth_manager
        # Buscar patrones específicos de try/except/pass
        pattern = r'(\s+)try:\s*\n(\s+)if cursor:\s*\n(\s+)cursor\.close\(\)\s*\n(\s+)except Exception:\s*\n(\s+)pass'
        replacement = r'\1try:\n\2if cursor:\n\3cursor.close()\n\4except Exception as e:\n\5logger.error(f"Error cerrando cursor: {e}")'
        
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            fixes += 1
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {fixes} correcciones aplicadas en auth_manager.py")
            return fixes
        else:
            print(f"  ℹ️ No se necesitaron cambios en auth_manager.py")
            return 0
    
    def fix_permissions_manager(self) -> int:
        """Corrige problemas específicos en permissions_manager.py"""
        file_path = Path("rexus/modules/usuarios/submodules/permissions_manager.py")
        
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            return 0
            
        print(f"🔧 Corrigiendo {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes = 0
        
        # Fix try/except/pass patterns específicos
        patterns = [
            # Pattern 1: if self.db_connection: seguido de try/except/pass
            (r'(\s+)if self\.db_connection:\s*\n(\s+)try:\s*\n(\s+)self\.db_connection\.close\(\)\s*\n(\s+)except Exception:\s*\n(\s+)pass',
             r'\1if self.db_connection:\n\2try:\n\3self.db_connection.close()\n\4except Exception as e:\n\5logger.error(f"Error cerrando conexión: {e}")'),
            
            # Pattern 2: except Exception as e: seguido de pass
            (r'(\s+)except Exception as e:\s*\n(\s+)pass',
             r'\1except Exception as e:\n\2logger.error(f"Error en operación: {e}")'),
            
            # Pattern 3: return con f-string
            (r'return \{\'success\': True, \'message\': f\'Rol cambiado a \{nuevo_rol\}\'\}',
             'return {"success": True, "message": f"Rol cambiado a {nuevo_rol}"}')
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                fixes += 1
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {fixes} correcciones aplicadas en permissions_manager.py")
            return fixes
        else:
            print(f"  ℹ️ No se necesitaron cambios en permissions_manager.py")
            return 0
    
    def run_all_fixes(self):
        """Ejecuta todas las correcciones"""
        print("🔧 CORRECCIONES FINALES - SUBMÓDULOS DE USUARIOS")
        print("=" * 55)
        
        total_fixes = 0
        total_fixes += self.fix_profiles_manager()
        total_fixes += self.fix_auth_manager()
        total_fixes += self.fix_permissions_manager()
        
        print(f"\n📊 RESUMEN:")
        print(f"  • Total de correcciones aplicadas: {total_fixes}")
        
        if total_fixes > 0:
            print(f"  ✅ Submódulos corregidos exitosamente")
            print(f"  🔄 Se recomienda verificar con get_errors nuevamente")
        else:
            print(f"  ℹ️ No se necesitaron correcciones adicionales")
        
        return total_fixes

def main():
    fixer = UsuariosSubmodulesFinalFixer()
    return fixer.run_all_fixes()

if __name__ == "__main__":
    main()
