UPDATE configuracion_sistema 
SET valor = @valor, tipo = @tipo, categoria = @categoria, descripcion = @descripcion, 
    activo = @es_editable, fecha_modificacion = GETDATE()
WHERE id = @config_id
