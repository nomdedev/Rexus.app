# Guía de Integración del Sistema de Feedback Visual

## Introducción

El sistema de feedback visual integrado proporciona mensajes consistentes en toda la aplicación, integrados automáticamente con el sistema de temas.

## Componentes del Sistema

### 1. FeedbackManager (`rexus/utils/feedback_manager.py`)
- Gestor centralizado de mensajes
- Integración automática con temas
- Cache de estilos para performance

### 2. FeedbackMixin (`rexus/ui/feedback_mixin.py`)
- Mixin para agregar feedback a cualquier widget
- Métodos de conveniencia
- Labels de estado inline

### 3. Integración con Temas
- Colores automáticos según el tema activo
- Actualización dinámica al cambiar tema
- Soporte para temas Light, Dark, Blue, High Contrast

## Uso Básico

### Opción 1: Usar el Mixin (Recomendado)

```python
from rexus.ui.feedback_mixin import FeedbackMixin
from rexus.utils.theme_manager import ThemeManager

class MiVista(QWidget, FeedbackMixin):
    def __init__(self, theme_manager=None):
        super().__init__()
        self.init_feedback(theme_manager)  # ¡Importante!
        
    def alguna_operacion(self):
        # Mostrar mensaje de carga
        self.mostrar_cargando("Procesando datos...")
        
        # Realizar operación...
        
        # Mostrar resultado
        self.mostrar_exito("Operación completada")
        
    def otra_operacion(self):
        # Mensaje con diálogo
        self.mostrar_mensaje("Información", "Datos guardados", "success")
        
        # Status inline temporal
        self.mostrar_status("Cambios aplicados", "success", 3000)
```

### Opción 2: Usar FeedbackWidget

```python
from rexus.ui.feedback_mixin import FeedbackWidget

class MiWidget(FeedbackWidget):
    def __init__(self, theme_manager=None):
        super().__init__(theme_manager)
        # El feedback ya está inicializado automáticamente
        
    def procesar(self):
        self.mostrar_cargando("Procesando...")
        # ... lógica ...
        self.mostrar_exito("Listo!")
```

### Opción 3: Agregar a Widget Existente

```python
from rexus.ui.feedback_mixin import add_feedback_to_widget

# Widget existente
mi_widget = QWidget()

# Agregar capacidades de feedback
add_feedback_to_widget(mi_widget, theme_manager)

# Ahora se puede usar
mi_widget.mostrar_mensaje("Info", "Widget mejorado", "info")
```

## Métodos Disponibles

### Mensajes con Diálogo
- `mostrar_mensaje(titulo, mensaje, tipo)` - Diálogo completo
- `mostrar_confirmacion(titulo, mensaje)` - Diálogo Sí/No

### Status Inline (Recomendado para UX)
- `mostrar_status(mensaje, tipo, duration)` - Status temporal
- `mostrar_cargando(mensaje)` - Indicador de carga
- `mostrar_exito(mensaje)` - Mensaje de éxito
- `mostrar_error(mensaje)` - Mensaje de error
- `mostrar_advertencia(mensaje)` - Mensaje de advertencia
- `mostrar_info(mensaje)` - Mensaje informativo

### Gestión de Status Labels
- `crear_status_label(nombre)` - Crear label de estado
- `ocultar_status(nombre)` - Ocultar status específico
- `ocultar_cargando(nombre)` - Ocultar indicador de carga

## Tipos de Mensaje

| Tipo | Uso | Color Base | Icono |
|------|-----|------------|-------|
| `info` | Información general | Azul del tema | ℹ️ |
| `success` | Operación exitosa | Verde del tema | ✅ |
| `warning` | Advertencias | Amarillo del tema | ⚠️ |
| `error` | Errores | Rojo del tema | ❌ |

## Múltiples Status Labels

```python
class MiVista(QWidget, FeedbackMixin):
    def __init__(self):
        super().__init__()
        self.init_feedback()
        
        # Crear múltiples status labels
        self.status_general = self.crear_status_label("general")
        self.status_red = self.crear_status_label("red")
        
    def operacion_compleja(self):
        # Diferentes status para diferentes áreas
        self.mostrar_status("Conectando...", "info", 0, "red")
        self.mostrar_status("Preparando...", "info", 0, "general")
        
        # ... lógica ...
        
        self.mostrar_status("Conectado", "success", 3000, "red")
        self.mostrar_status("Listo", "success", 3000, "general")
```

## Integración con Temas

El sistema se integra automáticamente con el ThemeManager:

