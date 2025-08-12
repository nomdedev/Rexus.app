-- Actualizar último acceso del usuario
UPDATE usuarios 
SET ultimo_acceso = CURRENT_TIMESTAMP,
    intentos_fallidos = 0,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE id = %(user_id)s;
