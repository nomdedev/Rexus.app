-- Obtener todos los herrajes activos con filtros opcionales
-- Parámetros:
--   :proveedor (opcional) - Filtra por proveedor (LIKE)
--   :codigo (opcional) - Filtra por código (LIKE)
--   :descripcion (opcional) - Filtra por nombre o descripción (LIKE)
-- Retorna: Lista completa de herrajes

SELECT * FROM herrajes
WHERE activo = 1
  AND (:proveedor IS NULL OR proveedor LIKE :proveedor)
  AND (:codigo IS NULL OR codigo LIKE :codigo)
  AND (:descripcion IS NULL OR (nombre LIKE :descripcion OR descripcion LIKE :descripcion))
ORDER BY codigo;
