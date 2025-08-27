-- Obtiene todos los equipos con información básica
SELECT id, nombre, tipo, estado, ubicacion, fecha_instalacion, ultimo_mantenimiento
FROM equipos 
ORDER BY nombre
