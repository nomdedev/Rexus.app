"""
Diálogos mejorados para Usuarios usando utilidades nuevas - Rexus.app v2.0.0

Implementa diálogos CRUD modernos usando las utilidades dialog_utils.py
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget
from datetime import date

from rexus.utils.dialog_utils import CrudDialogManager, create_standard_form_config
from rexus.utils.validation_utils import create_usuario_validator
from rexus.utils.format_utils import format_for_display


class UsuarioDialogManager:
    """Gestor de diálogos para el módulo de usuarios."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
        self.crud_manager = CrudDialogManager(parent_widget, controller)
        self.validator = create_usuario_validator()
    
    def get_form_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del formulario de usuario."""
        return create_standard_form_config(
            title="Gestión de Usuario",
            item_name="usuario",
            groups=[
                {
                    'title': 'Información Personal',
                    'fields': [
                        {
                            'name': 'nombre',
                            'label': 'Nome',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'apellido',
                            'label': 'Apellido',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'email',
                            'label': 'Email',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'telefono',
                            'label': 'Teléfono',
                            'type': 'text',
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Datos de Acceso',
                    'fields': [
                        {
                            'name': 'usuario',
                            'label': 'Usuario',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'password',
                            'label': 'Contraseña',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'rol',
                            'label': 'Rol',
                            'type': 'combo',
                            'options': ['ADMIN', 'SUPERVISOR', 'OPERADOR', 'CONTABILIDAD', 'INVENTARIO'],
                            'required': True,
                            'default': 'OPERADOR'
                        },
                        {
                            'name': 'estado',
                            'label': 'Estado',
                            'type': 'combo',
                            'options': ['Activo', 'Inactivo'],
                            'required': True,
                            'default': 'Activo'
                        }
                    ]
                },
                {
                    'title': 'Configuración',
                    'fields': [
                        {
                            'name': 'fecha_ingreso',
                            'label': 'Fecha de Ingreso',
                            'type': 'date',
                            'required': False,
                            'default': date.today()
                        },
                        {
                            'name': 'intentos_fallidos',
                            'label': 'Intentos Fallidos',
                            'type': 'int',
                            'required': False,
                            'min': 0,
                            'max': 10,
                            'default': 0
                        },
                        {
                            'name': 'cambiar_password',
                            'label': 'Debe cambiar contraseña',
                            'type': 'checkbox',
                            'required': False,
                            'default': False
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
                            'height': 80,
                            'required': False
                        }
                    ]
                }
            ],
            size=(700, 600)
        )
    
    def show_create_dialog(self) -> bool:
        """Muestra el diálogo para crear un nuevo usuario."""
        config = self.get_form_config()
        config['title'] = "Crear Nuevo Usuario"
        
        def create_callback(data: Dict[str, Any]) -> bool:
            # Validar datos antes de crear
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False
            
            # Crear usuario a través del controlador
            if self.controller:
                return self.controller.crear_usuario(data)
            return False
        
        return self.crud_manager.show_create_dialog(config, create_callback)
    
    def show_edit_dialog(self, user_data: Dict[str, Any]) -> bool:
        """Muestra el diálogo para editar un usuario existente."""
        config = self.get_form_config()
        config['title'] = f"Editar Usuario: {user_data.get('usuario', '')}"
        
        # Preparar datos actuales para el formulario
        current_data = self._prepare_form_data(user_data)
        
        def update_callback(data: Dict[str, Any]) -> bool:
            # No validar contraseña en edición si no se cambió
            if data.get('password') == current_data.get('password'):
                data.pop('password', None)
            
            # Validar datos
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False
            
            # Actualizar usuario a través del controlador
            if self.controller:
                return self.controller.actualizar_usuario(user_data.get('id'), data)
            return False
        
        return self.crud_manager.show_edit_dialog(config, current_data, update_callback)
    
    def confirm_and_delete(self, user_data: Dict[str, Any]) -> bool:
        """Confirma y elimina un usuario."""
        username = user_data.get('usuario', 'Usuario')
        user_id = user_data.get('id')
        
        def delete_callback() -> bool:
            if self.controller:
                return self.controller.eliminar_usuario(user_id)
            return False
        
        return self.crud_manager.confirm_and_delete(username, "usuario", delete_callback)
    
    def _prepare_form_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos del usuario para el formulario."""
        form_data = {}
        
        # Mapear campos directos
        direct_fields = ['nombre', 'apellido', 'email', 'telefono', 'usuario', 'rol', 'estado', 'observaciones']
        for field in direct_fields:
            form_data[field] = user_data.get(field, '')
        
        # Campos especiales
        form_data['password'] = '••••••••'  # Ocultar contraseña actual
        form_data['intentos_fallidos'] = user_data.get('intentos_fallidos', 0)
        form_data['cambiar_password'] = user_data.get('forzar_cambio_password', False)
        
        # Fecha de ingreso
        fecha_ingreso = user_data.get('fecha_ingreso')
        if fecha_ingreso:
            if isinstance(fecha_ingreso, str):
                try:
                    from datetime import datetime
                    form_data['fecha_ingreso'] = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
                except ValueError:
                    form_data['fecha_ingreso'] = date.today()
            else:
                form_data['fecha_ingreso'] = fecha_ingreso
        else:
            form_data['fecha_ingreso'] = date.today()
        
        return form_data


