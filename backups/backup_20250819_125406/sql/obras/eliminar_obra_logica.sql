UPDATE obras
SET activo = 0,
    updated_at = GETDATE(),
    usuario_eliminacion = @usuario
WHERE id = @obra_id
    AND activo = 1;