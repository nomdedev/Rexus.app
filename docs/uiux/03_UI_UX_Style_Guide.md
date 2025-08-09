# Guía de Estilo UI/UX - Rexus.app

## 🎨 **FILOSOFÍA DE DISEÑO**

Rexus.app sigue principios de **diseño limpio, profesional y consistente** para garantizar una experiencia de usuario fluida y productiva.

### Principios Fundamentales:
1. **Consistencia**: Todos los módulos deben seguir patrones visuales idénticos
2. **Accesibilidad**: Interfaz clara, contrastes adecuados y navegación intuitiva  
3. **Eficiencia**: Reducir la carga cognitiva del usuario con layouts organizados
4. **Profesionalidad**: Estética empresarial moderna y confiable

---

## 🎯 **SISTEMA DE COMPONENTES ESTANDARIZADOS**

### Implementación con `StandardComponents`

Todos los módulos DEBEN usar la clase `StandardComponents` para garantizar consistencia:

```python
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager

class ModuloView(QWidget):
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título estandarizado - OBLIGATORIO
        StandardComponents.create_title("Nombre del Módulo", layout)
        
        # Panel de control estandarizado
        control_panel = StandardComponents.create_control_panel()
        
        # Botones estandarizados
        btn_primary = StandardComponents.create_primary_button("Acción Principal")
        btn_secondary = StandardComponents.create_secondary_button("Cancelar") 
        btn_danger = StandardComponents.create_danger_button("Eliminar")
        
        # Tabla estandarizada
        tabla = StandardComponents.create_standard_table()
        
        # Aplicar tema del módulo - OBLIGATORIO
        style_manager.apply_module_theme(self)
```

---

## 🎨 **PALETA DE COLORES**

### Colores Primarios:
- **Primary**: `#1e40af` - Azul principal para botones de acción
- **Secondary**: `#3b82f6` - Azul secundario para hover y estados activos  
- **Success**: `#059669` - Verde para confirmaciones y éxito
- **Warning**: `#d97706` - Naranja para advertencias
- **Danger**: `#dc2626` - Rojo para eliminaciones y errores

### Colores de Soporte:
- **Light**: `#f8fafc` - Fondo principal de la aplicación
- **Dark**: `#1e293b` - Texto principal
- **Border**: `#e2e8f0` - Bordes y separadores
- **Background**: `#ffffff` - Fondo de componentes
- **Muted**: `#64748b` - Texto secundario

---

## 📐 **TIPOGRAFÍA**

### Jerarquía de Fuentes:
```python
FONTS = {
    'title': ('Segoe UI', 16, QFont.Weight.Bold),      # Títulos de módulo
    'subtitle': ('Segoe UI', 14, QFont.Weight.Normal), # Subtítulos de sección
    'body': ('Segoe UI', 13, QFont.Weight.Normal),     # Texto general
    'caption': ('Segoe UI', 11, QFont.Weight.Normal)   # Texto explicativo
}
```

### Uso:
- **Títulos**: Solo para headers principales de módulos
- **Subtítulos**: Para secciones dentro de módulos (GroupBox titles)
- **Body**: Para toda la interfaz estándar (labels, buttons, inputs)
- **Caption**: Para texto de ayuda y tooltips

---

## 📏 **ESPACIADO Y LAYOUT**

### Espaciados Estándar:
```python
SPACING = {
    'small': 5,      # Entre elementos relacionados
    'medium': 10,    # Espaciado general de layouts
    'large': 20,     # Entre secciones diferentes  
    'xlarge': 30     # Márgenes principales
}
```

### Márgenes de Contenedor:
- **Módulos principales**: `setContentsMargins(10, 10, 10, 10)`
- **Paneles de control**: `setContentsMargins(15, 10, 15, 10)`  
- **Formularios**: `setContentsMargins(20, 15, 20, 15)`

---

## 🔘 **COMPONENTES UI**

### 1. **Botones**

#### Primarios (Acciones Principales):
```python
btn = StandardComponents.create_primary_button("Guardar")
# Uso: Guardar, Agregar, Confirmar, Procesar
```

#### Secundarios (Acciones Secundarias):
```python  
btn = StandardComponents.create_secondary_button("Cancelar")
# Uso: Cancelar, Editar, Ver Detalles, Configurar
```

#### Peligro (Acciones Destructivas):
```python
btn = StandardComponents.create_danger_button("Eliminar")  
# Uso: Eliminar, Deshacer, Restablecer
```

#### Éxito (Confirmaciones):
```python
btn = StandardComponents.create_success_button("Completar")
# Uso: Completar, Aprobar, Finalizar
```

### 2. **Tablas**

Todas las tablas DEBEN usar:
```python
tabla = StandardComponents.create_standard_table()
```

**Características estandarizadas**:
- Headers con fondo azul corporativo
- Filas alternadas para mejor legibilidad
- Selección completa de filas
- Scrollbars personalizadas
- Hover effects en headers

### 3. **Paneles de Control**

```python
panel = StandardComponents.create_control_panel()
```

**Uso consistente**:
- Fondo claro con borde suave
- Padding interno de 15px
- Esquinas redondeadas (8px)
- Sombra sutil para profundidad

### 4. **Títulos de Módulo**

