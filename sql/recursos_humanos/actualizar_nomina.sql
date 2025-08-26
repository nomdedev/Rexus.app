-- Actualizar registro existente de nómina
UPDATE nomina 
SET salario_base = ?, dias_trabajados = ?, horas_extra = ?,
    bonos = ?, descuentos = ?, faltas = ?, bruto = ?,
    total_descuentos = ?, neto = ?, fecha_calculo = GETDATE()
WHERE empleado_id = ? AND mes = ? AND anio = ?
