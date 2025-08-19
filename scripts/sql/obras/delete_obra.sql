UPDATE obras
SET
    activo = 0,
    updated_at = GETDATE(),
    usuario_eliminacion = ?
WHERE id = ? AND activo = 1;