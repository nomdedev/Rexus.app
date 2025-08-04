# Guidelines MVC para Rexus.app

## Patrón Model-View-Controller (MVC)

### MODELO (Model)
- **Responsabilidad**: Lógica de negocio y acceso a datos
- **Contiene**: 
  - Conexiones a base de datos
  - Validaciones de datos
  - Cálculos y operaciones de negocio
  - Métodos CRUD (Create, Read, Update, Delete)
- **NO debe contener**: 
  - Imports de PyQt6 o interfaces gráficas
  - Lógica de presentación
  - Manejo directo de eventos UI

### VISTA (View)  
- **Responsabilidad**: Presentación e interfaz de usuario
- **Contiene**:
  - Widgets de PyQt6
  - Layouts y estilos
  - Manejo de eventos UI básicos
  - Formateo de datos para presentación
- **NO debe contener**:
  - Consultas SQL directas
  - Lógica de negocio compleja
  - Acceso directo a base de datos
  - Cálculos complejos

### CONTROLADOR (Controller)
- **Responsabilidad**: Coordinación entre modelo y vista
- **Contiene**:
  - Flujo de la aplicación
  - Validaciones de entrada
  - Coordinación de operaciones
  - Manejo de estados
- **NO debe contener**:
  - Lógica de negocio pesada
  - Manipulación directa de widgets
  - Consultas a base de datos

## Buenas Prácticas

1. **Vista usa Modelo**: `self.model.obtener_datos()` ✅
2. **No SQL en Vista**: `cursor.execute()` en view.py ❌
3. **No UI en Modelo**: `QMessageBox` en model.py ❌
4. **Controlador Liviano**: Métodos cortos y específicos ✅
5. **Documentación**: Docstrings en todos los métodos ✅

## Ejemplo Correcto

```python
# En view.py
class InventarioView(QWidget):
    def __init__(self, db_connection=None):
        super().__init__()
        self.model = InventarioModel(db_connection)  # ✅ Usa modelo
        self.init_ui()
    
    def cargar_productos(self):
        productos = self.model.obtener_productos()  # ✅ Delega al modelo
        self.actualizar_tabla(productos)

# En model.py  
class InventarioModel:
    def obtener_productos(self):
        cursor = self.db_connection.cursor()  # ✅ SQL en modelo
        cursor.execute("SELECT * FROM productos")
        return cursor.fetchall()
```

## Violaciones Comunes a Evitar

❌ Vista con SQL directo:
```python
# En view.py - MAL
cursor = self.db_connection.cursor()
cursor.execute("SELECT * FROM productos")
```

❌ Modelo con UI:
```python
# En model.py - MAL  
from PyQt6.QtWidgets import QMessageBox
QMessageBox.warning(None, "Error", "Mensaje")
```

❌ Controlador pesado:
```python
# En controller.py - MAL
def metodo_muy_largo_con_muchas_responsabilidades(self):
    # 100+ líneas de código
    # Lógica de negocio + UI + validaciones + cálculos
```
