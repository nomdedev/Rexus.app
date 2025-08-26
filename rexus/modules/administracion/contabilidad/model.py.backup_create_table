"""
Modelo de Contabilidad - Rexus.app v2.0.0

Modelo para el submódulo de contabilidad dentro de administración.
Gestiona asientos contables, cuentas, balances y reportes financieros.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal

# Importar logging
try:
from ....utils.app_logger import get_logger
logger = get_logger(__name__)
except ImportError:
import logging
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
from ....utils.unified_sanitizer import sanitize_string
SANITIZER_AVAILABLE = True
except ImportError:
logger.warning("Sanitizador unificado no disponible")
SANITIZER_AVAILABLE = False
sanitize_string = lambda x: str(x).strip()


class ContabilidadModel:
"""Modelo para la gestión de contabilidad y finanzas."""

def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        """
Inicializar modelo de contabilidad.

Args:
        db_connection: Conexión a la base de datos
usuario_actual: Usuario que está usando el sistema
"""
self.db_connection = db_connection
self.usuario_actual = usuario_actual

# Nombres de tablas
self.tabla_libro_contable = "libro_contable"
self.tabla_plan_cuentas = "plan_cuentas"
self.tabla_asientos_detalle = "asientos_detalle"
self.tabla_balances = "balances_contables"

# Crear tablas si no existen
self.crear_tablas()

logger.info("ContabilidadModel inicializado")

def crear_tablas(self):
        """Crea las tablas necesarias para contabilidad."""
if not self.db_connection:
        logger.warning("No hay conexión de base de datos para crear tablas")
return

try:
        cursor = self.db_connection.cursor()

# Tabla de libro contable (asientos principales)
cursor.execute("""
CREATE TABLE IF NOT EXISTS libro_contable (
id INTEGER PRIMARY KEY AUTOINCREMENT,
numero_asiento INTEGER NOT NULL,
fecha_asiento DATE NOT NULL,
tipo_asiento VARCHAR(50) NOT NULL,
concepto TEXT NOT NULL,
referencia VARCHAR(100),
debe DECIMAL(15,2) DEFAULT 0.00,
haber DECIMAL(15,2) DEFAULT 0.00,
saldo DECIMAL(15,2) DEFAULT 0.00,
estado VARCHAR(20) DEFAULT 'ACTIVO',
usuario_creacion VARCHAR(100),
fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla de plan de cuentas
cursor.execute("""
CREATE TABLE IF NOT EXISTS plan_cuentas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
codigo_cuenta VARCHAR(20) NOT NULL UNIQUE,
nombre_cuenta VARCHAR(200) NOT NULL,
tipo_cuenta VARCHAR(50) NOT NULL,
nivel INTEGER DEFAULT 1,
cuenta_padre VARCHAR(20),
descripcion TEXT,
activa BOOLEAN DEFAULT TRUE,
fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla de detalle de asientos
cursor.execute("""
CREATE TABLE IF NOT EXISTS asientos_detalle (
id INTEGER PRIMARY KEY AUTOINCREMENT,
asiento_id INTEGER NOT NULL,
codigo_cuenta VARCHAR(20) NOT NULL,
debe DECIMAL(15,2) DEFAULT 0.00,
haber DECIMAL(15,2) DEFAULT 0.00,
concepto_detalle TEXT,
FOREIGN KEY (asiento_id) REFERENCES libro_contable(id),
FOREIGN KEY (codigo_cuenta) REFERENCES plan_cuentas(codigo_cuenta)
)
""")

# Tabla de balances contables
cursor.execute("""
CREATE TABLE IF NOT EXISTS balances_contables (
id INTEGER PRIMARY KEY AUTOINCREMENT,
periodo VARCHAR(20) NOT NULL,
fecha_balance DATE NOT NULL,
codigo_cuenta VARCHAR(20) NOT NULL,
saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
debe_periodo DECIMAL(15,2) DEFAULT 0.00,
haber_periodo DECIMAL(15,2) DEFAULT 0.00,
saldo_final DECIMAL(15,2) DEFAULT 0.00,
usuario_generacion VARCHAR(100),
fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

self.db_connection.commit()
logger.info("Tablas de contabilidad creadas/verificadas exitosamente")

except Exception as e:
        logger.error(f"Error creando tablas de contabilidad: {e}")
if self.db_connection:
                self.db_connection.rollback()
raise

def crear_asiento_contable(self, fecha_asiento, tipo_asiento, concepto, monto, 
cuenta_debe, cuenta_haber, referencia=""):
        """
Crea un nuevo asiento contable con validación.

Args:
        fecha_asiento: Fecha del asiento
tipo_asiento: Tipo de asiento
concepto: Concepto/descripción
monto: Monto del asiento
cuenta_debe: Cuenta que se debita
cuenta_haber: Cuenta que se acredita
referencia: Referencia opcional

Returns:
        ID del asiento creado o None si hay error
"""
try:
        if not self.db_connection:
                logger.error("No hay conexión de base de datos")
return None

# Sanitizar datos de entrada
concepto_limpio = sanitize_string(concepto) if SANITIZER_AVAILABLE else concepto.strip()
tipo_asiento_limpio = sanitize_string(tipo_asiento) if SANITIZER_AVAILABLE else tipo_asiento.strip()
referencia_limpia = sanitize_string(referencia) if SANITIZER_AVAILABLE else referencia.strip()

# Validar monto
monto_decimal = Decimal(str(monto))
if monto_decimal <= 0:
                logger.error("El monto debe ser mayor a cero")
return None

# Obtener próximo número de asiento
numero_asiento = self._obtener_proximo_numero_asiento()

cursor = self.db_connection.cursor()

# Insertar asiento principal
cursor.execute("""
INSERT INTO libro_contable 
(numero_asiento, fecha_asiento, tipo_asiento, concepto, referencia,
debe, haber, saldo, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
numero_asiento,
fecha_asiento,
tipo_asiento_limpio,
concepto_limpio,
referencia_limpia,
float(monto_decimal),
float(monto_decimal),
0.00,  # El saldo se calcula después
self.usuario_actual,
datetime.now()
))

asiento_id = cursor.lastrowid

# Insertar detalle del asiento (debe)
cursor.execute("""
INSERT INTO asientos_detalle 
(asiento_id, codigo_cuenta, debe, haber, concepto_detalle)
VALUES (?, ?, ?, ?, ?)
""", (
asiento_id,
cuenta_debe,
float(monto_decimal),
0.00,
f"DEBE - {concepto_limpio}"
))

# Insertar detalle del asiento (haber)
cursor.execute("""
INSERT INTO asientos_detalle 
(asiento_id, codigo_cuenta, debe, haber, concepto_detalle)
VALUES (?, ?, ?, ?, ?)
""", (
asiento_id,
cuenta_haber,
0.00,
float(monto_decimal),
f"HABER - {concepto_limpio}"
))

self.db_connection.commit()

logger.info(f"Asiento contable creado: ID {asiento_id}, Número {numero_asiento}")
return asiento_id

except Exception as e:
        logger.error(f"Error creando asiento contable: {e}")
if self.db_connection:
                self.db_connection.rollback()
return None

def obtener_asientos_contables(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
Obtiene asientos contables con filtros opcionales.

Args:
        filtros: Diccionario con filtros de búsqueda

Returns:
        Lista de asientos contables
"""
try:
        if not self.db_connection:
                return []

filtros = filtros or {}

# Base query
query = """
SELECT 
id, numero_asiento, fecha_asiento, tipo_asiento, concepto,
referencia, debe, haber, saldo, estado, usuario_creacion,
fecha_creacion, fecha_modificacion
FROM libro_contable
WHERE 1=1
"""

params = []

# Aplicar filtros
if filtros.get('fecha_desde'):
                query += " AND fecha_asiento >= ?"
params.append(filtros['fecha_desde'])

if filtros.get('fecha_hasta'):
                query += " AND fecha_asiento <= ?"
params.append(filtros['fecha_hasta'])

if filtros.get('tipo_asiento'):
                query += " AND tipo_asiento = ?"
params.append(filtros['tipo_asiento'])

if filtros.get('concepto'):
                query += " AND concepto LIKE ?"
params.append(f"%{filtros['concepto']}%")

# Ordenar por fecha descendente
query += " ORDER BY fecha_asiento DESC, numero_asiento DESC"

# Aplicar límite
limite = min(filtros.get('limite', 1000), 5000)  # Máximo 5000
query += f" LIMIT {limite}"

cursor = self.db_connection.cursor()
cursor.execute(query, params)

asientos = []
for row in cursor.fetchall():
                asientos.append({
'id': row[0],
'numero_asiento': row[1],
'fecha_asiento': row[2],
'tipo_asiento': row[3],
'concepto': row[4],
'referencia': row[5],
'debe': row[6],
'haber': row[7],
'saldo': row[8],
'estado': row[9],
'usuario_creacion': row[10],
'fecha_creacion': row[11],
'fecha_modificacion': row[12]
})

logger.debug(f"Obtenidos {len(asientos)} asientos contables")
return asientos

except Exception as e:
        logger.error(f"Error obteniendo asientos contables: {e}")
return []

def obtener_estadisticas_financieras(self) -> Dict[str, Any]:
        """
Obtiene estadísticas financieras básicas.

Returns:
        Diccionario con estadísticas financieras
"""
try:
        if not self.db_connection:
                return {}

cursor = self.db_connection.cursor()

# Total de asientos
cursor.execute("SELECT COUNT(*) FROM libro_contable WHERE estado = 'ACTIVO'")
total_asientos = cursor.fetchone()[0] or 0

# Total debe y haber
cursor.execute("""
SELECT SUM(debe), SUM(haber) 
FROM libro_contable 
WHERE estado = 'ACTIVO'
""")
result = cursor.fetchone()
total_debe = float(result[0] or 0)
total_haber = float(result[1] or 0)

# Asientos por tipo
cursor.execute("""
SELECT tipo_asiento, COUNT(*), SUM(debe)
FROM libro_contable 
WHERE estado = 'ACTIVO'
GROUP BY tipo_asiento
ORDER BY COUNT(*) DESC
""")

asientos_por_tipo = []
for row in cursor.fetchall():
                asientos_por_tipo.append({
'tipo': row[0],
'cantidad': row[1],
'total_debe': float(row[2] or 0)
})

# Asientos recientes
cursor.execute("""
SELECT COUNT(*)
FROM libro_contable 
WHERE fecha_asiento >= date('now', '-30 days')
AND estado = 'ACTIVO'
""")
asientos_ultimo_mes = cursor.fetchone()[0] or 0

estadisticas = {
'total_asientos': total_asientos,
'total_debe': total_debe,
'total_haber': total_haber,
'diferencia': total_debe - total_haber,
'asientos_ultimo_mes': asientos_ultimo_mes,
'asientos_por_tipo': asientos_por_tipo,
'fecha_actualizacion': datetime.now().isoformat()
}

logger.debug("Estadísticas financieras calculadas")
return estadisticas

except Exception as e:
        logger.error(f"Error obteniendo estadísticas financieras: {e}")
return {}

def generar_balance_general(self, parametros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
Genera balance general para un período específico.

Args:
        parametros: Parámetros del balance (fecha_inicio, fecha_fin, etc.)

Returns:
        Datos del balance general
"""
try:
        if not self.db_connection:
                return None

fecha_inicio = parametros.get('fecha_inicio')
fecha_fin = parametros.get('fecha_fin')

if not fecha_inicio or not fecha_fin:
                logger.error("Fechas de inicio y fin son requeridas para el balance")
return None

cursor = self.db_connection.cursor()

# Obtener datos del balance
cursor.execute("""
SELECT 
ad.codigo_cuenta,
pc.nombre_cuenta,
pc.tipo_cuenta,
SUM(ad.debe) as total_debe,
SUM(ad.haber) as total_haber,
(SUM(ad.debe) - SUM(ad.haber)) as saldo
FROM asientos_detalle ad
INNER JOIN libro_contable lc ON ad.asiento_id = lc.id
INNER JOIN plan_cuentas pc ON ad.codigo_cuenta = pc.codigo_cuenta
WHERE lc.fecha_asiento BETWEEN ? AND ?
AND lc.estado = 'ACTIVO'
GROUP BY ad.codigo_cuenta, pc.nombre_cuenta, pc.tipo_cuenta
ORDER BY ad.codigo_cuenta
""", (fecha_inicio, fecha_fin))

cuentas = []
total_activos = 0
total_pasivos = 0
total_patrimonio = 0

for row in cursor.fetchall():
                cuenta = {
'codigo': row[0],
'nombre': row[1],
'tipo': row[2],
'debe': float(row[3] or 0),
'haber': float(row[4] or 0),
'saldo': float(row[5] or 0)
}
cuentas.append(cuenta)

# Clasificar por tipo de cuenta
if row[2] in ['ACTIVO', 'ACTIVO_CORRIENTE', 'ACTIVO_FIJO']:
                total_activos += cuenta['saldo']
elif row[2] in ['PASIVO', 'PASIVO_CORRIENTE', 'PASIVO_LARGO_PLAZO']:
                total_pasivos += abs(cuenta['saldo'])
elif row[2] in ['PATRIMONIO', 'CAPITAL']:
                total_patrimonio += abs(cuenta['saldo'])

balance = {
'periodo': f"{fecha_inicio} - {fecha_fin}",
'fecha_generacion': datetime.now().isoformat(),
'cuentas': cuentas,
'totales': {
'activos': total_activos,
'pasivos': total_pasivos,
'patrimonio': total_patrimonio,
'equilibrio': abs(total_activos - (total_pasivos + total_patrimonio)) < 0.01
},
'usuario_generacion': self.usuario_actual
}

logger.info(f"Balance general generado para período {fecha_inicio} - {fecha_fin}")
return balance

except Exception as e:
        logger.error(f"Error generando balance general: {e}")
return None

def generar_estado_resultados(self, parametros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
Genera estado de resultados para un período.

Args:
        parametros: Parámetros del estado (fecha_inicio, fecha_fin)

Returns:
        Datos del estado de resultados
"""
try:
        # Implementación básica del estado de resultados
logger.info("Generando estado de resultados")

estado = {
'periodo': f"{parametros.get('fecha_inicio')} - {parametros.get('fecha_fin')}",
'fecha_generacion': datetime.now().isoformat(),
'ingresos': 0,
'egresos': 0,
'utilidad_neta': 0,
'detalles': []
}

return estado

except Exception as e:
        logger.error(f"Error generando estado de resultados: {e}")
return None

def generar_libro_diario(self, parametros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
Genera libro diario para un período.

Args:
        parametros: Parámetros del libro (fecha_inicio, fecha_fin)

Returns:
        Datos del libro diario
"""
try:
        fecha_inicio = parametros.get('fecha_inicio')
fecha_fin = parametros.get('fecha_fin')

# Obtener asientos del período
filtros = {
'fecha_desde': fecha_inicio,
'fecha_hasta': fecha_fin,
'limite': 10000
}

asientos = self.obtener_asientos_contables(filtros)

libro = {
'periodo': f"{fecha_inicio} - {fecha_fin}",
'fecha_generacion': datetime.now().isoformat(),
'total_asientos': len(asientos),
'asientos': asientos,
'usuario_generacion': self.usuario_actual
}

logger.info(f"Libro diario generado con {len(asientos)} asientos")
return libro

except Exception as e:
        logger.error(f"Error generando libro diario: {e}")
return None

def _obtener_proximo_numero_asiento(self) -> int:
        """Obtiene el próximo número de asiento disponible."""
try:
        cursor = self.db_connection.cursor()
cursor.execute("SELECT MAX(numero_asiento) FROM libro_contable")
result = cursor.fetchone()
max_numero = result[0] if result and result[0] else 0
return max_numero + 1

except Exception as e:
        logger.error(f"Error obteniendo próximo número de asiento: {e}")
return 1

def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla para prevenir SQL injection."""
# Solo permitir caracteres alfanuméricos y guiones bajos
import re
if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        return table_name
else:
        raise ValueError(f"Nombre de tabla inválido: {table_name}")