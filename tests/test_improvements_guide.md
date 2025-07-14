# Guía de Mejoras para Tests en stock.app

## Mejores Prácticas

### 1. Estructura de Tests

- Usar el patrón Arrange-Act-Assert (AAA):
  ```python
  def test_algo():
      # Arrange (preparar)
      controller = Controller()
      mock_data = {'key': 'value'}

      # Act (actuar)
      result = controller.process(mock_data)

      # Assert (verificar)
      assert result == expected, "El resultado no coincide"
  ```

### 2. Fixtures Compartidos

- Crear fixtures en `conftest.py` para compartirlos entre tests:
  ```python
  # conftest.py
  import pytest

  @pytest.fixture
  def mock_database():
      # Configurar base de datos de prueba
      db = MockDatabase()
      yield db
      # Limpiar después de las pruebas
      db.cleanup()
  ```

### 3. Mocks y Patching

- Usar `unittest.mock` para aislar componentes:
  ```python
  from unittest.mock import patch

  @patch('modules.inventario.controller.Database')
  def test_with_mock_db(mock_db):
      mock_db.return_value.get_items.return_value = [{'id': 1}]
      controller = InventarioController()
      items = controller.get_all_items()
      assert items[0]['id'] == 1
  ```

### 4. Mensajes de Assert

- Incluir siempre mensajes descriptivos en los asserts:
  ```python
  # Mal
  assert result == 42

  # Bien
  assert result == 42, "El cálculo debería dar 42"
  ```

### 5. Organización de Tests

- Agrupar tests relacionados en clases:
  ```python
  class TestInventarioController:
      def test_add_item(self):
          # ...

      def test_remove_item(self):
          # ...
  ```

## Problemas Comunes y Soluciones

### 1. Importaciones Incorrectas

- **Problema**: `from modules.usuarios.controller import usuariosController`
- **Solución**: `from modules.usuarios.controller import Controller as UsuariosController`

### 2. Acceso a Miembros Protegidos

- **Problema**: `controller._process_data()`
- **Solución**: Crear métodos públicos para testing o usar `patch` para mock

### 3. Asserts sin Mensajes

- **Problema**: `assert result == expected`
- **Solución**: `assert result == expected, "El resultado no coincide con lo esperado"`

### 4. Setup/Teardown Duplicado

- **Problema**: Código de inicialización repetido en varios tests
- **Solución**: Usar fixtures compartidos en `conftest.py`

## Cheatsheet de pytest

```
# Ejecutar todos los tests
pytest

# Ejecutar tests de un archivo específico
pytest tests/test_inventario.py

# Ejecutar una función de test específica
pytest tests/test_inventario.py::test_add_item

# Mostrar salida en tests que fallan
pytest -v

# Generar informe de cobertura
pytest --cov=modules tests/
```
