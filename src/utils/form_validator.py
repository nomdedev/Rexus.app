"""
Form Validator Utility
Provides comprehensive validation for form inputs and user data.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple

class FormValidator:
    """
    Comprehensive form validation utility for Rexus.app
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Email regex pattern
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Phone regex pattern (Spain format)
        self.phone_pattern = re.compile(
            r'^(\+34|0034|34)?[6-9][0-9]{8}$'
        )
        
        # NIF/CIF pattern
        self.nif_pattern = re.compile(r'^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$')
        self.cif_pattern = re.compile(r'^[ABCDEFGHJNPQRSUVW][0-9]{7}[0-9A-J]$')
        
        # Product code pattern
        self.product_code_pattern = re.compile(r'^[A-Z0-9\-_]{3,20}$')
        
        # Password strength requirements
        self.password_min_length = 8
        self.password_max_length = 128
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not email:
            return False, "Email es requerido"
        
        if len(email) > 254:
            return False, "Email demasiado largo (máximo 254 caracteres)"
        
        if not self.email_pattern.match(email):
            return False, "Formato de email inválido"
        
        return True, ""
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not username:
            return False, "Nombre de usuario es requerido"
        
        if len(username) < 3:
            return False, "Nombre de usuario debe tener al menos 3 caracteres"
        
        if len(username) > 50:
            return False, "Nombre de usuario demasiado largo (máximo 50 caracteres)"
        
        # Only alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Nombre de usuario solo puede contener letras, números, _ y -"
        
        return True, ""
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not password:
            return False, "Contraseña es requerida"
        
        if len(password) < self.password_min_length:
            return False, f"Contraseña debe tener al menos {self.password_min_length} caracteres"
        
        if len(password) > self.password_max_length:
            return False, f"Contraseña demasiado larga (máximo {self.password_max_length} caracteres)"
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False, "Contraseña debe contener al menos una letra mayúscula"
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False, "Contraseña debe contener al menos una letra minúscula"
        
        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            return False, "Contraseña debe contener al menos un número"
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Contraseña debe contener al menos un carácter especial"
        
        return True, ""
    
    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Phone is optional
        
        # Remove spaces and hyphens
        clean_phone = re.sub(r'[\s-]', '', phone)
        
        if not self.phone_pattern.match(clean_phone):
            return False, "Formato de teléfono inválido (ejemplo: +34600123456)"
        
        return True, ""
    
    def validate_nif_cif(self, document: str) -> Tuple[bool, str]:
        """
        Validate NIF/CIF format.
        
        Args:
            document: NIF or CIF to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not document:
            return True, ""  # Document is optional
        
        document = document.upper().replace(' ', '')
        
        if self.nif_pattern.match(document):
            # Validate NIF check digit
            nif_letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
            number = document[:-1]
            letter = document[-1]
            
            if nif_letters[int(number) % 23] == letter:
                return True, ""
            else:
                return False, "NIF inválido (dígito de control incorrecto)"
        
        elif self.cif_pattern.match(document):
            return True, ""  # CIF validation is more complex, basic format check for now
        
        else:
            return False, "Formato de NIF/CIF inválido"
    
    def validate_product_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate product code format.
        
        Args:
            code: Product code to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not code:
            return False, "Código de producto es requerido"
        
        if not self.product_code_pattern.match(code):
            return False, "Código debe tener 3-20 caracteres alfanuméricos, guiones o guiones bajos"
        
        return True, ""
    
    def validate_price(self, price: Any) -> Tuple[bool, str]:
        """
        Validate price format and range.
        
        Args:
            price: Price to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if price is None or price == "":
            return False, "Precio es requerido"
        
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            return False, "Precio debe ser un número válido"
        
        if price_float < 0:
            return False, "Precio no puede ser negativo"
        
        if price_float > 999999.99:
            return False, "Precio demasiado alto (máximo 999,999.99)"
        
        return True, ""
    
    def validate_quantity(self, quantity: Any) -> Tuple[bool, str]:
        """
        Validate quantity format and range.
        
        Args:
            quantity: Quantity to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if quantity is None or quantity == "":
            return False, "Cantidad es requerida"
        
        try:
            quantity_float = float(quantity)
        except (ValueError, TypeError):
            return False, "Cantidad debe ser un número válido"
        
        if quantity_float < 0:
            return False, "Cantidad no puede ser negativa"
        
        if quantity_float > 999999:
            return False, "Cantidad demasiado alta (máximo 999,999)"
        
        return True, ""
    
    def validate_text_field(self, text: str, field_name: str, 
                           min_length: int = 0, max_length: int = 255, 
                           required: bool = True) -> Tuple[bool, str]:
        """
        Validate text field with custom requirements.
        
        Args:
            text: Text to validate
            field_name: Name of the field for error messages
            min_length: Minimum length required
            max_length: Maximum length allowed
            required: Whether field is required
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text or text.strip() == "":
            if required:
                return False, f"{field_name} es requerido"
            else:
                return True, ""
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f"{field_name} debe tener al menos {min_length} caracteres"
        
        if len(text) > max_length:
            return False, f"{field_name} demasiado largo (máximo {max_length} caracteres)"
        
        return True, ""
    
    def sanitize_html(self, text: str) -> str:
        """
        Basic HTML sanitization to prevent XSS.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Replace HTML entities
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }
        
        sanitized = text
        for char, replacement in replacements.items():
            sanitized = sanitized.replace(char, replacement)
        
        return sanitized
    
    def validate_user_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete user form data.
        
        Args:
            form_data: Dictionary with user form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate username
        valid, error = self.validate_username(form_data.get('usuario', ''))
        if not valid:
            errors.append(error)
        
        # Validate email
        email = form_data.get('email', '')
        if email:  # Only validate if provided
            valid, error = self.validate_email(email)
            if not valid:
                errors.append(error)
        
        # Validate password
        valid, error = self.validate_password(form_data.get('password', ''))
        if not valid:
            errors.append(error)
        
        # Validate full name
        valid, error = self.validate_text_field(
            form_data.get('nombre_completo', ''), 
            'Nombre completo', 
            min_length=2, 
            max_length=100
        )
        if not valid:
            errors.append(error)
        
        # Validate phone if provided
        phone = form_data.get('telefono', '')
        if phone:
            valid, error = self.validate_phone(phone)
            if not valid:
                errors.append(error)
        
        return len(errors) == 0, errors

# Global validator instance
form_validator = FormValidator()

def validate_form_data(form_data: Dict[str, Any], form_type: str) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate different form types.
    
    Args:
        form_data: Form data to validate
        form_type: Type of form ('user', 'product', 'login')
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    if form_type == 'user':
        return form_validator.validate_user_form(form_data)
    else:
        return True, []  # Default to valid for unknown types