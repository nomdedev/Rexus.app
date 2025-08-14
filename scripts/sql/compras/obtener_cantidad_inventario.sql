-- Obtener cantidad disponible de un producto activo
SELECT cantidad FROM inventario WHERE codigo = ? AND estado = 'ACTIVO'