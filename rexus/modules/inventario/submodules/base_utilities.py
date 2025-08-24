"""
Base Utilities - Funciones fundamentales para el módulo de Inventario
Refactorizado de InventarioModel para mejor mantenibilidad

Responsabilidades:
- Utilidades de seguridad SQL
- Validaciones de tabla y conexión
- Paginación base
- Conversión de datos
- Configuración y inicialización
- Generación de códigos QR y barras
"""

import datetime
import logging
import qrcode
# FIXME: Specify concrete exception types instead of generic Exceptionas e:
                        return False
finally:
        if 'cursor' in locals():
                cursor.close()

def crear_paginacion_query(self, base_query: str, offset: int, limit: int,
where_clause: str = "", order_clause: str = "") -> str:
        """
Crea una query paginada de forma segura.

Args:
        base_query: Query base
offset: Número de registros a saltar
limit: Número máximo de registros
where_clause: Cláusula WHERE adicional
order_clause: Cláusula ORDER BY

Returns:
        str: Query paginada
"""
try:
        # Sanitizar parámetros
offset = max(0, int(offset)) if offset else 0
limit = max(1, min(int(limit), 1000)) if limit else 50  # Máximo 1000 registros

# Construir query paginada
query_parts = [base_query]

if where_clause:
                query_parts.append(f"WHERE {where_clause}")

if order_clause:
                query_parts.append(f"ORDER BY {order_clause}")
else:
                query_parts.append("ORDER BY id DESC")  # Orden por defecto

# Agregar paginación SQL Server
query_parts.append(f"OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY")

return " ".join(query_parts)

except Exception as e:

def obtener_productos_demo(self) -> List[Dict[str, Any]]:
        """
Obtiene productos de demostración cuando no hay conexión a BD.

Returns:
        List: Lista de productos demo
"""
return [
{
'id': 1,
'codigo': 'DEMO-001',
'descripcion': 'Producto Demo 1',
'categoria': 'Categoría Demo',
'precio_unitario': 100.00,
'stock_actual': 50,
'stock_minimo': 10,
'estado_stock': 'NORMAL',
'proveedor': 'Proveedor Demo',
'fecha_creacion': self.obtener_timestamp_actual()
},
{
'id': 2,
'codigo': 'DEMO-002',
'descripcion': 'Producto Demo 2',
'categoria': 'Categoría Demo',
'precio_unitario': 250.00,
'stock_actual': 5,
'stock_minimo': 10,
'estado_stock': 'BAJO',
'proveedor': 'Proveedor Demo',
'fecha_creacion': self.obtener_timestamp_actual()
}
]

def log_operacion(self,
operacion: str,
detalles: str = "",
nivel: str = "INFO") -> None:
        """
Registra una operación en el log.

Args:
        operacion: Tipo de operación realizada
detalles: Detalles adicionales de la operación
nivel: Nivel de logging (INFO, WARNING, ERROR)
"""
try:
        mensaje = f"[INVENTARIO] {operacion}"
if detalles:
                mensaje += f" - {detalles}"

if nivel.upper() == "ERROR":
                logger.error(mensaje)
elif nivel.upper() == "WARNING":
                logger.warning(mensaje)
else:
                logger.info(mensaje)

except Exception as e:
        # Evitar loops de logging
logger.info(f"Error en logging: {e}")
