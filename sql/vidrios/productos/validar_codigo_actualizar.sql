-- Validar código único para actualización de vidrio
SELECT COUNT(*) as existe
FROM vidrios 
WHERE codigo = %(codigo)s 
  AND id != %(vidrio_id)s
  AND activo = 1;
