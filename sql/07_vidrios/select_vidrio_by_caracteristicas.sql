-- Verifica si ya existe un vidrio con las mismas características
SELECT id FROM vidrios 
WHERE tipo = @tipo 
  AND grosor = @grosor 
  AND ancho = @ancho 
  AND alto = @alto 
  AND color = @color 
  AND activo = 1
