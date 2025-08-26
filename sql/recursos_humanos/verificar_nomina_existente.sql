-- Verificar si ya existe registro de nómina para empleado/período
SELECT id FROM nomina 
WHERE empleado_id = ? AND mes = ? AND anio = ?
