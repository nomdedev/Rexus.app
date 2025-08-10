-- scripts/sql/logistica/estadisticas_entregas_por_estado.sql
-- Obtiene estadísticas de entregas agrupadas por estado
SELECT estado, COUNT(*) as cantidad
FROM [entregas]
GROUP BY estado