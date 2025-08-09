"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
DiÃ¡logo moderno mejorado para productos de inventario
Incluye todos los campos de la base de datos con feedback visual avanzado
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, 
    QCheckBox, QGroupBox, QVBoxLayout
)

# Importar componentes modernos con manejo de errores
try:
    from rexus.utils.modern_form_components import ModernFormDialog, FormValidators
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
except ImportError:
    print("[WARNING] Modern form components not available, using basic dialog")
    from PyQt6.QtWidgets import QDialog as ModernFormDialog
    
    class FormValidators:
        @staticmethod
        def code_format(value):
            return bool(value.strip() if hasattr(value, 'strip') else value)
        
        @staticmethod
        def required_field(value):
            return bool(value.strip() if hasattr(value, 'strip') else value)
        
        @staticmethod
        def numeric_range(value, min_val=None, max_val=None):
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    return False
                if max_val is not None and num > max_val:
                    return False
                return True
            except:
                return False
        
        @staticmethod
        def email_format(value):
            return '@' in str(value) if value else False


class ModernProductDialog(ModernFormDialog):
    """DiÃ¡logo moderno para crear/editar productos de inventario"""
    
    def __init__(self, parent=None, product_data: Optional[Dict] = None):
        self.product_data = product_data
        self.is_editing = product_data is not None
        
        title = "Editar Producto" if self.is_editing else "Nuevo Producto"
        super().__init__(title, parent)
        
        self.setup_form_fields()
        
        if self.is_editing:
            self.load_product_data()
            
    def setup_form_fields(self):
        """Configura todos los campos del formulario"""
        
        # SECCIÃN: INFORMACIÃN BÃSICA
        basic_section = self.add_section("ð¦ InformaciÃ³n BÃ¡sica")
        basic_layout = QVBoxLayout(basic_section)
        
        # CÃ³digo del producto
        codigo_input = QLineEdit()
        codigo_input.setPlaceholderText("Ej: INV-001234, HER-5678")
        self.add_field(
            "codigo", "CÃ³digo del Producto", codigo_input, 
            required=True,
            tooltip="CÃ³digo Ãºnico para identificar el producto (formato: AAA-123456)",
            validation_func=FormValidators.code_format
        )
        
        # DescripciÃ³n
        descripcion_input = QLineEdit()
        descripcion_input.setPlaceholderText("DescripciÃ³n detallada del producto")
        self.add_field(
            "descripcion", "DescripciÃ³n", descripcion_input,
            required=True,
            tooltip="DescripciÃ³n clara y detallada del producto",
            validation_func=FormValidators.required_field
        )
        
        # Categoria y subcategorÃ­a
        categoria_combo = QComboBox()
        categoria_combo.addItems([
            "INVENTARIO", "HERRAJE", "VIDRIO", "MARCO", "ACCESORIO", 
            "SELLADOR", "HERRAMIENTA", "MATERIAL"
        ])
        self.add_field(
            "categoria", "CategorÃ­a", categoria_combo,
            required=True,
            tooltip="CategorÃ­a principal del producto"
        )
        
        subcategoria_input = QLineEdit()
        subcategoria_input.setPlaceholderText("Ej: Bisagras, Manijas, Perfiles")
        self.add_field(
            "subcategoria", "SubcategorÃ­a", subcategoria_input,
            tooltip="SubcategorÃ­a especÃ­fica dentro de la categorÃ­a principal"
        )
        
        # Tipo especÃ­fico
        tipo_input = QLineEdit()
        tipo_input.setPlaceholderText("Tipo especÃ­fico del producto")
        self.add_field(
            "tipo", "Tipo", tipo_input,
            tooltip="Tipo o modelo especÃ­fico del producto"
        )
        
        # SECCIÃN: STOCK Y CANTIDADES
        stock_section = self.add_section("ð Control de Stock")
        stock_layout = QVBoxLayout(stock_section)
        
        # Stock actual
        stock_actual_input = QSpinBox()
        stock_actual_input.setRange(0, 999999)
        stock_actual_input.setSuffix(" unidades")
        self.add_field(
            "stock_actual", "Stock Actual", stock_actual_input,
            required=True,
            tooltip="Cantidad actual en inventario"
        )
        
        # Stock mÃ­nimo
        stock_minimo_input = QSpinBox()
        stock_minimo_input.setRange(0, 999999)
        stock_minimo_input.setSuffix(" unidades")
        self.add_field(
            "stock_minimo", "Stock MÃ­nimo", stock_minimo_input,
            tooltip="Cantidad mÃ­nima antes de reorden"
        )
        
        # Stock mÃ¡ximo
        stock_maximo_input = QSpinBox()
        stock_maximo_input.setRange(0, 999999)
        stock_maximo_input.setSuffix(" unidades")
        self.add_field(
            "stock_maximo", "Stock MÃ¡ximo", stock_maximo_input,
            tooltip="Capacidad mÃ¡xima de almacenamiento"
        )
        
        # Stock reservado
        stock_reservado_input = QSpinBox()
        stock_reservado_input.setRange(0, 999999)
        stock_reservado_input.setSuffix(" unidades")
        stock_reservado_input.setEnabled(False)  # Solo lectura, se calcula automÃ¡ticamente
        self.add_field(
            "stock_reservado", "Stock Reservado", stock_reservado_input,
            tooltip="Cantidad reservada para pedidos (solo lectura)"
        )
        
        # SECCIÃN: PRECIOS Y COSTOS
        precio_section = self.add_section("ð° Precios y Costos")
        precio_layout = QVBoxLayout(precio_section)
        
        # Precio unitario
        precio_unitario_input = QDoubleSpinBox()
        precio_unitario_input.setRange(0.01, 999999.99)
        precio_unitario_input.setDecimals(2)
        precio_unitario_input.setPrefix("$ ")
        self.add_field(
            "precio_unitario", "Precio Unitario", precio_unitario_input,
            required=True,
            tooltip="Precio de venta por unidad",
            validation_func=lambda x: FormValidators.numeric_range(x, 0.01)
        )
        
        # Precio promedio
        precio_promedio_input = QDoubleSpinBox()
        precio_promedio_input.setRange(0.00, 999999.99)
        precio_promedio_input.setDecimals(2)
        precio_promedio_input.setPrefix("$ ")
        self.add_field(
            "precio_promedio", "Precio Promedio", precio_promedio_input,
            tooltip="Precio promedio ponderado"
        )
        
        # Costo unitario
        costo_unitario_input = QDoubleSpinBox()
        costo_unitario_input.setRange(0.00, 999999.99)
        costo_unitario_input.setDecimals(2)
        costo_unitario_input.setPrefix("$ ")
        self.add_field(
            "costo_unitario", "Costo Unitario", costo_unitario_input,
            tooltip="Costo de adquisiciÃ³n por unidad"
        )
        
        # Unidad de medida
        unidad_combo = QComboBox()
        unidad_combo.addItems([
            "UN", "MT", "M2", "M3", "KG", "LT", "CM", "PAR", "JGO", "CAJA"
        ])
        self.add_field(
            "unidad_medida", "Unidad de Medida", unidad_combo,
            required=True,
            tooltip="Unidad en la que se mide el producto"
        )
        
        # SECCIÃN: CARACTERÃSTICAS FÃSICAS
        caracteristicas_section = self.add_section("ð§ CaracterÃ­sticas FÃ­sicas")
        caracteristicas_layout = QVBoxLayout(caracteristicas_section)
        
        # UbicaciÃ³n
        ubicacion_input = QLineEdit()
        ubicacion_input.setPlaceholderText("Ej: Estante A-1, DepÃ³sito 2")
        self.add_field(
            "ubicacion", "UbicaciÃ³n", ubicacion_input,
            tooltip="UbicaciÃ³n fÃ­sica en el almacÃ©n"
        )
        
        # Color
        color_input = QLineEdit()
        color_input.setPlaceholderText("Ej: Blanco, Negro, Natural")
        self.add_field(
            "color", "Color", color_input,
            tooltip="Color del producto"
        )
        
        # Material
        material_input = QLineEdit()
        material_input.setPlaceholderText("Ej: Aluminio, PVC, Acero")
        self.add_field(
            "material", "Material", material_input,
            tooltip="Material principal del producto"
        )
        
        # Marca
        marca_input = QLineEdit()
        marca_input.setPlaceholderText("Marca del fabricante")
        self.add_field(
            "marca", "Marca", marca_input,
            tooltip="Marca o fabricante del producto"
        )
        
        # Modelo
        modelo_input = QLineEdit()
        modelo_input.setPlaceholderText("Modelo especÃ­fico")
        self.add_field(
            "modelo", "Modelo", modelo_input,
            tooltip="Modelo o referencia especÃ­fica"
        )
        
        # Acabado
        acabado_combo = QComboBox()
        acabado_combo.setEditable(True)
        acabado_combo.addItems([
            "Natural", "Blanco", "Negro", "Bronce", "Cromado", 
            "Anodizado", "Lacado", "Pulido", "Mate", "Brillante"
        ])
        self.add_field(
            "acabado", "Acabado", acabado_combo,
            tooltip="Acabado superficial del producto"
        )
        
        # SECCIÃN: PROVEEDOR Y LOGÃSTICA
        proveedor_section = self.add_section("ð¢ Proveedor y LogÃ­stica")
        proveedor_layout = QVBoxLayout(proveedor_section)
        
        # Proveedor
        proveedor_input = QLineEdit()
        proveedor_input.setPlaceholderText("Nombre del proveedor")
        self.add_field(
            "proveedor", "Proveedor", proveedor_input,
            required=True,
            tooltip="Proveedor principal del producto",
            validation_func=FormValidators.required_field
        )
        
        # CÃ³digo del proveedor
        codigo_proveedor_input = QLineEdit()
        codigo_proveedor_input.setPlaceholderText("CÃ³digo en catÃ¡logo del proveedor")
        self.add_field(
            "codigo_proveedor", "CÃ³digo del Proveedor", codigo_proveedor_input,
            tooltip="CÃ³digo o referencia del producto en el catÃ¡logo del proveedor"
        )
        
        # Tiempo de entrega
        tiempo_entrega_input = QSpinBox()
        tiempo_entrega_input.setRange(0, 365)
        tiempo_entrega_input.setSuffix(" dÃ­as")
        self.add_field(
            "tiempo_entrega_dias", "Tiempo de Entrega", tiempo_entrega_input,
            tooltip="Tiempo estimado de entrega en dÃ­as"
        )
        
        # SECCIÃN: INFORMACIÃN ADICIONAL
        adicional_section = self.add_section("ð InformaciÃ³n Adicional")
        adicional_layout = QVBoxLayout(adicional_section)
        
        # Observaciones
        observaciones_input = QTextEdit()
        observaciones_input.setMaximumHeight(100)
        observaciones_input.setPlaceholderText("Observaciones, notas especiales, instrucciones de manejo...")
        self.add_field(
            "observaciones", "Observaciones", observaciones_input,
            tooltip="InformaciÃ³n adicional sobre el producto"
        )
        
        # CÃ³digo QR
        codigo_qr_input = QLineEdit()
        codigo_qr_input.setPlaceholderText("CÃ³digo QR o cÃ³digo de barras")
        self.add_field(
            "codigo_qr", "CÃ³digo QR/Barras", codigo_qr_input,
            tooltip="CÃ³digo QR o de barras para identificaciÃ³n rÃ¡pida"
        )
        
        # URL de imagen
        imagen_url_input = QLineEdit()
        imagen_url_input.setPlaceholderText("URL de la imagen del producto")
        self.add_field(
            "imagen_url", "URL de Imagen", imagen_url_input,
            tooltip="Enlace a imagen del producto"
        )
        
        # Propiedades especiales
        propiedades_input = QTextEdit()
        propiedades_input.setMaximumHeight(80)
        propiedades_input.setPlaceholderText("Propiedades tÃ©cnicas especiales en formato JSON")
        self.add_field(
            "propiedades_especiales", "Propiedades Especiales", propiedades_input,
            tooltip="Propiedades tÃ©cnicas adicionales en formato JSON"
        )
        
        # Estado del producto
        estado_combo = QComboBox()
        estado_combo.addItems([
            "DISPONIBLE", "AGOTADO", "DESCONTINUADO", "EN_TRANSITO", 
            "RESERVADO", "DAÃADO", "EN_REVISION"
        ])
        self.add_field(
            "estado", "Estado", estado_combo,
            required=True,
            tooltip="Estado actual del producto"
        )
        
        # Producto activo
        activo_checkbox = QCheckBox("Producto activo")
        activo_checkbox.setChecked(True)
        self.add_field(
            "activo", "Activo", activo_checkbox,
            tooltip="Marcar si el producto estÃ¡ activo en el sistema"
        )
        
    def load_product_data(self):
        """Carga los datos del producto para ediciÃ³n"""
        if not self.product_data:
            return
            
        for key, field in self.fields.items():
            if key in self.product_data:
                value = self.product_data[key]
                widget = field.widget
                
                if hasattr(widget, 'setText'):
                    widget.setText(str(value) if value else "")
                elif hasattr(widget, 'setValue'):
                    widget.setValue(value if value is not None else 0)
                elif hasattr(widget, 'setCurrentText'):
                    widget.setCurrentText(str(value) if value else "")
                elif hasattr(widget, 'setChecked'):
                    widget.setChecked(bool(value))
                elif hasattr(widget, 'setPlainText'):
                    widget.setPlainText(str(value) if value else "")
                    
    def get_product_data(self) -> Dict[str, Any]:
        """Obtiene los datos del producto del formulario"""
        return self.get_form_data()
        
    def validate_business_rules(self) -> tuple[bool, str]:
        """Valida reglas de negocio especÃ­ficas"""
        data = self.get_form_data()
        
        # Validar que stock mÃ­nimo <= stock mÃ¡ximo
        if data.get("stock_minimo", 0) > data.get("stock_maximo", 0):
            return False, "El stock mÃ­nimo no puede ser mayor al stock mÃ¡ximo"
            
        # Validar que stock actual no exceda stock mÃ¡ximo
        if data.get("stock_actual", 0) > data.get("stock_maximo", 0):
            return False, "El stock actual no puede exceder el stock mÃ¡ximo"
            
        # Validar que precio unitario > costo unitario
        precio = data.get("precio_unitario", 0)
        costo = data.get("costo_unitario", 0)
        if costo > 0 and precio <= costo:
            return False, "El precio unitario debe ser mayor al costo unitario"
            
        return True, ""
        
    def validate_and_save(self):
        """Valida incluyendo reglas de negocio antes de guardar"""
        # ValidaciÃ³n estÃ¡ndar de campos
        all_valid = True
        for field in self.fields.values():
            if not field.validate():
                all_valid = False
                
        if not all_valid:
            return
            
        # Validaciones de reglas de negocio
        is_valid, error_message = self.validate_business_rules()
        if not is_valid:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error de ValidaciÃ³n", error_message)
            return
            
        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando producto...")
        
        # Simular guardado (reemplazar con lÃ³gica real)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == "__main__":
    """Test del diÃ¡logo moderno"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test con producto nuevo
    dialog = ModernProductDialog()
    
    if dialog.exec() == dialog.DialogCode.Accepted:
        data = dialog.get_product_data()
        print("Datos del producto:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    
    app.exec()