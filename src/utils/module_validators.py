"""
Module Validators - Rexus.app
Specialized validators for each module in the system.
"""

import re
import datetime
from typing import Dict, List, Tuple, Any, Optional
from src.utils.form_validator import form_validator

class InventarioValidator:
    """Validator for Inventario module forms."""
    
    def validate_producto_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete producto form data.
        
        Args:
            form_data: Dictionary with producto form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate código
        valid, error = form_validator.validate_product_code(form_data.get('codigo', ''))
        if not valid:
            errors.append(error)
        
        # Validate descripción
        valid, error = form_validator.validate_text_field(
            form_data.get('descripcion', ''), 
            'Descripción', 
            min_length=3, 
            max_length=500
        )
        if not valid:
            errors.append(error)
        
        # Validate categoría
        valid, error = form_validator.validate_text_field(
            form_data.get('categoria', ''), 
            'Categoría', 
            min_length=2, 
            max_length=50
        )
        if not valid:
            errors.append(error)
        
        # Validate precio_unitario
        valid, error = form_validator.validate_price(form_data.get('precio_unitario'))
        if not valid:
            errors.append(error)
        
        # Validate stock_actual
        valid, error = form_validator.validate_quantity(form_data.get('stock_actual'))
        if not valid:
            errors.append(error)
        
        # Validate stock_minimo
        stock_minimo = form_data.get('stock_minimo', 0)
        if stock_minimo is not None:
            valid, error = form_validator.validate_quantity(stock_minimo)
            if not valid:
                errors.append(f"Stock mínimo: {error}")
        
        # Validate proveedor if provided
        proveedor = form_data.get('proveedor', '')
        if proveedor:
            valid, error = form_validator.validate_text_field(
                proveedor, 'Proveedor', min_length=2, max_length=100, required=False
            )
            if not valid:
                errors.append(error)
        
        return len(errors) == 0, errors

class HerrajesValidator:
    """Validator for Herrajes module forms."""
    
    TIPOS_VALIDOS = [
        "BISAGRA", "CERRADURA", "MANIJA", "TORNILLO", "RIEL", 
        "SOPORTE", "PESTILLO", "RUEDA", "GUIA", "OTRO"
    ]
    
    def validate_herraje_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete herraje form data.
        
        Args:
            form_data: Dictionary with herraje form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate código
        valid, error = form_validator.validate_product_code(form_data.get('codigo', ''))
        if not valid:
            errors.append(error)
        
        # Validate descripción
        valid, error = form_validator.validate_text_field(
            form_data.get('descripcion', ''), 
            'Descripción', 
            min_length=3, 
            max_length=500
        )
        if not valid:
            errors.append(error)
        
        # Validate tipo
        tipo = form_data.get('tipo', '')
        if tipo not in self.TIPOS_VALIDOS:
            errors.append(f"Tipo de herraje inválido. Debe ser uno de: {', '.join(self.TIPOS_VALIDOS)}")
        
        # Validate precio_unitario
        valid, error = form_validator.validate_price(form_data.get('precio_unitario'))
        if not valid:
            errors.append(error)
        
        # Validate material if provided
        material = form_data.get('material', '')
        if material:
            valid, error = form_validator.validate_text_field(
                material, 'Material', min_length=2, max_length=50, required=False
            )
            if not valid:
                errors.append(error)
        
        return len(errors) == 0, errors

