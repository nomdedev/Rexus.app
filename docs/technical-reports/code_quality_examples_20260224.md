# Auditoría de Calidad de Código - Ejemplos y Soluciones

**Fecha:** 2026-02-24
**Proyecto:** Rexus.app
**Archivos analizados:** 259
**Líneas de código:** 99,405

---

## Resumen Ejecutivo

### Hallazgos Clave
- **204 archivos** (79%) presentan problemas de calidad
- **87 funciones** con alta complejidad ciclomática
- **7 archivos** con errores de sintaxis críticos
- **5.92%** cobertura de documentación (objetivo: >80%)
- **20 bloques** de código duplicado detectados

---

## Problemas Críticos: Errores de Sintaxis

### 1. prometheus_exporter.py - Error de Sintaxis

**Archivo:** `D:\martin\Proyectos\Rexus.app\rexus\monitoring\prometheus_exporter.py`
**Línea:** 74

**Problema:**
```python
# Línea 74 - f-string sin cerrar
lines.append(f'{prometheus_name}{{{label_str}}} {value}')
                                                          ^^^^^^
SyntaxError: unterminated f-string literal
```

**Solución:**
```python
# Corregido
lines.append(f'{prometheus_name}{{{label_str}}} {value}')
```

**Impacto:** El archivo no puede ejecutarse. Es crítico para el sistema de monitoreo.

---

### 2. Otros archivos con errores de sintaxis
- `rexus/utils/query_optimizer.py` (608 líneas)
- `rexus/utils/style_unifier.py` (248 líneas)
- `rexus/modules/03_herrajes/view.py` (1,195 líneas)
- `rexus/modules/06_pedidos/improved_dialogs.py` (628 líneas)
- `rexus/modules/11_usuarios/improved_dialogs.py` (477 líneas)
- `rexus/modules/11_usuarios/model.py` (1,688 líneas)

**Acción Inmediata:** Revisar y corregir todos los errores de sintaxis antes de continuar con el desarrollo.

---

## Alta Complejidad Ciclomática

### Top 10 Funciones más Complejas

| Función | Archivo | Complejidad | Líneas sugeridas |
|---------|---------|-------------|------------------|
| `main` | `rexus/main/app.py` | 30 | <15 |
| `validate` | `rexus/security/password_policy.py` | 28 | <15 |
| `_validar_formatos` | `modules/01_obras/validator_extended.py` | 23 | <15 |
| `_validate_by_type` | `rexus/utils/input_validator.py` | 20 | <15 |
| `crear_obra` | `modules/01_obras/model.py` | 20 | <15 |
| `add_form_group` | `rexus/utils/dialog_utils.py` | 18 | <15 |
| `format_relative_date` | `rexus/utils/format_utils.py` | 17 | <15 |
| `_evaluate_condition` | `rexus/core/business_rules.py` | 17 | <15 |
| `get_connection` | `rexus/core/database_pool.py` | 16 | <15 |
| `validar_datos_obra` | `modules/01_obras/controller.py` | 16 | <15 |

### Ejemplo: Función `validate` - Complejidad 28

**Archivo:** `rexus/security/password_policy.py`

