-- 🔒 Eliminación lógica (soft delete) de obra
-- Reemplaza SQL embebido por consulta parametrizada
UPDATE obras 
SET activo = 0, 
    updated_at = GETDATE(), 
    usuario_eliminacion = @usuario
WHERE id = @obra_id 
    AND activo = 1;
