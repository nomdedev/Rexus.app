SELECT DISTINCT categoria
FROM productos
WHERE categoria IS NOT NULL AND categoria != '' AND activo = 1
ORDER BY categoria;