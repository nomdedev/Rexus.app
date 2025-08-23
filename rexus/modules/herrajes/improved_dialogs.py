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
                        ,
                        f"El pedido {pedido_data.get('numero_pedido')} ha sido creado exitosamente."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        ,
                        "No se pudo crear el pedido de herrajes."
                    )

        return False

    def _generar_numero_pedido(self) -> str:
        """Genera un número de pedido automático."""
        from datetime import datetime
        timestamp = datetime.now().strftime()
        return f"PED-HER-{timestamp}"
