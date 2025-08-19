SELECT modulo, COUNT(*) as cantidad
FROM auditoria_log
WHERE fecha_hora >= ?
GROUP BY modulo
ORDER BY cantidad DESC