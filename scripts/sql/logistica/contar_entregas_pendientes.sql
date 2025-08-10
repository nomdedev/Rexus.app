-- scripts/sql/logistica/contar_entregas_pendientes.sql
-- Cuenta las entregas en estado pendiente (programadas o en tránsito)
SELECT COUNT(*) FROM [entregas]
WHERE estado IN ('PROGRAMADA', 'EN_TRANSITO')