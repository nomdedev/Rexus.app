#!/usr/bin/env python3
"""
Utilidades de formateo de datos - Rexus.app v2.0.0

Proporciona funciones para formatear datos de manera consistente en toda la aplicación.
Maneja formateo de moneda, números, fechas, tamaños de archivo y texto.
"""

import logging
from typing import Union, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
import re

logger = logging.getLogger(__name__)


class CurrencyFormatter:
    """
    Formateador de moneda configurable para Rexus.app
    """

    def __init__(self, currency_symbol: str = "$", decimal_places: int = 2, locale: str = "es_AR"):
        """
        Inicializar formateador de moneda

        Args:
            currency_symbol: Símbolo de moneda
            decimal_places: Número de decimales
            locale: Configuración regional
        """
        self.currency_symbol = currency_symbol
        self.decimal_places = decimal_places
        self.locale = locale

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
            decimal_amount = Decimal(str(amount))

            # Redondear según la configuración
            rounded_amount = decimal_amount.quantize(
                Decimal(f"1e-{self.decimal_places}"),
                rounding=ROUND_HALF_UP
            )

            # Formatear con separadores de miles
            formatted_number = f"{rounded_amount:,.{self.decimal_places}f}"

            # Aplicar configuración regional
            if self.locale == "es_AR":
                formatted_number = formatted_number.replace(",", "X").replace(".", ",").replace("X", ".")

            return f"{self.currency_symbol}{formatted_number}"

        except (ValueError, TypeError, Exception) as e:
            logger.warning(f"Error formateando cantidad {amount}: {str(e)}")
            return f"{self.currency_symbol}0.00"

    def parse_amount(self, formatted_amount: str) -> Optional[Decimal]:
        """
        Parsea una cantidad formateada de vuelta a Decimal.

        Args:
            formatted_amount: Cantidad formateada

        Returns:
            Decimal: Cantidad parseada o None si falla
        """
        if not formatted_amount:
            return None

        try:
            # Remover símbolo de moneda y espacios
            clean_amount = formatted_amount.replace(self.currency_symbol, "").strip()

            # Manejar formato argentino
            if self.locale == "es_AR":
                clean_amount = clean_amount.replace(".", "").replace(",", ".")

            return Decimal(clean_amount)

        except (ValueError, TypeError):
            return None


class NumberFormatter:
    """
    Formateador de números con opciones avanzadas
    """

    def __init__(self, decimal_places: int = 2, use_thousands_separator: bool = True):
        """
        Inicializar formateador de números

        Args:
            decimal_places: Número de decimales
            use_thousands_separator: Usar separador de miles
        """
        self.decimal_places = decimal_places
        self.use_thousands_separator = use_thousands_separator

    def format_number(self, number: Union[int, float, Decimal, str]) -> str:
        """
        Formatea un número con opciones configurables.

        Args:
            number: Número a formatear

        Returns:
            str: Número formateado
        """
        if number is None:
            return "0"

        try:
            decimal_num = Decimal(str(number))
            rounded_num = decimal_num.quantize(
                Decimal(f"1e-{self.decimal_places}"),
                rounding=ROUND_HALF_UP
            )

            if self.use_thousands_separator:
                return f"{rounded_num:,.{self.decimal_places}f}"
            else:
                return f"{rounded_num:.{self.decimal_places}f}"

        except (ValueError, TypeError):
            return "0"

    def format_percentage(self, value: Union[int, float, Decimal], total: Union[int, float, Decimal]) -> str:
        """
        Formatea un porcentaje.

        Args:
            value: Valor actual
            total: Valor total

        Returns:
            str: Porcentaje formateado
        """
        if total == 0:
            return "0.00%"

        try:
            percentage = (Decimal(str(value)) / Decimal(str(total))) * 100
            return f"{percentage:.2f}%"
        except (ValueError, TypeError, ZeroDivisionError):
            return "0.00%"

    def format_file_size(self, bytes_size: Union[int, float]) -> str:
        """
        Formatea un tamaño de archivo en unidades legibles.

        Args:
            bytes_size: Tamaño en bytes

        Returns:
            str: Tamaño formateado
        """
        if bytes_size is None or bytes_size < 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(bytes_size)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return ".1f"


