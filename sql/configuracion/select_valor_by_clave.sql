-- Obtiene el valor de una configuración específica por clave
SELECT valor 
FROM configuracion_sistema 
WHERE clave = @clave 
AND activo = 1
