SELECT COUNT(*) as total_herrajes FROM productos WHERE estado = 'ACTIVO';
SELECT COUNT(DISTINCT proveedor) as proveedores_activos FROM productos WHERE estado = 'ACTIVO';
SELECT SUM(precio_unitario) as valor_total_inventario FROM productos WHERE estado = 'ACTIVO';
SELECT proveedor, COUNT(*) as cantidad FROM productos WHERE estado = 'ACTIVO' GROUP BY proveedor ORDER BY cantidad DESC;