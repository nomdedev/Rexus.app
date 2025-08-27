-- insert_log_seguridad.sql
-- Inserta un evento de seguridad en el log
-- Parámetros: :usuario_id, :accion, :modulo, :detalles, :fecha, :ip_address

INSERT INTO logs_seguridad (usuario_id, accion, modulo, detalles, fecha, ip_address)
VALUES (:usuario_id, :accion, :modulo, :detalles, :fecha, :ip_address)
