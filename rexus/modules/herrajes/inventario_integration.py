"""
MIT License

Copyright (c) 2025 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Integración Herrajes-Inventario - Rexus.app
==========================================

Proporciona servicios de integración entre el módulo de herrajes y el sistema
principal de inventario, permitiendo sincronización de stock, transferencias
y movimientos unificados.
"""

import logging
def corregir_discrepancias(self) -> Tuple[bool, str, int]:
        """
Corrige discrepancias de stock entre herrajes y su inventario.

Returns:
        Tuple[bool, str, int]: (éxito, mensaje, correcciones realizadas)
"""
if not self.db_connection:
        return False, "Sin conexión a la base de datos", 0

try:
        cursor = self.db_connection.cursor()
correcciones = 0

# Obtener discrepancias
cursor.execute("""
SELECT h.id, h.codigo, h.stock_actual, hi.stock_actual
FROM herrajes h
LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
WHERE h.estado = 'ACTIVO'
AND (h.stock_actual != ISNULL(hi.stock_actual, 0))
""")

discrepancias = cursor.fetchall()

for herraje_id, codigo, stock_herrajes, stock_inventario in discrepancias:
                # Usar stock_herrajes como fuente de verdad
if stock_inventario is None:
                # Crear entrada en herrajes_inventario
cursor.execute("""
INSERT INTO herrajes_inventario (herraje_id, stock_actual)
VALUES (?, ?)
""", (herraje_id, stock_herrajes))
else:
                # Actualizar stock en herrajes_inventario
cursor.execute("""
UPDATE herrajes_inventario
SET stock_actual = ?
WHERE herraje_id = ?
""", (stock_herrajes, herraje_id))

# Registrar corrección
cursor.execute("""
INSERT INTO historial (tabla, operacion, registro_id, usuario,
fecha, observaciones)
VALUES ('herrajes_inventario',
'CORRECCION',
?,
USER_NAME(),
GETDATE(), ?)
""", (herraje_id, f"Corrección automática de stock: {stock_inventario} -> {stock_herrajes}"))

correcciones += 1

self.db_connection.commit()
return True, f"Se corrigieron {correcciones} discrepancias de stock", correcciones

except Exception as e:
