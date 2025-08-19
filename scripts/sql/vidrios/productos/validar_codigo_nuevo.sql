SELECT COUNT(*) as existe
FROM vidrios
WHERE codigo = %(codigo)s
  AND activo = 1;