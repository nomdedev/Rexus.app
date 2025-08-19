SELECT usuario, COUNT(*) as cantidad
FROM auditoria_log
WHERE fecha_hora >= ?
GROUP BY usuario
ORDER BY cantidad DESC