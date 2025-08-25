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


import logging
logger = logging.getLogger(__name__)

from ...ui.components.dialog_utils import BaseFormDialog
from ...utils.form_validators import validate_required, validate_numeric


class HerrajesDialogs:
    """Diálogos mejorados para el módulo de herrajes."""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def dialog_create_herraje(self):
        """Diálogo para crear un nuevo herraje."""
        pedido_config = {
            'title': 'Crear Herraje',
            'size': (600, 400),
            'groups': [
                {
                    'title': 'Información Básica',
                    'fields': [
                        {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
                        {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True}
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
            return pedido_data
        
        return None

    def dialog_edit_herraje(self, herraje_data):
        """Diálogo para editar un herraje existente."""
        pedido_config = {
            'title': 'Editar Herraje',
            'size': (600, 400),
            'groups': [
                {
                    'title': 'Información Básica',
                    'fields': [
                        {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
                        {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True}
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
        
        # Llenar con datos existentes
        dialog.set_form_data(herraje_data)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_form_data()
            return updated_data
        
        return None
