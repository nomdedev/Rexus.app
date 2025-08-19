-- Script para crear un nuevo usuario
-- Parámetros: :usuario, :password, :nombre_completo, :email, :telefono, :rol
-- Retorna: ID del usuario creado

DECLARE @salt NVARCHAR(50) = CAST(NEWID() AS NVARCHAR(50));
DECLARE @password_hash VARBINARY(32) = HASHBYTES('SHA2_256', :password + @salt);

INSERT INTO usuarios (
    usuario,
    password_hash,
    salt,
    nombre_completo,
    email,
    telefono,
    rol,
    estado,
    activo,
    fecha_creacion,
    intentos_fallidos
)
VALUES (
    :usuario,
    @password_hash,
    @salt,
    :nombre_completo,
    :email,
    :telefono,
    ISNULL(:rol, 'Usuario'),
    'Activo',
    1,
    GETDATE(),
    0
);

SELECT SCOPE_IDENTITY() as nuevo_id;