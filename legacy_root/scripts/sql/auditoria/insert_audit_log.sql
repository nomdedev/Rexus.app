-- Inserción segura de registro de auditoría
-- Utiliza la tabla 'auditoria'
-- Todos los parámetros se deben pasar usando prepared statements

INSERT INTO auditoria (
    usuario_id, modulo, accion, tabla_afectada, registro_id,
    valores_anteriores, valores_nuevos, ip_address, user_agent,
    fecha_accion
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());