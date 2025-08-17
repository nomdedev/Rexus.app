-- Obtener estadísticas de mantenimiento
SELECT 
    COUNT(*) as total_equipos,
    SUM(CASE WHEN estado = 'Operativo' THEN 1 ELSE 0 END) as equipos_operativos,
    SUM(CASE WHEN estado = 'En Mantenimiento' THEN 1 ELSE 0 END) as equipos_mantenimiento,
    SUM(CASE WHEN estado = 'Fuera de Servicio' THEN 1 ELSE 0 END) as equipos_fuera_servicio
FROM equipos 
WHERE activo = 1;
