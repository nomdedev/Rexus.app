-- update_categoria_productos.sql
-- Actualiza la categoría de productos en inventario
-- Parámetros: :categoria_nueva, :categoria_actual

UPDATE inventario
SET categoria = :categoria_nueva, fecha_modificacion = GETDATE()
WHERE categoria = :categoria_actual