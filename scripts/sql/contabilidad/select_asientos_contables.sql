SELECT
    id, numero_asiento, fecha_asiento, tipo_asiento, concepto,
    referencia, debe, haber, saldo, estado, usuario_creacion,
    fecha_creacion, fecha_modificacion
FROM libro_contable
WHERE
    (? IS NULL OR fecha_asiento >= ?)
    AND (? IS NULL OR fecha_asiento <= ?)
    AND (? IS NULL OR ? = 'Todos' OR tipo_asiento = ?)
ORDER BY fecha_asiento DESC, numero_asiento DESC