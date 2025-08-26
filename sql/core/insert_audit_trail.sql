-- Archivo SQL: Insertar registro en audit trail
-- Ubicación: sql/core/insert_audit_trail.sql
-- Propósito: Corrección SQL injection en audit_trail.py log_change()

INSERT INTO audit_trail (
    tabla, accion, registro_id, usuario_id, usuario_nombre,
    datos_anteriores, datos_nuevos, modulo, detalles,
    fecha_cambio, ip_address
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?);