-- Verificar si un cliente está activo
SELECT COUNT(*) FROM clientes WHERE id = ? AND activo = 1