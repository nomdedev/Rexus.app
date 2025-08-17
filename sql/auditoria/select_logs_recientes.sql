-- Obtener logs de auditoría recientes
-- Parámetros: limite (número de registros)
SELECT TOP {limite}
    id, fecha_hora, usuario, modulo, accion, descripcion,
    tabla_afectada, registro_id, nivel_criticidad, resultado
FROM auditoria_log
ORDER BY fecha_hora DESC