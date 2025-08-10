# Guía de Estándares UI/UX - Rexus.app

## Versión 2.0.0 - Generada automáticamente

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Sistema de Colores](#sistema-de-colores)
3. [Tipografía](#tipografía)
4. [Espaciado y Layout](#espaciado-y-layout)
5. [Componentes UI](#componentes-ui)
6. [Accesibilidad](#accesibilidad)
7. [Patrones de Interacción](#patrones-de-interacción)
8. [Implementación](#implementación)

---

## 🎨 Introducción

Esta guía define los estándares de diseño para la aplicación Rexus.app, asegurando consistencia visual, accesibilidad y una experiencia de usuario óptima en todos los módulos.

### Objetivos
- **Consistencia**: Interfaces uniformes en todos los módulos
- **Accesibilidad**: Cumplimiento WCAG 2.1 AA
- **Usabilidad**: Experiencia intuitiva y eficiente
- **Mantenibilidad**: Código reutilizable y escalable

---

## 🎨 Sistema de Colores

### Paleta Principal

| Color | Código Hex | Uso Principal | RGB |
|-------|------------|---------------|-----|
| Verde Primario | `#2E7D32` | Botones principales, headers | (46, 125, 50) |
| Verde Secundario | `#388E3C` | Hover states, destacados | (56, 142, 60) |
| Verde Claro | `#4CAF50` | Elementos de éxito, confirmación | (76, 175, 80) |
| Azul Información | `#1976D2` | Enlaces, información | (25, 118, 210) |

### Paleta de Estados

| Estado | Color | Código Hex | Uso |
|--------|-------|------------|-----|
| Éxito | Verde | `#4CAF50` | Confirmaciones, operaciones exitosas |
| Advertencia | Naranja | `#FF9800` | Alertas, precauciones |
| Error | Rojo | `#F44336` | Errores, validaciones fallidas |
| Información | Azul | `#2196F3` | Mensajes informativos |

### Paleta Neutral

| Elemento | Color | Código Hex | Uso |
|----------|-------|------------|-----|
| Texto Principal | Negro | `#212121` | Texto principal |
| Texto Secundario | Gris Oscuro | `#757575` | Texto secundario |
| Bordes | Gris Claro | `#E0E0E0` | Bordes de elementos |
| Fondo | Blanco | `#FFFFFF` | Fondo principal |
| Fondo Alternativo | Gris Muy Claro | `#F5F5F5` | Fondos alternativos |

### Implementación en Código

```python
from utils.rexus_styles import RexusStyles

# Uso de colores estándar
button.setStyleSheet(RexusStyles.estilo_boton_primario())
color_primario = RexusStyles.color_primario()
```

---

## 📝 Tipografía

### Fuentes Principales

| Tipo | Fuente | Tamaño | Peso | Uso |
|------|--------|--------|------|-----|
| Títulos | Arial | 16px | Bold | Títulos principales |
| Subtítulos | Arial | 14px | Bold | Subtítulos, headers de sección |
| Texto Normal | Arial | 11px | Regular | Texto de interfaz |
| Texto Pequeño | Arial | 9px | Regular | Etiquetas, metadatos |
| Monospace | Courier New | 11px | Regular | Código, datos técnicos |

### Jerarquía Visual

```
TÍTULO PRINCIPAL (16px, Bold)
├── Subtítulo de Sección (14px, Bold)
│   ├── Texto Normal (11px, Regular)
│   ├── Texto de Ayuda (9px, Regular)
│   └── Código/Datos (11px, Courier New)
```

### Implementación

```python
# Usando estilos centralizados
titulo_font = RexusStyles.fuente_titulo()
normal_font = RexusStyles.fuente_normal()
mono_font = RexusStyles.fuente_monospace()

# Aplicación directa
label.setFont(titulo_font)
```

---

## 📏 Espaciado y Layout

### Sistema de Espaciado

| Nivel | Valor | Uso |
|-------|-------|-----|
| Pequeño | 5px | Separación mínima entre elementos |
| Normal | 10px | Espaciado estándar |
| Grande | 15px | Separación entre secciones |
| Extra | 20px | Márgenes de contenedores |

### Márgenes Estándar

```python
# Contenedores principales
contenedor.setContentsMargins(20, 20, 20, 20)

# Elementos internos
elemento.setContentsMargins(10, 10, 10, 10)

# Espaciado entre elementos
layout.setSpacing(10)
```

### Grid System

- **Contenedor principal**: Márgenes de 20px
- **Columnas**: Espaciado de 15px entre columnas
- **Filas**: Espaciado de 10px entre filas
- **Grupos de elementos**: Separación de 15px

---

## 🔧 Componentes UI

### Botones

#### Botón Primario
```python
# Estilo automático
boton.setStyleSheet(RexusStyles.estilo_boton_primario())

# Propiedades requeridas
boton.setAccessibleName("Nombre descriptivo del botón")
boton.setToolTip("Descripción de la acción que realiza")
```

**Especificaciones:**
- Color de fondo: Verde primario (`#2E7D32`)
- Texto: Blanco
- Padding: 8px vertical, 16px horizontal
- Border-radius: 5px
- Fuente: Arial 11px Bold

#### Botón Secundario
- Color de fondo: Transparente
- Borde: 2px sólido Verde primario
- Texto: Verde primario

### Campos de Entrada

#### QLineEdit Estándar
```python
campo.setStyleSheet(RexusStyles.estilo_input())
campo.setAccessibleName("Nombre del campo")
campo.setPlaceholderText("Texto de ayuda")
```

**Especificaciones:**
- Borde: 2px gris claro (`#DDDDDD`)
- Padding: 5px
- Border-radius: 4px
- Focus: Borde verde primario

### Tablas

#### QTableWidget Estándar
```python
tabla.setStyleSheet(RexusStyles.estilo_tabla())
tabla.setAlternatingRowColors(True)
```

**Especificaciones:**
- Headers: Fondo verde primario, texto blanco
- Filas alternas: Fondo `#F9F9F9`
- Selección: Fondo verde claro

---

## ♿ Accesibilidad

### Cumplimiento WCAG 2.1 AA

#### Contraste de Colores
- **Texto normal**: Mínimo 4.5:1
- **Texto grande**: Mínimo 3:1
- **Elementos no textuales**: Mínimo 3:1

#### Navegación por Teclado
```python
# Todos los elementos interactivos deben ser accesibles
elemento.setFocusPolicy(Qt.FocusPolicy.TabFocus)

# Orden de tabulación lógico
self.setTabOrder(campo1, campo2)
self.setTabOrder(campo2, boton1)
```

#### Nombres y Descripciones Accesibles
```python
# OBLIGATORIO para todos los elementos interactivos
boton.setAccessibleName("Guardar registro")
boton.setAccessibleDescription("Guarda los cambios realizados en el formulario")

# Para campos de entrada
campo.setAccessibleName("Nombre del cliente")
label.setBuddy(campo)  # Asociar etiqueta con campo
```

#### Tooltips Descriptivos
```python
# OBLIGATORIO para todos los botones
boton.setToolTip("Guarda los cambios - Ctrl+S")

# Para elementos complejos
tabla.setToolTip("Tabla de registros - Use flechas para navegar")
```

### Lista de Verificación de Accesibilidad

- [ ] Todos los botones tienen `setAccessibleName()`
- [ ] Todos los campos tienen `setAccessibleName()`
- [ ] Todos los elementos interactivos tienen `setToolTip()`
- [ ] Imágenes informativas tienen `setAccessibleDescription()`
- [ ] Orden de tabulación es lógico
- [ ] Contraste de colores cumple WCAG AA
- [ ] Funcionalidad disponible por teclado

---

## 🖱️ Patrones de Interacción

### Estados de Elementos

#### Botones
1. **Normal**: Estado por defecto
2. **Hover**: Cambio visual al pasar el mouse
3. **Pressed**: Feedback visual al hacer clic
4. **Disabled**: Estado no interactivo
5. **Focus**: Indicador visual de foco de teclado

#### Campos de Entrada
1. **Empty**: Estado vacío inicial
2. **Focused**: Campo activo para entrada
3. **Filled**: Campo con contenido
4. **Error**: Estado de validación fallida
5. **Disabled**: Campo no editable

### Feedback Visual

#### Mensajes de Estado
```python
# Éxito
QMessageBox.information(self, "Éxito", "Operación completada exitosamente")

# Error
QMessageBox.critical(self, "Error", "No se pudo completar la operación")

# Advertencia
QMessageBox.warning(self, "Advertencia", "Verifique los datos ingresados")
```

#### Indicadores de Progreso
- **Operaciones cortas** (< 3s): Sin indicador
- **Operaciones medianas** (3-10s): Barra de progreso
- **Operaciones largas** (> 10s): Progreso con cancelación

---

## 💻 Implementación

### Estructura de Archivos

```
utils/
├── rexus_styles.py          # Estilos centralizados
├── ui_components.py         # Componentes reutilizables
└── accessibility_helpers.py # Helpers de accesibilidad
```

### Importación en Módulos

```python
# En cada archivo view.py
from utils.rexus_styles import RexusStyles
from utils.ui_components import RexusButton, RexusInput
from utils.accessibility_helpers import setup_accessibility

class ModuloView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        setup_accessibility(self)  # Configuración automática
```

### Ejemplo de Implementación Completa

```python
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from utils.rexus_styles import RexusStyles

class EjemploView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(RexusStyles.ESPACIADO_NORMAL)
        layout.setContentsMargins(
            RexusStyles.MARGEN_EXTRA,
            RexusStyles.MARGEN_EXTRA,
            RexusStyles.MARGEN_EXTRA,
            RexusStyles.MARGEN_EXTRA
        )
        
        # Título
        titulo = QLabel("Título de la Sección")
        titulo.setFont(RexusStyles.fuente_titulo())
        layout.addWidget(titulo)
        
        # Campo de entrada
        campo = QLineEdit()
        campo.setStyleSheet(RexusStyles.estilo_input())
        campo.setAccessibleName("Campo de ejemplo")
        campo.setPlaceholderText("Ingrese texto aquí")
        layout.addWidget(campo)
        
        # Botón principal
        boton = QPushButton("Acción Principal")
        boton.setStyleSheet(RexusStyles.estilo_boton_primario())
        boton.setAccessibleName("Ejecutar acción principal")
        boton.setToolTip("Ejecuta la acción principal - Enter")
        layout.addWidget(boton)
        
        # Configurar orden de tabulación
        self.setTabOrder(campo, boton)
        
        self.setLayout(layout)
```

---

## 📊 Métricas de Calidad

### Objetivos de Rendimiento
- **Tiempo de carga UI**: < 1 segundo
- **Tiempo de respuesta**: < 200ms para acciones locales
- **Memoria UI**: < 50MB por módulo

### Métricas de Accesibilidad
- **Cobertura de nombres accesibles**: 100%
- **Cobertura de tooltips**: 100%
- **Cumplimiento WCAG AA**: 100%

### Métricas de Consistencia
- **Uso de colores estándar**: > 95%
- **Uso de fuentes estándar**: > 98%
- **Uso de espaciado estándar**: > 90%

---

## 🔄 Proceso de Revisión

### Checklist Pre-Commit
- [ ] Estilos aplicados desde `RexusStyles`
- [ ] Accesibilidad implementada completamente
- [ ] Colores dentro de la paleta estándar
- [ ] Fuentes y espaciado estandarizados
- [ ] Pruebas de navegación por teclado
- [ ] Validación de contraste de colores

### Herramientas de Auditoría
```bash
# Auditoría completa
python scripts/ui_ux/audit_simple.py

# Aplicar correcciones automáticas
python scripts/ui_ux/apply_fixes.py

# Validación de accesibilidad
python scripts/ui_ux/audit_accessibility.py
```

---

## 📚 Recursos Adicionales

### Referencias
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Material Design Guidelines](https://material.io/design)

### Contacto
Para dudas sobre estos estándares, contactar al equipo de desarrollo UI/UX.

---

**Última actualización**: 2025-01-05  
**Versión**: 2.0.0  
**Estado**: Implementado automáticamente
