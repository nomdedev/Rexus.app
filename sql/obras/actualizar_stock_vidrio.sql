-- Actualizar stock de vidrio (SQLite)
-- Parámetros: :cantidad, :material_id
-- Retorna: Reduce el stock del vidrio

UPDATE vidrios 
SET 
    stock = stock - :cantidad, 
    fecha_modificacion = datetime('now') 
WHERE id = :material_id;