```python
StandardComponents.create_title("Nombre del Módulo", layout)
```

**Características**:
- Gradiente azul corporativo
- Texto blanco en negrita (16px)
- Esquinas redondeadas (8px)  
- Padding interno generoso (20px horizontal, 15px vertical)

---

## 🎭 **GESTIÓN DE TEMAS**

### Usar StyleManager

```python
from rexus.ui.style_manager import style_manager

# En el constructor del módulo
style_manager.apply_module_theme(self)

# Cambiar tema global (opcional)
style_manager.apply_global_theme('professional')
```

### Temas Disponibles:
- **professional** (por defecto): Tema corporativo azul
- **light**: Tema claro y minimalista
- **minimal**: Tema ultra-limpio
- **optimized**: Tema optimizado para rendimiento

---

## ✅ **CHECKLIST DE IMPLEMENTACIÓN**

### Para Cada Módulo Nuevo:

- [ ] Importar `StandardComponents` y `style_manager`
- [ ] Usar `StandardComponents.create_title()` para el header
- [ ] Aplicar `style_manager.apply_module_theme(self)` al final de `init_ui()`
- [ ] Usar botones estandarizados según su función
- [ ] Implementar tablas con `create_standard_table()`
- [ ] Aplicar márgenes estándar a layouts: `(10, 10, 10, 10)`
- [ ] Usar `create_control_panel()` para paneles de herramientas
- [ ] Seguir jerarquía de fuentes para textos
- [ ] Validar consistencia visual con otros módulos

### Para Módulos Existentes (Migración):

- [ ] Reemplazar `setStyleSheet()` inline con componentes estándar
- [ ] Migrar método `configurar_estilos()` a `style_manager.apply_module_theme()`
- [ ] Sustituir creación manual de botones con `StandardComponents`
- [ ] Actualizar tablas a `create_standard_table()`
- [ ] Agregar título estandarizado si falta
- [ ] Remover estilos CSS personalizados conflictivos

---

## 🚫 **ANTI-PATRONES - EVITAR**

### ❌ **NO Hacer:**

1. **Estilos inline dispersos**:
```python
# INCORRECTO
widget.setStyleSheet("background: #ffffff; border: 1px solid #cccccc;")
```

2. **Colores hardcodeados**:
```python  
# INCORRECTO
button.setStyleSheet("background: blue; color: white;")
```

3. **Inconsistencia en botones**:
```python
# INCORRECTO - cada botón con estilo diferente
btn1.setStyleSheet("background: red;")
btn2.setStyleSheet("background: #ff0000;") 
btn3.setStyleSheet("background: crimson;")
```

4. **Títulos inconsistentes**:
```python
# INCORRECTO - cada módulo con título diferente
title = QLabel("MODULO INVENTARIO")  # All caps
title2 = QLabel("obras")  # lowercase  
title3 = QLabel("Administracion-")  # Con guión
```

### ✅ **Hacer en Su Lugar:**

1. **Componentes estandarizados**:
```python
# CORRECTO
panel = StandardComponents.create_control_panel()
```

2. **Colores desde constantes**:
```python
# CORRECTO  
colors = StandardComponents.COLORS
widget.setStyleSheet(f"background: {colors['primary']};")
```

3. **Botones por función**:
```python
# CORRECTO
btn_save = StandardComponents.create_primary_button("Guardar")
btn_cancel = StandardComponents.create_secondary_button("Cancelar")
btn_delete = StandardComponents.create_danger_button("Eliminar")
```

4. **Títulos consistentes**:
```python
# CORRECTO
StandardComponents.create_title("Inventario", layout)
StandardComponents.create_title("Administración", layout)  
StandardComponents.create_title("Obras", layout)
```

---

## 🔧 **HERRAMIENTAS DE DESARROLLO**

### Validar Consistencia:
```bash
# Buscar estilos inline problemáticos
grep -r "setStyleSheet" rexus/modules/ 

# Verificar uso de componentes estándar
grep -r "StandardComponents" rexus/modules/

# Comprobar aplicación de temas
grep -r "style_manager.apply_module_theme" rexus/modules/
```

### Testing Visual:
1. Navegar por todos los módulos
2. Verificar que títulos tengan el mismo estilo
3. Comprobar que botones mantengan consistencia
4. Validar que tablas usen el mismo theme
5. Confirmar que colores coincidan con la paleta

---

## 📊 **MÉTRICAS DE CALIDAD UI/UX**

### Objetivos de Consistencia:
- ✅ **100%** de módulos con títulos estandarizados
- ✅ **100%** de botones usando `StandardComponents`
- ✅ **100%** de tablas con estilo consistente  
- ✅ **0** instancias de `setStyleSheet()` inline problemático
- ✅ **1** tema global aplicado consistentemente

### Estado Actual Post-Auditoría 2025:
- **Componentes Estandarizados**: ✅ Implementados
- **Gestor de Estilos**: ✅ Implementado
- **Migración Administración**: ✅ Completada
- **Migración Configuración**: ✅ Completada  
- **Documentación**: ✅ Completada

---

**Fecha de Creación**: Agosto 2025  
**Última Actualización**: Agosto 2025  
**Responsable**: Equipo UI/UX Rexus.app  
**Estado**: ✅ **ACTIVO** - Implementación en progreso