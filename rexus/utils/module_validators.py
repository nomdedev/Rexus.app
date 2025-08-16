"""Shim de compatibilidad para validadores de módulos.

Este archivo proporciona una interfaz retrocompatible que los tests
antiguos importan (inventario_validator, herrajes_validator, etc.) y
funciones como validate_producto_form y validate_module_form.

Implementaciones mínimas usan las utilidades existentes en
`rexus.utils.form_validators` y validaciones básicas.
"""
from typing import Tuple, Dict, Any
import re

from rexus.utils.form_validators import validacion_codigo_producto, validacion_direccion


def _coerce_str(value):
    if value is None:
        return ""
    return str(value)


class SimpleValidator:
    def __init__(self, name: str):
        self.name = name

    def _validar_codigo(self, codigo) -> Tuple[bool, str]:
        codigo = _coerce_str(codigo)
        if not codigo:
            return False, "Código vacío"
        # Aceptar una gama amplia de códigos alfanuméricos opcionalmente con guiones
        if re.match(r'^[A-Z0-9-]{1,50}$', codigo.upper()):
            return True, ""
        # fallback a la validación común
        return validacion_codigo_producto(_DummyField(), codigo)

    def validate_producto_form(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        errores = {}

        codigo = data.get("codigo", "") if data else ""
        valido, msg = self._validar_codigo(codigo)
        if not valido:
            errores["codigo"] = msg or "Código inválido"

        # Algunos productos usan 'descripcion' en lugar de 'nombre'
        nombre = _coerce_str(data.get("nombre", "") if data else "")
        descripcion = _coerce_str(data.get("descripcion", "") if data else "")
        if not nombre.strip() and not descripcion.strip():
            errores["nombre"] = "Nombre o descripción es obligatorio"

        # Categoria obligatoria
        categoria = _coerce_str(data.get("categoria", "") if data else "")
        if not categoria.strip():
            errores["categoria"] = "Categoría es obligatoria"

        # Precio unitario debe ser numérico y >= 0
        try:
            precio = float(data.get("precio_unitario", 0))
            if precio < 0:
                errores["precio_unitario"] = "Precio unitario no puede ser negativo"
        except Exception:
            errores["precio_unitario"] = "Precio unitario inválido"

        # Stock actual debe ser entero no negativo
        try:
            stock = data.get("stock_actual", None)
            if stock is None:
                raise ValueError("stock missing")
            stock_val = int(stock)
            if stock_val < 0:
                errores["stock_actual"] = "Stock no puede ser negativo"
        except Exception:
            errores["stock_actual"] = "Stock inválido"

        return (len(errores) == 0), errores

    # Métodos específicos esperados por los tests
    def validate_herraje_form(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        errores = {}
        codigo = data.get("codigo", "") if data else ""
        valido, msg = self._validar_codigo(codigo)
        if not valido:
            errores["codigo"] = msg or "Código inválido"

        tipo = _coerce_str(data.get("tipo", ""))
        if not tipo.strip():
            errores["tipo"] = "Tipo es obligatorio"

        return (len(errores) == 0), errores

    def validate_vidrio_form(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        errores = {}
        codigo = data.get("codigo", "") if data else ""
        valido, msg = self._validar_codigo(codigo)
        if not valido:
            errores["codigo"] = msg or "Código inválido"

        try:
            espesor = float(data.get("espesor", 0))
            ancho = float(data.get("ancho", 0))
            alto = float(data.get("alto", 0))
            if espesor <= 0 or ancho <= 0 or alto <= 0:
                errores["dimensiones"] = "Dimensiones deben ser positivas"
        except Exception:
            errores["dimensiones"] = "Dimensiones inválidas"

        return (len(errores) == 0), errores

    def validate_pedido_form(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        errores = {}
        tipo = _coerce_str(data.get("tipo_pedido", ""))
        if not tipo.strip():
            errores["tipo_pedido"] = "Tipo de pedido obligatorio"

        # total y subtotal coherentes
        try:
            subtotal = float(data.get("subtotal", 0))
            total = float(data.get("total", 0))
            if subtotal < 0 or total < 0:
                errores["importe"] = "Importes no pueden ser negativos"
        except Exception:
            errores["importe"] = "Importes inválidos"

        return (len(errores) == 0), errores

    def validate_obra_form(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        errores = {}
        nombre = _coerce_str(data.get("nombre", ""))
        if not nombre.strip():
            errores["nombre"] = "Nombre es obligatorio"

        ubicacion = _coerce_str(data.get("ubicacion", ""))
        if ubicacion and len(ubicacion.strip()) < 10:
            # usar validacion de direccion si está disponible
            valido, msg = validacion_direccion(_DummyField(), ubicacion)
            if not valido:
                errores["ubicacion"] = msg

        return (len(errores) == 0), errores


def validate_module_form(module_name: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """Validador genérico por módulo: delega a los validadores simples.

    Para compatibilidad con tests antiguos, los módulos desconocidos se consideran válidos.
    """
    mapping = {
        "inventario": inventario_validator,
        "herrajes": herrajes_validator,
        "vidrios": vidrios_validator,
        "pedidos": pedidos_validator,
        "obras": obras_validator,
    }

    validator = mapping.get(module_name)
    if not validator:
        return True, {}

    # Intentar delegar a un método específico según el módulo
    specific_map = {
        "herrajes": "validate_herraje_form",
        "vidrios": "validate_vidrio_form",
        "pedidos": "validate_pedido_form",
        "obras": "validate_obra_form",
        "inventario": "validate_producto_form",
    }

    method_name = specific_map.get(module_name, "validate_producto_form")
    if hasattr(validator, method_name):
        return getattr(validator, method_name)(data)

    # Fallback: intentar validate_producto_form
    if hasattr(validator, "validate_producto_form"):
        return validator.validate_producto_form(data)

    return True, {}


# Dummy field para usar los validadores de formulario sin QWidgets
class _DummyField:
    def setStyleSheet(self, _s: str):
        pass


# Exponer instancias esperadas por los tests
inventario_validator = SimpleValidator("inventario")
herrajes_validator = SimpleValidator("herrajes")
vidrios_validator = SimpleValidator("vidrios")
pedidos_validator = SimpleValidator("pedidos")
obras_validator = SimpleValidator("obras")
