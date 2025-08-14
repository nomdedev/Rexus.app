"""
Utilidades de formateo de datos - Rexus.app v2.0.0

Proporciona funciones para formatear datos de manera consistente en toda la aplicación.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Union
from decimal import Decimal, ROUND_HALF_UP


class CurrencyFormatter:
    """Formateador de moneda."""

    def __init__(self, currency_symbol: str = "$", decimal_places: int = 2):
        self.currency_symbol = currency_symbol
        self.decimal_places = decimal_places

    def format_amount(self, amount: Union[int, float, Decimal, str]) -> str:
        """
        Formatea una cantidad como moneda.

        Args:
            amount: Cantidad a formatear

        Returns:
            str: Cantidad formateada como moneda
        """
        if amount is None:
            return f"{self.currency_symbol}0.00"

        try:
            # Convertir a Decimal para precisión
            if isinstance(amount, str):
                decimal_amount = Decimal(amount)
            else:
                decimal_amount = Decimal(str(amount))

            # Redondear a los decimales especificados
            rounded_amount = decimal_amount.quantize(
                Decimal('0.01') if self.decimal_places == 2 else Decimal('0.' + '0' * self.decimal_places),
                rounding=ROUND_HALF_UP
            )

            # Formatear con separadores de miles
            formatted = f"{rounded_amount:,.{self.decimal_places}f}"

            return f"{self.currency_symbol}{formatted}"

        except (ValueError, TypeError, ArithmeticError):
            return f"{self.currency_symbol}0.00"

    def format_amount_short(self,
amount: Union[int,
        float,
        Decimal,
        str]) -> str:
        """
        Formatea una cantidad como moneda en formato corto (K, M, etc.).

        Args:
            amount: Cantidad a formatear

        Returns:
            str: Cantidad formateada en formato corto
        """
        if amount is None:
            return f"{self.currency_symbol}0"

        try:
            num_amount = float(amount)

            if abs(num_amount) >= 1_000_000:
                return f"{self.currency_symbol}{num_amount/1_000_000:.1f}M"
            elif abs(num_amount) >= 1_000:
                return f"{self.currency_symbol}{num_amount/1_000:.1f}K"
            else:
                return f"{self.currency_symbol}{num_amount:.0f}"

        except (ValueError, TypeError):
            return f"{self.currency_symbol}0"


class DateFormatter:
    """Formateador de fechas."""

    @staticmethod
    def format_date(date_value: Union[date,
datetime,
        str],
        format_string: str = "%d/%m/%Y") -> str:
        """
        Formatea una fecha.

        Args:
            date_value: Fecha a formatear
            format_string: Formato de salida

        Returns:
            str: Fecha formateada
        """
        if date_value is None:
            return ""

        try:
            if isinstance(date_value, str):
                # Intentar parsear string como fecha ISO
                if 'T' in date_value:  # DateTime ISO format
                    parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                else:  # Date ISO format
                    parsed_date = datetime.strptime(date_value, '%Y-%m-%d')
                return parsed_date.strftime(format_string)
            elif isinstance(date_value, datetime):
                return date_value.strftime(format_string)
            elif isinstance(date_value, date):
                return date_value.strftime(format_string)
            else:
                return str(date_value)
        except (ValueError, TypeError):
            return str(date_value) if date_value else ""

    @staticmethod
    def format_datetime(datetime_value: Union[datetime, str],
                       format_string: str = "%d/%m/%Y %H:%M") -> str:
        """
        Formatea una fecha y hora.

        Args:
            datetime_value: Fecha y hora a formatear
            format_string: Formato de salida

        Returns:
            str: Fecha y hora formateada
        """
        if datetime_value is None:
            return ""

        try:
            if isinstance(datetime_value, str):
                if 'T' in datetime_value:
                    parsed_datetime = datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
                else:
                    parsed_datetime = datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
                return parsed_datetime.strftime(format_string)
            elif isinstance(datetime_value, datetime):
                return datetime_value.strftime(format_string)
            else:
                return str(datetime_value)
        except (ValueError, TypeError):
            return str(datetime_value) if datetime_value else ""

    @staticmethod
    def format_relative_date(date_value: Union[date, datetime, str]) -> str:
        """
        Formatea una fecha de forma relativa (ej: "hace 2 días").

        Args:
            date_value: Fecha a formatear

        Returns:
            str: Fecha formateada de forma relativa
        """
        if date_value is None:
            return ""

        try:
            if isinstance(date_value, str):
                if 'T' in date_value:
                    target_date = datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
                else:
                    target_date = datetime.strptime(date_value, '%Y-%m-%d').date()
            elif isinstance(date_value, datetime):
                target_date = date_value.date()
            elif isinstance(date_value, date):
                target_date = date_value
            else:
                return str(date_value)

            today = date.today()
            diff = (today - target_date).days

            if diff == 0:
                return "Hoy"
            elif diff == 1:
                return "Ayer"
            elif diff == -1:
                return "Mañana"
            elif diff > 1:
                if diff < 7:
                    return f"Hace {diff} días"
                elif diff < 30:
                    weeks = diff // 7
                    return f"Hace {weeks} semana{'s' if weeks > 1 else ''}"
                elif diff < 365:
                    months = diff // 30
                    return f"Hace {months} mes{'es' if months > 1 else ''}"
                else:
                    years = diff // 365
                    return f"Hace {years} año{'s' if years > 1 else ''}"
            else:  # diff < -1
                diff = abs(diff)
                if diff < 7:
                    return f"En {diff} días"
                elif diff < 30:
                    weeks = diff // 7
                    return f"En {weeks} semana{'s' if weeks > 1 else ''}"
                elif diff < 365:
                    months = diff // 30
                    return f"En {months} mes{'es' if months > 1 else ''}"
                else:
                    years = diff // 365
                    return f"En {years} año{'s' if years > 1 else ''}"

        except (ValueError, TypeError):
            return str(date_value) if date_value else ""


class NumberFormatter:
    """Formateador de números."""

    @staticmethod
    def format_number(number: Union[int, float, Decimal, str],
                     decimal_places: int = 2, use_thousands_separator: bool = True) -> str:
        """
        Formatea un número.

        Args:
            number: Número a formatear
            decimal_places: Número de decimales
            use_thousands_separator: Si usar separador de miles

        Returns:
            str: Número formateado
        """
        if number is None:
            return "0"

        try:
            if isinstance(number, str):
                num_value = float(number)
            else:
                num_value = float(number)

            if use_thousands_separator:
                return f"{num_value:,.{decimal_places}f}"
            else:
                return f"{num_value:.{decimal_places}f}"

        except (ValueError, TypeError):
            return str(number) if number else "0"

    @staticmethod
    def format_percentage(value: Union[int, float, Decimal, str],
                         decimal_places: int = 1) -> str:
        """
        Formatea un número como porcentaje.

        Args:
            value: Valor a formatear (0.15 = 15%)
            decimal_places: Número de decimales

        Returns:
            str: Porcentaje formateado
        """
        if value is None:
            return "0%"

        try:
            num_value = float(value)
            percentage = num_value * 100
            return f"{percentage:.{decimal_places}f}%"
        except (ValueError, TypeError):
            return "0%"

    @staticmethod
    def format_file_size(size_bytes: Union[int, float]) -> str:
        """
        Formatea un tamaño de archivo.

        Args:
            size_bytes: Tamaño en bytes

        Returns:
            str: Tamaño formateado
        """
        if size_bytes is None:
            return "0 B"

        try:
            size = float(size_bytes)

            if size < 1024:
                return f"{size:.0f} B"
            elif size < 1024**2:
                return f"{size/1024:.1f} KB"
            elif size < 1024**3:
                return f"{size/(1024**2):.1f} MB"
            elif size < 1024**4:
                return f"{size/(1024**3):.1f} GB"
            else:
                return f"{size/(1024**4):.1f} TB"

        except (ValueError, TypeError):
            return "0 B"


class TextFormatter:
    """Formateador de texto."""

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Trunca un texto a una longitud máxima.

        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo para texto truncado

        Returns:
            str: Texto truncado
        """
        if not text:
            return ""

        if len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formatea un número de teléfono.

        Args:
            phone: Número de teléfono

        Returns:
            str: Teléfono formateado
        """
        if not phone:
            return ""

        # Remover todo excepto dígitos y +
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

        if not clean_phone:
            return phone

        # Formato argentino
        if clean_phone.startswith('+54'):
            if len(clean_phone) == 13:  # +54 11 1234-5678
                return f"+54 {clean_phone[3:5]} {clean_phone[5:9]}-{clean_phone[9:13]}"
            elif len(clean_phone) == 12:  # +54 9 11 1234-5678
                return f"+54 9 {clean_phone[4:6]} {clean_phone[6:10]}-{clean_phone[10:14]}"

        # Formato local argentino
        if len(clean_phone) == 10:  # 11 1234-5678
            return f"{clean_phone[:2]} {clean_phone[2:6]}-{clean_phone[6:10]}"
        elif len(clean_phone) == 8:  # 1234-5678
            return f"{clean_phone[:4]}-{clean_phone[4:8]}"

        return phone

    @staticmethod
    def capitalize_words(text: str) -> str:
        """
        Capitaliza cada palabra de un texto.

        Args:
            text: Texto a capitalizar

        Returns:
            str: Texto con palabras capitalizadas
        """
        if not text:
            return ""

        return ' '.join(word.capitalize() for word in text.split())

    @staticmethod
    def format_code(code: str, separator: str = "-", group_size: int = 4) -> str:
        """
        Formatea un código con separadores.

        Args:
            code: Código a formatear
            separator: Separador a usar
            group_size: Tamaño de cada grupo

        Returns:
            str: Código formateado
        """
        if not code:
            return ""

        # Remover separadores existentes
        clean_code = ''.join(c for c in code if c.isalnum())

        # Agrupar caracteres
        groups = [clean_code[i:i+group_size] for i in range(0, len(clean_code), group_size)]

        return separator.join(groups)


class StatusFormatter:
    """Formateador de estados."""

    STATUS_COLORS = {
        'ACTIVO': '#27ae60',
        'INACTIVO': '#95a5a6',
        'PENDIENTE': '#f39c12',
        'APROBADO': '#27ae60',
        'RECHAZADO': '#e74c3c',
        'COMPLETADO': '#2ecc71',
        'EN_PROCESO': '#3498db',
        'CANCELADO': '#e74c3c',
        'PAUSADO': '#f39c12',
        'PLANIFICACION': '#9b59b6',
    }

    STATUS_LABELS = {
        'ACTIVO': 'Activo',
        'INACTIVO': 'Inactivo',
        'PENDIENTE': 'Pendiente',
        'APROBADO': 'Aprobado',
        'RECHAZADO': 'Rechazado',
        'COMPLETADO': 'Completado',
        'EN_PROCESO': 'En Proceso',
        'CANCELADO': 'Cancelado',
        'PAUSADO': 'Pausado',
        'PLANIFICACION': 'Planificación',
    }

    @staticmethod
    def format_status(status: str) -> str:
        """
        Formatea un estado para mostrar.

        Args:
            status: Estado a formatear

        Returns:
            str: Estado formateado
        """
        if not status:
            return ""

        return StatusFormatter.STATUS_LABELS.get(status.upper(), status.title())

    @staticmethod
    def get_status_color(status: str) -> str:
        """
        Obtiene el color asociado a un estado.

        Args:
            status: Estado

        Returns:
            str: Color hexadecimal
        """
        if not status:
            return '#95a5a6'

        return StatusFormatter.STATUS_COLORS.get(status.upper(), '#95a5a6')

    @staticmethod
    def format_priority(priority: str) -> str:
        """
        Formatea una prioridad.

        Args:
            priority: Prioridad a formatear

        Returns:
            str: Prioridad formateada
        """
        priority_map = {
            'HIGH': '🔴 Alta',
            'MEDIUM': '🟡 Media',
            'LOW': '🟢 Baja',
            'URGENT': '[HOT] Urgente',
        }

        return priority_map.get(priority.upper() if priority else '', priority)


class TableFormatter:
    """Formateador para datos de tablas."""

    @staticmethod
    def format_table_data(data: List[Dict[str, Any]],
                         column_formatters: Dict[str, callable] = None) -> List[Dict[str, Any]]:
        """
        Formatea datos para mostrar en tabla.

        Args:
            data: Lista de diccionarios con datos
            column_formatters: Formateadores por columna

        Returns:
            List[Dict[str, Any]]: Datos formateados
        """
        if not data:
            return []

        formatted_data = []
        formatters = column_formatters or {}

        for row in data:
            formatted_row = {}
            for key, value in row.items():
                if key in formatters:
                    formatted_row[key] = formatters[key](value)
                else:
                    formatted_row[key] = str(value) if value is not None else ""
            formatted_data.append(formatted_row)

        return formatted_data

    @staticmethod
    def create_default_formatters() -> Dict[str, callable]:
        """
        Crea formateadores por defecto para columnas comunes.

        Returns:
            Dict[str, callable]: Diccionario de formateadores
        """
        currency_formatter = CurrencyFormatter()

        return {
            'fecha': lambda x: DateFormatter.format_date(x),
            'fecha_creacion': lambda x: DateFormatter.format_date(x),
            'fecha_modificacion': lambda x: DateFormatter.format_datetime(x),
            'ultimo_login': lambda x: DateFormatter.format_datetime(x),
            'precio': lambda x: currency_formatter.format_amount(x),
            'importe': lambda x: currency_formatter.format_amount(x),
            'total': lambda x: currency_formatter.format_amount(x),
            'subtotal': lambda x: currency_formatter.format_amount(x),
            'presupuesto': lambda x: currency_formatter.format_amount(x),
            'estado': lambda x: StatusFormatter.format_status(x),
            'telefono': lambda x: TextFormatter.format_phone(x),
            'stock_actual': lambda x: NumberFormatter.format_number(x, 0),
            'stock_minimo': lambda x: NumberFormatter.format_number(x, 0),
            'porcentaje': lambda x: NumberFormatter.format_percentage(x),
        }


# Instancias globales para uso común
currency_formatter = CurrencyFormatter()
date_formatter = DateFormatter()
number_formatter = NumberFormatter()
text_formatter = TextFormatter()
status_formatter = StatusFormatter()
table_formatter = TableFormatter()


def format_for_display(value: Any, data_type: str = 'text') -> str:
    """
    Función de conveniencia para formatear cualquier valor para mostrar.

    Args:
        value: Valor a formatear
        data_type: Tipo de dato ('currency',
'date',
            'datetime',
            'number',
            'percentage',
            'status',
            'phone')

    Returns:
        str: Valor formateado
    """
    if value is None:
        return ""

    if data_type == 'currency':
        return currency_formatter.format_amount(value)
    elif data_type == 'date':
        return date_formatter.format_date(value)
    elif data_type == 'datetime':
        return date_formatter.format_datetime(value)
    elif data_type == 'number':
        return number_formatter.format_number(value)
    elif data_type == 'percentage':
        return number_formatter.format_percentage(value)
    elif data_type == 'status':
        return status_formatter.format_status(value)
    elif data_type == 'phone':
        return text_formatter.format_phone(value)
    else:
        return str(value)
