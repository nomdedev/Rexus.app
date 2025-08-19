SELECT v.tipo, COUNT(*) as cantidad
FROM vidrios v
WHERE v.activo = 1
GROUP BY v.tipo
ORDER BY cantidad DESC;