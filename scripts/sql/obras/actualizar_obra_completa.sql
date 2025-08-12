-- 🔒 Actualización completa de obra
-- Reemplaza f-string vulnerable por consulta parametrizada segura
UPDATE obras 
SET nombre = @nombre,
    descripcion = @descripcion,
    direccion = @direccion,
    cliente = @cliente,
    estado = @estado,
    fecha_inicio = @fecha_inicio,
    fecha_fin_estimada = @fecha_fin_estimada,
    presupuesto_total = @presupuesto_total,
    presupuesto_utilizado = @presupuesto_utilizado,
    observaciones = @observaciones,
    updated_at = GETDATE()
WHERE id = @obra_id 
    AND activo = 1;
