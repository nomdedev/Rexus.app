"""
Motor de Reglas de Negocio - Rexus.app
Sistema centralizado para reglas de negocio configurables

Características:
- Reglas configurables desde BD o YAML
- Motor de evaluación de reglas
- Validaciones centralizadas
- Cálculos de negocio (descuentos, plazos, etc.)
"""

import logging
import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Tipos de reglas."""
    VALIDATION = "validation"
    CALCULATION = "calculation"
    CONDITION = "condition"
    ACTION = "action"


class RuleSeverity(Enum):
    """Severidad de reglas."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class BusinessRule:
    """Representa una regla de negocio."""
    id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    enabled: bool = True
    conditions: List[Dict] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evalúa si la regla aplica al contexto dado.

        Args:
            context: Contexto de evaluación

        Returns:
            True si la regla aplica
        """
        if not self.enabled:
            return False

        for condition in self.conditions:
            if not self._evaluate_condition(condition, context):
                return False

        return True

    def _evaluate_condition(self, condition: Dict, context: Dict) -> bool:
        """Evalúa una condición individual."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Obtener valor del contexto (soporta nested paths)
        context_value = self._get_nested_value(context, field)

        # Evaluar según operador
        if operator == "eq":
            return context_value == value
        elif operator == "ne":
            return context_value != value
        elif operator == "gt":
            return context_value is not None and context_value > value
        elif operator == "gte":
            return context_value is not None and context_value >= value
        elif operator == "lt":
            return context_value is not None and context_value < value
        elif operator == "lte":
            return context_value is not None and context_value <= value
        elif operator == "in":
            return context_value in value
        elif operator == "not_in":
            return context_value not in value
        elif operator == "contains":
            return value in context_value if context_value else False
        elif operator == "regex":
            return bool(re.match(value, str(context_value))) if context_value else False
        elif operator == "is_null":
            return context_value is None
        elif operator == "is_not_null":
            return context_value is not None
        else:
            logger.warning(f"Operador desconocido: {operator}")
            return True

    def _get_nested_value(self, obj: Dict, path: str):
        """Obtiene valor con ruta anidada (ej: 'pedido.monto')."""
        keys = path.split(".")
        value = obj
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
        return value


