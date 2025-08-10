SELECT responsable, COUNT(*) as cantidad
FROM obras
GROUP BY responsable
ORDER BY cantidad DESC