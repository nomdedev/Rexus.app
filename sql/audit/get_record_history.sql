-- Obtener historial completo de un registro específico
SELECT * FROM audit_trail
WHERE tabla = ? AND registro_id = ?
ORDER BY fecha_cambio DESC;
