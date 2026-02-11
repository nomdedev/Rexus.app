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
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configurar logging
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad unificadas
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name
    from rexus.utils.sql_script_loader import sql_script_loader

    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security utilities not fully available: {e}")
    SECURITY_AVAILABLE = False
    unified_sanitizer = None
    validate_table_name = None
    sql_script_loader = None

# Constantes del módulo
DB_ERROR_MESSAGE = "Error de conexión con la base de datos"
TABLA_INVENTARIO = "inventario_perfiles"
TABLA_MOVIMIENTOS = "historial"
TABLA_RESERVAS = "reserva_materiales"

# Estados de stock válidos
ESTADOS_STOCK = {
    'CRITICO': 'Crítico',
    'BAJO': 'Bajo',
    'NORMAL': 'Normal',
    'ALTO': 'Alto',
    'EXCESO': 'Exceso'
}

# Rangos de stock para determinación de estado
RANGOS_STOCK = {
    'critico': 0,
    'bajo': 10,
    'normal': 50,
    'alto': 100
}


class BaseUtilities:
    """Utilidades fundamentales para el módulo de Inventario."""

    def __init__(self, db_connection=None):
        """
        Inicializa las utilidades base con conexión de BD.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.security_available = SECURITY_AVAILABLE

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Inicializar utilidades de seguridad
        if self.security_available:
            self.sanitizer = unified_sanitizer
            logger.info("Utilidades de seguridad cargadas en BaseUtilities")
        else:
            self.sanitizer = None
            logger.warning("Utilidades de seguridad no disponibles en BaseUtilities")

    def validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de la tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            ValueError: Si el nombre no es válido
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Nombre de tabla inválido")

        # Usar validador unificado si está disponible
        if validate_table_name:
            try:
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                logger.error(f"Error de seguridad SQL: {e}")
                raise ValueError(f"Nombre de tabla inseguro: {table_name}")

        # Validación básica como fallback
        table_name = table_name.strip().lower()

        # Lista blanca de tablas válidas para inventario
        tablas_validas = {
            'inventario_perfiles', 'historial', 'reserva_materiales',
            'obras', 'usuarios', 'categorias_inventario'
        }

        if table_name not in tablas_validas:
            raise ValueError(f"Tabla no autorizada: {table_name}")

        return table_name

    def execute_secure_script(self, script_name: str, params: Tuple = None) -> Any:
        """
        Ejecuta un script SQL de forma segura desde archivos externos.

        Args:
            script_name: Nombre del script SQL a ejecutar
            params: Parámetros para el script

        Returns:
            Resultado de la consulta o None en caso de error
        """
        if not self.db_connection:
            logger.error("Sin conexión a base de datos")
            return None

        try:
            # Usar SQL script loader si está disponible
            if sql_script_loader:
                query = sql_script_loader.load_script('inventario', script_name)
                if not query:
                    logger.error(f"Script no encontrado: {script_name}")
                    return None
            else:
                # Fallback: cargar script manualmente
                script_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'sql' / 'inventario' / f'{script_name}.sql'
                if not script_path.exists():
                    logger.error(f"Archivo de script no encontrado: {script_path}")
                    return None

                with open(script_path, 'r', encoding='utf-8') as f:
                    query = f.read()

            cursor = self.db_connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Determinar si es SELECT o modificación
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            else:
                self.db_connection.commit()
                return cursor.rowcount

        except Exception as e:
            logger.error(f"Error ejecutando script {script_name}: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()

    def verificar_tablas(self) -> bool:
        """
        Verifica que las tablas requeridas existan en la base de datos.

        Returns:
            bool: True si todas las tablas existen
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            tablas_requeridas = [
                TABLA_INVENTARIO,
                TABLA_MOVIMIENTOS,
                TABLA_RESERVAS
            ]

            for tabla in tablas_requeridas:
                # Usar query segura para verificar existencia de tabla
                cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?",
                    (tabla,)
                )

                if cursor.fetchone()[0] == 0:
                    logger.error(f"Tabla requerida no encontrada: {tabla}")
                    return False

            logger.info("Todas las tablas requeridas están disponibles")
            return True

        except Exception as e:
            logger.error(f"Error verificando tablas: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()

    def sanitizar_entrada(self,
value: Any,
        tipo: str = 'string',
        max_length: int = None) -> Any:
        """
        Sanitiza entrada de datos usando el sistema unificado.

        Args:
            value: Valor a sanitizar
            tipo: Tipo de sanitización ('string', 'numeric', 'email')
            max_length: Longitud máxima para strings

        Returns:
            Valor sanitizado
        """
        if not self.sanitizer:
            # Fallback básico sin sanitización completa
            if tipo == 'string' and isinstance(value, str):
                return value.strip()[:max_length] if max_length else value.strip()
            return value

        try:
            if tipo == 'string':
                return self.sanitizer.sanitize_string(value, max_length)
            elif tipo == 'numeric':
                return self.sanitizer.sanitize_numeric(value)
            elif tipo == 'email':
                return self.sanitizer.sanitize_email(value)
            else:
                return self.sanitizer.sanitize_string(str(value), max_length)

        except Exception as e:
            logger.warning(f"Error sanitizando entrada: {e}")
            return None

    def determinar_estado_stock(self, cantidad_actual: int, stock_minimo: int = None, stock_maximo: int = None) -> str:
        """
        Determina el estado del stock basado en cantidad y rangos.

        Args:
            cantidad_actual: Cantidad actual en inventario
            stock_minimo: Stock mínimo configurado
            stock_maximo: Stock máximo configurado

        Returns:
            str: Estado del stock
        """
        try:
            cantidad = int(cantidad_actual) if cantidad_actual else 0

            # Usar rangos configurados si están disponibles
            if stock_minimo is not None:
                if cantidad == 0:
                    return 'CRITICO'
                elif cantidad <= stock_minimo:
                    return 'BAJO'
                elif stock_maximo and cantidad >= stock_maximo:
                    return 'EXCESO'
                else:
                    return 'NORMAL'

            # Usar rangos por defecto
            if cantidad <= RANGOS_STOCK['critico']:
                return 'CRITICO'
            elif cantidad <= RANGOS_STOCK['bajo']:
                return 'BAJO'
            elif cantidad <= RANGOS_STOCK['normal']:
                return 'NORMAL'
            elif cantidad <= RANGOS_STOCK['alto']:
                return 'ALTO'
            else:
                return 'EXCESO'

        except (ValueError, TypeError):
            logger.warning(f"Error determinando estado de stock para cantidad: {cantidad_actual}")
            return 'DESCONOCIDO'

    def generar_codigo_qr(self, contenido: str, tamaño: int = 10) -> Optional[bytes]:
        """
        Genera un código QR para el contenido especificado.

        Args:
            contenido: Contenido para el código QR
            tamaño: Tamaño del código QR (1-40)

        Returns:
            bytes: Imagen del código QR en formato PNG o None si hay error
        """
        try:
            # Sanitizar contenido
            contenido_limpio = self.sanitizar_entrada(contenido, 'string', 200)
            if not contenido_limpio:
                return None

            # Crear código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=max(1, min(tamaño, 20)),  # Limitar tamaño
                border=4,
            )

            qr.add_data(contenido_limpio)
            qr.make(fit=True)

            # Generar imagen
            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')

            return img_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error generando código QR: {e}")
            return None

    def generar_codigo_barra(self, codigo: str) -> Optional[str]:
        """
        Genera representación de código de barras (placeholder).

        Args:
            codigo: Código para generar la barra

        Returns:
            str: Representación del código o None si hay error
        """
        try:
            # Sanitizar código
            codigo_limpio = self.sanitizar_entrada(codigo, 'string', 50)
            if not codigo_limpio:
                return None

            # Generar representación simple (en producción usar librería especializada)
            # Por ahora, devolver código formateado
            codigo_formateado = ''.join(c for c in codigo_limpio if c.isalnum())

            if len(codigo_formateado) < 8:
                codigo_formateado = codigo_formateado.ljust(8, '0')

            return codigo_formateado

        except Exception as e:
            logger.error(f"Error generando código de barra: {e}")
            return None

    def convertir_fila_a_dict(self,
row: Tuple,
        columnas: List[str]) -> Dict[str,
        Any]:
        """
        Convierte una fila de base de datos a diccionario.

        Args:
            row: Fila de datos de la base de datos
            columnas: Nombres de las columnas

        Returns:
            Dict con los datos de la fila
        """
        if not row or not columnas:
            return {}

        try:
            return {
                columna: valor
                for columna, valor in zip(columnas, row)
            }
        except Exception as e:
            logger.error(f"Error convirtiendo fila a diccionario: {e}")
            return {}

    def obtener_timestamp_actual(self) -> str:
        """
        Obtiene timestamp actual en formato estándar.

        Returns:
            str: Timestamp formateado
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def validar_conexion_db(self) -> bool:
        """
        Valida que la conexión a la base de datos esté activa.

        Returns:
            bool: True si la conexión es válida
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Conexión de BD inválida: {e}")
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
            logger.error(f"Error creando query de paginación: {e}")
            return base_query  # Fallback a query sin paginación

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
            print(f"Error en logging: {e}")