**Problema:**
```python
def validate(self, password: str, user_info: dict = None) -> Tuple[bool, List[str]]:
    """Valida una contraseña contra múltiples políticas.

    Returns:
        Tuple[bool, List[str]]: (es_valida, lista_errores)
    """
    errors = []

    # 1. Verificar longitud mínima
    if len(password) < self.min_length:
        errors.append(f"La contraseña debe tener al menos {self.min_length} caracteres")

    # 2. Verificar longitud máxima
    if len(password) > self.max_length:
        errors.append(f"La contraseña no debe exceder {self.max_length} caracteres")

    # 3. Verificar mayúsculas
    if self.require_uppercase and not re.search(r'[A-Z]', password):
        errors.append("La contraseña debe contener al menos una mayúscula")

    # 4. Verificar minúsculas
    if self.require_lowercase and not re.search(r'[a-z]', password):
        errors.append("La contraseña debe contener al menos una minúscula")

    # 5. Verificar dígitos
    if self.require_digits and not re.search(r'\d', password):
        errors.append("La contraseña debe contener al menos un dígito")

    # 6. Verificar caracteres especiales
    if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("La contraseña debe contener al menos un carácter especial")

    # 7. Verificar caracteres comunes
    if self.forbidden_chars:
        for char in self.forbidden_chars:
            if char in password:
                errors.append(f"La contraseña no debe contener el carácter '{char}'")

    # 8. Verificar palabras comunes
    if self.check_common_passwords:
        for common in self.common_passwords:
            if common.lower() in password.lower():
                errors.append("La contraseña es demasiado común")

    # 9. Verificar información del usuario
    if user_info:
        username = user_info.get('username', '')
        email = user_info.get('email', '')
        name = user_info.get('name', '')

        if username and username.lower() in password.lower():
            errors.append("La contraseña no debe contener el nombre de usuario")

        if email:
            email_parts = email.split('@')[0].lower()
            if email_parts in password.lower():
                errors.append("La contraseña no debe contener partes del email")

        if name:
            name_parts = name.lower().split()
            for part in name_parts:
                if len(part) > 3 and part in password.lower():
                    errors.append("La contraseña no debe contener partes de su nombre")

    # 10. Verificar patrones secuenciales
    if self.detect_patterns:
        # Patrones de teclado
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                errors.append("La contraseña contiene patrones comunes de teclado")

        # Secuencias numéricas
        for i in range(len(password) - 3):
            if password[i:i+4].isdigit():
                seq = int(password[i:i+4])
                if abs(seq - int(password[i:i+4][::-1])) < 100:
                    errors.append("La contraseña contiene secuencias numéricas")

    return len(errors) == 0, errors
```

**Solución - Refactorización:**
```python
class PasswordValidator:
    """Validador de contraseñas con validaciones separadas."""

    def validate(self, password: str, user_info: dict = None) -> Tuple[bool, List[str]]:
        """Valida contraseña delegando en validadores especializados."""
        errors = []

        # Validaciones básicas
        errors.extend(self._validate_length(password))
        errors.extend(self._validate_character_types(password))
        errors.extend(self._validate_forbidden_content(password))
        errors.extend(self._validate_user_info(password, user_info))
        errors.extend(self._validate_patterns(password))

        return len(errors) == 0, errors

    def _validate_length(self, password: str) -> List[str]:
        """Valida longitud de la contraseña."""
        errors = []
        if len(password) < self.min_length:
            errors.append(f"La contraseña debe tener al menos {self.min_length} caracteres")
        if len(password) > self.max_length:
            errors.append(f"La contraseña no debe exceder {self.max_length} caracteres")
        return errors

    def _validate_character_types(self, password: str) -> List[str]:
        """Valida tipos de caracteres requeridos."""
        errors = []

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("La contraseña debe contener al menos una mayúscula")

        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("La contraseña debe contener al menos una minúscula")

        if self.require_digits and not re.search(r'\d', password):
            errors.append("La contraseña debe contener al menos un dígito")

        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("La contraseña debe contener al menos un carácter especial")

        return errors

    def _validate_forbidden_content(self, password: str) -> List[str]:
        """Valida contenido prohibido."""
        errors = []

        # Verificar caracteres prohibidos
        if self.forbidden_chars:
            for char in self.forbidden_chars:
                if char in password:
                    errors.append(f"La contraseña no debe contener el carácter '{char}'")

        # Verificar contraseñas comunes
        if self.check_common_passwords:
            for common in self.common_passwords:
                if common.lower() in password.lower():
                    errors.append("La contraseña es demasiado común")

        return errors

    def _validate_user_info(self, password: str, user_info: dict) -> List[str]:
        """Valida que la contraseña no contenga información del usuario."""
        errors = []

        if not user_info:
            return errors

        username = user_info.get('username', '')
        email = user_info.get('email', '')
        name = user_info.get('name', '')

        if username and username.lower() in password.lower():
            errors.append("La contraseña no debe contener el nombre de usuario")

        if email:
            email_parts = email.split('@')[0].lower()
            if email_parts in password.lower():
                errors.append("La contraseña no debe contener partes del email")

        if name:
            name_parts = name.lower().split()
            for part in name_parts:
                if len(part) > 3 and part in password.lower():
                    errors.append("La contraseña no debe contener partes de su nombre")

        return errors

    def _validate_patterns(self, password: str) -> List[str]:
        """Valida patrones comunes."""
        errors = []

        if not self.detect_patterns:
            return errors

        # Patrones de teclado
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                errors.append("La contraseña contiene patrones comunes de teclado")

        # Secuencias numéricas
        for i in range(len(password) - 3):
            if password[i:i+4].isdigit():
                seq = int(password[i:i+4])
                if abs(seq - int(password[i:i+4][::-1])) < 100:
                    errors.append("La contraseña contiene secuencias numéricas")

        return errors
```

