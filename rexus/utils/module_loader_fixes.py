#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Loader Fixes - Parches para métodos de carga faltantes
Agrega métodos cargar_[modulo] a controladores que no los tienen
"""

import logging
from typing import Any, Dict

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("module.loader.fixes")
except ImportError:
    logger = logging.getLogger("module.loader.fixes")

class ModuleLoaderFixes:
    """Fixes para métodos de carga faltantes en controladores."""
    
    @staticmethod
    def patch_controller_missing_methods(controller, module_name: str):
        """Agrega métodos de carga faltantes a un controlador."""
        
        method_name = f"cargar_{module_name.lower()}"
        
        if not hasattr(controller, method_name):
            logger.info(f"Agregando método faltante {method_name} a {controller.__class__.__name__}")
            
            # Crear método de carga específico
            def dynamic_load_method():
                return ModuleLoaderFixes._generic_load_data(controller, module_name)
            
            # Asignar método al controlador
            setattr(controller, method_name, dynamic_load_method)
    
    @staticmethod
    def _generic_load_data(controller, module_name: str) -> bool:
        """Método genérico de carga de datos."""
        try:
            logger.info(f"Cargando datos iniciales para {module_name}")
            
            # Verificar si el modelo tiene método de obtener datos
            if hasattr(controller, 'model') and controller.model:
                
                # Intentar métodos comunes de obtención de datos
                data_methods = [
                    f'obtener_{module_name.lower()}',
                    f'obtener_todos_{module_name.lower()}',
                    f'get_all_{module_name.lower()}',
                    'obtener_todos',
                    'get_all'
                ]
                
                for method_name in data_methods:
                    if hasattr(controller.model, method_name):
                        try:
                            data_method = getattr(controller.model, method_name)
                            datos = data_method()
                            logger.info(f"Datos cargados usando {method_name}: {len(datos) if isinstance(datos, list) else 'N/A'} registros")
                            
                            # Actualizar vista si está disponible
                            if hasattr(controller, 'view') and controller.view:
                                ModuleLoaderFixes._update_view_with_data(controller.view, datos, module_name)
                            
                            return True
                        except Exception as e:
                            logger.warning(f"Error usando método {method_name}: {str(e)}")
                            continue
                
                # Si no se encuentra método específico, intentar carga de estadísticas
                if hasattr(controller.model, 'obtener_estadisticas'):
                    try:
                        stats = controller.model.obtener_estadisticas()
                        logger.info(f"Estadísticas cargadas para {module_name}: {stats}")
                        return True
                    except Exception as e:
                        logger.warning(f"Error cargando estadísticas: {str(e)}")
            
            logger.info(f"Carga de datos completada para {module_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando datos para {module_name}: {str(e)}")
            return False
    
    @staticmethod
    def _update_view_with_data(view, datos, module_name: str):
        """Actualiza la vista con los datos cargados."""
        try:
            # Métodos comunes de actualización de vista
            update_methods = [
                f'actualizar_{module_name.lower()}',
                f'cargar_{module_name.lower()}',
                'actualizar_tabla',
                'actualizar_datos',
                'refresh_data',
                'load_data'
            ]
            
            for method_name in update_methods:
                if hasattr(view, method_name):
                    try:
                        update_method = getattr(view, method_name)
                        if callable(update_method):
                            update_method(datos)
                            logger.debug(f"Vista actualizada usando {method_name}")
                            return
                    except Exception as e:
                        logger.warning(f"Error actualizando vista con {method_name}: {str(e)}")
                        continue
            
            logger.debug(f"No se encontró método de actualización específico para {module_name}")
            
        except Exception as e:
            logger.error(f"Error actualizando vista para {module_name}: {str(e)}")

# Mapeo de módulos que necesitan patches
MODULES_NEEDING_PATCHES = {
    'vidrios': ['cargar_vidrios'],
    'logistica': ['cargar_logistica'],
    'compras': ['cargar_compras'],
    'mantenimiento': ['cargar_mantenimiento'],
    'auditoria': ['cargar_auditoria'],
    'pedidos': ['cargar_pedidos'],
    'obras': ['cargar_obras'],
    'inventario': ['cargar_inventario']
}

def apply_module_patches(controller, module_name: str):
    """Aplica patches necesarios a un controlador de módulo."""
    
    module_name_lower = module_name.lower()
    
    if module_name_lower in MODULES_NEEDING_PATCHES:
        methods_needed = MODULES_NEEDING_PATCHES[module_name_lower]
        
        for method_name in methods_needed:
            if not hasattr(controller, method_name):
                logger.info(f"Aplicando patch: {method_name} para {module_name}")
                ModuleLoaderFixes.patch_controller_missing_methods(controller, module_name)

def patch_all_controllers(controllers_dict: Dict[str, Any]):
    """Aplica patches a todos los controladores en un diccionario."""
    
    for module_name, controller in controllers_dict.items():
        if controller:
            apply_module_patches(controller, module_name)