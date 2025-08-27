-- Elimina una configuración editable
DELETE FROM configuracion_sistema 
WHERE id = @config_id 
AND activo = 1 AND es_editable = 1
