# Documentación Técnica - Módulo Compras

## Información General

**Módulo**: Compras  
**Archivo Principal**: `rexus/modules/compras/view.py`  
**Versión**: 2.1.0  
**Fecha de Última Actualización**: 05 de agosto de 2025  
**Desarrollador**: GitHub Copilot  
**Licencia**: MIT License  

## Descripción

El módulo de Compras es un componente crítico del sistema Rexus.app que gestiona todas las operaciones relacionadas con órdenes de compra, proveedores y procesos de adquisición. Proporciona una interfaz moderna y robusta para la creación, seguimiento y gestión de compras empresariales.

## Arquitectura del Módulo

### Estructura de Clases

#### 1. ComprasView (Clase Principal)
```python
class ComprasView(QWidget):
    """Vista principal del módulo de compras."""
```

**Responsabilidades:**
- Gestión de la interfaz principal del módulo
- Coordinación de operaciones de compra
- Manejo de filtros y búsquedas
- Validación de datos de entrada
- Integración con el sistema de logging

**Señales PyQt6:**
- `orden_creada = pyqtSignal(dict)`: Emitida cuando se crea una nueva orden
- `orden_actualizada = pyqtSignal(int, str)`: Emitida cuando se actualiza una orden
- `busqueda_realizada = pyqtSignal(dict)`: Emitida cuando se ejecuta una búsqueda

#### 2. DialogNuevaOrden (Clase de Diálogo)
```python
class DialogNuevaOrden(QDialog):
    """Diálogo para crear una nueva orden de compra."""
```

**Responsabilidades:**
- Captura de datos para nuevas órdenes
- Validación de formularios
- Sanitización de datos de entrada
- Integración con sistema de logging

## Características Implementadas

### 1. Sistema de Logging Avanzado
```python
def __init__(self):
    super().__init__()
    self.controller = None
    self.logger = logging.getLogger(__name__)
    self.init_ui()
```

**Funcionalidades:**
- Registro detallado de operaciones críticas
- Trazabilidad completa de acciones de usuario
- Monitoreo de errores y excepciones
- Logging de validaciones y sanitización

### 2. Sanitización de Datos Robusta

#### En Búsquedas:
```python
def buscar_compras(self):
    try:
        self.logger.info("Iniciando búsqueda de compras")
        
        # Sanitizar texto de búsqueda
        texto_busqueda = DataSanitizer.sanitize_text(self.input_busqueda.text().strip())
        
        filtros = {
            "proveedor": texto_busqueda,
            "estado": self.combo_estado.currentText(),
            "fecha_inicio": self.date_desde.date().toString('yyyy-MM-dd'),
            "fecha_fin": self.date_hasta.date().toString('yyyy-MM-dd'),
        }
```

#### En Formularios:
```python
def obtener_datos(self):
    try:
        self.logger.info("Obteniendo y sanitizando datos del formulario de compras")
        
        # Sanitizar datos de entrada
        proveedor_limpio = DataSanitizer.sanitize_text(self.input_proveedor.text().strip())
        numero_orden_limpio = DataSanitizer.sanitize_text(self.input_numero_orden.text().strip())
        observaciones_limpias = DataSanitizer.sanitize_text(self.input_observaciones.toPlainText().strip())
```

### 3. Validación de Órdenes Duplicadas

```python
def validar_orden_duplicada(self, numero_orden, proveedor):
    """Valida si ya existe una orden con el mismo número para el mismo proveedor."""
    try:
        self.logger.info(f"Validando orden duplicada: {numero_orden} para {proveedor}")
        
        # Recorrer tabla de compras para buscar duplicados
        for row in range(self.tabla_compras.rowCount()):
            proveedor_item = self.tabla_compras.item(row, 1)  # Columna proveedor
            numero_item = self.tabla_compras.item(row, 2)     # Columna número orden
            
            if proveedor_item and numero_item:
                # Normalizar datos para comparación
                proveedor_norm = DataSanitizer.sanitize_text(proveedor).lower()
                proveedor_existente_norm = DataSanitizer.sanitize_text(proveedor_existente).lower()
                numero_norm = DataSanitizer.sanitize_text(numero_orden).lower()
                numero_existente_norm = DataSanitizer.sanitize_text(numero_existente).lower()
                
                if proveedor_norm == proveedor_existente_norm and numero_norm == numero_existente_norm:
                    self.logger.warning(f"Orden duplicada encontrada: {numero_orden} para {proveedor}")
                    return True
        
        return False
```