class VidriosValidator:
    """Validator for Vidrios module forms."""
    
    TIPOS_VALIDOS = [
        "FLOTADO", "TEMPLADO", "LAMINADO", "DVH", "REFLECTIVO", 
        "ACUSTICO", "TERMICO", "DECORATIVO", "OTRO"
    ]
    
    def validate_vidrio_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete vidrio form data.
        
        Args:
            form_data: Dictionary with vidrio form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate código
        valid, error = form_validator.validate_product_code(form_data.get('codigo', ''))
        if not valid:
            errors.append(error)
        
        # Validate descripción
        valid, error = form_validator.validate_text_field(
            form_data.get('descripcion', ''), 
            'Descripción', 
            min_length=3, 
            max_length=500
        )
        if not valid:
            errors.append(error)
        
        # Validate tipo
        tipo = form_data.get('tipo', '')
        if tipo and tipo not in self.TIPOS_VALIDOS:
            errors.append(f"Tipo de vidrio inválido. Debe ser uno de: {', '.join(self.TIPOS_VALIDOS)}")
        
        # Validate espesor (thickness in mm)
        espesor = form_data.get('espesor')
        if espesor is not None:
            try:
                espesor_float = float(espesor)
                if espesor_float <= 0 or espesor_float > 50:
                    errors.append("Espesor debe estar entre 0.1 y 50 mm")
            except (ValueError, TypeError):
                errors.append("Espesor debe ser un número válido")
        
        # Validate dimensiones if provided
        ancho = form_data.get('ancho')
        alto = form_data.get('alto')
        
        if ancho is not None:
            valid, error = form_validator.validate_quantity(ancho)
            if not valid:
                errors.append(f"Ancho: {error}")
        
        if alto is not None:
            valid, error = form_validator.validate_quantity(alto)
            if not valid:
                errors.append(f"Alto: {error}")
        
        return len(errors) == 0, errors

