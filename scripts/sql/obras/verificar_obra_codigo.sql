SELECT codigo
FROM obras
WHERE id = @obra_id
    AND activo = 1;