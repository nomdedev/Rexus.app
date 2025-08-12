#!/usr/bin/env python3
"""
Script de Refactorización MVC para Rexus.app
Corrige violaciones del patrón Model-View-Controller detectadas
"""

import re
from pathlib import Path


def fix_mvc_violations():
    """Corrige las violaciones MVC detectadas"""
    print("REFACTORIZACION MVC - REPARANDO VIOLACIONES CRITICAS")
    print("=" * 60)

    project_root = Path(__file__).parent.parent.parent

    # Reparar violación crítica: inventario/view.py acceso directo a BD
    fix_inventario_view_db_access(project_root)

    print("\nREFACTORIZACION COMPLETADA")
    print("Patrones MVC mejorados en Rexus.app")


def fix_inventario_view_db_access(project_root):
    """Corrige acceso directo a BD en inventario/view.py"""
    print("\n1. CORRIGIENDO: inventario/view.py - Acceso directo a BD")

    view_file = project_root / "rexus" / "modules" / "inventario" / "view.py"
    model_file = project_root / "rexus" / "modules" / "inventario" / "model.py"

    if not view_file.exists():
        print(f"   ERROR: {view_file} no encontrado")
        return

    if not model_file.exists():
        print(f"   ERROR: {model_file} no encontrado")
        return

    # Leer archivo view actual
    with open(view_file, "r", encoding="utf-8") as f:
        view_content = f.read()

    # Crear backup
    backup_file = str(view_file) + ".backup_mvc"
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(view_content)

    print(f"   Backup creado: {backup_file}")

    # PASO 1: Agregar import del modelo
    if "from .model import InventarioModel" not in view_content:
        # Buscar donde agregar el import
        lines = view_content.split("\n")
        import_added = False

        for i, line in enumerate(lines):
            if line.startswith("from PyQt6") and not import_added:
                # Agregar import del modelo después de los imports de PyQt6
                lines.insert(i + 1, "from .model import InventarioModel")
                import_added = True
                break

        if import_added:
            view_content = "\n".join(lines)
            print("   + Import de InventarioModel agregado")

    # PASO 2: Modificar constructor para usar modelo en lugar de db_connection directa
    old_init_pattern = r'def __init__\(self, db_connection=None, usuario_actual="SISTEMA"\):\s*super\(\).__init__\(\)\s*self\.db_connection = db_connection'

    new_init = """def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        super().__init__()
        # Usar modelo en lugar de acceso directo a BD
        self.model = InventarioModel(db_connection, usuario_actual)
        self.usuario_actual = usuario_actual"""

    if re.search(old_init_pattern, view_content, re.DOTALL):
        view_content = re.sub(old_init_pattern, new_init, view_content, flags=re.DOTALL)
        print("   + Constructor refactorizado para usar modelo")

    # PASO 3: Reemplazar cualquier uso directo de self.db_connection
    # Buscar y reportar usos directos
    direct_db_uses = re.findall(r"self\.db_connection\.[^=\s]*", view_content)
    if direct_db_uses:
        print(f"   ATENCION: {len(direct_db_uses)} usos directos de BD encontrados:")
        for use in set(direct_db_uses):
            print(f"     - {use}")
        print("   Estos deben ser refactorizados manualmente para usar self.model")

    # PASO 4: Agregar método helper para delegar al modelo
    helper_method = '''
    def get_model(self):
        """Retorna el modelo de inventario para operaciones de datos"""
        return self.model
    
    def refresh_data(self):
        """Actualiza los datos desde el modelo"""
        if hasattr(self, 'model') and self.model:
            # Llamar a métodos del modelo para actualizar la vista
            # Este método debe ser implementado según las necesidades específicas
            pass'''

    if "def get_model(self):" not in view_content:
        # Agregar al final de la clase, antes del último método
        lines = view_content.split("\n")

        # Encontrar el final de la clase
        class_end = len(lines) - 1
        for i in range(len(lines) - 1, -1, -1):
            if (
                lines[i].strip()
                and not lines[i].startswith(" ")
                and not lines[i].startswith("\t")
            ):
                class_end = i
                break

        # Insertar métodos helper antes del final
        helper_lines = helper_method.split("\n")
        for j, helper_line in enumerate(helper_lines):
            lines.insert(class_end + j, helper_line)

        view_content = "\n".join(lines)
        print("   + Métodos helper agregados")

    # Escribir archivo refactorizado
    with open(view_file, "w", encoding="utf-8") as f:
        f.write(view_content)

    print("   COMPLETADO: inventario/view.py refactorizado para usar patrón MVC")

    # PASO 5: Verificar que el modelo existe y tiene la interfaz necesaria
    verify_model_interface(model_file)


