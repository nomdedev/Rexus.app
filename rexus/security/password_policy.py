"""
Política de Contraseñas - Rexus.app
Define y valida políticas de contraseñas seguras según estándares NIST SP 800-63B

Esta implementación sigue:
- NIST SP 800-63B Digital Identity Guidelines
- OWASP Password Storage Cheat Sheet
- PCI-DSS Requirements
"""

import re
import string
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PasswordPolicyConfig:
    """Configuración de política de contraseñas."""

    # Longitud
    min_length: int = 12
    max_length: int = 128

    # Caracteres requeridos
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True

    # Patrones prohibidos
    forbid_common_passwords: bool = True
    forbid_sequences: bool = True
    forbid_repeated_chars: bool = True
    forbid_user_info: bool = True

    # Historia
    prevent_reuse: int = 5  # No reusar últimas 5 contraseñas
    min_days_between_changes: int = 1  # Mínimo 1 día entre cambios

    # Expiración
    expire_days: int = 90  # Expirar cada 90 días
    warn_days_before: int = 7  # Advertir 7 días antes de expirar

    # Caracteres especiales permitidos
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Secuencias prohibidas (qwerty, numéricas, alfabéticas)
    forbidden_sequences = [
        "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "1234567890", "0987654321",
        "abcdefgh", "zyxwvutsrq",
        "abcd1234", "password123", "admin123"
    ]


