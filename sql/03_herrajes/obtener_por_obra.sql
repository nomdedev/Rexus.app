-- Obtener herrajes asignados a una obra específica
-- Parámetros:
--   :obra_id (requerido) - ID de la obra
-- Retorna: Herrajes con cantidades asignadas e instaladas

SELECT h.*, ho.cantidad_requerida, ho.cantidad_instalada, ho.observaciones
FROM herrajes h
INNER JOIN herrajes_obra ho ON h.id = ho.herraje_id
WHERE ho.obra_id = :obra_id
ORDER BY h.codigo;
