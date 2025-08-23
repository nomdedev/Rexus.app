#!/usr/bin/env python3
"""
Sistema de Validación de Entrada Completa - Rexus.app

Proporciona validación robusta para todos los tipos de entrada del usuario
para prevenir inyecciones SQL, XSS, y otros ataques de seguridad.

Fecha: 15/08/2025
Componente: Seguridad - Validación de Entrada
"""

import re
import html
import json
import decimal
                    })
        def crear_usuario(self, nombre, email):
            # Los argumentos ya están validados y sanitizados
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obtener argumentos del método (excluyendo 'self')
            func_args = func.__code__.co_varnames[1:func.__code__.co_argcount]
            arg_values = dict(zip(func_args, args[1:]))  # Excluir 'self'
            arg_values.update(kwargs)
            
            # Validar argumentos
            is_valid, errors, sanitized_data = input_validator.validate_form_data(arg_values, validation_schema)
            
            if not is_valid:
                error_msg = "; ".join(errors.values())
                raise ValueError(f"Datos de entrada no válidos: {error_msg}")
            
            # Llamar función original con datos sanitizados
            new_kwargs = {k: v for k, v in sanitized_data.items() if k not in func_args[:len(args)-1]}
            new_args = args[:1] + tuple(sanitized_data.get(arg, args[i+1]) for i, arg in enumerate(func_args[:len(args)-1]))
            
            return func(*new_args, **new_kwargs)
        return wrapper
    return decorator