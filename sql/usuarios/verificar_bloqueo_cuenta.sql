-- Verificar intentos fallidos y tiempo de bloqueo
-- Archivo: verificar_bloqueo_cuenta.sql

SELECT 
    ISNULL(intentos_fallidos, 0) as intentos,
    ultimo_intento_fallido,
    CASE 
        WHEN ultimo_intento_fallido IS NULL THEN 1
        WHEN DATEDIFF(SECOND, ultimo_intento_fallido, GETDATE()) > ?
        THEN 1
        ELSE 0
    END as tiempo_expirado
FROM usuarios 
WHERE LOWER(username) = ?;
