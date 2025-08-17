-- Contar acciones por módulo desde una fecha
-- Parámetros: fecha_desde
SELECT modulo, COUNT(*) as cantidad
FROM auditoria_log
WHERE fecha_hora >= ?
GROUP BY modulo
ORDER BY cantidad DESC