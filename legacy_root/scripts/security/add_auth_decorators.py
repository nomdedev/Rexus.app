#!/usr/bin/env python3
"""
Script para agregar decoradores @auth_required faltantes
Rexus.app - Seguridad Crítica

Identifica y agrega decoradores de autorización a métodos que requieren permisos.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Métodos que requieren autorización (por patrón de nombre)
METHODS_REQUIRING_AUTH = [
    # Operaciones CRUD
    'agregar_', 'crear_', 'nuevo_', 'guardar_', 'insertar_',
    'editar_', 'actualizar_', 'modificar_', 'update_',
    'eliminar_', 'borrar_', 'delete_', 'remove_',
    
    # Operaciones de negocio críticas
    'registrar_', 'procesar_', 'ejecutar_', 'confirmar_',
    'aprobar_', 'rechazar_', 'validar_', 'verificar_',
    'exportar_', 'importar_', 'generar_', 'enviar_',
    'liberar_', 'reservar_', 'asignar_', 'transferir_'
]

# Archivos a procesar (controladores principales)
CONTROLLER_FILES = [
    'rexus/modules/usuarios/controller.py',
    'rexus/modules/inventario/controller.py',  
    'rexus/modules/logistica/controller.py',
    'rexus/modules/obras/controller.py',
    'rexus/modules/compras/controller.py'
]

class AuthDecoratorAdder:
    """Agrega decoradores @auth_required a métodos que los necesitan."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.methods_processed = 0
        self.decorators_added = 0
        self.errors = []
        
    def needs_auth_decorator(self, method_name: str) -> bool:
        """Verifica si un método necesita decorador de autorización."""
        # Saltar métodos especiales y privados
        if method_name.startswith('_'):
            return False
        
        # Saltar métodos seguros
        safe_methods = ['get_', 'load_', 'cargar_', 'listar_', 'mostrar_', 'conectar_']
        if any(method_name.startswith(safe) for safe in safe_methods):
            return False
            
        # Verificar si requiere autorización
        return any(method_name.startswith(pattern) for pattern in METHODS_REQUIRING_AUTH)
    
    def has_auth_decorator(self, lines: List[str], method_line_index: int) -> bool:
        """Verifica si un método ya tiene decorador de autorización."""
        # Buscar hacia atrás desde la línea del método
        for i in range(method_line_index - 1, max(method_line_index - 5, 0), -1):
            line = lines[i].strip()
            if '@auth_required' in line or '@require_permission' in line:
                return True
            if line and not line.startswith('@') and not line.startswith('#'):
                break
        return False
    
    def get_method_permission(self, method_name: str) -> str:
        """Determina el permiso requerido para un método."""
        if any(pattern in method_name for pattern in ['agregar_', 'crear_', 'nuevo_', 'guardar_']):
            return 'CREATE'
        elif any(pattern in method_name for pattern in ['editar_', 'actualizar_', 'modificar_']):
            return 'UPDATE'  
        elif any(pattern in method_name for pattern in ['eliminar_', 'borrar_', 'delete_']):
            return 'DELETE'
        elif any(pattern in method_name for pattern in ['exportar_', 'generar_', 'procesar_']):
            return 'EXPORT'
        else:
            return 'MANAGE'  # Permiso genérico para otras operaciones
    
    def add_auth_import(self, lines: List[str]) -> List[str]:
        """Agrega import de auth_manager si no existe."""
        has_auth_import = any('from rexus.core.auth_manager import' in line for line in lines)
        
        if not has_auth_import:
            # Buscar una línea de import existente para insertar después
            import_line_index = 0
            for i, line in enumerate(lines):
                if line.startswith('from rexus.') or line.startswith('import '):
                    import_line_index = i + 1
            
            # Insertar import
            auth_import = "from rexus.core.auth_manager import AuthManager, auth_required\n"
            lines.insert(import_line_index, auth_import)
            return lines
        
        return lines
    
    def process_controller_file(self, file_path: Path) -> bool:
        """Procesa un archivo de controlador agregando decoradores."""
        try:
            if not file_path.exists():
                print(f"[SKIP] Archivo no encontrado: {file_path}")
                return True
                
            print(f"[PROCESS] Procesando: {file_path}")
            
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_lines = len(lines)
            modified = False
            
            # Agregar import si es necesario
            lines = self.add_auth_import(lines)
            if len(lines) > original_lines:
                modified = True
                print(f"  [ADD] Import de auth_manager agregado")
            
            # Procesar métodos
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Buscar definiciones de métodos
                method_match = re.match(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
                if method_match:
                    method_name = method_match.group(1)
                    self.methods_processed += 1
                    
                    # Verificar si necesita decorador
                    if (self.needs_auth_decorator(method_name) and 
                        not self.has_auth_decorator(lines, i)):
                        
                        # Determinar nivel de indentación
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        indent_str = ' ' * indent
                        
                        # Crear decorador apropiado
                        permission = self.get_method_permission(method_name)
                        decorator = f"{indent_str}@auth_required(permission='{permission}')\n"
                        
                        # Insertar decorador
                        lines.insert(i, decorator)
                        modified = True
                        self.decorators_added += 1
                        
                        print(f"  [ADD] @auth_required('{permission}') -> {method_name}()")
                        i += 1  # Saltar la línea que acabamos de insertar
                
                i += 1
            
            # Guardar archivo si fue modificado
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"  [SAVE] Archivo actualizado con {self.decorators_added} decoradores")
            else:
                print(f"  [OK] No se requieren cambios")
            
            return True
            
        except Exception as e:
            error_msg = f"Error procesando {file_path}: {e}"
            print(f"  [ERROR] {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def run_batch_processing(self) -> bool:
        """Ejecuta el procesamiento en lote de todos los controladores."""
        print("=" * 60)
        print("AGREGADOR DE DECORADORES @auth_required")
        print("Rexus.app - Seguridad Crítica")
        print("=" * 60)
        
        success_count = 0
        
        for controller_file in CONTROLLER_FILES:
            file_path = self.project_root / controller_file
            if self.process_controller_file(file_path):
                success_count += 1
            print()  # Línea en blanco entre archivos
        
        # Reporte final
        self.generate_report(success_count, len(CONTROLLER_FILES))
        
        return success_count == len(CONTROLLER_FILES)
    
    def generate_report(self, success_count: int, total_files: int):
        """Genera reporte final."""
        print("=" * 60)
        print("REPORTE DE DECORADORES @auth_required")
        print("=" * 60)
        print(f"Archivos procesados exitosamente: {success_count}/{total_files}")
        print(f"Métodos analizados: {self.methods_processed}")
        print(f"Decoradores agregados: {self.decorators_added}")
        print(f"Errores encontrados: {len(self.errors)}")
        
        if self.errors:
            print("\nErrores:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        if self.decorators_added > 0:
            print(f"[EXITO] Se agregaron {self.decorators_added} decoradores de autorización")
            print("[NOTA] Verificar que los permisos sean correctos para cada método")
        else:
            print("[OK] Todos los métodos críticos ya tienen autorización")
        print("=" * 60)


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent.parent
    
    print("Iniciando agregado de decoradores @auth_required...")
    print(f"Directorio del proyecto: {project_root}")
    print()
    
    processor = AuthDecoratorAdder(project_root)
    success = processor.run_batch_processing()
    
    if success:
        print("\n[COMPLETADO] Procesamiento exitoso")
        return 0
    else:
        print("\n[ERROR] Procesamiento completado con errores")
        return 1


if __name__ == "__main__":
    exit(main())