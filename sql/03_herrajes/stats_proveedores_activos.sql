-- Contar proveedores únicos activos
-- Parámetros: Ninguno
-- Retorna: COUNT(DISTINCT) de proveedores

SELECT COUNT(DISTINCT proveedor)
FROM herrajes
WHERE activo = 1
  AND proveedor IS NOT NULL;