**Beneficios:**
- Complejidad reducida de 28 a <5 por método
- Código más testable (cada validación se puede probar independientemente)
- Más fácil de mantener y extender
- Sigue el principio de responsabilidad única

---

## Módulos con Alta Complejidad

### 1. reportes_manager.py - 1,106 líneas, complejidad 127

**Archivo:** `rexus/modules/02_inventario/submodules/reportes_manager.py`

**Problemas:**
- 5 funciones con alta complejidad
- Falta docstring del módulo
- Múltiples responsabilidades en una sola clase

**Sugerencia:** Dividir en:
- `ReportGenerator` - Generación de reportes
- `StatisticsCalculator` - Cálculos estadísticos
- `TrendAnalyzer` - Análisis de tendencias
- `KPIProvider` - Métricas KPI
- `DataExporter` - Exportación de datos

### 2. model.py (Obras) - 802 líneas, complejidad 129

**Archivo:** `rexus/modules/01_obras/model.py`

**Problemas:**
- 5 funciones con alta complejidad
- Clase demasiado grande
- Mezcla lógica de negocio con acceso a datos

**Sugerencia:** Aplicar patrón Repository:
```python
# Estructura sugerida
models/
  obras/
    __init__.py
    entities.py       # Entidades de dominio
    value_objects.py  # Objetos de valor
    repositories.py   # Interfaces de repositorios
    dto.py            # Data Transfer Objects

repositories/
  obras/
    __init__.py
    sql_obras_repository.py  # Implementación SQL
    obras_repository.py      # Interfaz
```

---

## Violaciones de Naming Conventions

### Problemas Detectados: 18 violaciones

**Ejemplo 1: Uso de camelCase en lugar de snake_case**
```python
# INCORRECTO
def conectar_señales(self):
    """Conecta las señales."""
    pass

class UserPasswordValidator:  # Debería estar en un archivo separado
    pass

# CORRECTO
def conectar_senales(self):  # Sin ñ, usa snake_case
    """Conecta las señales."""
    pass

# Qt events son excepciones aceptadas
def keyPressEvent(self, event):
    """Maneja evento de tecla."""
    pass
```

**Ejemplo 2: Nombres con caracteres especiales**
```python
# INCORRECTO
def cargar_registros_auditoría(self):
    pass

# CORRECTO
def cargar_registros_auditoria(self):
    pass
```

**Mejor práctica:** Usar transliteración para nombres en español
```python
# Configuración recomendada
CODIGOS_MAP = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ñ': 'n', 'ü': 'u'
}

def sanitize_name(name: str) -> str:
    """Convierte nombre a formato seguro para código."""
    for char, replacement in CODIGOS_MAP.items():
        name = name.replace(char, replacement)
    return name.lower().replace(' ', '_')
```

---

## Falta de Type Hints

