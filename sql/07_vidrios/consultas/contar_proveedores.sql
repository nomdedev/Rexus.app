SELECT COUNT(DISTINCT v.proveedor) as total_proveedores
FROM vidrios v
WHERE v.activo = 1;