SELECT COUNT(*) as transportes_disponibles
FROM [transportes]
WHERE activo = 1 AND disponible = 1;