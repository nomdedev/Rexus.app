DELETE FROM auditoria_log
WHERE fecha_hora < ? AND nivel_criticidad NOT IN ('CRÍTICA')