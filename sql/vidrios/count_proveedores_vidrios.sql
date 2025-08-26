-- Contar proveedores distintos de vidrios
SELECT COUNT(DISTINCT proveedor) FROM vidrios WHERE estado = 'ACTIVO';
