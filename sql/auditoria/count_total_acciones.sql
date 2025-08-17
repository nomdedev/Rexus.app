-- Contar total de acciones de auditoría desde una fecha
-- Parámetros: fecha_desde
SELECT COUNT(*) FROM auditoria_log
WHERE fecha_hora >= ?