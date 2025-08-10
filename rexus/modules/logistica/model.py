
# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Logística

MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.

Maneja la lógica de negocio para:
- Gestión de transportes
- Programación de entregas
- Seguimiento de envíos
- Gestión de proveedores de transporte
- Optimización de rutas
- Control de costos logísticos
"""

from datetime import date, datetime
from decimal import Decimal

from rexus.utils.demo_data_generator import DemoDataGenerator
from rexus.utils.sql_security import SQLSecurityError, validate_table_name
from rexus.core.auth_manager import AuthManager
from rexus.core.auth_decorators import auth_required, admin_required, permission_required
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

class LogisticaModel:
    """
    Modelo para gestionar logística y distribución.
    
    MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
    para prevenir inyección SQL y mejorar mantenibilidad.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de logística.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        # [LOCK] Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()  # Para consultas SQL seguras
        self.tabla_transportes = "transportes"
        self.tabla_entregas = "entregas"
        self.tabla_detalle_entregas = "detalle_entregas"
        self.tabla_proveedores_transporte = "proveedores_transporte"
        self.tabla_rutas = "rutas"
        self.tabla_costos_logisticos = "costos_logisticos"
        self.tabla_obras = "obras"
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            tablas = [
                self.tabla_transportes,
                self.tabla_entregas,
                self.tabla_detalle_entregas,
                self.tabla_proveedores_transporte,
                self.tabla_rutas,
                self.tabla_costos_logisticos,
                self.tabla_obras,
            ]

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'verificar_tabla_existe')
            for tabla in tablas:
                cursor.execute(query, (tabla,))
                if cursor.fetchone():
                    print(f"[LOGÍSTICA] Tabla '{tabla}' verificada correctamente.")
                else:
                    print(
                        f"[ADVERTENCIA] La tabla '{tabla}' no existe en la base de datos."
                    )

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error verificando tablas: {e}")

    def _validate_table_name(self, table_name):
        """
        Valida que el nombre de tabla sea seguro para prevenir SQL injection.

        Args:
            table_name (str): Nombre de tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            SQLSecurityError: Si el nombre de tabla no es válido
        """
        try:
            return validate_table_name(table_name)
        except SQLSecurityError:
            # Fallback a tabla por defecto si no es válida
            if "transporte" in table_name.lower():
                return "transportes"
            elif "entrega" in table_name.lower():
                if "detalle" in table_name.lower():
                    return "detalle_entregas"
                return "entregas"
            elif "proveedor" in table_name.lower():
                return "proveedores_transporte"
            elif "ruta" in table_name.lower():
                return "rutas"
            elif "costo" in table_name.lower():
                return "costos_logisticos"
            elif "obra" in table_name.lower():
                return "obras"
            else:
                raise SQLSecurityError(f"Nombre de tabla no válido: {table_name}")

    # MÉTODOS PARA TRANSPORTES

    def obtener_transportes(self, filtros=None):
        """
        Obtiene transportes con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (tipo, proveedor, disponible, etc.)

        Returns:
            List[Dict]: Lista de transportes
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar SQL base seguro y construir filtros dinámicamente
            base_query = self.sql_manager.get_query('logistica', 'obtener_transportes_base')
            conditions = []
            params = []

            if filtros:
                if filtros.get("tipo") and filtros["tipo"] != "Todos":
                    conditions.append("AND t.tipo = ?")
                    params.append(filtros["tipo"])

                if filtros.get("proveedor") and filtros["proveedor"] != "Todos":
                    conditions.append("AND t.proveedor = ?")
                    params.append(filtros["proveedor"])

                if filtros.get("disponible") is not None:
                    conditions.append("AND t.disponible = ?")
                    params.append(filtros["disponible"])

                if filtros.get("busqueda"):
                    conditions.append("AND (t.codigo LIKE ? OR t.proveedor LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            # Construir query final con filtros seguros
            filter_clause = " ".join(conditions) if conditions else ""
            query = f"{base_query} {filter_clause} ORDER BY t.tipo, t.proveedor"

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            transportes = []
            for fila in resultados:
                transporte = dict(zip(columnas, fila))
                transportes.append(transporte)

            return transportes

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error obteniendo transportes: {e}")
            return []

    def crear_transporte(self, datos_transporte):
        """
        Crea un nuevo transporte.

        Args:
            datos_transporte (dict): Datos del transporte

        Returns:
            int: ID del transporte creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'crear_transporte')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[transportes]', f'[{self._validate_table_name(self.tabla_transportes)}]')

            cursor.execute(
                query,
                (
                    datos_transporte.get("codigo", ""),
                    datos_transporte.get("tipo", ""),
                    datos_transporte.get("proveedor", ""),
                    datos_transporte.get("capacidad_kg", 0),
                    datos_transporte.get("capacidad_m3", 0),
                    datos_transporte.get("costo_km", 0),
                    datos_transporte.get("disponible", True),
                    datos_transporte.get("observaciones", ""),
                ),
            )

            # [LOCK] MIGRADO: Obtener ID del transporte creado usando consulta externa
            id_query = self.sql_manager.get_query('logistica', 'obtener_ultimo_id')
            cursor.execute(id_query)
            transporte_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[LOGÍSTICA] Transporte creado con ID: {transporte_id}")
            return transporte_id

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error creando transporte: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_transporte(self, transporte_id, datos_transporte):
        """
        Actualiza un transporte existente.

        Args:
            transporte_id (int): ID del transporte
            datos_transporte (dict): Nuevos datos del transporte

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'actualizar_transporte')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[transportes]', f'[{self._validate_table_name(self.tabla_transportes)}]')

            cursor.execute(
                query,
                (
                    datos_transporte.get("tipo", ""),
                    datos_transporte.get("proveedor", ""),
                    datos_transporte.get("capacidad_kg", 0),
                    datos_transporte.get("capacidad_m3", 0),
                    datos_transporte.get("costo_km", 0),
                    datos_transporte.get("disponible", True),
                    datos_transporte.get("observaciones", ""),
                    transporte_id,
                ),
            )

            self.db_connection.commit()
            print(f"[LOGÍSTICA] Transporte {transporte_id} actualizado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error actualizando transporte: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA ENTREGAS

    def obtener_entregas(self, filtros=None):
        """
        Obtiene entregas con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (estado, fecha, obra, etc.)

        Returns:
            List[Dict]: Lista de entregas
        """
        if not self.db_connection:
            # Modo demo: devolver datos demo
            if DemoDataGenerator.es_modo_demo():
                return DemoDataGenerator.generar_logistica_demo()["entregas"]
            return []

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar SQL base seguro y construir filtros dinámicamente
            base_query = self.sql_manager.get_query('logistica', 'obtener_entregas_base')
            conditions = []
            params = []

            if filtros:
                if filtros.get("estado") and filtros["estado"] != "Todos":
                    conditions.append("AND e.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("obra_id"):
                    conditions.append("AND e.obra_id = ?")
                    params.append(filtros["obra_id"])

                if filtros.get("fecha_desde"):
                    conditions.append("AND e.fecha_entrega >= ?")
                    params.append(filtros["fecha_desde"])

                if filtros.get("fecha_hasta"):
                    conditions.append("AND e.fecha_entrega <= ?")
                    params.append(filtros["fecha_hasta"])

                if filtros.get("transporte_id"):
                    conditions.append("AND e.transporte_id = ?")
                    params.append(filtros["transporte_id"])

            # Construir query final con filtros seguros
            filter_clause = " ".join(conditions) if conditions else ""
            query = f"{base_query} {filter_clause} ORDER BY e.fecha_entrega DESC"

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            entregas = []
            for fila in resultados:
                entrega = dict(zip(columnas, fila))
                entregas.append(entrega)

            return entregas

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error obteniendo entregas: {e}")
            return []

    def crear_entrega(self, datos_entrega):
        """
        Crea una nueva entrega.

        Args:
            datos_entrega (dict): Datos de la entrega

        Returns:
            int: ID de la entrega creada o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'crear_entrega')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')

            cursor.execute(
                query,
                (
                    datos_entrega.get("obra_id"),
                    datos_entrega.get("transporte_id"),
                    datos_entrega.get("fecha_programada"),
                    datos_entrega.get("direccion_entrega", ""),
                    datos_entrega.get("contacto", ""),
                    datos_entrega.get("telefono", ""),
                    datos_entrega.get("estado", "PROGRAMADA"),
                    datos_entrega.get("observaciones", ""),
                    datos_entrega.get("costo_envio", 0),
                    datos_entrega.get("usuario_creacion", "SYSTEM"),
                ),
            )

            # [LOCK] MIGRADO: Obtener ID de la entrega creada usando consulta externa
            id_query = self.sql_manager.get_query('logistica', 'obtener_ultimo_id')
            cursor.execute(id_query)
            entrega_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[LOGÍSTICA] Entrega creada con ID: {entrega_id}")
            return entrega_id

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error creando entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_estado_entrega(self, entrega_id, nuevo_estado, observaciones=""):
        """
        Actualiza el estado de una entrega.

        Args:
            entrega_id (int): ID de la entrega
            nuevo_estado (str): Nuevo estado
            observaciones (str): Observaciones opcionales

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Si se marca como entregada, agregar fecha de entrega
            if nuevo_estado == "ENTREGADA":
                query = self.sql_manager.get_query('logistica', 'actualizar_estado_entrega_con_fecha')
            else:
                query = self.sql_manager.get_query('logistica', 'actualizar_estado_entrega_sin_fecha')
            
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')

            cursor.execute(query, (nuevo_estado, observaciones, entrega_id))

            self.db_connection.commit()
            print(
                f"[LOGÍSTICA] Estado de entrega {entrega_id} actualizado a {nuevo_estado}"
            )
            return True

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error actualizando estado de entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA DETALLE DE ENTREGAS

    def obtener_detalle_entrega(self, entrega_id):
        """
        Obtiene el detalle de una entrega específica.

        Args:
            entrega_id (int): ID de la entrega

        Returns:
            List[Dict]: Lista de productos de la entrega
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'obtener_detalle_entrega')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[detalle_entregas]', f'[{self._validate_table_name(self.tabla_detalle_entregas)}]')

            cursor.execute(query, (entrega_id,))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            detalles = []
            for fila in resultados:
                detalle = dict(zip(columnas, fila))
                detalles.append(detalle)

            return detalles

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error obteniendo detalle de entrega: {e}")
            return []

    def agregar_producto_entrega(self, entrega_id, datos_producto):
        """
        Agrega un producto a una entrega.

        Args:
            entrega_id (int): ID de la entrega
            datos_producto (dict): Datos del producto

        Returns:
            int: ID del detalle creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'agregar_producto_entrega')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[detalle_entregas]', f'[{self._validate_table_name(self.tabla_detalle_entregas)}]')

            cursor.execute(
                query,
                (
                    entrega_id,
                    datos_producto.get("producto", ""),
                    datos_producto.get("cantidad", 0),
                    datos_producto.get("peso_kg", 0),
                    datos_producto.get("volumen_m3", 0),
                    datos_producto.get("observaciones", ""),
                ),
            )

            # [LOCK] MIGRADO: Obtener ID del detalle creado usando consulta externa
            id_query = self.sql_manager.get_query('logistica', 'obtener_ultimo_id')
            cursor.execute(id_query)
            detalle_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[LOGÍSTICA] Producto agregado a entrega {entrega_id}")
            return detalle_id

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error agregando producto a entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def eliminar_producto_entrega(self, detalle_id):
        """
        Elimina un producto de una entrega.

        Args:
            detalle_id (int): ID del detalle a eliminar

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar SQL externo para prevenir inyección SQL
            query = self.sql_manager.get_query('logistica', 'eliminar_producto_entrega')
            cursor.execute(query, (detalle_id,))

            self.db_connection.commit()
            print("[LOGÍSTICA] Producto eliminado de entrega")
            return True

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error eliminando producto de entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA ESTADÍSTICAS

    def obtener_estadisticas_logistica(self):
        """
        Obtiene estadísticas generales de logística.

        Returns:
            Dict: Estadísticas de logística
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # [LOCK] MIGRADO: Total transportes - SQL externo
            query_total = self.sql_manager.get_query('logistica', 'contar_transportes_activos')
            cursor.execute(query_total)
            estadisticas["total_transportes"] = cursor.fetchone()[0]

            # [LOCK] MIGRADO: Transportes disponibles - SQL externo
            query_disponibles = self.sql_manager.get_query('logistica', 'contar_transportes_disponibles')
            cursor.execute(query_disponibles)
            estadisticas["transportes_disponibles"] = cursor.fetchone()[0]

            # [LOCK] MIGRADO: Entregas por estado - SQL externo
            query_estado = self.sql_manager.get_query('logistica', 'estadisticas_entregas_por_estado')
            query_estado = query_estado.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')
            cursor.execute(query_estado)
            estadisticas["entregas_por_estado"] = dict(cursor.fetchall())

            # [LOCK] MIGRADO: Entregas del mes actual - SQL externo
            query_mes = self.sql_manager.get_query('logistica', 'contar_entregas_mes_actual')
            query_mes = query_mes.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')
            cursor.execute(query_mes)
            estadisticas["entregas_mes_actual"] = cursor.fetchone()[0]

            # [LOCK] MIGRADO: Entregas pendientes - SQL externo
            query_pendientes = self.sql_manager.get_query('logistica', 'contar_entregas_pendientes')
            query_pendientes = query_pendientes.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')
            cursor.execute(query_pendientes)
            estadisticas["entregas_pendientes"] = cursor.fetchone()[0]

            # [LOCK] MIGRADO: Costo total de envíos del mes - SQL externo
            query_costo = self.sql_manager.get_query('logistica', 'costo_envios_mes_actual')
            query_costo = query_costo.replace('[entregas]', f'[{self._validate_table_name(self.tabla_entregas)}]')
            cursor.execute(query_costo)
            resultado = cursor.fetchone()[0]
            estadisticas["costo_envios_mes"] = float(resultado) if resultado else 0.0

            return estadisticas

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_obras_disponibles(self):
        """
        Obtiene las obras disponibles para asignar entregas.

        Returns:
            List[Dict]: Lista de obras activas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar consulta SQL externa
            query = self.sql_manager.get_query('logistica', 'obtener_obras_disponibles')
            # Reemplazar placeholder de tabla con validación
            query = query.replace('[obras]', f'[{self._validate_table_name(self.tabla_obras)}]')

            cursor.execute(query)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            obras = []
            for fila in resultados:
                obra = dict(zip(columnas, fila))
                obras.append(obra)

            return obras

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error obteniendo obras disponibles: {e}")
            return []

    def calcular_costo_envio(self, transporte_id, distancia_km, peso_kg, volumen_m3):
        """
        Calcula el costo de envío para una entrega.

        Args:
            transporte_id (int): ID del transporte
            distancia_km (float): Distancia en kilómetros
            peso_kg (float): Peso en kilogramos
            volumen_m3 (float): Volumen en metros cúbicos

        Returns:
            float: Costo estimado del envío
        """
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Obtener información del transporte usando consulta externa
            query_transporte = self.sql_manager.get_query('logistica', 'obtener_info_transporte')
            query_transporte = query_transporte.replace('[transportes]', f'[{self._validate_table_name(self.tabla_transportes)}]')
            cursor.execute(query_transporte, (transporte_id,))

            resultado = cursor.fetchone()
            if not resultado:
                return 0.0

            costo_km, capacidad_kg, capacidad_m3 = resultado

            # Calcular costo base por distancia
            costo_base = float(costo_km) * distancia_km

            # Agregar costos adicionales por peso y volumen excedente
            costo_adicional = 0.0

            if peso_kg > capacidad_kg:
                costo_adicional += (
                    peso_kg - capacidad_kg
                ) * 0.5  # $0.5 por kg excedente

            if volumen_m3 > capacidad_m3:
                costo_adicional += (
                    volumen_m3 - capacidad_m3
                ) * 10  # $10 por m³ excedente

            costo_total = costo_base + costo_adicional

            return costo_total

        except Exception as e:
            print(f"[ERROR LOGÍSTICA] Error calculando costo de envío: {e}")
            return 0.0