### 4. Gestión Avanzada de UI

#### Panel de Control:
- Filtros por proveedor, estado y fechas
- Búsqueda en tiempo real
- Controles de navegación temporal

#### Tabla de Compras:
- Visualización de datos tabulares
- Estados con códigos de color
- Botones de acción por fila
- Ordenamiento y filtrado

#### Panel de Estadísticas:
- Métricas en tiempo real
- Indicadores visuales
- Gráficos de resumen

### 5. Manejo Robusto de Errores

```python
def abrir_dialog_nueva_orden(self):
    try:
        self.logger.info("Abriendo diálogo para nueva orden de compra")
        
        dialog = DialogNuevaOrden(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            
            # Validar orden duplicada
            if self.validar_orden_duplicada(datos.get("numero_orden", ""), datos.get("proveedor", "")):
                error_msg = f"Ya existe una orden con número '{datos.get('numero_orden')}' para el proveedor '{datos.get('proveedor')}'"
                self.logger.warning(f"Intento de crear orden duplicada: {error_msg}")
                show_error(self, "Orden duplicada", error_msg)
                return
            
            self.orden_creada.emit(datos)
            self.logger.info(f"Orden creada exitosamente: {datos.get('numero_orden')} - {datos.get('proveedor')}")
        else:
            self.logger.info("Diálogo de nueva orden cancelado por el usuario")
            
    except Exception as e:
        error_msg = f"Error al crear nueva orden: {str(e)}"
        self.logger.error(error_msg)
        show_error(self, "Error", error_msg)
```

## Estructura de Datos

### Orden de Compra
```python
{
    "proveedor": "string",                    # Nombre del proveedor (sanitizado)
    "numero_orden": "string",                 # Número único de orden (sanitizado)
    "fecha_pedido": "YYYY-MM-DD",            # Fecha del pedido
    "fecha_entrega_estimada": "YYYY-MM-DD",  # Fecha estimada de entrega
    "estado": "string",                       # Estado actual de la orden
    "descuento": "float",                     # Descuento aplicado
    "impuestos": "float",                     # Impuestos calculados
    "observaciones": "string",                # Observaciones (sanitizadas)
    "usuario_creacion": "string"              # Usuario que creó la orden
}
```

### Filtros de Búsqueda
```python
{
    "proveedor": "string",           # Filtro por proveedor (sanitizado)
    "estado": "string",              # Filtro por estado
    "fecha_inicio": "YYYY-MM-DD",    # Fecha de inicio del rango
    "fecha_fin": "YYYY-MM-DD"        # Fecha de fin del rango
}
```

## Estados de Órdenes

| Estado | Descripción | Color UI |
|--------|-------------|----------|
| `PENDIENTE` | Orden creada, pendiente de aprobación | Amarillo |
| `APROBADA` | Orden aprobada, lista para procesar | Cyan |
| `RECIBIDA` | Orden recibida completamente | Verde |
| `CANCELADA` | Orden cancelada | Rojo |

## Validaciones Implementadas

### 1. Validación de Datos Obligatorios
- Proveedor no puede estar vacío
- Número de orden es requerido
- Fechas deben ser válidas

### 2. Validación de Duplicados
- Combinación proveedor + número de orden debe ser única
- Normalización de texto para comparaciones precisas
- Logging de intentos de duplicación

### 3. Validación de Fechas
- Fecha de entrega no puede ser anterior a fecha de pedido
- Formato de fecha estandardizado (YYYY-MM-DD)

### 4. Sanitización de Entradas
- Todos los campos de texto son sanitizados
- Eliminación de caracteres peligrosos
- Normalización de espacios en blanco

## Seguridad

### Medidas Implementadas

1. **Sanitización de Datos:**
   - Uso de `DataSanitizer` en todas las entradas
   - Prevención de inyección de código
   - Validación de tipos de datos

2. **Logging de Seguridad:**
   - Registro de todas las operaciones críticas
   - Trazabilidad de acciones de usuario
   - Monitoreo de intentos de acceso no autorizado

3. **Validación de Entrada:**
   - Verificación de longitud de campos
   - Validación de formatos específicos
   - Manejo seguro de excepciones

