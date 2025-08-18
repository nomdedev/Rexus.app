-- Actualizar último acceso de usuario
-- Archivo: actualizar_ultimo_acceso.sql
-- Módulo: Usuarios  
-- Descripción: Actualiza timestamp de último acceso y resetea intentos fallidos

UPDATE [usuarios] 
SET 
    intentos_fallidos = 0, 
    ultimo_acceso = GETDATE(),
    fecha_modificacion = GETDATE()
WHERE LOWER(usuario) = LOWER(?) AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'username': username})
