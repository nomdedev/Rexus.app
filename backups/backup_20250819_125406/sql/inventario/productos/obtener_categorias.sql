SELECT DISTINCT categoria
FROM [inventario]
WHERE activo = 1
    AND categoria IS NOT NULL
    AND categoria != ''
ORDER BY categoria ASC;