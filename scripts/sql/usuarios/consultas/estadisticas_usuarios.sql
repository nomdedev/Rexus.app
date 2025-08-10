-- Estadísticas de usuarios
SELECT 
    COUNT(*) as total_usuarios,
    SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as usuarios_activos,
    SUM(CASE WHEN cuenta_bloqueada = 1 THEN 1 ELSE 0 END) as usuarios_bloqueados,
    COUNT(DISTINCT rol) as total_roles,
    AVG(intentos_fallidos) as promedio_intentos_fallidos
FROM usuarios;