class PasswordValidator:
    """Validador de contraseñas según políticas de seguridad."""

    # Lista de contraseñas comunes (extraída de breaches conocidos)
    COMMON_PASSWORDS = {
        "password", "123456", "password123", "admin", "qwerty",
        "12345678", "abc123", "letmein", "monkey", "dragon",
        "111111", "baseball", "iloveyou", "master", "sunshine",
        "ashley", "bailey", "passw0rd", "shadow", "123123",
        "654321", "superman", "qazwsx", "michael", "football",
        "password1", "hello", "jennifer", "charlie", "andrew",
        "lovely", "jessica", "000000", "george", "amanda",
        "chelsea", "buster", "1234567890", "joshua", "matthew",
        "qwer1234", "123qwe", "nicholas", "patr1ck", "samsung",
        "qwerty1234", "123qwasdf", "qwerty123", "socram", "medina"
    }

    def __init__(self, config: PasswordPolicyConfig = None):
        """
        Inicializa el validador.

        Args:
            config: Configuración de política (usa default si no se proporciona)
        """
        self.config = config or PasswordPolicyConfig()
        self._history: Dict[str, List[str]] = defaultdict(list)
        self._expiry_cache: Dict[str, datetime] = {}

    def validate(self,
                password: str,
                username: str = None,
                user_info: Dict = None) -> Tuple[bool, List[str], List[str]]:
        """
        Valida una contraseña según la política.

        Args:
            password: Contraseña a validar
            username: Nombre de usuario (para verificar que no esté incluida)
            user_info: Información adicional del usuario

        Returns:
            (es_válida, errores, advertencias)
        """
        errors = []
        warnings = []

        # 1. Validar longitud
        if len(password) < self.config.min_length:
            errors.append(f"La contraseña debe tener al menos {self.config.min_length} caracteres")
        elif len(password) > self.config.max_length:
            errors.append(f"La contraseña no puede exceder {self.config.max_length} caracteres")

        # 2. Validar caracteres requeridos
        if self.config.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Debe contener al menos una letra mayúscula (A-Z)")

        if self.config.require_lowercase and not any(c.islower() for c in password):
            errors.append("Debe contener al menos una letra minúscula (a-z)")

        if self.config.require_digits and not any(c.isdigit() for c in password):
            errors.append("Debe contener al menos un número (0-9)")

        if self.config.require_special:
            special_count = sum(1 for c in password if c in self.config.special_chars)
            if special_count == 0:
                errors.append(f"Debe contener al menos un carácter especial ({self.config.special_chars[:5]}...)")

        # 3. Validar contraseñas comunes
        if self.config.forbid_common_passwords:
            password_lower = password.lower()
            # Verificar contraseñas comunes exactas
            if password_lower in self.COMMON_PASSWORDS:
                errors.append("Esta contraseña es demasiado común y fácil de adivinar")

            # Verificar si contiene variaciones comunes
            for common in self.COMMON_PASSWORDS:
                if common in password_lower or password_lower in common:
                    warnings.append("La contraseña contiene patrones comunes que deben evitarse")
                    break

        # 4. Validar secuencias
        if self.config.forbid_sequences:
            sequence_found = self._find_sequences(password)
            if sequence_found:
                errors.append(f"Contiene secuencias predecibles: {', '.join(sequence_found)}")

        # 5. Validar caracteres repetidos
        if self.config.forbid_repeated_chars:
            if self._has_repeated_chars(password, max_repeats=3):
                errors.append("Contiene caracteres repetidos consecutivamente (ej: aaa, 111)")

        # 6. Validar información del usuario
        if self.config.forbid_user_info and user_info:
            user_info_found = self._check_user_info(password, user_info)
            if user_info_found:
                errors.append(f"La contraseña no puede contener: {', '.join(user_info_found)}")

        # 7. Validar contra historial
        if username:
            if self._is_reused_password(username, password):
                errors.append(f"No puedes reusar ninguna de tus últimas {self.config.prevent_reuse} contraseñas")

        # 8. Calcular fortaleza
        is_valid = len(errors) == 0

        # Advertencias sobre fortaleza
        if is_valid:
            strength = self._calculate_strength(password)
            if strength < 60:
                warnings.append("La contraseña cumple los requisitos mínimos pero podría ser más fuerte")
            elif strength < 80:
                warnings.append("La contraseña es moderadamente fuerte")

        return is_valid, errors, warnings

    def _find_sequences(self, password: str, min_length: int = 3) -> List[str]:
        """Encuentra secuencias predecibles en la contraseña."""
        found = []
        password_lower = password.lower()

        for sequence in self.config.forbidden_sequences:
            seq_lower = sequence.lower()
            if len(seq_lower) < min_length:
                continue

            # Verificar secuencia directa
            for i in range(len(password_lower) - min_length + 1):
                substring = password_lower[i:i + len(seq_lower)]
                if substring in seq_lower or seq_lower in substring:
                    found.append(sequence)
                    break

        return found

    def _has_repeated_chars(self, password: str, max_repeats: int = 3) -> bool:
        """Verifica si hay caracteres repetidos."""
        for i in range(len(password) - max_repeats):
            if password[i] * max_repeats == password[i:i + max_repeats]:
                return True
        return False

    def _check_user_info(self, password: str, user_info: Dict) -> List[str]:
        """Verifica si la contraseña contiene información del usuario."""
        found = []
        password_lower = password.lower()

        # Campos comunes a verificar
        fields_to_check = ['username', 'nombre', 'apellido', 'email', 'telefono']

        for field in fields_to_check:
            value = str(user_info.get(field, '')).lower()
            if value and len(value) >= 3 and value in password_lower:
                found.append(field)
            # Verificar también sin separadores
            value_no_sep = re.sub(r'[^a-z0-9]', '', value)
            if len(value_no_sep) >= 3 and value_no_sep in password_lower:
                found.append(field)

        return found

    def _is_reused_password(self, username: str, password: str) -> bool:
        """Verifica si la contraseña fue usada anteriormente."""
        # Generar hash de la contraseña para comparación
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if password_hash in self._history[username]:
            return True
        return False

    def _calculate_strength(self, password: str) -> float:
        """
        Calcula la fortaleza de una contraseña (0-100).

        Considera:
        - Longitud
        - Variedad de caracteres
        - Entropía
        """
        strength = 0

        # Longitud (hasta 40 puntos)
        strength += min(len(password) * 2, 40)

        # Variedad de caracteres
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in self.config.special_chars for c in password)

        variety = sum([has_upper, has_lower, has_digit, has_special])
        strength += variety * 10  # Hasta 40 puntos por variedad

        # Bonus por longitud extra
        if len(password) >= 16:
            strength += 10

        # Bonus por caracteres especiales múltiples
        special_count = sum(1 for c in password if c in self.config.special_chars)
        if special_count >= 3:
            strength += 10

        return min(strength, 100)

    def add_to_history(self, username: str, password_hash: str):
        """Agrega un hash al historial del usuario."""
        self._history[username].append(password_hash)

        # Mantener solo las últimas N contraseñas
        if len(self._history[username]) > self.config.prevent_reuse:
            self._history[username].pop(0)

    def set_password_expiry(self, username: str, expiry_date: datetime = None):
        """Establece la fecha de expiración de la contraseña."""
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=self.config.expire_days)
        self._expiry_cache[username] = expiry_date

    def is_password_expired(self, username: str) -> Tuple[bool, Optional[int]]:
        """
        Verifica si la contraseña ha expirado.

        Returns:
            (está_expirada, días_restantes)
        """
        if username not in self._expiry_cache:
            return False, None

        expiry = self._expiry_cache[username]
        now = datetime.now()

        if now >= expiry:
            return True, 0

        days_remaining = (expiry - now).days
        return False, days_remaining

    def generate_password(self, length: int = 16,
                          use_uppercase: bool = True,
                          use_lowercase: bool = True,
                          use_digits: bool = True,
                          use_special: bool = True) -> str:
        """
        Genera una contraseña segura aleatoria.

        Args:
            length: Longitud deseada
            use_uppercase: Incluir mayúsculas
            use_lowercase: Incluir minúsculas
            use_digits: Incluir números
            use_special: Incluir especiales

        Returns:
            Contraseña generada
        """
        import secrets
        import string

        charset = ""
        if use_lowercase:
            charset += string.ascii_lowercase
        if use_uppercase:
            charset += string.ascii_uppercase
        if use_digits:
            charset += string.digits
        if use_special:
            charset += self.config.special_chars

        if not charset:
            charset = string.ascii_lowercase + string.digits

        password = ''.join(secrets.choice(charset) for _ in range(length))

        # Verificar que cumpla con los requisitos
        is_valid, errors, _ = self.validate(password, username=None)

        # Si no cumple, regenerar (hasta 3 intentos)
        attempts = 0
        while not is_valid and attempts < 3:
            password = ''.join(secrets.choice(charset) for _ in range(length))
            is_valid, errors, _ = self.validate(password, username=None)
            attempts += 1

        return password

    def check_expiry_warning(self, username: str) -> Tuple[bool, Optional[int]]:
        """
        Verifica si hay que advertir sobre expiración próxima.

        Returns:
            (advertir, días_restantes)
        """
        if username not in self._expiry_cache:
            return False, None

        expiry = self._expiry_cache[username]
        now = datetime.now()
        days_until_expiry = (expiry - now).days

        if days_until_expiry <= self.config.warn_days_before:
            return True, days_until_expiry

        return False, None

    def get_password_policy_summary(self) -> Dict:
        """Retorna un resumen de la política de contraseñas."""
        return {
            "min_length": self.config.min_length,
            "max_length": self.config.max_length,
            "require_uppercase": self.config.require_uppercase,
            "require_lowercase": self.config.require_lowercase,
            "require_digits": self.config.require_digits,
            "require_special": self.config.require_special,
            "special_chars": self.config.special_chars,
            "prevent_reuse": self.config.prevent_reuse,
            "expire_days": self.config.expire_days,
            "warn_days_before": self.config.warn_days_before
        }


