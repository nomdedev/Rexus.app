SELECT
COUNT(*) as total_compras,
SUM(total) as total_compras_monto,
SUM(monto_pagado) as total_pagado,
SUM(saldo_pendiente) as total_pendiente
FROM pagos_materiales;
