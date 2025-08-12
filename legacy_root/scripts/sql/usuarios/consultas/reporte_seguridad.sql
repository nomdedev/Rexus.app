-- Reporte de seguridad de usuarios
SELECT 
    u.id,
    u.username,
    u.email,
    u.intentos_fallidos,
    u.cuenta_bloqueada,
    u.ultimo_acceso,
    DATEDIFF(day, u.ultimo_acceso, CURRENT_TIMESTAMP) as dias_sin_acceso
FROM usuarios u
WHERE u.activo = 1
    AND (u.intentos_fallidos > 3 
         OR u.cuenta_bloqueada = 1 
         OR DATEDIFF(day, u.ultimo_acceso, CURRENT_TIMESTAMP) > 30)
ORDER BY u.intentos_fallidos DESC, dias_sin_acceso DESC;
