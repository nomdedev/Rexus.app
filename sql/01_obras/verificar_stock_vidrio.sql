-- Verificar stock disponible de vidrio (SQLite)
-- Parámetros: :material_id
-- Retorna: stock disponible del vidrio

SELECT stock
FROM vidrios 
WHERE id = :material_id AND activo = 1;