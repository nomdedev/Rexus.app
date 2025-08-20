-- Verificar cantidad disponible en inventario (SQLite)
-- Parámetros: :material_id
-- Retorna: cantidad disponible del material

SELECT cantidad_disponible
FROM inventario 
WHERE id = :material_id AND activo = 1;