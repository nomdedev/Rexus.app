-- Contar proveedores activos eficientemente
SELECT 
    COUNT(*) as total_proveedores,
    SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as proveedores_activos,
    SUM(CASE WHEN estado = 'INACTIVO' THEN 1 ELSE 0 END) as proveedores_inactivos
FROM proveedores