@dataclass
class ValidationResult:
    """Resultado de una validación."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class BusinessValidator:
    """
    Validador centralizado de reglas de negocio.

    Example:
        validator = BusinessValidator()

        # Validar pedido
        result = validator.validate_pedido({
            'cliente_id': 123,
            'items': [...],
            'monto': 50000
        })

        if not result.is_valid:
            print(result.errors)
    """

    def __init__(self):
        """Inicializa el validador."""
        self.rules = self._load_default_rules()

    def _load_default_rules(self) -> Dict[str, List[BusinessRule]]:
        """Carga reglas por defecto."""
        return {
            "pedido": self._get_pedido_rules(),
            "producto": self._get_producto_rules(),
            "compra": self._get_compra_rules(),
            "obra": self._get_obra_rules(),
            "cliente": self._get_cliente_rules(),
        }

    def _get_pedido_rules(self) -> List[BusinessRule]:
        """Reglas de validación de pedidos."""
        return [
            BusinessRule(
                id="pedido_cliente_requerido",
                name="Cliente Requerido",
                description="Todo pedido debe tener un cliente asignado",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "cliente_id", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El cliente es requerido"}]
            ),
            BusinessRule(
                id="pedido_items_requeridos",
                name="Items Requeridos",
                description="Todo pedido debe tener al menos un item",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "items", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El pedido debe tener al menos un item"}]
            ),
            BusinessRule(
                id="pedido_monto_positivo",
                name="Monto Positivo",
                description="El monto del pedido debe ser positivo",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "monto", "operator": "lte", "value": 0}
                ],
                actions=[{"type": "error", "message": "El monto debe ser mayor a cero"}]
            ),
            BusinessRule(
                id="pedido_monto_minimo",
                name="Monto Mínimo",
                description="El monto mínimo de pedido es $1000",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.MEDIUM,
                conditions=[
                    {"field": "monto", "operator": "gt", "value": 0},
                    {"field": "monto", "operator": "lt", "value": 1000}
                ],
                actions=[{"type": "error", "message": "El monto mínimo de pedido es $1000"}]
            ),
        ]

    def _get_producto_rules(self) -> List[BusinessRule]:
        """Reglas de validación de productos."""
        return [
            BusinessRule(
                id="producto_nombre_requerido",
                name="Nombre Requerido",
                description="Todo producto debe tener nombre",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "nombre", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El nombre del producto es requerido"}]
            ),
            BusinessRule(
                id="producto_precio_positivo",
                name="Precio Positivo",
                description="El precio debe ser positivo",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.HIGH,
                conditions=[
                    {"field": "precio", "operator": "lte", "value": 0}
                ],
                actions=[{"type": "error", "message": "El precio debe ser mayor a cero"}]
            ),
            BusinessRule(
                id="producto_stock_minimo",
                name="Stock Mínimo",
                description="El stock mínimo debe ser menor o igual al stock actual",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.MEDIUM,
                conditions=[
                    {"field": "stock_minimo", "operator": "gt", "value": 0},
                    {"field": "stock_minimo", "operator": "gt", "value": "stock"}
                ],
                actions=[{"type": "warning", "message": "El stock mínimo no puede ser mayor al stock actual"}]
            ),
        ]

    def _get_compra_rules(self) -> List[BusinessRule]:
        """Reglas de validación de compras."""
        return [
            BusinessRule(
                id="compra_proveedor_requerido",
                name="Proveedor Requerido",
                description="Toda compra debe tener un proveedor",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "proveedor_id", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El proveedor es requerido"}]
            ),
            BusinessRule(
                id="compra_monto_positivo",
                name="Monto Positivo",
                description="El monto de compra debe ser positivo",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "monto", "operator": "lte", "value": 0}
                ],
                actions=[{"type": "error", "message": "El monto debe ser mayor a cero"}]
            ),
        ]

    def _get_obra_rules(self) -> List[BusinessRule]:
        """Reglas de validación de obras."""
        return [
            BusinessRule(
                id="obra_nombre_requerido",
                name="Nombre Requerido",
                description="Toda obra debe tener nombre",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "nombre", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El nombre de la obra es requerido"}]
            ),
            BusinessRule(
                id="obra_presupuesto_positivo",
                name="Presupuesto Positivo",
                description="El presupuesto debe ser positivo",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.HIGH,
                conditions=[
                    {"field": "presupuesto", "operator": "lte", "value": 0}
                ],
                actions=[{"type": "error", "message": "El presupuesto debe ser mayor a cero"}]
            ),
            BusinessRule(
                id="obra_fechas_validas",
                name="Fechas Válidas",
                description="La fecha fin debe ser posterior a la fecha inicio",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.HIGH,
                conditions=[
                    {"field": "fecha_inicio", "operator": "is_not_null", "value": None},
                    {"field": "fecha_fin", "operator": "is_not_null", "value": None},
                    {"field": "fecha_fin", "operator": "lte", "value": "fecha_inicio"}
                ],
                actions=[{"type": "error", "message": "La fecha fin debe ser posterior a la fecha inicio"}]
            ),
        ]

    def _get_cliente_rules(self) -> List[BusinessRule]:
        """Reglas de validación de clientes."""
        return [
            BusinessRule(
                id="cliente_nombre_requerido",
                name="Nombre Requerido",
                description="Todo cliente debe tener nombre",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.CRITICAL,
                conditions=[
                    {"field": "nombre", "operator": "is_null", "value": None}
                ],
                actions=[{"type": "error", "message": "El nombre del cliente es requerido"}]
            ),
            BusinessRule(
                id="cliente_email_valido",
                name="Email Válido",
                description="El email debe tener formato válido",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.HIGH,
                conditions=[
                    {"field": "email", "operator": "is_not_null", "value": None},
                    {"field": "email", "operator": "regex", "value": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
                ],
                actions=[{"type": "error", "message": "El email no tiene un formato válido"}]
            ),
        ]

    def validate(self, entity_type: str, data: Dict) -> ValidationResult:
        """
        Valida datos contra reglas de negocio.

        Args:
            entity_type: Tipo de entidad (pedido, producto, etc.)
            data: Datos a validar

        Returns:
            Resultado de validación
        """
        result = ValidationResult(is_valid=True)
        rules = self.rules.get(entity_type, [])

        for rule in rules:
            if rule.evaluate(data):
                # Ejecutar acciones de la regla
                for action in rule.actions:
                    action_type = action.get("type")

                    if action_type == "error":
                        result.is_valid = False
                        result.errors.append(action.get("message"))
                        logger.warning(f"Regla '{rule.id}' violada: {action.get('message')}")

                    elif action_type == "warning":
                        result.warnings.append(action.get("message"))
                        logger.info(f"Warning de regla '{rule.id}': {action.get('message')}")

        return result

    # Métodos de conveniencia para cada entidad
    def validate_pedido(self, pedido: Dict) -> ValidationResult:
        """Valida un pedido."""
        return self.validate("pedido", pedido)

    def validate_producto(self, producto: Dict) -> ValidationResult:
        """Valida un producto."""
        return self.validate("producto", producto)

    def validate_compra(self, compra: Dict) -> ValidationResult:
        """Valida una compra."""
        return self.validate("compra", compra)

    def validate_obra(self, obra: Dict) -> ValidationResult:
        """Valida una obra."""
        return self.validate("obra", obra)

    def validate_cliente(self, cliente: Dict) -> ValidationResult:
        """Valida un cliente."""
        return self.validate("cliente", cliente)

    def add_rule(self, entity_type: str, rule: BusinessRule):
        """Agrega una regla personalizada."""
        if entity_type not in self.rules:
            self.rules[entity_type] = []
        self.rules[entity_type].append(rule)
        logger.info(f"Regla agregada: {rule.id} para {entity_type}")

    def remove_rule(self, entity_type: str, rule_id: str):
        """Elimina una regla."""
        if entity_type in self.rules:
            self.rules[entity_type] = [
                r for r in self.rules[entity_type] if r.id != rule_id
            ]
            logger.info(f"Regla eliminada: {rule_id} de {entity_type}")


class BusinessCalculator:
    """
    Calculadora de reglas de negocio.

    Example:
        calc = BusinessCalculator()

        # Calcular descuento
        descuento = calc.calcular_descuento(pedido)

        # Calcular plazo de entrega
        plazo = calc.calcular_plazo_entrega(pedido)
    """

    def __init__(self):
        """Inicializa la calculadora."""
        self.reglas_descuento = self._load_descuento_rules()
        self.reglas_plazo = self._load_plazo_rules()

    def _load_descuento_rules(self) -> List[Dict]:
        """Reglas de descuento."""
        return [
            {"monto_min": 1000000, "porcentaje": 0.10, "nombre": "Descuento 10%"},
            {"monto_min": 500000, "porcentaje": 0.05, "nombre": "Descuento 5%"},
            {"monto_min": 100000, "porcentaje": 0.02, "nombre": "Descuento 2%"},
        ]

    def _load_plazo_rules(self) -> List[Dict]:
        """Reglas de plazo de entrega."""
        return [
            {"prioridad": "URGENTE", "dias": 3},
            {"prioridad": "ALTA", "dias": 5},
            {"prioridad": "NORMAL", "dias": 7},
            {"prioridad": "BAJA", "dias": 10},
        ]

    def calcular_descuento(self, pedido: Dict) -> Dict:
        """
        Calcula el descuento aplicable a un pedido.

        Args:
            pedido: Datos del pedido

        Returns:
            Diccionario con descuento calculado
        """
        monto = pedido.get("monto", 0)
        descuento = 0.0
        regla_aplicada = None

        for regla in self.reglas_descuento:
            if monto >= regla["monto_min"]:
                descuento = regla["porcentaje"]
                regla_aplicada = regla["nombre"]
                break

        monto_descuento = monto * descuento

        return {
            "porcentaje": descuento,
            "monto": monto_descuento,
            "monto_final": monto - monto_descuento,
            "regla_aplicada": regla_aplicada
        }

    def calcular_plazo_entrega(self, pedido: Dict) -> int:
        """
        Calcula el plazo de entrega en días.

        Args:
            pedido: Datos del pedido

        Returns:
            Días de plazo
        """
        prioridad = pedido.get("prioridad", "NORMAL").upper()

        for regla in self.reglas_plazo:
            if regla["prioridad"] == prioridad:
                return regla["dias"]

        return 7  # Default

    def calcular_stock_minimo(self, producto: Dict) -> int:
        """
        Calcula el stock mínimo recomendado.

        Args:
            producto: Datos del producto

        Returns:
            Stock mínimo recomendado
        """
        # Regla: stock mínimo = consumo mensual promedio * 1.5
        consumo_mensual = producto.get("consumo_mensual_promedio", 10)
        return max(5, int(consumo_mensual * 1.5))

    def calcular_precio_recomendado(self, producto: Dict) -> float:
        """
        Calcula el precio recomendado basado en costo.

        Args:
            producto: Datos del producto

        Returns:
            Precio recomendado
        """
        costo = producto.get("costo", 0)
        margen = producto.get("margen", 0.30)  # 30% default

        if costo <= 0:
            return 0

        return costo * (1 + margen)


# Instancias globales
_validator_instance = None
_calculator_instance = None


def get_business_validator() -> BusinessValidator:
    """Obtiene la instancia singleton del validador."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = BusinessValidator()
    return _validator_instance


def get_business_calculator() -> BusinessCalculator:
    """Obtiene la instancia singleton de la calculadora."""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = BusinessCalculator()
    return _calculator_instance


# Funciones de conveniencia
def validate_pedido(pedido: Dict) -> ValidationResult:
    """Valida un pedido."""
    return get_business_validator().validate_pedido(pedido)


def validate_producto(producto: Dict) -> ValidationResult:
    """Valida un producto."""
    return get_business_validator().validate_producto(producto)


def calcular_descuento(pedido: Dict) -> Dict:
    """Calcula descuento de un pedido."""
    return get_business_calculator().calcular_descuento(pedido)