# Instancia global
_password_validator_instance = None


def get_password_validator() -> PasswordValidator:
    """Obtiene la instancia singleton del PasswordValidator."""
    global _password_validator_instance
    if _password_validator_instance is None:
        _password_validator_instance = PasswordValidator()
    return _password_validator_instance


# Función de conveniencia para validación rápida
def validate_password(password: str, username: str = None) -> Tuple[bool, List[str]]:
    """
    Valida una contraseña rápidamente.

    Args:
        password: Contraseña a validar
        username: Nombre de usuario

    Returns:
        (es_válida, errores)
    """
    validator = get_password_validator()
    is_valid, errors, warnings = validator.validate(password, username)
    return is_valid, errors + warnings


# Decorador para requerir contraseña segura en parámetros
def require_strong_password(param_name: str = "password"):
    """
    Decorador para validar contraseñas en funciones.

    Args:
        param_name: Nombre del parámetro que contiene la contraseña

    Example:
        @require_strong_password("new_password")
        def cambiar_password(username, old_password, new_password):
            # new_password será validada automáticamente
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obtener la contraseña del parámetro
            password = kwargs.get(param_name) or (
                args[2] if len(args) > 2 else None
            )

            if password:
                validator = get_password_validator()
                is_valid, errors, warnings = validator.validate(password)

                if not is_valid:
                    raise ValueError(
                        f"Contraseña no cumple los requisitos: {', '.join(errors)}"
                    )

            return func(*args, **kwargs)

        return wrapper
    return decorator
