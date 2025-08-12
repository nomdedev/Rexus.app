-- Validar que cliente existe y está activo
-- Archivo: validar_cliente_existe.sql
-- Módulo: Pedidos
-- Descripción: Verifica existencia y estado de cliente

SELECT id 
FROM [clientes] 
WHERE id = @cliente_id AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'cliente_id': cliente_id})
-- return cursor.fetchone() is not None