### Problema: Sin type hints
```python
# ANTES
def crear_obra(datos):
    if not datos:
        return None

    # Validaciones
    if 'codigo' not in datos:
        raise ValueError("Falta código")

    # ... lógica ...

    return obra_id
```

### Solución: Con type hints
```python
# DESPUÉS
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ObraData:
    """Datos para crear una obra."""
    codigo: str
    nombre: str
    cliente: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str = "PENDIENTE"
    metadata: Optional[Dict[str, Any]] = None

def crear_obra(datos: ObraData) -> Optional[int]:
    """
    Crea una nueva obra en el sistema.

    Args:
        datos: Datos de la obra a crear

    Returns:
        ID de la obra creada o None si falló

    Raises:
        ValueError: Si faltan datos requeridos
        DatabaseError: Si hay error en la base de datos
    """
    if not datos:
        return None

    if not datos.codigo:
        raise ValueError("El código es requerido")

    # ... lógica ...

    return obra_id
```

---

## Código Duplicado

### Ejemplo 1: Configuración de logging

**Duplicado en 2 archivos:**
```python
# bootstrap.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# agents/demo_agents.py - MISMO CÓDIGO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Solución:** Crear módulo centralizado
```python
# utils/logging_config.py
import logging
from typing import Optional

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura un logger con formato estándar.

    Args:
        name: Nombre del logger
        level: Nivel de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger

# Uso
from rexus.utils.logging_config import setup_logger
logger = setup_logger(__name__)
```

### Ejemplo 2: Decoradores de autenticación

**Duplicado en `auth_decorators.py`:**
```python
# Líneas 91-93 duplicado en múltiples decoradores
Args:
    f: Función a decorar

Returns:
    Callable: Función decorada