```python
# Al crear la vista, pasar el theme_manager
theme_manager = get_theme_manager()
vista = MiVista(theme_manager)

# Los colores se actualizan automáticamente al cambiar tema
theme_manager.set_theme("dark")  # Los mensajes usan colores dark
theme_manager.set_theme("blue")  # Los mensajes usan colores blue
```

## Migración de Código Existente

### Antes:
```python
def guardar_datos(self):
    try:
        # ... lógica ...
        QMessageBox.information(self, "Éxito", "Datos guardados")
    except Exception as e:
        QMessageBox.critical(self, "Error", str(e))
```

### Después:
```python
def guardar_datos(self):
    self.mostrar_cargando("Guardando datos...")
    try:
        # ... lógica ...
        self.mostrar_exito("Datos guardados correctamente")
    except Exception as e:
        self.mostrar_error(f"Error guardando: {str(e)}")
```

## Mejores Prácticas

### 1. Feedback Inmediato
```python
# ✅ Bueno - Feedback inmediato
def buscar(self):
    self.mostrar_cargando("Buscando...")
    realizar_busqueda()
    self.mostrar_exito("Búsqueda completada")

# ❌ Malo - Sin feedback
def buscar(self):
    realizar_busqueda()  # Usuario no sabe qué pasa
```

### 2. Mensajes Informativos
```python
# ✅ Bueno - Mensaje específico
self.mostrar_exito("5 registros encontrados y actualizados")

# ❌ Malo - Mensaje genérico
self.mostrar_exito("Éxito")
```

### 3. Duración Apropiada
```python
# ✅ Bueno - Duraciones apropiadas
self.mostrar_exito("Guardado", 2000)      # Éxito: corto
self.mostrar_error("Error crítico", 8000) # Error: más tiempo
self.mostrar_info("Procesando...", 0)     # Info: hasta completar

# ❌ Malo - Todas la misma duración
self.mostrar_error("Error crítico", 1000) # Muy poco tiempo
```

### 4. Status vs Diálogos
```python
# ✅ Bueno - Status para acciones frecuentes
def auto_guardar(self):
    self.mostrar_status("Guardado automático", "success", 2000)

# ✅ Bueno - Diálogo para acciones importantes
def eliminar_definitivo(self):
    if self.mostrar_confirmacion("Confirmar", "¿Eliminar permanentemente?"):
        # ... eliminar ...
        self.mostrar_mensaje("Éxito", "Registro eliminado", "success")
```

## Ejemplo Completo

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from rexus.ui.feedback_mixin import FeedbackMixin
from rexus.utils.theme_manager import get_theme_manager

class EjemploCompleto(QWidget, FeedbackMixin):
    def __init__(self):
        super().__init__()
        
        # Inicializar feedback con theme manager
        theme_manager = get_theme_manager()
        self.init_feedback(theme_manager)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Status label principal
        self.status_main = self.crear_status_label("main")
        layout.addWidget(self.status_main)
        
        # Botones de ejemplo
        btn_info = QPushButton("Mostrar Info")
        btn_info.clicked.connect(lambda: self.mostrar_info("Información del sistema"))
        layout.addWidget(btn_info)
        
        btn_success = QPushButton("Simular Éxito")
        btn_success.clicked.connect(self.simular_exito)
        layout.addWidget(btn_success)
        
        btn_error = QPushButton("Simular Error")
        btn_error.clicked.connect(lambda: self.mostrar_error("Error de ejemplo"))
        layout.addWidget(btn_error)
        
        btn_loading = QPushButton("Simular Carga")
        btn_loading.clicked.connect(self.simular_carga)
        layout.addWidget(btn_loading)
    
    def simular_exito(self):
        self.mostrar_exito("Operación completada exitosamente")
    
    def simular_carga(self):
        self.mostrar_cargando("Procesando datos...")
        # Simular trabajo asíncrono
        QTimer.singleShot(3000, lambda: self.mostrar_exito("Proceso completado"))
```

## Solución de Problemas

### Error: "Feedback no inicializado"
```python
# Asegúrate de llamar init_feedback en __init__
def __init__(self):
    super().__init__()
    self.init_feedback()  # ¡Necesario!
```

### Los colores no cambian con el tema
```python
# Asegúrate de pasar el theme_manager
theme_manager = get_theme_manager()
self.init_feedback(theme_manager)
```

### Status label no aparece
```python
# Asegúrate de agregar el label al layout
status_label = self.crear_status_label()
layout.addWidget(status_label)  # ¡Importante!
```