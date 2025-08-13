-- Calcula la suma total de presupuestos de obras activas
SELECT SUM(presupuesto_total) FROM obras WHERE activo = 1