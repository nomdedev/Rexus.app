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
Diálogos mejorados para Usuarios usando utilidades nuevas - Rexus.app v2.0.0

Implementa diálogos CRUD modernos usando las utilidades dialog_utils.py
"""


import logging
logger = logging.getLogger(__name__)

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
                    ,
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
                    ,
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
                        ,
                        f"La contraseña de {user_data.get('usuario')} ha sido actualizada."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        ,
                        "No se pudo actualizar la contraseña."
                    )

        return False
