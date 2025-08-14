"""
Utilidades de validación extendidas - Rexus.app v2.0.0

Proporciona validadores avanzados y reglas de negocio comunes.
"""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Union, Callable
from decimal import Decimal, InvalidOperation


class ValidationResult:
    """Resultado de una validación."""

    def __init__(self, is_valid: bool = True, message: str = ""):
        self.is_valid = is_valid
        self.message = message

    def __bool__(self):
        return self.is_valid

    def __str__(self):
        return self.message if not self.is_valid else "Válido"


class AdvancedValidator:
    """Validador avanzado con reglas de negocio."""

    @staticmethod
    def validate_required(value: Any, field_name: str = "Campo") -> ValidationResult:
        """Valida que un campo sea requerido."""
        if value is None:
            return ValidationResult(False, f"{field_name} es obligatorio")

        if isinstance(value, str) and not value.strip():
            return ValidationResult(False, f"{field_name} no puede estar vacío")

        if isinstance(value, (list, dict)) and len(value) == 0:
            return ValidationResult(False, f"{field_name} no puede estar vacío")

        return ValidationResult(True)

    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = None,
                              field_name: str = "Campo") -> ValidationResult:
        """Valida la longitud de una cadena."""
        if not isinstance(value, str):
            return ValidationResult(False, f"{field_name} debe ser texto")

        length = len(value.strip())

        if length < min_length:
            return ValidationResult(False, f"{field_name} debe tener al menos {min_length} caracteres")

        if max_length and length > max_length:
            return ValidationResult(False, f"{field_name} no puede tener más de {max_length} caracteres")

        return ValidationResult(True)

    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Valida formato de email."""
        if not email:
            return ValidationResult(False, "Email es obligatorio")

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return ValidationResult(False, "Formato de email inválido")

        return ValidationResult(True)

    @staticmethod
    def validate_phone(phone: str) -> ValidationResult:
        """Valida formato de teléfono."""
        if not phone:
            return ValidationResult(False, "Teléfono es obligatorio")

        # Remover espacios y caracteres especiales para validación
        clean_phone = re.sub(r'[^\d+]', '', phone)

        if len(clean_phone) < 7:
            return ValidationResult(False, "Teléfono debe tener al menos 7 dígitos")

        if len(clean_phone) > 15:
            return ValidationResult(False, "Teléfono no puede tener más de 15 dígitos")

        return ValidationResult(True)

    @staticmethod
    def validate_number_range(value: Union[int, float, str], min_value: float = None,
                             max_value: float = None, field_name: str = "Número") -> ValidationResult:
        """Valida que un número esté en un rango específico."""
        try:
            num_value = float(value) if value is not None else None
        except (ValueError, TypeError):
            return ValidationResult(False, f"{field_name} debe ser un número válido")

        if num_value is None:
            return ValidationResult(False, f"{field_name} es obligatorio")

        if min_value is not None and num_value < min_value:
            return ValidationResult(False, f"{field_name} debe ser mayor o igual a {min_value}")

        if max_value is not None and num_value > max_value:
            return ValidationResult(False, f"{field_name} debe ser menor o igual a {max_value}")

        return ValidationResult(True)

    @staticmethod
    def validate_positive_number(value: Union[int, float, str],
                                field_name: str = "Número") -> ValidationResult:
        """Valida que un número sea positivo."""
        return AdvancedValidator.validate_number_range(value, min_value=0, field_name=field_name)

    @staticmethod
    def validate_date_range(value: Union[date, datetime, str], min_date: date = None,
                           max_date: date = None, field_name: str = "Fecha") -> ValidationResult:
        """Valida que una fecha esté en un rango específico."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return ValidationResult(False, f"{field_name} debe tener formato YYYY-MM-DD")
        elif isinstance(value, datetime):
            value = value.date()

        if not isinstance(value, date):
            return ValidationResult(False, f"{field_name} debe ser una fecha válida")

        if min_date and value < min_date:
            return ValidationResult(False, f"{field_name} no puede ser anterior a {min_date}")

        if max_date and value > max_date:
            return ValidationResult(False, f"{field_name} no puede ser posterior a {max_date}")

        return ValidationResult(True)

    @staticmethod
    def validate_future_date(value: Union[date, datetime, str],
                            field_name: str = "Fecha") -> ValidationResult:
        """Valida que una fecha sea futura."""
        return AdvancedValidator.validate_date_range(
            value, min_date=date.today(), field_name=field_name
        )

    @staticmethod
    def validate_past_date(value: Union[date, datetime, str],
                          field_name: str = "Fecha") -> ValidationResult:
        """Valida que una fecha sea pasada."""
        return AdvancedValidator.validate_date_range(
            value, max_date=date.today(), field_name=field_name
        )

    @staticmethod
    def validate_codigo_formato(codigo: str, pattern: str = None,
                               field_name: str = "Código") -> ValidationResult:
        """Valida formato de código."""
        if not codigo:
            return ValidationResult(False, f"{field_name} es obligatorio")

        if pattern:
            if not re.match(pattern, codigo):
                return ValidationResult(False, f"{field_name} no tiene el formato correcto")

        # Validación básica: solo alfanuméricos y guiones
        if not re.match(r'^[A-Za-z0-9\-_]+$', codigo):
            return ValidationResult(False, f"{field_name} solo puede contener letras, números, guiones y guiones bajos")

        return ValidationResult(True)

    @staticmethod
    def validate_decimal_precision(value: Union[str, float, Decimal],
                                  max_digits: int, decimal_places: int,
                                  field_name: str = "Valor") -> ValidationResult:
        """Valida precisión decimal."""
        try:
            if isinstance(value, str):
                decimal_value = Decimal(value)
            else:
                decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return ValidationResult(False, f"{field_name} debe ser un número válido")

        # Verificar dígitos totales
        sign, digits, exponent = decimal_value.as_tuple()
        total_digits = len(digits)

        if total_digits > max_digits:
            return ValidationResult(False, f"{field_name} no puede tener más de {max_digits} dígitos")

        # Verificar decimales
        if exponent < 0 and abs(exponent) > decimal_places:
            return ValidationResult(False, f"{field_name} no puede tener más de {decimal_places} decimales")

        return ValidationResult(True)


