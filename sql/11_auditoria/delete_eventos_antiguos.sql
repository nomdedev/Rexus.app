-- Eliminar eventos de auditoría antiguos según política de retención
-- Parámetros: :dias_retencion
-- Retorna: número de registros eliminados

DELETE FROM auditoria_eventos 
WHERE timestamp < datetime('now', '-' || :dias_retencion || ' days');