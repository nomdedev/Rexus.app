-- Consulta para obtener el estado general del sistema
-- Parámetros: ninguno
-- Retorna: Estado completo del sistema

SELECT 
    'Sistema' as componente,
    CASE 
        WHEN COUNT(*) > 0 THEN 'Operativo'
        ELSE 'Error'
    END as estado,
    COUNT(*) as total_tablas,
    GETDATE() as fecha_verificacion,
    @@VERSION as version_bd,
    DB_NAME() as base_datos_actual
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'

UNION ALL

SELECT 
    'Usuarios' as componente,
    CASE 
        WHEN COUNT(*) > 0 THEN 'Activo'
        ELSE 'Sin usuarios'
    END as estado,
    COUNT(*) as total_usuarios,
    MAX(fecha_creacion) as ultima_actividad,
    'N/A' as info_adicional,
    'users' as contexto
FROM usuarios
WHERE activo = 1

UNION ALL

SELECT 
    'Inventario' as componente,
    CASE 
        WHEN COUNT(*) > 0 THEN 'Activo'
        ELSE 'Vacío'
    END as estado,
    COUNT(*) as total_productos,
    MAX(fecha_creacion) as ultima_actividad,
    'N/A' as info_adicional,
    'inventario' as contexto
FROM inventario_perfiles
WHERE activo = 1;