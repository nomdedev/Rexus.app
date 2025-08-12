-- Script seguro para obtener lista de proveedores únicos
-- Uso: Ejecutar desde backend sin parámetros

SELECT DISTINCT proveedor 
FROM herrajes 
WHERE estado = 'ACTIVO' 
ORDER BY proveedor;