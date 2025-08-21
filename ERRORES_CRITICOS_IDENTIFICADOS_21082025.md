# 🚨 ERRORES CRÍTICOS IDENTIFICADOS - 21/08/2025

**Análisis completo de errores detectados en la terminal del sistema**

---

## 📋 ERRORES CRÍTICOS DE BASE DE DATOS

### **1. ERROR: Invalid object name 'sqlite_master'**
```
ERROR: ('42S02', "[42S02] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid object name 'sqlite_master'. (208)")
```

**Módulos Afectados:**
- Obras: `sql/obras/verificar_tabla_sqlite.sql`
- Inventario: `sql/inventario/verificar_tabla_existe.sql`

**Causa:** Consultas SQL diseñadas para SQLite siendo ejecutadas en SQL Server
**Solución:** Crear versiones específicas para SQL Server

### **2. ERROR: Incorrect syntax near 'IF'**
```
ERROR: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near the keyword 'IF'. (156)")
```

**Módulo Afectado:** Pedidos - `sql/pedidos/create_pedidos_table.sql`
**Causa:** Sintaxis SQLite en SQL Server
**Solución:** Reescribir queries con sintaxis T-SQL

### **3. ERROR: Invalid column name 'descuento'**
```
ERROR: ('42S22', "[42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'descuento'. (207)")
```

**Módulo Afectado:** Compras - estadísticas
**Causa:** Columna 'descuento' no existe en tabla de compras
**Solución:** Verificar estructura de tabla y ajustar queries

---

## 🎨 ERRORES DE ESTILO CSS

### **4. Unknown property 'transform' y 'box-shadow'**
```
Unknown property transform
Unknown property box-shadow
```

**Causa:** PyQt6 no soporta todas las propiedades CSS modernas
**Impacto:** Efectos visuales no se aplican
**Solución:** Usar propiedades CSS compatibles con PyQt6

---

## 🔗 ERRORES DE CONEXIÓN Y CONFIGURACIÓN

### **5. WARNING: QtWebEngine no disponible**
```
WARNING: QtWebEngine no disponible: No module named 'PyQt6.QtWebEngine'
```

**Impacto:** Funcionalidades web limitadas
**Solución:** Instalar PyQt6-WebEngine o implementar fallbacks

### **6. WARNING: Archivo de tema no encontrado**
```
WARNING: Archivo de tema no encontrado: resources\qss\theme_optimized_clean.qss
```

**Impacto:** Tema visual no se aplica correctamente
**Solución:** Crear archivo de tema faltante

### **7. ERROR: Conexión de BD no disponible**
```
WARNING: Conexión de BD no disponible para [módulo]
```

**Módulos Afectados:** Usuarios, Compras, Herrajes
**Causa:** Conexiones BD no se pasan correctamente a controladores

---

## 🏗️ ERRORES DE ESTRUCTURA Y LAYOUT

### **8. QLayout: Attempting to add QLayout**
```
QLayout: Attempting to add QLayout "" to [Widget] "", which already has a layout
```

**Módulos Afectados:** Compras, Auditoría
**Causa:** Intentar agregar layout a widget que ya tiene uno
**Solución:** Verificar layouts antes de asignar

### **9. QWindowsWindow::setGeometry: Unable to set geometry**
```
QWindowsWindow::setGeometry: Unable to set geometry [dimensiones]
```

**Causa:** Dimensiones de ventana exceden límites del monitor
**Solución:** Validar dimensiones antes de aplicar

---

## 🔧 ERRORES DE FUNCIONALIDAD ESPECÍFICOS

### **10. ERROR: Error crítico creando [módulo]**
**Módulos Afectados:**
- Obras: Error SQL sqlite_master
- Inventario: Error SQL sqlite_master  
- Pedidos: Error sintaxis SQL

### **11. ERROR: 'NoneType' object has no attribute 'cursor'**
```
ERROR: Error obteniendo estadísticas: 'NoneType' object has no attribute 'cursor'
```

**Módulo Afectado:** Vidrios
**Causa:** Conexión BD es None cuando se intenta usar

### **12. WARNING: Método cargar_[módulo] no encontrado**
```
WARNING: [Módulo] Método cargar_modulo no encontrado en controlador
```