class DateFormatter:
    """
    Formateador de fechas con soporte para múltiples formatos
    """

    def __init__(self, locale: str = "es_AR"):
        """
        Inicializar formateador de fechas

        Args:
            locale: Configuración regional
        """
        self.locale = locale

    def format_date(self, date_value: Union[date, datetime, str],
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

        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando fecha {date_value}: {str(e)}")
            return ""

    def format_datetime(self, datetime_value: Union[datetime, str],
                       format_string: str = "%d/%m/%Y %H:%M:%S") -> str:
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
                parsed_datetime = datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
                return parsed_datetime.strftime(format_string)
            elif isinstance(datetime_value, datetime):
                return datetime_value.strftime(format_string)
            else:
                return str(datetime_value)

        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando datetime {datetime_value}: {str(e)}")
            return ""

    def get_relative_time(self, date_obj: Union[datetime, date, str]) -> str:
        """
        Obtiene tiempo relativo (ej: "hace 2 horas", "ayer", etc.)

        Args:
            date_obj: Fecha a convertir

        Returns:
            str: Tiempo relativo
        """
        if date_obj is None:
            return ""

        try:
            if isinstance(date_obj, str):
                if 'T' in date_obj:
                    target_date = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
                else:
                    target_date = datetime.strptime(date_obj, '%Y-%m-%d')
            elif isinstance(date_obj, date) and not isinstance(date_obj, datetime):
                target_date = datetime.combine(date_obj, datetime.min.time())
            else:
                target_date = date_obj

            now = datetime.now()
            diff = now - target_date

            if diff.days == 0:
                if diff.seconds < 60:
                    return "ahora mismo"
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
                else:
                    hours = diff.seconds // 3600
                    return f"hace {hours} hora{'s' if hours != 1 else ''}"
            elif diff.days == 1:
                return "ayer"
            elif diff.days < 7:
                return f"hace {diff.days} días"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"hace {weeks} semana{'s' if weeks != 1 else ''}"
            elif diff.days < 365:
                months = diff.days // 30
                return f"hace {months} mes{'es' if months != 1 else ''}"
            else:
                years = diff.days // 365
                return f"hace {years} año{'s' if years != 1 else ''}"

        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Error calculando tiempo relativo para {date_obj}: {str(e)}")
            return ""


class TextFormatter:
    """
    Formateador de texto con funciones útiles
    """

    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Trunca texto a una longitud máxima.

        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo a agregar si se trunca

        Returns:
            str: Texto truncado
        """
        if not text or len(text) <= max_length:
            return text or ""

        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def capitalize_words(text: str) -> str:
        """
        Capitaliza la primera letra de cada palabra.

        Args:
            text: Texto a capitalizar

        Returns:
            str: Texto capitalizado
        """
        if not text:
            return ""

        return " ".join(word.capitalize() for word in text.split())

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normaliza espacios en blanco (remueve espacios extra).

        Args:
            text: Texto a normalizar

        Returns:
            str: Texto normalizado
        """
        if not text:
            return ""

        return " ".join(text.split())

    @staticmethod
    def remove_accents(text: str) -> str:
        """
        Remueve acentos de un texto.

        Args:
            text: Texto con acentos

        Returns:
            str: Texto sin acentos
        """
        if not text:
            return ""

        # Mapa de caracteres con acentos
        accents_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }

        for accented, normal in accents_map.items():
            text = text.replace(accented, normal)

        return text

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convierte texto a slug (URL-friendly).

        Args:
            text: Texto a convertir

        Returns:
            str: Slug generado
        """
        if not text:
            return ""

        # Remover acentos y convertir a minúsculas
        text = TextFormatter.remove_accents(text).lower()

        # Reemplazar caracteres no alfanuméricos con guiones
        text = re.sub(r'[^a-z0-9]+', '-', text)

        # Remover guiones al inicio y final
        return text.strip('-')


# Instancias globales para uso común
default_currency_formatter = CurrencyFormatter()
default_number_formatter = NumberFormatter()
default_date_formatter = DateFormatter()
default_text_formatter = TextFormatter()


# Funciones de conveniencia para uso directo
def format_currency(amount: Union[int, float, Decimal, str]) -> str:
    """Formatea una cantidad como moneda usando el formateador por defecto."""
    return default_currency_formatter.format_amount(amount)


def format_number(number: Union[int, float, Decimal, str]) -> str:
    """Formatea un número usando el formateador por defecto."""
    return default_number_formatter.format_number(number)


def format_percentage(value: Union[int, float, Decimal], total: Union[int, float, Decimal]) -> str:
    """Formatea un porcentaje usando el formateador por defecto."""
    return default_number_formatter.format_percentage(value, total)


def format_file_size(bytes_size: Union[int, float]) -> str:
    """Formatea un tamaño de archivo usando el formateador por defecto."""
    return default_number_formatter.format_file_size(bytes_size)


def format_date(date_value: Union[date, datetime, str], format_string: str = "%d/%m/%Y") -> str:
    """Formatea una fecha usando el formateador por defecto."""
    return default_date_formatter.format_date(date_value, format_string)


def format_datetime(datetime_value: Union[datetime, str], format_string: str = "%d/%m/%Y %H:%M:%S") -> str:
    """Formatea una fecha y hora usando el formateador por defecto."""
    return default_date_formatter.format_datetime(datetime_value, format_string)


def get_relative_time(date_obj: Union[datetime, date, str]) -> str:
    """Obtiene tiempo relativo usando el formateador por defecto."""
    return default_date_formatter.get_relative_time(date_obj)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto usando el formateador por defecto."""
    return default_text_formatter.truncate_text(text, max_length, suffix)


def capitalize_words(text: str) -> str:
    """Capitaliza palabras usando el formateador por defecto."""
    return default_text_formatter.capitalize_words(text)


def slugify(text: str) -> str:
    """Convierte a slug usando el formateador por defecto."""
    return default_text_formatter.slugify(text)
