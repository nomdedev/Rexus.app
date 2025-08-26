SELECT id, tipo 
FROM vidrios 
WHERE id = @vidrio_id 
  AND activo = 1
