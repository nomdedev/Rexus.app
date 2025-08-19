"""
Sistema de validación de formularios para Rexus.app

Proporciona validadores comunes para campos de formularios
con feedback visual integrado.
"""

import re
from typing import Optional, Tuple, List, Dict
from PyQt6.QtWidgets import QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import QDate


class FormValidator:
    """Validador de formularios con feedback visual."""

    # Estilos para feedback visual
    STYLE_ERROR = """
        border: 2px solid #e74c3c;
        background-color: #ffeaea;
    """

    STYLE_SUCCESS = """
        border: 2px solid #27ae60;
        background-color: #eafaf1;
    """

    STYLE_NORMAL = """
        border: 1px solid #bdc3c7;
        background-color: white;
    """

    @staticmethod
    def validar_campo_obligatorio(campo,
valor: str,
        nombre_campo: str) -> Tuple[bool,
        str]:
        """
        Valida que un campo obligatorio no esté vacío.

        Args:
            campo: Widget del formulario
            valor: Valor a validar
            nombre_campo: Nombre del campo para mensajes

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Manejar None y convertir a string si es necesario
        if valor is None:
            valor = ""
        elif not isinstance(valor, str):
            valor = str(valor)
            
        if not valor or not valor.strip():
            FormValidator._aplicar_estilo_error(campo)
            return False, f"{nombre_campo} es obligatorio"

        FormValidator._aplicar_estilo_success(campo)
        return True, ""

    @staticmethod
    def validar_email(campo, email: str) -> Tuple[bool, str]:
        """Valida formato de email."""
        # Manejar None y convertir a string si es necesario
        if email is None:
            email = ""
        elif not isinstance(email, str):
            email = str(email)
            
        if not email.strip():
            FormValidator._aplicar_estilo_error(campo)
            return False, "Email es obligatorio"

        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, email):
            FormValidator._aplicar_estilo_error(campo)
            return False, "Formato de email inválido"

        FormValidator._aplicar_estilo_success(campo)
        return True, ""

    @staticmethod
    def validar_telefono(campo, telefono: str) -> Tuple[bool, str]:
        """Valida formato de teléfono argentino."""
        # Manejar None y convertir a string si es necesario
        if telefono is None:
            telefono = ""
        elif not isinstance(telefono, str):
            telefono = str(telefono)
            
        if not telefono.strip():
            return True, ""  # Campo opcional

        # Patrones válidos: +54 11 1234-5678, 221-1234567, 11-12345678, etc.
        patrones = [
            r'^\+54\s?\d{2,3}\s?\d{4}-?\d{4}$',  # +54 11 1234-5678
            r'^\d{3}-?\d{7}$',                    # 221-1234567
            r'^\d{2}-?\d{8}$',                    # 11-12345678
            r'^\d{10,11}$'                        # 1112345678
        ]

        telefono_limpio = telefono.replace(' ', '').replace('-', '')

        for patron in patrones:
            if re.match(patron, telefono) or re.match(patron, telefono_limpio):
                FormValidator._aplicar_estilo_success(campo)
                return True, ""

        FormValidator._aplicar_estilo_error(campo)
        return False, "Formato de teléfono inválido (ej: 221-1234567, +54 11 1234-5678)"

    @staticmethod
    def validar_numero(campo, valor: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Tuple[bool, str]:
        """Valida que el valor sea un número válido."""
        # Manejar None y convertir a string si es necesario
        if valor is None:
            valor = ""
        elif not isinstance(valor, str):
            valor = str(valor)
            
        if not valor.strip():
            FormValidator._aplicar_estilo_error(campo)
            return False, "Valor numérico requerido"

        try:
            numero = float(valor)

            if min_val is not None and numero < min_val:
                FormValidator._aplicar_estilo_error(campo)
                return False, f"El valor debe ser mayor o igual a {min_val}"

            if max_val is not None and numero > max_val:
                FormValidator._aplicar_estilo_error(campo)
                return False, f"El valor debe ser menor o igual a {max_val}"

            FormValidator._aplicar_estilo_success(campo)
            return True, ""

        except ValueError:
            FormValidator._aplicar_estilo_error(campo)
            return False, "Valor numérico inválido"

    @staticmethod
    def validar_fecha(campo,
fecha: QDate,
        fecha_minima: Optional[QDate] = None) -> Tuple[bool,
        str]:
        """Valida una fecha."""
        if not fecha.isValid():
            FormValidator._aplicar_estilo_error(campo)
            return False, "Fecha inválida"

        if fecha_minima and fecha < fecha_minima:
            FormValidator._aplicar_estilo_error(campo)
            return False, f"La fecha debe ser posterior a {fecha_minima.toString('dd/MM/yyyy')}"

        FormValidator._aplicar_estilo_success(campo)
        return True, ""

    @staticmethod
    def validar_longitud_texto(campo,
texto: str,
        min_len: int = 0,
        max_len: int = 1000) -> Tuple[bool,
        str]:
        """Valida la longitud de un texto."""
        # Manejar None y convertir a string si es necesario
        if texto is None:
            texto = ""
        elif not isinstance(texto, str):
            texto = str(texto)
            
        longitud = len(texto.strip())

        if longitud < min_len:
            FormValidator._aplicar_estilo_error(campo)
            return False, f"Mínimo {min_len} caracteres requeridos"

        if longitud > max_len:
            FormValidator._aplicar_estilo_error(campo)
            return False, f"Máximo {max_len} caracteres permitidos"

        if longitud > 0:
            FormValidator._aplicar_estilo_success(campo)
        else:
            FormValidator._aplicar_estilo_normal(campo)

        return True, ""

    @staticmethod
    def _aplicar_estilo_error(campo):
        """Aplica estilo de error al campo."""
        campo.setStyleSheet(FormValidator.STYLE_ERROR)

    @staticmethod
    def _aplicar_estilo_success(campo):
        """Aplica estilo de éxito al campo."""
        campo.setStyleSheet(FormValidator.STYLE_SUCCESS)

    @staticmethod
    def _aplicar_estilo_normal(campo):
        """Aplica estilo normal al campo."""
        campo.setStyleSheet(FormValidator.STYLE_NORMAL)

    @staticmethod
    def limpiar_estilos(campo):
        """Limpia los estilos de validación del campo."""
        FormValidator._aplicar_estilo_normal(campo)


class FormValidatorManager:
    """Gestor de validación para formularios completos."""

    def __init__(self):
        self.validadores = {}
        self.errores = {}

    def agregar_validacion(self, campo, validador_func, *args, **kwargs):
        """
        Agrega una validación a un campo.

        Args:
            campo: Widget del formulario
            validador_func: Función de validación
            *args, **kwargs: Argumentos para la función de validación
        """
        if campo not in self.validadores:
            self.validadores[campo] = []

        self.validadores[campo].append((validador_func, args, kwargs))

    def validar_formulario(self) -> Tuple[bool, Dict[str, str]]:
        """
        Valida todo el formulario.

        Returns:
            Tuple[bool, Dict]: (es_valido, diccionario_de_errores)
        """
        self.errores.clear()
        es_valido = True

        for campo, validaciones in self.validadores.items():
            for validador_func, args, kwargs in validaciones:
                try:
                    # Obtener valor del campo según su tipo
                    if isinstance(campo, QLineEdit):
                        valor = campo.text()
                        valido, mensaje = validador_func(campo, valor, *args, **kwargs)
                    elif isinstance(campo, QComboBox):
                        valor = campo.currentText()
                        valido, mensaje = validador_func(campo, valor, *args, **kwargs)
                    elif isinstance(campo, QDateEdit):
                        valor = campo.date()
                        valido, mensaje = validador_func(campo, valor, *args, **kwargs)
                    elif isinstance(campo, QTextEdit):
                        valor = campo.toPlainText()
                        valido, mensaje = validador_func(campo, valor, *args, **kwargs)
                    elif isinstance(campo, (QSpinBox, QDoubleSpinBox)):
                        valor = str(campo.value())
                        valido, mensaje = validador_func(campo, valor, *args, **kwargs)
                    else:
                        continue

                    if not valido:
                        self.errores[campo] = mensaje
                        es_valido = False
                        break  # Solo mostrar el primer error por campo

                except Exception as e:
                    self.errores[campo] = f"Error de validación: {str(e)}"
                    es_valido = False

        return es_valido, self.errores

    def limpiar_validaciones(self):
        """Limpia todas las validaciones y estilos."""
        for campo in self.validadores.keys():
            FormValidator.limpiar_estilos(campo)
        self.errores.clear()

    def obtener_mensajes_error(self) -> List[str]:
        """Obtiene lista de mensajes de error."""
        return list(self.errores.values())


# Validaciones predefinidas comunes
def validacion_direccion(campo, direccion: str) -> Tuple[bool, str]:
    """Validación específica para direcciones."""
    # Manejar None y convertir a string si es necesario
    if direccion is None:
        direccion = ""
    elif not isinstance(direccion, str):
        direccion = str(direccion)
        
    if not direccion.strip():
        FormValidator._aplicar_estilo_error(campo)
        return False, "La dirección es obligatoria"

    if len(direccion.strip()) < 10:
        FormValidator._aplicar_estilo_error(campo)
        return False, "La dirección debe ser más específica (mínimo 10 caracteres)"

    FormValidator._aplicar_estilo_success(campo)
    return True, ""


def validacion_codigo_producto(campo, codigo: str) -> Tuple[bool, str]:
    """Validación para códigos de producto."""
    # Manejar None y convertir a string si es necesario
    if codigo is None:
        codigo = ""
    elif not isinstance(codigo, str):
        codigo = str(codigo)
    
    # Validar que no esté vacío después de limpiar espacios
    codigo_limpio = codigo.strip()
    if not codigo_limpio:
        FormValidator._aplicar_estilo_error(campo)
        return False, "El código es obligatorio"

    # Formato esperado: ABC-1234 o similar
    if not re.match(r'^[A-Z]{2,4}-\d{3,6}$', codigo_limpio.upper()):
        FormValidator._aplicar_estilo_error(campo)
        return False, "Formato de código inválido (ej: VID-1234, HER-5678)"

    FormValidator._aplicar_estilo_success(campo)
    return True, ""