def verify_model_interface(model_file):
    """Verifica que el modelo tiene la interfaz necesaria"""
    print("\n2. VERIFICANDO: Interfaz del modelo InventarioModel")

    with open(model_file, "r", encoding="utf-8") as f:
        model_content = f.read()

    # Verificar que la clase InventarioModel existe
    if "class InventarioModel" in model_content:
        print("   + Clase InventarioModel encontrada")
    else:
        print("   ERROR: Clase InventarioModel no encontrada en model.py")
        return

    # Verificar métodos básicos necesarios
    required_methods = [
        "obtener_productos",
        "agregar_producto",
        "actualizar_producto",
        "eliminar_producto",
        "obtener_movimientos",
    ]

    missing_methods = []
    for method in required_methods:
        if f"def {method}(" not in model_content:
            missing_methods.append(method)

    if missing_methods:
        print(f"   ATENCION: Métodos faltantes en modelo: {missing_methods}")
        print("   Estos métodos deben ser implementados para completar la interfaz")
    else:
        print("   + Interfaz del modelo verificada")


def create_mvc_guidelines():
    """Crea documento con guidelines MVC para el proyecto"""
    print("\n3. CREANDO: Guidelines MVC para el proyecto")

    guidelines_content = """# Guidelines MVC para Rexus.app

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

1. **Vista usa Modelo**: `self.model.obtener_datos()` [CHECK]
2. **No SQL en Vista**: `cursor.execute()` en view.py [ERROR]
3. **No UI en Modelo**: `QMessageBox` en model.py [ERROR]
4. **Controlador Liviano**: Métodos cortos y específicos [CHECK]
5. **Documentación**: Docstrings en todos los métodos [CHECK]

## Ejemplo Correcto

```python
# En view.py
class InventarioView(QWidget):
    def __init__(self, db_connection=None):
        super().__init__()
        self.model = InventarioModel(db_connection)  # [CHECK] Usa modelo
        self.init_ui()
    
    def cargar_productos(self):
        productos = self.model.obtener_productos()  # [CHECK] Delega al modelo
        self.actualizar_tabla(productos)

# En model.py  
class InventarioModel:
    def obtener_productos(self):
        cursor = self.db_connection.cursor()  # [CHECK] SQL en modelo
        cursor.execute("SELECT * FROM productos")
        return cursor.fetchall()
```

## Violaciones Comunes a Evitar

[ERROR] Vista con SQL directo:
```python
# En view.py - MAL
cursor = self.db_connection.cursor()
cursor.execute("SELECT * FROM productos")
```

[ERROR] Modelo con UI:
```python
# En model.py - MAL  
from PyQt6.QtWidgets import QMessageBox
QMessageBox.warning(None, "Error", "Mensaje")
```

[ERROR] Controlador pesado:
```python
# En controller.py - MAL
def metodo_muy_largo_con_muchas_responsabilidades(self):
    # 100+ líneas de código
    # Lógica de negocio + UI + validaciones + cálculos
```
"""

    guidelines_file = Path(__file__).parent.parent.parent / "docs" / "MVC_GUIDELINES.md"
    guidelines_file.parent.mkdir(exist_ok=True)

    with open(guidelines_file, "w", encoding="utf-8") as f:
        f.write(guidelines_content)

    print(f"   Guidelines creadas: {guidelines_file}")


def main():
    """Función principal"""
    fix_mvc_violations()
    create_mvc_guidelines()

    print("\n" + "=" * 60)
    print("REFACTORIZACION MVC COMPLETADA")
    print("=" * 60)
    print("SIGUIENTE PASOS:")
    print("1. Revisar cambios en inventario/view.py")
    print("2. Implementar métodos faltantes en inventario/model.py si es necesario")
    print("3. Probar funcionalidad para verificar que no se rompió nada")
    print("4. Aplicar patrones similares a otros módulos si es necesario")
    print("5. Revisar guidelines MVC en docs/MVC_GUIDELINES.md")


if __name__ == "__main__":
    main()
