-- select_estadisticas_generales.sql
-- Obtiene estadísticas generales del sistema
-- Sin parámetros

SELECT
    (SELECT COUNT(*) FROM recibos WHERE MONTH(fecha_emision) = MONTH(GETDATE())) as recibos_mes,
    (SELECT SUM(monto) FROM recibos WHERE MONTH(fecha_emision) = MONTH(GETDATE())) as monto_recibos_mes,
    (SELECT COUNT(*) FROM pagos_obras WHERE MONTH(fecha_pago) = MONTH(GETDATE())) as pagos_obras_mes,
    (SELECT SUM(monto) FROM pagos_obras WHERE MONTH(fecha_pago) = MONTH(GETDATE())) as monto_pagos_mes