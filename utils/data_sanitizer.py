"""Data Sanitizer"""

import re
import html
import logging

class DataSanitizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|\#|/\*|\*/)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\'\s*(OR|AND)\s*\')',
        ]

        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
        ]

    def sanitize_string(self, text, max_length=None):
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        text = html.escape(text)

        for pattern in self.xss_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text.strip()

    def sanitize_sql_input(self, text):
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Posible SQL injection detectado: {text[:50]}...")
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()

    def sanitize_numeric(self, value, data_type=int, default=0):
        try:
            return data_type(value)
        except (ValueError, TypeError):
            return default

    def sanitize_dict(self, data_dict):
        if not isinstance(data_dict, dict):
            return {}

        sanitized = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [self.sanitize_string(str(v)) if isinstance(v, str) else v for v in value]
            else:
                sanitized[key] = value

        return sanitized

data_sanitizer = DataSanitizer()
