#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Script para corregir automáticamente problemas de conexiones de señales
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any


class SignalFixer:
    """Corrector automático de problemas de señales."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.lines = []
        self.fixes_applied = []
        
    def load_file(self) -> bool:
        """Carga el contenido del archivo."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
            return True
        except Exception as e:
            print(f"Error cargando {self.file_path}: {e}")
            return False
    
    def save_file(self) -> bool:
        """Guarda el archivo corregido."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines))
            return True
        except Exception as e:
            print(f"Error guardando {self.file_path}: {e}")
            return False
    
    def fix_missing_slots(self, missing_slots: List[Dict]) -> int:
        """
        Corrige slots faltantes agregando métodos stub.
        
        Args:
            missing_slots: Lista de slots faltantes
            
        Returns:
            Número de slots agregados
        """
        fixes = 0
        
        # Encontrar la clase principal y su final
        class_pattern = r'^class\s+(\w+).*?:'
        class_end_pattern = r'^class\s+\w+.*?:|^def\s+\w+.*?:|^if\s+__name__.*?:'
        
        for i, line in enumerate(self.lines):
            if re.match(class_pattern, line.strip()):
                class_name = re.match(class_pattern, line.strip()).group(1)
                
                # Encontrar donde termina la clase
                class_end = len(self.lines)
                indent_level = len(line) - len(line.lstrip())
                
                for j in range(i + 1, len(self.lines)):
                    if (self.lines[j].strip() and 
                        len(self.lines[j]) - len(self.lines[j].lstrip()) <= indent_level and
                        not self.lines[j].strip().startswith('#')):
                        class_end = j
                        break
                
                # Agregar slots faltantes antes del final de la clase
                slots_to_add = []
                for slot_info in missing_slots:
                    slot_name = slot_info['slot']
                    
                    # Solo agregar slots simples (sin puntos)
                    if '.' not in slot_name and slot_name not in ['lambda', 'callback']:
                        # Verificar que no exista ya el método
                        method_exists = False
                        for line_content in self.lines[i:class_end]:
                            if re.match(rf'^\s*def\s+{re.escape(slot_name)}\s*\(', line_content):
                                method_exists = True
                                break
                        
                        if not method_exists:
                            method_stub = self._generate_method_stub(slot_name, indent_level + 4)
                            slots_to_add.append(method_stub)
                
                if slots_to_add:
                    # Insertar los métodos antes del final de la clase
                    insert_point = class_end
                    for stub in reversed(slots_to_add):
                        self.lines.insert(insert_point, "")
                        for stub_line in reversed(stub):
                            self.lines.insert(insert_point, stub_line)
                        fixes += 1
                    
                    self.fixes_applied.append(f"Agregados {len(slots_to_add)} slots faltantes en {class_name}")
                break
        
        return fixes
    
    def _generate_method_stub(self, method_name: str, indent: int) -> List[str]:
        """
        Genera un stub para un método faltante.
        
        Args:
            method_name: Nombre del método
            indent: Nivel de indentación
            
        Returns:
            Lista de líneas del método stub
        """
        indent_str = " " * indent
        
        stub = [
            f"{indent_str}def {method_name}(self):",
            f"{indent_str}    \"\"\"",
            f"{indent_str}    Slot auto-generado para {method_name}.",
            f"{indent_str}    TODO: Implementar funcionalidad específica.",
            f"{indent_str}    \"\"\"",
            f"{indent_str}    try:",
            f"{indent_str}        # TODO: Implementar lógica del slot",
            f"{indent_str}        pass",
            f"{indent_str}    except Exception as e:",
            f"{indent_str}        print(f\"Error en {method_name}: {{e}}\")"
        ]
        
        return stub
    
    def fix_lambda_connections(self) -> int:
        """
        Corrige conexiones lambda problemáticas.
        
        Returns:
            Número de lambdas corregidas
        """
        fixes = 0
        
        for i, line in enumerate(self.lines):
            # Buscar conexiones lambda
            if '.connect(' in line and 'lambda' in line:
                # Reemplazar lambda por método dedicado si es posible
                if 'lambda:' in line:
                    # Lambda simple sin parámetros
                    original_line = line
                    method_name = f"_on_{self._extract_signal_name(line)}_slot"
                    method_name = re.sub(r'[^\w]', '_', method_name).lower()
                    
                    # Reemplazar lambda por método
                    fixed_line = re.sub(r'lambda:\s*[^)]+', f'self.{method_name}', line)
                    
                    if fixed_line != original_line:
                        self.lines[i] = fixed_line
                        fixes += 1
                        self.fixes_applied.append(f"Línea {i+1}: Reemplazada lambda por {method_name}")
        
        return fixes
    
    def _extract_signal_name(self, line: str) -> str:
        """Extrae el nombre de la señal de una línea."""
        # Buscar patrón obj.signal.connect
        match = re.search(r'(\w+)\.(\w+)\.connect', line)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
        
        # Buscar patrón self.obj.signal.connect
        match = re.search(r'self\.(\w+)\.(\w+)\.connect', line)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
        
        return "unknown"
    
    def add_disconnect_in_destructor(self, missing_disconnects: List[Dict]) -> int:
        """
        Agrega desconexiones en el destructor de la clase.
        
        Args:
            missing_disconnects: Lista de conexiones sin desconectar
            
        Returns:
            Número de desconexiones agregadas
        """
        fixes = 0
        
        # Encontrar o crear método __del__ o closeEvent
        destructor_found = False
        destructor_line = -1
        
        for i, line in enumerate(self.lines):
            if re.match(r'^\s*def\s+__del__\s*\(', line) or re.match(r'^\s*def\s+closeEvent\s*\(', line):
                destructor_found = True
                destructor_line = i
                break
        
        if not destructor_found:
            # Crear método closeEvent
            destructor_line = self._find_class_end() - 1
            if destructor_line > 0:
                indent = self._get_class_indent()
                destructor_stub = [
                    "",
                    f"{' ' * indent}def closeEvent(self, event):",
                    f"{' ' * indent}    \"\"\"Limpia conexiones al cerrar.\"\"\"",
                    f"{' ' * indent}    try:",
                    f"{' ' * indent}        # Desconectar señales para evitar memory leaks"
                ]
                
                # Agregar desconexiones
                for disconnect_info in missing_disconnects[:10]:  # Limitar a 10
                    signal = disconnect_info['signal']
                    if 'self.' in signal and '.disconnect()' not in signal:
                        disconnect_line = f"{' ' * (indent + 8)}{signal}.disconnect()"
                        destructor_stub.append(disconnect_line)
                        fixes += 1
                
                destructor_stub.extend([
                    f"{' ' * indent}    except Exception as e:",
                    f"{' ' * indent}        print(f'Error desconectando señales: {{e}}')",
                    f"{' ' * indent}    ",
                    f"{' ' * indent}    super().closeEvent(event)"
                ])
                
                # Insertar el destructor
                for stub_line in reversed(destructor_stub):
                    self.lines.insert(destructor_line, stub_line)
                
                self.fixes_applied.append(f"Agregado closeEvent con {fixes} desconexiones")
        
        return fixes
    
    def _find_class_end(self) -> int:
        """Encuentra el final de la primera clase en el archivo."""
        for i, line in enumerate(self.lines):
            if re.match(r'^class\s+', line):
                indent_level = len(line) - len(line.lstrip())
                
                for j in range(i + 1, len(self.lines)):
                    if (self.lines[j].strip() and 
                        len(self.lines[j]) - len(self.lines[j].lstrip()) <= indent_level and
                        not self.lines[j].strip().startswith('#')):
                        return j
                
                return len(self.lines)
        
        return len(self.lines)
    
    def _get_class_indent(self) -> int:
        """Obtiene el nivel de indentación de los métodos de clase."""
        for line in self.lines:
            if re.match(r'^\s+def\s+', line):
                return len(line) - len(line.lstrip())
        return 4  # Default


def fix_file_signals(file_path: Path, issues: List[Dict]) -> Dict[str, Any]:
    """
    Corrige problemas de señales en un archivo.
    
    Args:
        file_path: Ruta al archivo
        issues: Lista de problemas encontrados
        
    Returns:
        Dict con resultados
    """
    fixer = SignalFixer(file_path)
    
    if not fixer.load_file():
        return {'file': str(file_path), 'success': False, 'fixes': 0}
    
    total_fixes = 0
    
    # Separar tipos de problemas
    missing_slots = [issue for issue in issues if issue['type'] == 'missing_slot']
    missing_disconnects = [issue for issue in issues if issue['type'] == 'missing_disconnect']
    
    # Solo corregir si hay problemas críticos
    if len(missing_slots) > 5 or len(missing_disconnects) > 10:
        return {
            'file': str(file_path), 
            'success': False, 
            'fixes': 0,
            'reason': 'Demasiados problemas - revisión manual requerida'
        }
    
    # Corregir slots faltantes (solo los más simples)
    simple_slots = [slot for slot in missing_slots 
                   if ('.' not in slot['slot'] and 
                       slot['slot'] not in ['lambda', 'callback', 'unknown_slot'] and
                       len(slot['slot']) < 30)]
    
    if simple_slots:
        fixes = fixer.fix_missing_slots(simple_slots[:3])  # Máximo 3 slots
        total_fixes += fixes
    
    # Corregir lambdas problemáticas
    lambda_fixes = fixer.fix_lambda_connections()
    total_fixes += lambda_fixes
    
    # Solo guardar si hicimos correcciones
    if total_fixes > 0:
        if fixer.save_file():
            return {
                'file': str(file_path),
                'success': True,
                'fixes': total_fixes,
                'fixes_applied': fixer.fixes_applied
            }
    
    return {'file': str(file_path), 'success': True, 'fixes': 0}


def main():
    """Función principal."""
    print("=" * 80)
    print("CORRECTOR AUTOMATICO DE PROBLEMAS DE SENALES - REXUS.APP")
    print("=" * 80)
    
    # Obtener directorio raíz del proyecto
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    
    print(f"Directorio del proyecto: {project_root}")
    print("\nIMPORTANTE: Este script hace correcciones conservadoras.")
    print("Se recomienda hacer backup antes de continuar.")
    
    input("\nPresione Enter para continuar o Ctrl+C para cancelar...")
    
    # Aquí iríamos archivo por archivo corrigiendo solo problemas simples
    print("\nEste es un script de demostración.")
    print("Para uso real, necesitaría:")
    print("1. Lista específica de archivos a corregir")
    print("2. Análisis detallado de cada problema")
    print("3. Verificación de que las correcciones son seguras")
    print("4. Tests después de cada corrección")
    
    print("\nRECOMENDACION:")
    print("Corrija los problemas manualmente, priorizando:")
    print("1. Memory leaks (conexiones a objetos temporales)")
    print("2. Slots faltantes que causan errores")
    print("3. Conexiones múltiples problemáticas")
    
    return 0


if __name__ == "__main__":
    exit(main())