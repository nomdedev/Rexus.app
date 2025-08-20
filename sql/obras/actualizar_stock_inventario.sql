-- Actualizar cantidad disponible en inventario (SQLite)
-- Parámetros: :cantidad, :material_id
-- Retorna: Reduce la cantidad disponible del material

UPDATE inventario 
SET 
    cantidad_disponible = cantidad_disponible - :cantidad, 
    fecha_modificacion = datetime('now') 
WHERE id = :material_id;