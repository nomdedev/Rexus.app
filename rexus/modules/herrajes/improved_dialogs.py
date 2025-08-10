"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Diálogos mejorados para Herrajes usando utilidades nuevas - Rexus.app v2.0.0

Implementa diálogos CRUD modernos usando las utilidades dialog_utils.py
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget
from datetime import date

from rexus.utils.dialog_utils import CrudDialogManager, create_standard_form_config
from rexus.utils.validation_utils import FormValidationManager, AdvancedValidator
from rexus.utils.format_utils import format_for_display
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class HerrajeDialogManager:
    """Gestor de diálogos para el módulo de herrajes."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
        self.crud_manager = CrudDialogManager(parent_widget, controller)
        self.validator = self._create_herraje_validator()
    
    def _create_herraje_validator(self) -> FormValidationManager:
        """Crea un validador específico para herrajes."""
        manager = FormValidationManager()
        
        # Validadores de campos
        manager.add_field_validator("codigo", manager.create_required_validator("Código"))
        manager.add_field_validator("descripcion", manager.create_required_validator("Descripción"))
        manager.add_field_validator("tipo", manager.create_required_validator("Tipo"))
        manager.add_field_validator("proveedor", manager.create_required_validator("Proveedor"))
        manager.add_field_validator("precio_unitario", lambda v: AdvancedValidator.validate_positive_number(v, "Precio unitario"))
        manager.add_field_validator("stock_actual", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock actual"))
        manager.add_field_validator("stock_minimo", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock mínimo"))
        
        # Validador personalizado para coherencia de stock
        def validate_stock_coherent(data):
            stock_actual = data.get("stock_actual", 0)
            stock_minimo = data.get("stock_minimo", 0)
            try:
                if float(stock_actual) < 0:
                    from rexus.utils.validation_utils import ValidationResult
                    return ValidationResult(False, "Stock actual no puede ser negativo")
                if float(stock_minimo) < 0:
                    from rexus.utils.validation_utils import ValidationResult
                    return ValidationResult(False, "Stock mínimo no puede ser negativo")
            except (ValueError, TypeError):
                pass
            
            from rexus.utils.validation_utils import ValidationResult
            return ValidationResult(True)
        
        manager.add_custom_validator("stock_coherent", validate_stock_coherent)
        
        return manager
    
    def get_form_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del formulario de herraje."""
        return create_standard_form_config(
            title="Gestión de Herraje",
            item_name="herraje",
            groups=[
                {
                    'title': 'Información Básica',
                    'fields': [
                        {
                            'name': 'codigo',
                            'label': 'Código',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'descripcion',
                            'label': 'Descripción',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'tipo',
                            'label': 'Tipo',
                            'type': 'combo',
                            'options': ['BISAGRA', 'CERRADURA', 'MANIJA', 'TORNILLO', 'RIEL', 'SOPORTE', 'OTRO'],
                            'required': True,
                            'default': 'OTRO'
                        },
                        {
                            'name': 'categoria',
                            'label': 'Categoría',
                            'type': 'text',
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Proveedor y Precios',
                    'fields': [
                        {
                            'name': 'proveedor',
                            'label': 'Proveedor',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'precio_unitario',
                            'label': 'Precio Unitario',
                            'type': 'float',
                            'required': True,
                            'min': 0.0,
                            'max': 999999.99,
                            'decimals': 2,
                            'default': 0.0
                        },
                        {
                            'name': 'unidad_medida',
                            'label': 'Unidad de Medida',
                            'type': 'combo',
                            'options': ['UNIDAD', 'PAR', 'JUEGO', 'METRO', 'KILOGRAMO'],
                            'required': True,
                            'default': 'UNIDAD'
                        }
                    ]
                },
                {
                    'title': 'Inventario',
                    'fields': [
                        {
                            'name': 'stock_actual',
                            'label': 'Stock Actual',
                            'type': 'int',
                            'required': True,
                            'min': 0,
                            'max': 99999,
                            'default': 0
                        },
                        {
                            'name': 'stock_minimo',
                            'label': 'Stock Mínimo',
                            'type': 'int',
                            'required': True,
                            'min': 0,
                            'max': 99999,
                            'default': 1
                        },
                        {
                            'name': 'ubicacion',
                            'label': 'Ubicación',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'estado',
                            'label': 'Estado',
                            'type': 'combo',
                            'options': ['ACTIVO', 'INACTIVO', 'DESCONTINUADO'],
                            'required': True,
                            'default': 'ACTIVO'
                        }
                    ]
                },
                {
                    'title': 'Detalles Técnicos',
                    'fields': [
                        {
                            'name': 'marca',
                            'label': 'Marca',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'modelo',
                            'label': 'Modelo',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'color',
                            'label': 'Color',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'material',
                            'label': 'Material',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'dimensiones',
                            'label': 'Dimensiones',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'peso',
                            'label': 'Peso (kg)',
                            'type': 'float',
                            'required': False,
                            'min': 0.0,
                            'max': 9999.999,
                            'decimals': 3,
                            'default': 0.0
                        }
                    ]
                },
                {
                    'title': 'Observaciones',
                    'fields': [
                        {
                            'name': 'observaciones',
                            'label': 'Observaciones',
                            'type': 'textarea',
                            'height': 60,
                            'required': False
                        },
                        {
                            'name': 'especificaciones',
                            'label': 'Especificaciones Técnicas',
                            'type': 'textarea',
                            'height': 60,
                            'required': False
                        }
                    ]
                }
            ],
            size=(800, 700)
        )
    
    def show_create_dialog(self) -> bool:
        """Muestra el diálogo para crear un nuevo herraje."""
        config = self.get_form_config()
        config['title'] = "Crear Nuevo Herraje"
        
        def create_callback(data: Dict[str, Any]) -> bool:
            # Validar datos antes de crear
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False
            
            # Crear herraje a través del controlador
            if self.controller:
                return self.controller.crear_herraje(data)
            return False
        
        return self.crud_manager.show_create_dialog(config, create_callback)
    
    def show_edit_dialog(self, herraje_data: Dict[str, Any]) -> bool:
        """Muestra el diálogo para editar un herraje existente."""
        config = self.get_form_config()
        config['title'] = f"Editar Herraje: {herraje_data.get('codigo', '')}"
        
        # Preparar datos actuales para el formulario
        current_data = self._prepare_form_data(herraje_data)
        
        def update_callback(data: Dict[str, Any]) -> bool:
            # Validar datos
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False
            
            # Actualizar herraje a través del controlador
            if self.controller:
                return self.controller.actualizar_herraje(herraje_data.get('id'), data)
            return False
        
        return self.crud_manager.show_edit_dialog(config, current_data, update_callback)
    
    def confirm_and_delete(self, herraje_data: Dict[str, Any]) -> bool:
        """Confirma y elimina un herraje."""
        codigo = herraje_data.get('codigo', 'Herraje')
        herraje_id = herraje_data.get('id')
        
        def delete_callback() -> bool:
            if self.controller:
                return self.controller.eliminar_herraje(herraje_id)
            return False
        
        return self.crud_manager.confirm_and_delete(codigo, "herraje", delete_callback)
    
    def _prepare_form_data(self, herraje_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos del herraje para el formulario."""
        form_data = {}
        
        # Mapear campos directos
        direct_fields = [
            'codigo', 'descripcion', 'tipo', 'categoria', 'proveedor', 
            'unidad_medida', 'ubicacion', 'estado', 'marca', 'modelo', 
            'color', 'material', 'dimensiones', 'observaciones', 'especificaciones'
        ]
        
        for field in direct_fields:
            form_data[field] = herraje_data.get(field, '')
        
        # Campos numéricos
        form_data['precio_unitario'] = herraje_data.get('precio_unitario', 0.0)
        form_data['stock_actual'] = herraje_data.get('stock_actual', 0)
        form_data['stock_minimo'] = herraje_data.get('stock_minimo', 1)
        form_data['peso'] = herraje_data.get('peso', 0.0)
        
        return form_data


class HerrajeObrasDialog:
    """Diálogo especializado para asignar herrajes a obras."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
    
    def show_asignar_obra_dialog(self, herraje_data: Dict[str, Any]) -> bool:
        """Muestra diálogo para asignar herraje a una obra."""
        from rexus.utils.dialog_utils import BaseFormDialog
        from PyQt6.QtWidgets import QDialog
        
        # Configuración del formulario
        asignacion_config = {
            'title': f'Asignar a Obra - {herraje_data.get("codigo", "Herraje")}',
            'size': (500, 350),
            'groups': [
                {
                    'title': 'Información del Herraje',
                    'fields': [
                        {
                            'name': 'info_herraje',
                            'label': 'Herraje',
                            'type': 'text',
                            'default': f"{herraje_data.get('codigo', '')} - {herraje_data.get('descripcion', '')}",
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Asignación a Obra',
                    'fields': [
                        {
                            'name': 'obra_codigo',
                            'label': 'Código de Obra',
                            'type': 'combo',
                            'options': ['OBR-2024-001', 'OBR-2024-002', 'OBR-2024-003'],  # Se llenará dinámicamente
                            'required': True
                        },
                        {
                            'name': 'cantidad',
                            'label': 'Cantidad',
                            'type': 'int',
                            'required': True,
                            'min': 1,
                            'max': 99999,
                            'default': 1
                        },
                        {
                            'name': 'fecha_necesaria',
                            'label': 'Fecha Necesaria',
                            'type': 'date',
                            'required': False,
                            'default': date.today()
                        },
                        {
                            'name': 'observaciones',
                            'label': 'Observaciones',
                            'type': 'textarea',
                            'height': 60,
                            'required': False
                        }
                    ]
                }
            ]
        }
        
        dialog = BaseFormDialog(
            self.parent,
            asignacion_config['title'],
            asignacion_config['size']
        )
        
        # Agregar campos
        for group in asignacion_config['groups']:
            dialog.add_form_group(group['title'], group['fields'])
        
        # Deshabilitar el campo de información del herraje
        if 'info_herraje' in dialog.form_fields:
            dialog.form_fields['info_herraje']['widget'].setEnabled(False)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            asignacion_data = dialog.get_form_data()
            
            # Procesar asignación a través del controlador
            if self.controller:
                success = self.controller.asignar_herraje_obra(
                    herraje_data.get('id'),
                    asignacion_data
                )
                
                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Asignación Exitosa",
                        f"El herraje {herraje_data.get('codigo')} ha sido asignado a la obra {asignacion_data.get('obra_codigo')}."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        "Error en Asignación",
                        "No se pudo completar la asignación del herraje a la obra."
                    )
        
        return False


class HerrajePedidosDialog:
    """Diálogo especializado para crear pedidos de herrajes."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
    
    def show_crear_pedido_dialog(self, herrajes_seleccionados: list = None) -> bool:
        """Muestra diálogo para crear un pedido de herrajes."""
        from rexus.utils.dialog_utils import BaseFormDialog
        from PyQt6.QtWidgets import QDialog
        
        # Configuración del formulario
        pedido_config = {
            'title': 'Crear Pedido de Herrajes',
            'size': (600, 450),
            'groups': [
                {
                    'title': 'Información del Pedido',
                    'fields': [
                        {
                            'name': 'numero_pedido',
                            'label': 'Número de Pedido',
                            'type': 'text',
                            'required': True,
                            'default': self._generar_numero_pedido()
                        },
                        {
                            'name': 'proveedor',
                            'label': 'Proveedor',
                            'type': 'combo',
                            'options': ['Herrajes del Sur SA', 'Accesorios Premium SRL', 'Herrajes Industriales SA'],
                            'required': True
                        },
                        {
                            'name': 'fecha_pedido',
                            'label': 'Fecha del Pedido',
                            'type': 'date',
                            'required': True,
                            'default': date.today()
                        },
                        {
                            'name': 'fecha_entrega',
                            'label': 'Fecha Entrega Estimada',
                            'type': 'date',
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Detalles',
                    'fields': [
                        {
                            'name': 'prioridad',
                            'label': 'Prioridad',
                            'type': 'combo',
                            'options': ['BAJA', 'NORMAL', 'ALTA', 'URGENTE'],
                            'required': True,
                            'default': 'NORMAL'
                        },
                        {
                            'name': 'observaciones',
                            'label': 'Observaciones',
                            'type': 'textarea',
                            'height': 80,
                            'required': False
                        }
                    ]
                }
            ]
        }
        
        dialog = BaseFormDialog(
            self.parent,
            pedido_config['title'],
            pedido_config['size']
        )
        
        # Agregar campos
        for group in pedido_config['groups']:
            dialog.add_form_group(group['title'], group['fields'])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pedido_data = dialog.get_form_data()
            
            # Crear pedido a través del controlador
            if self.controller:
                success = self.controller.crear_pedido_herrajes(
                    pedido_data,
                    herrajes_seleccionados or []
                )
                
                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Pedido Creado",
                        f"El pedido {pedido_data.get('numero_pedido')} ha sido creado exitosamente."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        "Error al Crear Pedido",
                        "No se pudo crear el pedido de herrajes."
                    )
        
        return False
    
    def _generar_numero_pedido(self) -> str:
        """Genera un número de pedido automático."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        return f"PED-HER-{timestamp}"