class UsuarioPermisosDialog:
    """Diálogo especializado para gestión de permisos de usuario."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
    
    def show_permisos_dialog(self, user_data: Dict[str, Any]) -> bool:
        """Muestra diálogo de permisos para un usuario."""
        from rexus.utils.dialog_utils import BaseFormDialog
        from PyQt6.QtWidgets import QDialog
        
        # Configuración de permisos por módulo
        permisos_config = {
            'title': f'Permisos - {user_data.get("usuario", "Usuario")}',
            'size': (500, 400),
            'groups': [
                {
                    'title': 'Permisos por Módulo',
                    'fields': [
                        {
                            'name': 'inventario_ver',
                            'label': 'Inventario - Ver',
                            'type': 'checkbox',
                            'default': True
                        },
                        {
                            'name': 'inventario_editar',
                            'label': 'Inventario - Editar',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'obras_ver',
                            'label': 'Obras - Ver',
                            'type': 'checkbox',
                            'default': True
                        },
                        {
                            'name': 'obras_editar',
                            'label': 'Obras - Editar',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'compras_ver',
                            'label': 'Compras - Ver',
                            'type': 'checkbox',
                            'default': True
                        },
                        {
                            'name': 'compras_editar',
                            'label': 'Compras - Editar',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'contabilidad_ver',
                            'label': 'Contabilidad - Ver',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'contabilidad_editar',
                            'label': 'Contabilidad - Editar',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'usuarios_ver',
                            'label': 'Usuarios - Ver',
                            'type': 'checkbox',
                            'default': False
                        },
                        {
                            'name': 'usuarios_editar',
                            'label': 'Usuarios - Editar',
                            'type': 'checkbox',
                            'default': False
                        }
                    ]
                }
            ]
        }
        
        dialog = BaseFormDialog(
            self.parent,
            permisos_config['title'],
            permisos_config['size']
        )
        
        # Agregar campos de permisos
        for group in permisos_config['groups']:
            dialog.add_form_group(group['title'], group['fields'])
        
        # Cargar permisos actuales del usuario
        if self.controller:
            permisos_actuales = self.controller.obtener_permisos_usuario(user_data.get('id'))
            if permisos_actuales:
                dialog.set_form_data(permisos_actuales)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            permisos_data = dialog.get_form_data()
            
            # Guardar permisos a través del controlador
            if self.controller:
                success = self.controller.actualizar_permisos_usuario(
                    user_data.get('id'), 
                    permisos_data
                )
                
                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Permisos Actualizados",
                        f"Los permisos de {user_data.get('usuario')} han sido actualizados."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        "Error",
                        "No se pudieron actualizar los permisos."
                    )
        
        return False


class UsuarioPasswordDialog:
    """Diálogo especializado para cambio de contraseñas."""
    
    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
    
    def show_reset_password_dialog(self, user_data: Dict[str, Any]) -> bool:
        """Muestra diálogo para resetear contraseña de usuario."""
        from rexus.utils.dialog_utils import BaseFormDialog
        from PyQt6.QtWidgets import QDialog
        
        password_config = {
            'title': f'Resetear Contraseña - {user_data.get("usuario", "Usuario")}',
            'size': (400, 300),
            'groups': [
                {
                    'title': 'Nueva Contraseña',
                    'fields': [
                        {
                            'name': 'nueva_password',
                            'label': 'Nueva Contraseña',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'confirmar_password',
                            'label': 'Confirmar Contraseña',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'forzar_cambio',
                            'label': 'Forzar cambio en próximo login',
                            'type': 'checkbox',
                            'default': True
                        }
                    ]
                }
            ]
        }
        
        dialog = BaseFormDialog(
            self.parent,
            password_config['title'],
            password_config['size']
        )
        
        # Agregar campos
        for group in password_config['groups']:
            dialog.add_form_group(group['title'], group['fields'])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password_data = dialog.get_form_data()
            
            # Validar que las contraseñas coincidan
            if password_data['nueva_password'] != password_data['confirmar_password']:
                from rexus.utils.message_system import show_error
                show_error(
                    self.parent,
                    "Error de Validación",
                    "Las contraseñas no coinciden."
                )
                return False
            
            # Validar fortaleza de contraseña
            from rexus.utils.validation_utils import BusinessValidator
            validation_result = BusinessValidator.validate_password_strength(
                password_data['nueva_password']
            )
            
            if not validation_result.is_valid:
                from rexus.utils.message_system import show_error
                show_error(
                    self.parent,
                    "Contraseña Débil",
                    validation_result.message
                )
                return False
            
            # Actualizar contraseña a través del controlador
            if self.controller:
                success = self.controller.resetear_password_usuario(
                    user_data.get('id'),
                    password_data['nueva_password'],
                    password_data['forzar_cambio']
                )
                
                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Contraseña Actualizada",
                        f"La contraseña de {user_data.get('usuario')} ha sido actualizada."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        "Error",
                        "No se pudo actualizar la contraseña."
                    )
        
        return False