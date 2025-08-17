SELECT COUNT(*) as total_herrajes FROM herrajes WHERE estado = 'ACTIVO';
SELECT COUNT(DISTINCT proveedor) as proveedores_activos FROM herrajes WHERE estado = 'ACTIVO';
SELECT SUM(precio_unitario) as valor_total_inventario FROM herrajes WHERE estado = 'ACTIVO';
SELECT proveedor, COUNT(*) as cantidad FROM herrajes WHERE estado = 'ACTIVO' GROUP BY proveedor ORDER BY cantidad DESC;
