SELECT COUNT(*) FROM auditoria_log
WHERE fecha_hora >= ? AND resultado = 'FALLIDO'