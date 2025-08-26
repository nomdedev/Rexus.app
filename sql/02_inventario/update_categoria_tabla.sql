-- update_categoria_tabla.sql  
-- Actualiza la categoría en la tabla categorías
-- Parámetros: :categoria_nueva, :categoria_actual

UPDATE categorias
SET nombre = :categoria_nueva, fecha_modificacion = GETDATE()
WHERE nombre = :categoria_actual