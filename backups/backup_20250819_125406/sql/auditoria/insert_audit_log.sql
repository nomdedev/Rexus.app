INSERT INTO auditoria_log (
    usuario, modulo, accion, descripcion, tabla_afectada, registro_id,
    valores_anteriores, valores_nuevos, nivel_criticidad, resultado, error_mensaje,
    fecha_hora
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());