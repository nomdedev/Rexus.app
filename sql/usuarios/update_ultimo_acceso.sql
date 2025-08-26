UPDATE usuarios 
SET ultimo_acceso = CURRENT_TIMESTAMP,
    intentos_fallidos = 0
WHERE id = @user_id
