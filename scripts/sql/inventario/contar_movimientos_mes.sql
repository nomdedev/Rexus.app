-- Cuenta movimientos de inventario del mes actual
SELECT COUNT(*) FROM historial
WHERE accion LIKE 'INVENTARIO_%'
  AND MONTH(fecha) = MONTH(GETDATE())
  AND YEAR(fecha) = YEAR(GETDATE())