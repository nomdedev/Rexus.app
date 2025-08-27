-- select_estadisticas_libro_contable.sql
-- Obtiene estadísticas del libro contable
-- Sin parámetros

SELECT
    SUM(debe) as total_debe,
    SUM(haber) as total_haber,
    SUM(saldo) as saldo_total,
    COUNT(*) as total_asientos
FROM libro_contable
WHERE estado = 'ACTIVO'