# Documentación Técnica - Sistema Optimizado

## 🏗️ Arquitectura del Sistema

### Componentes Principales
```
stock.app/
├── utils/
│   ├── universal_search.py          # Sistema de búsqueda universal
│   ├── accessibility_helper.py      # Helper de accesibilidad
│   ├── contrast_fixer.py           # Corrector automático de contraste
│   ├── search_feedback_manager.py  # Gestor de feedback de búsqueda
│   └── theme_manager_fixed.py      # Gestor de temas optimizado
├── resources/qss/
│   ├── theme_qt_compatible.qss     # Tema principal compatible con Qt
│   ├── theme_optimized.qss         # Tema optimizado
│   └── theme_fixed.qss             # Tema con correcciones
├── components/
│   └── modern_header.py            # Header moderno con búsqueda
└── modules/
    └── [todos los módulos]         # Módulos integrados
```

## 🔧 APIs y Interfaces

### UniversalSearch
```python
class UniversalSearch:
    def search_in_table(self, table, query) -> List[Match]
    def highlight_matches(self, table, matches)
    def clear_highlights(self, table)
    def connect_search_widget(self, widget)
```

### AccessibilityHelper
```python
class AccessibilityHelper:
    def setup_button_accessibility(self, button)
    def setup_table_accessibility(self, table)
    def setup_label_accessibility(self, label)
    def apply_to_widget(self, widget)
```

### SearchFeedbackManager
```python
class SearchFeedbackManager:
    def register_feedback_label(self, label)
    def show_search_feedback(self, message, status_type, duration)
    def _hide_feedback(self, label)
```

## 🎨 Sistema de Temas

### Estructura de Temas
```css
/* Jerarquía de estilos */
QWidget { /* Estilos base */ }
QTableWidget { /* Estilos específicos de tabla */ }
QTableWidget::item { /* Estilos de elementos de tabla */ }
QTableWidget::item:selected { /* Estilos de selección */ }
```

### Propiedades Compatibles
- ✅ color, background-color
- ✅ border, border-radius
- ✅ padding, margin
- ✅ font-family, font-size, font-weight
- ❌ box-shadow (eliminado)
- ❌ outline (eliminado)
- ❌ text-shadow (eliminado)

## 🔍 Sistema de Búsqueda

### Algoritmo de Búsqueda
1. **Normalización**: Eliminación de acentos y conversión a minúsculas
2. **Tokenización**: División en términos de búsqueda
3. **Coincidencia**: Búsqueda en texto, números y datos formateados
4. **Resaltado**: Aplicación de estilos CSS a coincidencias

### Configuración de Búsqueda
```python
# Configuración por defecto
search_config = {
    "case_sensitive": False,
    "accent_sensitive": False,
    "numeric_search": True,
    "highlight_color": "#ffeb3b",
    "highlight_background": "rgba(255, 235, 59, 0.3)"
}
```

## ♿ Accesibilidad

### Estándares Cumplidos
- **WCAG 2.1 AA**: Contraste mínimo 4.5:1
- **Navegación por Teclado**: Todos los elementos accesibles
- **Lectores de Pantalla**: Nombres y descripciones accesibles
- **Feedback Visual**: Indicadores claros de estado

### Implementación
```python
# Configuración automática de accesibilidad
def setup_accessibility(self):
    if hasattr(self, 'accessibility_helper'):
        self.accessibility_helper.apply_to_widget(self)
```

## 🚀 Optimizaciones de Rendimiento

### Técnicas Aplicadas
1. **Lazy Loading**: Carga diferida de componentes pesados
2. **Caching**: Cache de estilos y configuraciones
3. **Debouncing**: Optimización de búsquedas en tiempo real
4. **Memory Management**: Gestión eficiente de recursos Qt

### Métricas de Rendimiento
- **Tiempo de Carga**: <2 segundos para módulos principales
- **Memoria**: <50MB para aplicación completa
- **CPU**: <5% en operaciones normales

## 🛡️ Seguridad

### Validación de Entrada
```python
def validate_search_query(query):
    # Limitar longitud
    if len(query) > 1000:
        return False

    # Sanitizar caracteres especiales
    query = re.sub(r'[<>"']', '', query)

    # Validar contenido
    if not query.strip():
        return False

    return True
```

### Logging de Auditoría
```python
# Registro de acciones importantes
logger.info(f"Búsqueda realizada: {query} - Usuario: {user_id}")
logger.info(f"Tema cambiado: {old_theme} -> {new_theme}")
logger.info(f"Módulo accedido: {module_name}")
```

## 📊 Monitoreo y Debugging

### Logs Disponibles
- **app.log**: Log principal de la aplicación
- **app_json.log**: Log estructurado en JSON
- **audit.log**: Log de auditoría y seguridad

### Debugging
```python
# Habilitar modo debug
export STOCK_APP_DEBUG=1
export STOCK_APP_LOG_LEVEL=DEBUG
```

## 🔄 Mantenimiento

### Actualizaciones de Temas
1. Modificar archivos QSS en `resources/qss/`
2. Ejecutar `utils/qss_cleaner.py` para validar compatibilidad
3. Probar con `utils/contrast_fixer.py` para verificar contraste

### Actualizaciones de Búsqueda
1. Modificar `utils/universal_search.py`
2. Actualizar configuración en módulos afectados
3. Probar con `demo_mejoras_visuales.py`

### Actualizaciones de Accesibilidad
1. Modificar `utils/accessibility_helper.py`
2. Ejecutar `validar_accesibilidad.py` para verificar cambios
3. Probar con lectores de pantalla

## 🧪 Testing

### Scripts de Testing
- **visual_tester_complete.py**: Testing visual completo
- **demo_mejoras_visuales.py**: Demo de mejoras
- **validar_accesibilidad.py**: Validación de accesibilidad

### Casos de Prueba
1. **Búsqueda Universal**: Probar en todos los módulos
2. **Cambio de Tema**: Verificar consistencia visual
3. **Accesibilidad**: Probar con navegación por teclado
4. **Rendimiento**: Medir tiempos de carga y uso de memoria