class BusinessValidator:
    """Validador con reglas de negocio específicas de Rexus."""

    @staticmethod
    def validate_obra_codigo(codigo: str) -> ValidationResult:
        """Valida código de obra."""
        if not codigo:
            return ValidationResult(False, "Código de obra es obligatorio")

        # Formato: OBR-YYYY-NNN
        pattern = r'^OBR-\d{4}-\d{3}$'
        if not re.match(pattern, codigo):
            return ValidationResult(False, "Código debe tener formato OBR-YYYY-NNN")

        return ValidationResult(True)

    @staticmethod
    def validate_usuario_codigo(usuario: str) -> ValidationResult:
        """Valida código de usuario."""
        if not usuario:
            return ValidationResult(False, "Usuario es obligatorio")

        if len(usuario) < 3:
            return ValidationResult(False, "Usuario debe tener al menos 3 caracteres")

        if len(usuario) > 20:
            return ValidationResult(False, "Usuario no puede tener más de 20 caracteres")

        if not re.match(r'^[a-zA-Z0-9_]+$', usuario):
            return ValidationResult(False, "Usuario solo puede contener letras, números y guiones bajos")

        return ValidationResult(True)

    @staticmethod
    def validate_password_strength(password: str) -> ValidationResult:
        """Valida fortaleza de contraseña."""
        if not password:
            return ValidationResult(False, "Contraseña es obligatoria")

        if len(password) < 8:
            return ValidationResult(False, "Contraseña debe tener al menos 8 caracteres")

        if len(password) > 128:
            return ValidationResult(False, "Contraseña no puede tener más de 128 caracteres")

        # Al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            return ValidationResult(False, "Contraseña debe contener al menos una letra minúscula")

        # Al menos una letra mayúscula
        if not re.search(r'[A-Z]', password):
            return ValidationResult(False, "Contraseña debe contener al menos una letra mayúscula")

        # Al menos un número
        if not re.search(r'\d', password):
            return ValidationResult(False, "Contraseña debe contener al menos un número")

        return ValidationResult(True)

    @staticmethod
    def validate_inventario_codigo(codigo: str) -> ValidationResult:
        """Valida código de inventario."""
        if not codigo:
            return ValidationResult(False, "Código de inventario es obligatorio")

        # Formato: INV-XXX-NNNN
        pattern = r'^INV-[A-Z]{3}-\d{4}$'
        if not re.match(pattern, codigo):
            return ValidationResult(False, "Código debe tener formato INV-XXX-NNNN")

        return ValidationResult(True)

    @staticmethod
    def validate_orden_compra(numero_orden: str) -> ValidationResult:
        """Valida número de orden de compra."""
        if not numero_orden:
            return ValidationResult(False, "Número de orden es obligatorio")

        # Formato: OC-YYYY-NNNN
        pattern = r'^OC-\d{4}-\d{4}$'
        if not re.match(pattern, numero_orden):
            return ValidationResult(False, "Número debe tener formato OC-YYYY-NNNN")

        return ValidationResult(True)

    @staticmethod
    def validate_presupuesto_coherente(presupuesto_min: float, presupuesto_max: float) -> ValidationResult:
        """Valida coherencia entre presupuestos mínimo y máximo."""
        if presupuesto_min is not None and presupuesto_max is not None:
            if presupuesto_min > presupuesto_max:
                return ValidationResult(False, "Presupuesto mínimo no puede ser mayor al máximo")

        return ValidationResult(True)

    @staticmethod
    def validate_fechas_coherentes(fecha_inicio: Union[date, datetime, str],
                                  fecha_fin: Union[date, datetime, str]) -> ValidationResult:
        """Valida coherencia entre fechas de inicio y fin."""
        # Convertir strings a fecha si es necesario
        if isinstance(fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            except ValueError:
                return ValidationResult(False, "Fecha de inicio debe tener formato YYYY-MM-DD")

        if isinstance(fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                return ValidationResult(False, "Fecha de fin debe tener formato YYYY-MM-DD")

        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()

        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.date()

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            return ValidationResult(False, "Fecha de inicio no puede ser posterior a fecha de fin")

        return ValidationResult(True)


class FormValidationManager:
    """Gestor de validación para formularios complejos."""

    def __init__(self):
        self.validators = {}
        self.custom_validators = {}

    def add_field_validator(self,
field_name: str,
        validator: Callable[[Any],
        ValidationResult]):
        """Agrega un validador para un campo específico."""
        if field_name not in self.validators:
            self.validators[field_name] = []
        self.validators[field_name].append(validator)

    def add_custom_validator(self,
name: str,
        validator: Callable[[Dict],
        ValidationResult]):
        """Agrega un validador personalizado que opera sobre todo el formulario."""
        self.custom_validators[name] = validator

    def validate_form(self,
form_data: Dict[str,
        Any]) -> tuple[bool,
        List[str]]:
        """
        Valida un formulario completo.

        Args:
            form_data: Datos del formulario

        Returns:
            tuple[bool, List[str]]: (es_válido, lista_errores)
        """
        errors = []

        # Validar campos individuales
        for field_name, validators in self.validators.items():
            field_value = form_data.get(field_name)

            for validator in validators:
                result = validator(field_value)
                if not result.is_valid:
                    errors.append(result.message)
                    break  # Solo mostrar el primer error por campo

        # Validar reglas personalizadas
        for validator_name, validator in self.custom_validators.items():
            result = validator(form_data)
            if not result.is_valid:
                errors.append(result.message)

        return len(errors) == 0, errors

    def create_required_validator(self, field_name: str):
        """Crea un validador de campo requerido."""
        return lambda value: AdvancedValidator.validate_required(value, field_name)

    def create_length_validator(self,
field_name: str,
        min_length: int = 0,
        max_length: int = None):
        """Crea un validador de longitud."""
        return lambda value: AdvancedValidator.validate_string_length(
            value or "", min_length, max_length, field_name
        )

    def create_number_range_validator(self,
field_name: str,
        min_value: float = None,
        max_value: float = None):
        """Crea un validador de rango numérico."""
        return lambda value: AdvancedValidator.validate_number_range(
            value, min_value, max_value, field_name
        )


def create_obra_validator() -> FormValidationManager:
    """Crea un validador específico para obras."""
    manager = FormValidationManager()

    # Validadores de campos
    manager.add_field_validator("codigo", lambda v: BusinessValidator.validate_obra_codigo(v))
    manager.add_field_validator("nombre", manager.create_required_validator("Nombre de obra"))
    manager.add_field_validator("cliente", manager.create_required_validator("Cliente"))
    manager.add_field_validator("direccion", manager.create_required_validator("Dirección"))
    manager.add_field_validator("telefono", lambda v: AdvancedValidator.validate_phone(v))
    manager.add_field_validator("email", lambda v: AdvancedValidator.validate_email(v) if v else ValidationResult(True))
    manager.add_field_validator("presupuesto", lambda v: AdvancedValidator.validate_positive_number(v, "Presupuesto"))

    # Validadores personalizados
    def validate_fechas_obra(data):
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        if fecha_inicio and fecha_fin:
            return BusinessValidator.validate_fechas_coherentes(fecha_inicio, fecha_fin)
        return ValidationResult(True)

    manager.add_custom_validator("fechas_coherentes", validate_fechas_obra)

    return manager


def create_usuario_validator() -> FormValidationManager:
    """Crea un validador específico para usuarios."""
    manager = FormValidationManager()

    manager.add_field_validator("usuario", lambda v: BusinessValidator.validate_usuario_codigo(v))
    manager.add_field_validator("password", lambda v: BusinessValidator.validate_password_strength(v))
    manager.add_field_validator("nombre", manager.create_required_validator("Nombre"))
    manager.add_field_validator("apellido", manager.create_required_validator("Apellido"))
    manager.add_field_validator("email", lambda v: AdvancedValidator.validate_email(v))

    return manager


def create_inventario_validator() -> FormValidationManager:
    """Crea un validador específico para inventario."""
    manager = FormValidationManager()

    manager.add_field_validator("codigo", lambda v: BusinessValidator.validate_inventario_codigo(v))
    manager.add_field_validator("descripcion", manager.create_required_validator("Descripción"))
    manager.add_field_validator("tipo", manager.create_required_validator("Tipo"))
    manager.add_field_validator("importe", lambda v: AdvancedValidator.validate_positive_number(v, "Importe"))
    manager.add_field_validator("stock_actual", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock actual"))
    manager.add_field_validator("stock_minimo", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock mínimo"))

    return manager
