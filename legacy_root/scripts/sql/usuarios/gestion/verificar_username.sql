-- Verificar unicidad de username
SELECT COUNT(*) as count
FROM usuarios 
WHERE username = %(username)s 
    AND activo = 1;
