-- Contar acciones por usuario desde una fecha
-- Parámetros: fecha_desde
SELECT usuario, COUNT(*) as cantidad
FROM auditoria_log
WHERE fecha_hora >= ?
GROUP BY usuario
ORDER BY cantidad DESC