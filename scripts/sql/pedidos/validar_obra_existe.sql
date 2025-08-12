-- Validar que obra existe y está activa
-- Archivo: validar_obra_existe.sql
-- Módulo: Pedidos
-- Descripción: Verifica existencia y estado de obra

SELECT id 
FROM [obras] 
WHERE id = @obra_id AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'obra_id': obra_id})
-- return cursor.fetchone() is not None
