-- Autenticar usuario con credenciales
-- Archivo: autenticar_usuario.sql
-- Módulo: Usuarios
-- Descripción: Valida credenciales de usuario y retorna datos de sesión

SELECT 
    id, 
    usuario, 
    password_hash, 
    nombre_completo, 
    email, 
    telefono, 
    rol, 
    estado,
    intentos_fallidos,
    bloqueado_hasta,
    ultimo_acceso,
    fecha_creacion,
    fecha_modificacion
FROM [usuarios] 
WHERE LOWER(usuario) = LOWER(?) 
    AND activo = 1
    AND estado IN ('ACTIVO', 'PRIMERA_VEZ');

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'username': username})
-- user_data = cursor.fetchone()
