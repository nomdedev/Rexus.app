"""
Data Sanitizer - Rexus.app
Comprehensive data sanitization for all user inputs.
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union

class DataSanitizer:
    """
    Comprehensive data sanitization utility.
    Handles XSS prevention, SQL injection prevention, and data cleaning.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Dangerous HTML tags and attributes
        self.dangerous_tags = [
            'script', 'iframe', 'object', 'embed', 'form', 'input',
            'button', 'textarea', 'select', 'option', 'meta', 'link',
            'style', 'title', 'head', 'html', 'body'
        ]
        
        self.dangerous_attributes = [
            'onload', 'onerror', 'onclick', 'onmouseover', 'onmouseout',
            'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset',
            'javascript:', 'data:', 'vbscript:', 'expression('
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|\#|\/\*|\*\/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(UNION\s+SELECT)",
            r"(\bINTO\s+OUTFILE\b)",
            r"(\bLOAD_FILE\b)"
        ]
        
        self.sql_regex = re.compile('|'.join(self.sql_patterns), re.IGNORECASE)
    
    def sanitize_string(self, text: str, max_length: int = 1000, 
                       allow_html: bool = False) -> str:
        """
        Sanitize a string input.
        
        Args:
            text: String to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
            
        Returns:
            Sanitized string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        if not allow_html:
            # Escape HTML entities
            text = html.escape(text, quote=True)
        else:
            # Remove dangerous HTML tags and attributes
            text = self._sanitize_html(text)
        
        # Check for SQL injection patterns
        if self.sql_regex.search(text):
            self.logger.warning(f"Potential SQL injection attempt detected: {text[:100]}")
            # Replace suspicious patterns with safe alternatives
            text = re.sub(self.sql_regex, '[BLOCKED]', text, flags=re.IGNORECASE)
        
        return text
    
    def sanitize_email(self, email: str) -> str:
        """
        Sanitize email address.
        
        Args:
            email: Email to sanitize
            
        Returns:
            Sanitized email
        """
        if not email or not isinstance(email, str):
            return ""
        
        # Basic cleanup
        email = email.strip().lower()
        
        # Remove dangerous characters
        email = re.sub(r'[<>"\'\\\x00-\x1f\x7f]', '', email)
        
        # Limit length
        if len(email) > 254:
            email = email[:254]
        
        return email
    
    def sanitize_phone(self, phone: str) -> str:
        """
        Sanitize phone number.
        
        Args:
            phone: Phone number to sanitize
            
        Returns:
            Sanitized phone number
        """
        if not phone or not isinstance(phone, str):
            return ""
        
        # Keep only digits, +, -, spaces, and parentheses
        phone = re.sub(r'[^0-9+\-\s()]', '', phone.strip())
        
        # Limit length
        if len(phone) > 20:
            phone = phone[:20]
        
        return phone
    
    def sanitize_numeric(self, value: Any, min_val: float = None, 
                        max_val: float = None) -> Optional[float]:
        """
        Sanitize numeric input.
        
        Args:
            value: Value to sanitize
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Sanitized numeric value or None if invalid
        """
        if value is None or value == "":
            return None
        
        try:
            # Convert to float
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point and minus
                value = re.sub(r'[^0-9.\-]', '', value)
            
            num_val = float(value)
            
            # Check bounds
            if min_val is not None and num_val < min_val:
                return min_val
            if max_val is not None and num_val > max_val:
                return max_val
            
            return num_val
            
        except (ValueError, TypeError):
            return None
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Filename to sanitize  
            
        Returns:
            Safe filename
        """
        if not filename or not isinstance(filename, str):
            return "untitled"
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            max_name_len = 255 - len(ext)
            filename = name[:max_name_len] + ext
        
        # Ensure not empty
        if not filename:
            filename = "untitled"
        
        return filename
    
    def sanitize_json_string(self, json_str: str) -> str:
        """
        Sanitize JSON string input.
        
        Args:
            json_str: JSON string to sanitize
            
        Returns:
            Sanitized JSON string
        """
        if not json_str or not isinstance(json_str, str):
            return "{}"
        
        # Remove null bytes and control characters
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str.strip())
        
        # Basic JSON validation - ensure it starts with { and ends with }
        json_str = json_str.strip()
        if not json_str.startswith('{'):
            json_str = '{' + json_str
        if not json_str.endswith('}'):
            json_str = json_str + '}'
        
        # Limit length
        if len(json_str) > 10000:
            json_str = json_str[:10000] + '}'
        
        return json_str
    
    def sanitize_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize complete form data dictionary.
        
        Args:
            form_data: Dictionary of form data
            
        Returns:
            Dictionary with sanitized data
        """
        if not isinstance(form_data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in form_data.items():
            # Sanitize key name
            clean_key = self.sanitize_string(str(key), max_length=50)
            
            if isinstance(value, str):
                # Determine sanitization based on field name
                if 'email' in clean_key.lower():
                    sanitized[clean_key] = self.sanitize_email(value)
                elif 'phone' in clean_key.lower() or 'telefono' in clean_key.lower():
                    sanitized[clean_key] = self.sanitize_phone(value)
                elif 'precio' in clean_key.lower() or 'price' in clean_key.lower():
                    sanitized[clean_key] = self.sanitize_numeric(value, min_val=0)
                elif 'cantidad' in clean_key.lower() or 'quantity' in clean_key.lower():
                    sanitized[clean_key] = self.sanitize_numeric(value, min_val=0)
                elif 'descripcion' in clean_key.lower() or 'observaciones' in clean_key.lower():
                    # Allow longer text for descriptions
                    sanitized[clean_key] = self.sanitize_string(value, max_length=2000)
                else:
                    # Default string sanitization
                    sanitized[clean_key] = self.sanitize_string(value)
            
            elif isinstance(value, (int, float)):
                sanitized[clean_key] = self.sanitize_numeric(value)
            
            elif isinstance(value, list):
                # Sanitize list elements
                sanitized[clean_key] = [
                    self.sanitize_string(str(item)) if isinstance(item, str) else item
                    for item in value[:100]  # Limit list length
                ]
            
            else:
                # Convert other types to string and sanitize
                sanitized[clean_key] = self.sanitize_string(str(value))
        
        return sanitized
    
    def _sanitize_html(self, text: str) -> str:
        """
        Internal HTML sanitization.
        
        Args:
            text: HTML text to sanitize
            
        Returns:
            Sanitized HTML
        """
        # Remove dangerous tags
        for tag in self.dangerous_tags:
            pattern = f'<\\s*{tag}[^>]*>.*?<\\s*/\\s*{tag}\\s*>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
            # Also remove self-closing tags
            pattern = f'<\\s*{tag}[^>]*/?\\s*>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove dangerous attributes
        for attr in self.dangerous_attributes:
            pattern = f'{attr}\\s*=\\s*["\'][^"\']*["\']'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def log_sanitization_attempt(self, original: str, sanitized: str, 
                                field_name: str = "unknown") -> None:
        """
        Log sanitization attempts for security monitoring.
        
        Args:
            original: Original input
            sanitized: Sanitized output
            field_name: Name of the field being sanitized
        """
        if original != sanitized:
            self.logger.warning(
                f"Data sanitized in field '{field_name}': "
                f"Original length: {len(original)}, "
                f"Sanitized length: {len(sanitized)}"
            )

# Global sanitizer instance
data_sanitizer = DataSanitizer()

def sanitize_input(data: Any, field_type: str = "string") -> Any:
    """
    Convenience function for data sanitization.
    
    Args:
        data: Data to sanitize
        field_type: Type of field (string, email, phone, numeric, etc.)
        
    Returns:
        Sanitized data
    """
    if field_type == "email":
        return data_sanitizer.sanitize_email(data)
    elif field_type == "phone":
        return data_sanitizer.sanitize_phone(data)
    elif field_type == "numeric":
        return data_sanitizer.sanitize_numeric(data)
    elif field_type == "filename":
        return data_sanitizer.sanitize_filename(data)
    elif field_type == "json":
        return data_sanitizer.sanitize_json_string(data)
    else:
        return data_sanitizer.sanitize_string(data)