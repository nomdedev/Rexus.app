SELECT
COUNT(*) as total_pagos,
SUM(monto) as total_monto,
COUNT(DISTINCT obra_id) as obras_con_pagos
FROM pagos_obras
WHERE estado = 'PAGADO';
