-- Contar obras completadas en un período (SQLite)
-- Parámetros: :fecha_inicio, :fecha_fin
-- Retorna: COUNT de obras completadas en el período

SELECT COUNT(*) as total_obras
FROM obras
WHERE estado = 'COMPLETADA'
  AND fecha_finalizacion BETWEEN :fecha_inicio AND :fecha_fin;