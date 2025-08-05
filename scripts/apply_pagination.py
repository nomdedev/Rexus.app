#!/usr/bin/env python3
"""
Script para aplicar paginación a tablas grandes
Rexus.app - Optimización de Rendimiento

Identifica tablas grandes (>1000 registros) y aplica paginación
para mejorar el rendimiento y la experiencia de usuario.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class PaginationApplier:
    """Aplica paginación a modelos y vistas que lo requieren."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules_path = project_root / "rexus" / "modules"
        self.changes_applied = 0
        self.files_modified = []
        
        # Módulos que probablemente tienen tablas grandes
        self.target_modules = [
            "inventario",
            "obras", 
            "pedidos",
            "compras",
            "logistica",
            "usuarios"
        ]
    
    def identify_large_tables(self):
        """Identifica módulos que probablemente manejan tablas grandes."""
        print("[ANALYSIS] Identificando módulos con tablas grandes...")
        
        large_table_modules = []
        
        for module in self.target_modules:
            module_path = self.modules_path / module
            if not module_path.exists():
                continue
                
            model_file = module_path / "model.py"
            if model_file.exists():
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar indicadores de tablas grandes
                indicators = [
                    'SELECT \* FROM',
                    'obtener_todos',
                    'get_all',
                    'cargar_todos',
                    'limit',
                    'offset'
                ]
                
                has_indicators = any(indicator.lower() in content.lower() 
                                   for indicator in indicators)
                
                # Verificar si ya tiene paginación
                has_pagination = any(pagination_term in content.lower() 
                                   for pagination_term in ['pagination', 'paginated', 'offset', 'fetch'])
                
                if has_indicators and not has_pagination:
                    large_table_modules.append(module)
                    print(f"  [DETECTED] {module} - Requiere paginación")
                elif has_pagination:
                    print(f"  [OK] {module} - Ya tiene paginación")
                else:
                    print(f"  [SKIP] {module} - No requiere paginación")
        
        return large_table_modules
    
    def add_pagination_to_model(self, module_name: str) -> bool:
        """Agrega paginación a un modelo específico."""
        model_file = self.modules_path / module_name / "model.py"
        
        if not model_file.exists():
            return False
        
        print(f"  [MODIFY] Agregando paginación a {module_name}/model.py")
        
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Agregar import de paginación si no existe
        if 'from rexus.utils.pagination import' not in content:
            # Buscar lugar para insertar import
            import_lines = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if line.startswith('from rexus.utils.') or line.startswith('import '):
                    import_lines.append(i)
            
            if import_lines:
                insert_line = max(import_lines) + 1
                lines.insert(insert_line, 'from rexus.utils.pagination import PaginatedTableMixin, PaginationInfo, create_pagination_query')
                content = '\n'.join(lines)
        
        # Agregar herencia de PaginatedTableMixin a la clase principal
        class_pattern = rf'class {module_name.title()}Model[:\(]'
        class_match = re.search(class_pattern, content, re.IGNORECASE)
        
        if class_match and 'PaginatedTableMixin' not in content:
            # Modificar la clase para heredar de PaginatedTableMixin
            class_line = class_match.group(0)
            if ':' in class_line:
                new_class_line = class_line.replace(':', '(PaginatedTableMixin):')
            else:
                new_class_line = class_line.replace('(', '(PaginatedTableMixin, ')
            
            content = content.replace(class_line, new_class_line)
        
        # Agregar método get_paginated_data si no existe
        if 'def get_paginated_data(' not in content:
            paginated_method = f'''
    def get_paginated_data(self, offset: int, limit: int, filters: Dict = None) -> Tuple[List[Dict], int]:
        """
        Obtiene datos paginados para {module_name}.
        
        Args:
            offset: Registros a saltar
            limit: Registros a obtener
            filters: Filtros adicionales
            
        Returns:
            Tupla (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0
            
            cursor = self.db_connection.cursor()
            
            # Consulta base
            base_query = "SELECT * FROM {module_name}"
            where_clause = ""
            params = []
            
            # Aplicar filtros si existen
            if filters:
                conditions = []
                for key, value in filters.items():
                    if value:
                        conditions.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
                
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)
            
            # Consulta de conteo
            count_query = f"SELECT COUNT(*) FROM {module_name}{where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Consulta paginada
            paginated_query = f"{base_query}{where_clause} ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])
            
            # Convertir resultados a diccionarios
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results, total_count
            
        except Exception as e:
            print(f"Error obteniendo datos paginados de {module_name}: {e}")
            return [], 0
'''
            # Agregar al final de la clase
            content = content.rstrip() + paginated_method
        
        # Agregar método helper para obtener con paginación
        if f'def obtener_{module_name}_paginados(' not in content:
            helper_method = f'''
    def obtener_{module_name}_paginados(self, page: int = 1, page_size: int = 50, filtros: Dict = None):
        """
        Obtiene {module_name} con paginación.
        
        Args:
            page: Número de página
            page_size: Registros por página  
            filtros: Filtros de búsqueda
            
        Returns:
            Tupla (datos, información_paginación)
        """
        return self.get_paginated_results(page, page_size, filtros)
'''
            content = content.rstrip() + helper_method
        
        # Guardar si hubo cambios
        if content != original_content:
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_applied += 1
            self.files_modified.append(str(model_file))
            return True
        
        return False
    
    def add_pagination_to_view(self, module_name: str) -> bool:
        """Agrega controles de paginación a una vista."""
        view_file = self.modules_path / module_name / "view.py"
        
        if not view_file.exists():
            return False
        
        print(f"  [MODIFY] Agregando controles de paginación a {module_name}/view.py")
        
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Agregar import de paginación
        if 'from rexus.utils.pagination import' not in content:
            # Buscar lugar para insertar import
            lines = content.split('\n')
            import_line = 0
            
            for i, line in enumerate(lines):
                if line.startswith('from PyQt6.QtWidgets import'):
                    import_line = i + 1
                    break
            
            lines.insert(import_line, 'from rexus.utils.pagination import PaginationWidget, PaginationInfo')
            content = '\n'.join(lines)
        
        # Agregar inicialización del widget de paginación en __init__
        init_pattern = r'def __init__\(self.*?\):'
        init_match = re.search(init_pattern, content)
        
        if init_match and 'self.pagination_widget' not in content:
            # Buscar el final del método __init__
            init_start = init_match.end()
            lines = content[init_start:].split('\n')
            
            # Agregar inicialización de paginación
            pagination_init = '''
        # Inicialización de paginación
        self.pagination_widget = PaginationWidget()
        self.pagination_widget.page_changed.connect(self.on_page_changed)
        self.pagination_widget.page_size_changed.connect(self.on_page_size_changed)
        self.current_page = 1
        self.page_size = 50'''
            
            # Insertar después de super().__init__()
            for i, line in enumerate(lines):
                if 'super().__init__()' in line:
                    lines.insert(i + 1, pagination_init)
                    break
            
            content = content[:init_start] + '\n'.join(lines)
        
        # Agregar métodos de manejo de paginación si no existen
        if 'def on_page_changed(' not in content:
            pagination_methods = f'''
    def on_page_changed(self, page: int):
        """Maneja el cambio de página."""
        self.current_page = page
        self.cargar_datos_paginados()
    
    def on_page_size_changed(self, page_size: int):
        """Maneja el cambio de tamaño de página."""
        self.page_size = page_size
        self.current_page = 1
        self.cargar_datos_paginados()
    
    def cargar_datos_paginados(self):
        """Carga datos con paginación."""
        if hasattr(self, 'controller') and self.controller:
            try:
                # Obtener filtros actuales si existen
                filtros = getattr(self, 'obtener_filtros_actuales', lambda: {{}})()
                
                # Solicitar datos paginados al controlador
                if hasattr(self.controller, 'obtener_datos_paginados'):
                    datos, pagination_info = self.controller.obtener_datos_paginados(
                        self.current_page, self.page_size, filtros
                    )
                    
                    # Actualizar tabla
                    self.cargar_datos_en_tabla(datos)
                    
                    # Actualizar widget de paginación
                    self.pagination_widget.update_pagination(pagination_info)
                    
            except Exception as e:
                print(f"Error cargando datos paginados: {{e}}")
    
    def obtener_filtros_actuales(self) -> dict:
        """Obtiene los filtros actuales de la interfaz."""
        # Implementar según los filtros específicos de cada vista
        return {{}}
'''
            content = content.rstrip() + pagination_methods
        
        # Guardar si hubo cambios
        if content != original_content:
            with open(view_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_applied += 1
            self.files_modified.append(str(view_file))
            return True
        
        return False
    
    def add_pagination_to_controller(self, module_name: str) -> bool:
        """Agrega métodos de paginación al controlador."""
        controller_file = self.modules_path / module_name / "controller.py"
        
        if not controller_file.exists():
            return False
        
        print(f"  [MODIFY] Agregando métodos de paginación a {module_name}/controller.py")
        
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Agregar método para obtener datos paginados
        if 'def obtener_datos_paginados(' not in content:
            paginated_method = f'''
    def obtener_datos_paginados(self, page: int, page_size: int, filtros: dict = None):
        """
        Obtiene datos paginados del modelo.
        
        Args:
            page: Número de página
            page_size: Registros por página
            filtros: Filtros de búsqueda
            
        Returns:
            Tupla (datos, información_paginación)
        """
        try:
            if hasattr(self.model, 'obtener_{module_name}_paginados'):
                return self.model.obtener_{module_name}_paginados(page, page_size, filtros)
            elif hasattr(self.model, 'get_paginated_results'):
                return self.model.get_paginated_results(page, page_size, filtros)
            else:
                # Fallback sin paginación
                from rexus.utils.pagination import PaginationInfo
                datos = getattr(self.model, f'obtener_{module_name}', lambda: [])()
                pagination_info = PaginationInfo(1, len(datos), len(datos))
                return datos, pagination_info
                
        except Exception as e:
            print(f"Error obteniendo datos paginados: {{e}}")
            from rexus.utils.pagination import PaginationInfo
            return [], PaginationInfo(1, 0, 0)
'''
            content = content.rstrip() + paginated_method
        
        # Guardar si hubo cambios
        if content != original_content:
            with open(controller_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_applied += 1
            self.files_modified.append(str(controller_file))
            return True
        
        return False
    
    def run_pagination_application(self):
        """Ejecuta la aplicación de paginación a todos los módulos requeridos."""
        print("=" * 60)
        print("APLICADOR DE PAGINACIÓN A TABLAS GRANDES")
        print("Rexus.app - Optimización de Rendimiento")
        print("=" * 60)
        
        # Identificar módulos que requieren paginación
        modules_needing_pagination = self.identify_large_tables()
        
        if not modules_needing_pagination:
            print("\n[INFO] No se encontraron módulos que requieran paginación")
            return True
        
        print(f"\n[PROCESS] Aplicando paginación a {len(modules_needing_pagination)} módulos...")
        
        # Aplicar paginación a cada módulo
        for module in modules_needing_pagination:
            print(f"\n[MODULE] Procesando {module}...")
            
            # Modificar modelo
            model_modified = self.add_pagination_to_model(module)
            
            # Modificar vista
            view_modified = self.add_pagination_to_view(module)
            
            # Modificar controlador
            controller_modified = self.add_pagination_to_controller(module)
            
            if any([model_modified, view_modified, controller_modified]):
                print(f"  [SUCCESS] Paginación aplicada a {module}")
            else:
                print(f"  [SKIP] {module} no requirió cambios")
        
        # Generar reporte
        self.generate_report()
        
        return self.changes_applied > 0
    
    def generate_report(self):
        """Genera reporte de aplicación de paginación."""
        print("\n" + "=" * 60)
        print("REPORTE DE PAGINACIÓN APLICADA")
        print("=" * 60)
        print(f"Cambios aplicados: {self.changes_applied}")
        print(f"Archivos modificados: {len(self.files_modified)}")
        
        if self.files_modified:
            print("\\nArchivos modificados:")
            for file_path in self.files_modified:
                print(f"  - {file_path}")
        
        print("\\n" + "=" * 60)
        if self.changes_applied > 0:
            print("[EXITO] Paginación aplicada exitosamente")
            print("[BENEFICIOS]:")
            print("- Mejor rendimiento en tablas grandes")
            print("- Reducción del uso de memoria")
            print("- Mejora en la experiencia de usuario")
            print("- Tiempo de carga más rápido")
        else:
            print("[INFO] No se requirieron cambios de paginación")
        print("=" * 60)


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent
    
    print("Iniciando aplicación de paginación...")
    print(f"Directorio del proyecto: {project_root}")
    print()
    
    applier = PaginationApplier(project_root)
    success = applier.run_pagination_application()
    
    if success:
        print("\\n[COMPLETADO] Paginación aplicada exitosamente")
        return 0
    else:
        print("\\n[INFO] No se requirieron cambios")
        return 0


if __name__ == "__main__":
    exit(main())