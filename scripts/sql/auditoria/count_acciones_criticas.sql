SELECT COUNT(*) FROM auditoria_log
WHERE fecha_hora >= ? AND nivel_criticidad IN ('ALTA', 'CRÍTICA')