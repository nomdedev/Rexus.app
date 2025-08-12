# 📄 Plantilla de Implementación de Exportación - Rexus.app

## 🎯 Objetivo
Esta plantilla proporciona instrucciones paso a paso para implementar funcionalidad de exportación estándar en cualquier módulo de Rexus.app.

---

## 📋 Pasos de Implementación

### 1. Importar el Sistema de Exportación

```python
# En el archivo view.py del módulo
from rexus.utils.export_manager import ModuleExportMixin, export_manager
```

### 2. Integrar el Mixin en la Vista

```python
# Cambiar la declaración de clase
class MiModuloView(QWidget, ModuleExportMixin):
    def __init__(self):
        QWidget.__init__(self)
        ModuleExportMixin.__init__(self)
        self.init_ui()
```

### 3. Agregar Botón de Exportación

```python
def init_ui(self):
    # ... código existente ...
    
    # En el panel de control, agregar botón de exportación
    self.add_export_button(control_layout, "📄 Exportar Datos")
    
    # O crear botón manualmente:
    # self.btn_exportar = RexusButton("📄 Exportar", "secondary")
    # self.btn_exportar.clicked.connect(self.show_export_dialog)
    # control_layout.addWidget(self.btn_exportar)
```

### 4. Personalizar Métodos de Exportación (Opcional)

Si necesitas lógica personalizada, sobrescribe estos métodos:

```python
def export_table_data(self, export_format: str = 'excel'):
    """Exportación personalizada para este módulo."""
    # Obtener datos específicos del módulo
    data = self._get_module_specific_data()
    headers = ["ID", "Nombre", "Descripción", "Estado", "Fecha"]
    
    return self.export_manager.export_data(
        data=data,
        headers=headers,
        module_name="mi_modulo",
        export_format=export_format,
        parent_widget=self
    )

def _get_module_specific_data(self) -> List[Dict[str, Any]]:
    """Obtiene datos específicos del módulo."""
    # Implementar lógica específica aquí
    if self.controller:
        return self.controller.get_export_data()
    else:
        return self._extract_table_data()  # Método base
```

---

## 🔧 Implementación en el Controlador (Opcional)

Para mayor flexibilidad, implementa el método en el controlador:

```python
# En controller.py
def get_export_data(self) -> List[Dict[str, Any]]:
    """Obtiene datos optimizados para exportación."""
    try:
        # Usar el model para obtener datos
        return self.model.get_all_for_export()
    except Exception as e:
        logging.error(f"Error obteniendo datos para exportar: {e}")
        return []
```

## 🔧 Implementación en el Modelo (Opcional)

```python
# En model.py
def get_all_for_export(self) -> List[Dict[str, Any]]:
    """Obtiene todos los registros formateados para exportación."""
    try:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, estado, fecha_creacion
            FROM mi_tabla 
            ORDER BY id
        """)
        
        columns = [desc[0] for desc in cursor.description]
        data = []
        
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            data.append(record)
        
        return data
        
    except Exception as e:
        logging.error(f"Error en consulta de exportación: {e}")
        return []
```

---

## 📝 Ejemplo Completo

```python
"""
Vista de Ejemplo con Exportación Integrada
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from rexus.ui.components import RexusButton, RexusTable
from rexus.utils.export_manager import ModuleExportMixin


class EjemploView(QWidget, ModuleExportMixin):
    """Vista de ejemplo con exportación."""
    
    def __init__(self):
        QWidget.__init__(self)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Panel de control
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Botones estándar
        self.btn_nuevo = RexusButton("Nuevo", "primary")
        control_layout.addWidget(self.btn_nuevo)
        
        # BOTÓN DE EXPORTACIÓN - AGREGADO AUTOMÁTICAMENTE
        self.add_export_button(control_layout)
        
        layout.addWidget(control_panel)
        
        # Tabla principal
        self.tabla_principal = RexusTable()
        self.tabla_principal.setColumnCount(4)
        self.tabla_principal.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Estado"
        ])
        layout.addWidget(self.tabla_principal)
    
    # Método personalizado opcional
    def export_table_data(self, export_format: str = 'excel'):
        """Exportación personalizada para este módulo."""
        if self.controller:
            data = self.controller.get_export_data()
        else:
            data = self._extract_table_data()
        
        headers = ["ID", "Nombre", "Descripción", "Estado"]
        
        return self.export_manager.export_data(
            data=data,
            headers=headers,
            module_name="ejemplo",
            export_format=export_format,
            parent_widget=self
        )
```

---

## ✅ Checklist de Implementación

- [ ] Importar `ModuleExportMixin` y `export_manager`
- [ ] Integrar mixin en la clase de vista
- [ ] Agregar botón de exportación al panel de control
- [ ] Verificar que la tabla principal tenga el nombre `tabla_principal`
- [ ] (Opcional) Implementar métodos personalizados en controlador/modelo
- [ ] (Opcional) Personalizar método `export_table_data()` si es necesario
- [ ] Probar exportación en Excel y CSV
- [ ] Documentar funcionalidades específicas del módulo

---

## 🎯 Resultado Esperado

Después de implementar esta plantilla:

1. ✅ **Botón "📄 Exportar"** visible en el panel de control
2. ✅ **Diálogo de selección** con opciones Excel, CSV, PDF
3. ✅ **Exportación funcional** a Excel y CSV
4. ✅ **Manejo de errores** integrado
5. ✅ **Mensajes informativos** para el usuario
6. ✅ **Ubicación estándar** en Documents/Rexus_Exports/

---

## 📚 Módulos que Requieren Esta Implementación

1. **USUARIOS** - Exportar lista de usuarios
2. **CONFIGURACIÓN** - Exportar configuraciones del sistema
3. **AUDITORÍA** - Exportar logs de auditoría
4. **LOGÍSTICA** - Exportar datos de transportes
5. **VIDRIOS** - Completar exportación (parcial)
6. **HERRAJES** - Completar exportación (parcial)
7. **OBRAS** - Completar exportación (parcial)
8. **ADMINISTRACIÓN** - Exportar datos administrativos
9. **MANTENIMIENTO** - Exportar registros de mantenimiento

**Tiempo estimado por módulo**: 15-30 minutos
**Tiempo total estimado**: 2-4 horas para todos los módulos