**Módulos Afectados:** Vidrios, Logística, Compras, Mantenimiento, Auditoría
**Impacto:** Datos iniciales no se cargan correctamente

---

## 📊 RESUMEN DE ERRORES POR CATEGORÍA

| Categoría | Cantidad | Severidad | Estado |
|-----------|----------|-----------|--------|
| **SQL/Base de Datos** | 3 | CRÍTICO | 🔴 Requiere acción inmediata |
| **CSS/Estilos** | 100+ | MEDIO | 🟡 Funcionalidad no afectada |
| **Conexiones BD** | 5 | ALTO | 🟠 Afecta funcionalidad |
| **Layouts** | 3 | BAJO | 🟢 Visual solamente |
| **Dependencias** | 2 | MEDIO | 🟡 Funcionalidad limitada |
| **Métodos Faltantes** | 6 | ALTO | 🟠 Datos no se cargan |

---

## 🎯 PLAN DE CORRECCIÓN PRIORIZADO

### **PRIORIDAD 1 - CRÍTICO (Resolver Inmediatamente)**

1. **Corregir queries SQL incompatibles**
   - Crear versiones SQL Server de todos los queries SQLite
   - Verificar estructura de tablas en BD de destino
   - Implementar detección automática de tipo de BD

2. **Arreglar conexiones de BD en controladores**
   - Pasar conexiones BD correctamente a todos los controladores
   - Implementar validación de conexión antes de usar

3. **Completar métodos cargar_[módulo] faltantes**
   - Implementar métodos específicos de carga para cada módulo
   - Estandarizar interface de carga de datos

### **PRIORIDAD 2 - ALTO (Resolver en 24-48h)**

1. **Corregir errores de layout**
   - Verificar layouts existentes antes de asignar nuevos
   - Implementar limpieza de layouts

2. **Instalar dependencias faltantes**
   - PyQt6-WebEngine para funcionalidades web
   - Crear fallbacks para cuando no esté disponible

3. **Crear archivos de tema faltantes**
   - Generar theme_optimized_clean.qss
   - Implementar sistema de fallback de temas

### **PRIORIDAD 3 - MEDIO (Resolver en una semana)**

1. **Optimizar propiedades CSS**
   - Reemplazar propiedades no soportadas por PyQt6
   - Crear sistema de estilos compatible

2. **Validar geometrías de ventanas**
   - Implementar validación de dimensiones de pantalla
   - Ajustar tamaños automáticamente

---

## 🔧 SOLUCIONES ESPECÍFICAS

### **SQL Server Compatibility Layer**
```python
# Crear clase para traducir queries SQLite a SQL Server
class SQLDialectTranslator:
    def translate_sqlite_to_sqlserver(self, query):
        # Implementar traducción automática
        pass
```

### **BD Connection Validator**
```python
# Validar conexión antes de usar
def validate_db_connection(self):
    if not self.db_connection or not hasattr(self.db_connection, 'cursor'):
        raise ConnectionError("BD connection not available")
```

### **Layout Manager**
```python
# Limpiar layouts existentes
def setup_layout_safe(widget, new_layout):
    if widget.layout():
        widget.layout().deleteLater()
    widget.setLayout(new_layout)
```

---

## 📈 MÉTRICAS DE PROGRESO

### **Estado Actual:**
- **Errores Críticos:** 12 identificados
- **Módulos Afectados:** 8 de 12 (66%)
- **Funcionalidad Comprometida:** ~40%

### **Objetivo:**
- **Errores Críticos:** 0
- **Módulos Funcionales:** 12 de 12 (100%)
- **Funcionalidad Comprometida:** 0%

---

## 🎯 PRÓXIMOS PASOS

1. **Implementar SQLDialectTranslator** para queries compatibles
2. **Corregir conexiones BD** en todos los controladores
3. **Completar métodos de carga** faltantes
4. **Instalar dependencias** faltantes
5. **Validar y documentar** todas las correcciones

**Tiempo estimado de corrección completa:** 2-3 días de trabajo intensivo

---

**📊 Documento generado:** 21/08/2025 - 17:15  
**🎯 Status:** ERRORES IDENTIFICADOS Y CATALOGADOS  
**🚀 Ready for:** CORRECCIÓN SISTEMÁTICA INMEDIATA