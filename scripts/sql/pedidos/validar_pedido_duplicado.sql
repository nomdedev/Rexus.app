-- Validar que no existe pedido duplicado
-- Archivo: validar_pedido_duplicado.sql
-- Módulo: Pedidos
-- Descripción: Verifica unicidad de número de pedido

SELECT id 
FROM [pedidos] 
WHERE numero_pedido = @numero_pedido;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'numero_pedido': numero_pedido})
-- return cursor.fetchone() is not None
