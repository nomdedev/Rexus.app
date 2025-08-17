-- Calcular suma de precios de vidrios activos
SELECT SUM(precio_m2) FROM vidrios WHERE estado = 'ACTIVO'