class PedidosValidator:
    """Validator for Pedidos module forms."""
    
    TIPOS_PEDIDO = [
        "COMPRA", "VENTA", "INTERNO", "OBRA", "DEVOLUCION", "AJUSTE", "PRODUCCION"
    ]
    
    ESTADOS_PEDIDO = [
        "PENDIENTE", "CONFIRMADO", "EN_PROCESO", "ENVIADO", "ENTREGADO", 
        "CANCELADO", "DEVUELTO"
    ]
    
    def validate_pedido_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete pedido form data.
        
        Args:
            form_data: Dictionary with pedido form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate tipo_pedido
        tipo_pedido = form_data.get('tipo_pedido', '')
        if tipo_pedido not in self.TIPOS_PEDIDO:
            errors.append(f"Tipo de pedido inválido. Debe ser uno de: {', '.join(self.TIPOS_PEDIDO)}")
        
        # Validate estado
        estado = form_data.get('estado', '')
        if estado and estado not in self.ESTADOS_PEDIDO:
            errors.append(f"Estado inválido. Debe ser uno de: {', '.join(self.ESTADOS_PEDIDO)}")
        
        # Validate fecha_pedido
        fecha_pedido = form_data.get('fecha_pedido')
        if fecha_pedido:
            if not self._validate_date(fecha_pedido):
                errors.append("Fecha de pedido inválida")
        
        # Validate fecha_entrega_estimada
        fecha_entrega = form_data.get('fecha_entrega_estimada')
        if fecha_entrega:
            if not self._validate_date(fecha_entrega):
                errors.append("Fecha de entrega inválida")
            elif fecha_pedido and self._parse_date(fecha_entrega) < self._parse_date(fecha_pedido):
                errors.append("Fecha de entrega no puede ser anterior a fecha de pedido")
        
        # Validate cliente_id or proveedor_id
        cliente_id = form_data.get('cliente_id')
        proveedor_id = form_data.get('proveedor_id')
        
        if not cliente_id and not proveedor_id:
            errors.append("Debe especificar cliente o proveedor")
        
        if cliente_id:
            valid, error = self._validate_id(cliente_id, "Cliente ID")
            if not valid:
                errors.append(error)
        
        if proveedor_id:
            valid, error = self._validate_id(proveedor_id, "Proveedor ID")
            if not valid:
                errors.append(error)
        
        # Validate totales
        subtotal = form_data.get('subtotal')
        if subtotal is not None:
            valid, error = form_validator.validate_price(subtotal)
            if not valid:
                errors.append(f"Subtotal: {error}")
        
        total = form_data.get('total')
        if total is not None:
            valid, error = form_validator.validate_price(total)
            if not valid:
                errors.append(f"Total: {error}")
        
        return len(errors) == 0, errors
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date string format."""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            try:
                datetime.datetime.strptime(date_str, '%d/%m/%Y')
                return True
            except ValueError:
                return False
    
    def _parse_date(self, date_str: str) -> datetime.datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return datetime.datetime.strptime(date_str, '%d/%m/%Y')
    
    def _validate_id(self, id_value: Any, field_name: str) -> Tuple[bool, str]:
        """Validate ID field."""
        try:
            int_id = int(id_value)
            if int_id <= 0:
                return False, f"{field_name} debe ser un número positivo"
            return True, ""
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número válido"

class ObrasValidator:
    """Validator for Obras module forms."""
    
    ESTADOS_OBRA = [
        "PLANIFICACION", "INICIADA", "EN_PROCESO", "PAUSADA", 
        "FINALIZADA", "CANCELADA", "ENTREGADA"
    ]
    
    ETAPAS_OBRA = [
        "DISEÑO", "PREPARACION", "ESTRUCTURA", "CERRAMIENTO", 
        "INSTALACIONES", "ACABADOS", "ENTREGA", "GARANTIA"
    ]
    
    def validate_obra_form(self, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete obra form data.
        
        Args:
            form_data: Dictionary with obra form data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate codigo_obra
        valid, error = form_validator.validate_product_code(form_data.get('codigo_obra', ''))
        if not valid:
            errors.append(f"Código de obra: {error}")
        
        # Validate nombre
        valid, error = form_validator.validate_text_field(
            form_data.get('nombre', ''), 
            'Nombre de obra', 
            min_length=3, 
            max_length=200
        )
        if not valid:
            errors.append(error)
        
        # Validate descripción
        descripcion = form_data.get('descripcion', '')
        if descripcion:
            valid, error = form_validator.validate_text_field(
                descripcion, 'Descripción', min_length=10, max_length=2000, required=False
            )
            if not valid:
                errors.append(error)
        
        # Validate estado
        estado = form_data.get('estado', '')
        if estado and estado not in self.ESTADOS_OBRA:
            errors.append(f"Estado inválido. Debe ser uno de: {', '.join(self.ESTADOS_OBRA)}")
        
        # Validate etapa_actual
        etapa = form_data.get('etapa_actual', '')
        if etapa and etapa not in self.ETAPAS_OBRA:
            errors.append(f"Etapa inválida. Debe ser una de: {', '.join(self.ETAPAS_OBRA)}")
        
        # Validate fechas
        fecha_inicio = form_data.get('fecha_inicio')
        if fecha_inicio and not self._validate_date(fecha_inicio):
            errors.append("Fecha de inicio inválida")
        
        fecha_fin_estimada = form_data.get('fecha_fin_estimada')
        if fecha_fin_estimada:
            if not self._validate_date(fecha_fin_estimada):
                errors.append("Fecha de fin estimada inválida")
            elif fecha_inicio and self._parse_date(fecha_fin_estimada) < self._parse_date(fecha_inicio):
                errors.append("Fecha de fin no puede ser anterior a fecha de inicio")
        
        # Validate presupuesto
        presupuesto = form_data.get('presupuesto_inicial')
        if presupuesto is not None:
            valid, error = form_validator.validate_price(presupuesto)
            if not valid:
                errors.append(f"Presupuesto inicial: {error}")
        
        # Validate ubicación
        ubicacion = form_data.get('ubicacion', '')
        if ubicacion:
            valid, error = form_validator.validate_text_field(
                ubicacion, 'Ubicación', min_length=5, max_length=500, required=False
            )
            if not valid:
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date string format."""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            try:
                datetime.datetime.strptime(date_str, '%d/%m/%Y')
                return True
            except ValueError:
                return False
    
    def _parse_date(self, date_str: str) -> datetime.datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return datetime.datetime.strptime(date_str, '%d/%m/%Y')

# Global validator instances
inventario_validator = InventarioValidator()
herrajes_validator = HerrajesValidator()
vidrios_validator = VidriosValidator()
pedidos_validator = PedidosValidator()
obras_validator = ObrasValidator()

def validate_module_form(module_name: str, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate forms by module name.
    
    Args:
        module_name: Name of the module
        form_data: Form data to validate
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    module_name = module_name.lower()
    
    if module_name == 'inventario':
        return inventario_validator.validate_producto_form(form_data)
    elif module_name == 'herrajes':
        return herrajes_validator.validate_herraje_form(form_data)
    elif module_name == 'vidrios':
        return vidrios_validator.validate_vidrio_form(form_data)
    elif module_name == 'pedidos':
        return pedidos_validator.validate_pedido_form(form_data)
    elif module_name == 'obras':
        return obras_validator.validate_obra_form(form_data)
    else:
        return True, []  # Unknown module, no validation