-- scripts/sql/logistica/actualizar_transporte.sql
-- Actualiza un transporte existente
UPDATE [transportes]
SET tipo = ?, proveedor = ?, capacidad_kg = ?, capacidad_m3 = ?,
    costo_km = ?, disponible = ?, observaciones = ?, fecha_modificacion = GETDATE()
WHERE id = ?