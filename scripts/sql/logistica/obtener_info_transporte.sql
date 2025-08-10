-- scripts/sql/logistica/obtener_info_transporte.sql
-- Obtiene información específica de un transporte para cálculo de costos
SELECT costo_km, capacidad_kg, capacidad_m3
FROM [transportes]
WHERE id = ?