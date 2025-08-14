-- Obtener cantidad disponible de un producto de inventario
SELECT cantidad_disponible FROM inventario WHERE id = ? AND activo = 1