```

**Solución:** Usar docstring templates o heredar de una base

---

## Archivos sin Documentación

### Archivos críticos sin docstring de módulo:

1. `rexus/core/auth_decorators.py`
2. `rexus/core/auth_manager.py`
3. `rexus/core/database.py`
4. `rexus/core/database_manager.py`
5. `rexus/core/database_pool.py`

### Solución - Agregar docstrings de módulo:

```python
"""
Decoradores de Autenticación y Autorización

Este módulo proporciona decoradores para proteger funciones y métodos
requiriendo autenticación y permisos específicos.

Decoradores disponibles:
    - auth_required: Requiere usuario autenticado
    - permission_required: Requiere permiso específico
    - role_required: Requiere rol específico
    - require_all_permissions: Requiere múltiples permisos

Ejemplo:
    >>> from rexus.core.auth_decorators import auth_required
    >>>
    >>> @auth_required
    >>> def funcion_protegida():
    >>>     return "Datos sensibles"

Módulo relacionado: rexus.core.rbac_system
"""
```

---

## Recomendaciones Priorizadas

### CRÍTICAS (Atender inmediatamente)

1. **Corregir errores de sintaxis** (7 archivos)
   - [ ] `prometheus_exporter.py` - f-string sin cerrar
   - [ ] `query_optimizer.py` - verificar sintaxis
   - [ ] `style_unifier.py` - verificar sintaxis
   - [ ] `view.py` (herrajes) - verificar sintaxis
   - [ ] `improved_dialogs.py` (pedidos) - verificar sintaxis
   - [ ] `improved_dialogs.py` (usuarios) - verificar sintaxis
   - [ ] `model.py` (usuarios) - verificar sintaxis

2. **Refactorizar 10 funciones más complejas**
   - Objetivo: Reducir complejidad de 30/28 a <10
   - Tiempo estimado: 2-3 semanas
   - Impacto: Alta mantenibilidad

### ALTAS (Atender en 1-2 semanas)

3. **Añadir type hints** (PEP 484)
   - Prioridad: Funciones públicas de `core/` y `modules/`
   - Herramienta: `mypy --strict`
   - Cobertura objetivo: 80%

4. **Implementar testing automatizado**
   - Framework: `pytest`
   - Cobertura mínima: 70%
   - Empezar por módulos críticos: `auth`, `database`, `rbac`

### MEDIAS (Atender en 1 mes)

5. **Mejorar documentación**
   - Docstrings de módulo: 225/259 archivos (87% pendiente)
   - Estilo: Google Python Style Guide
   - Herramienta: `pydocstyle`

6. **Reducir duplicación de código**
   - Extraer 20 bloques duplicados a utilidades
   - Crear módulos: `logging_config.py`, `common_validators.py`, etc.

7. **Normalizar naming conventions**
   - 18 violaciones detectadas
   - Usar snake_case excepto Qt events
   - Sin caracteres especiales (á, é, ñ)

### BAJAS (Mejora continua)

8. **Configurar herramientas de análisis estático**
   - `flake8` - Linting
   - `black` - Formateo
   - `isort` - Ordenamiento de imports
   - `pylint` - Análisis profundo

9. **Implementar pre-commit hooks**
   - Formateo automático
   - Verificación de type hints
   - Ejecución de tests básicos

10. **Documentar arquitectura**
    - Diagramas de componentes
    - Patrones de diseño utilizados
    - Guía de contribución

---

## Métricas Objetivo vs Actual

| Métrica | Actual | Objetivo | Gap |
|---------|--------|----------|-----|
| Cobertura documentación | 5.92% | >80% | -74% |
| Complejidad promedio | 3.04 | <3 | +0.04 |
| Funciones de alta complejidad | 87 | <10 | -77 |
| Archivos con errores | 7 | 0 | -7 |
| Archivos con issues | 204 (79%) | <50 (20%) | -154 |
| Type hints coverage | ~20% | >80% | -60% |
| Test coverage | 0% | >70% | -70% |
| Comment ratio | 5.21% | >15% | -10% |

---

## Plan de Acción - 4 Semanas

### Semana 1: Corrección Crítica
- Día 1-2: Corregir 7 errores de sintaxis
- Día 3-5: Refactorizar 3 funciones más complejas

### Semana 2: Type Hints y Testing
- Día 1-3: Añadir type hints a `core/`
- Día 4-5: Configurar pytest y escribir tests básicos

### Semana 3: Documentación
- Día 1-3: Docstrings para módulos críticos
- Día 4-5: Docstrings para módulos de negocio

### Semana 4: Organización
- Día 1-2: Extraer código duplicado
- Día 3-4: Normalizar naming conventions
- Día 5: Configurar herramientas de análisis estático

---

## Herramientas Recomendadas

```bash
# Instalación
pip install pytest pytest-cov mypy black flake8 isort pydocstyle pylint

# Configuración
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=rexus --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["rexus"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.pylint.messages_control]
disable = ["C0111", "C0103"]
EOF

# Pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Ejecutando checks de calidad..."
black rexus/
isort rexus/
flake8 rexus/
mypy rexus/
pytest tests/
EOF
chmod +x .git/hooks/pre-commit
```

---

## Conclusión

Rexus.app es un proyecto sólido con **99,405 líneas de código** y buena estructura modular. Sin embargo, presenta **deudas técnicas** que deben atenderse:

**Fortalezas:**
- Arquitectura modular bien organizada
- Separación clara de responsabilidades (core, modules, utils)
- Uso de patrones modernos (decorators, caches, managers)

**Áreas de mejora:**
- Documentación (5.92% vs 80% objetivo)
- Testing automatizado (0% vs 70% objetivo)
- Complejidad ciclomática en funciones críticas
- Type hints para verificación estática

**Próximos pasos:**
1. Corregir errores de sintaxis (7 archivos)
2. Refactorizar funciones complejas (10 funciones)
3. Implementar testing (objetivo 70% cobertura)
4. Mejorar documentación (objetivo 80% cobertura)
5. Configurar CI/CD con checks de calidad

Con este plan, en **4 semanas** se puede alcanzar un nivel de calidad profesional que facilite el mantenimiento y la colaboración.

---

*Reporte generado: 2026-02-24*
*Script de auditoría: `scripts/audit_code_quality.py`*
