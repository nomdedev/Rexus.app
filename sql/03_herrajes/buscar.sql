-- Buscar herrajes por término general en múltiples campos
-- Parámetros:
--   :termino (requerido) - Término de búsqueda (LIKE)
-- Retorna: Herrajes que coinciden con el término

SELECT * FROM herrajes
WHERE activo = 1
  AND (
    codigo LIKE :termino OR
    nombre LIKE :termino OR
    descripcion LIKE :termino OR
    proveedor LIKE :termino
  )
ORDER BY codigo;
