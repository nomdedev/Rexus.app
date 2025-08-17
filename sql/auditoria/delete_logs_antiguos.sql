-- Eliminar logs antiguos (limpieza automática)
-- Parámetros: fecha_limite
-- Conserva logs críticos
DELETE FROM auditoria_log
WHERE fecha_hora < ? AND nivel_criticidad NOT IN ('CRÍTICA')