## Metodología de Testing

### Casos de Prueba Cubiertos

1. **Creación de Órdenes:**
   - Orden válida nueva
   - Intento de orden duplicada
   - Datos incompletos
   - Caracteres especiales en campos

2. **Búsquedas:**
   - Búsqueda por proveedor
   - Filtros por estado
   - Rangos de fechas
   - Búsquedas vacías

3. **Validaciones:**
   - Detección de duplicados
   - Sanitización de datos
   - Manejo de errores

### Cobertura de Edge Cases

- Órdenes con números muy largos
- Proveedores con caracteres especiales
- Fechas límite del sistema
- Campos con contenido malicioso

## Integración con el Sistema

### Dependencias

```python
# Utilidades del sistema
from rexus.utils.data_sanitizer import DataSanitizer
from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.utils.form_validators import FormValidator, FormValidatorManager

# Componentes del core
from rexus.core.auth_manager import AuthManager

# Framework Qt
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialog, QTableWidget
```

### Señales y Slots

```python
# Señales emitidas por el módulo
self.orden_creada.emit(datos_orden)
self.orden_actualizada.emit(orden_id, nuevo_estado)
self.busqueda_realizada.emit(filtros)
```

## Configuración y Personalización

### Parámetros Configurables

```python
# Configuración de validación
LONGITUD_MAXIMA_NUMERO_ORDEN = 50
LONGITUD_MAXIMA_PROVEEDOR = 100
DIAS_MAXIMOS_ENTREGA = 365

# Configuración de UI
FILAS_POR_PAGINA = 50
TIMEOUT_BUSQUEDA = 5000  # ms
COLORES_ESTADO = {
    'PENDIENTE': '#FFFF00',
    'APROBADA': '#00FFFF',
    'RECIBIDA': '#00FF00',
    'CANCELADA': '#FF0000'
}
```

## Logs y Monitoreo

### Tipos de Logs Generados

1. **Operaciones Críticas:**
   ```
   INFO: Iniciando búsqueda de compras
   INFO: Orden creada exitosamente: ORD-001 - Proveedor ABC
   WARNING: Intento de crear orden duplicada: ORD-001 para Proveedor ABC
   ```

2. **Errores y Excepciones:**
   ```
   ERROR: Error al crear nueva orden: Invalid data format
   ERROR: Error al cargar compras en tabla: Database connection failed
   ```

3. **Validaciones:**
   ```
   INFO: Validando orden duplicada: ORD-001 para Proveedor ABC
   WARNING: Orden duplicada encontrada: ORD-001 para Proveedor ABC
   ```

## Mantenimiento y Extensibilidad

### Puntos de Extensión

1. **Nuevos Estados de Orden:**
   - Agregar a la enumeración de estados
   - Definir color en configuración
   - Implementar lógica de transición

2. **Campos Adicionales:**
   - Extender estructura de datos
   - Agregar al formulario de captura
   - Incluir en validaciones

3. **Nuevos Filtros:**
   - Agregar controles de UI
   - Implementar lógica de filtrado
   - Incluir en logging

### Consideraciones de Performance

- Paginación en tablas grandes
- Caché de consultas frecuentes
- Validación asíncrona para grandes volúmenes
- Optimización de búsquedas con índices

## Roadmap de Mejoras

### Versión 2.2.0 (Planificado)
- [ ] Integración con API de proveedores
- [ ] Validación de disponibilidad en tiempo real
- [ ] Workflow de aprobaciones multinivel
- [ ] Notificaciones automatizadas

### Versión 2.3.0 (Futuro)
- [ ] Análisis predictivo de compras
- [ ] Integración con sistemas ERP externos
- [ ] Dashboard avanzado con métricas KPI
- [ ] API REST para integración externa

## Conclusiones

El módulo de Compras representa una implementación robusta y segura para la gestión de órdenes de compra empresariales. Con características avanzadas de seguridad, validación y logging, proporciona una base sólida para operaciones críticas de negocio.

Las mejoras implementadas en esta versión incluyen:
- Sistema de logging completo
- Sanitización robusta de datos
- Validación de órdenes duplicadas
- Manejo avanzado de errores
- UI responsive y accesible

La arquitectura modular permite extensibilidad futura manteniendo la estabilidad y seguridad del sistema existente.
