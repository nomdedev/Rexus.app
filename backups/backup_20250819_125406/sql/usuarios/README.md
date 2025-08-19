# Queries SQL para módulo usuarios

Queries extraídas automáticamente del código para mayor seguridad.

## Archivos disponibles:

- `delete_usuarios_1.sql`: Query extraída del código

## Uso:

```python
# En el modelo:
sql = self.sql_manager.get_query('usuarios', 'nombre_query')
cursor.execute(sql, params)
```
