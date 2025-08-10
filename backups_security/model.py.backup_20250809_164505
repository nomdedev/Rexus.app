from rexus.core.auth_decorators import auth_required, admin_required, permission_required
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
"""
Modelo de Pedidos - Rexus.app v2.0.0

Gestión completa de pedidos con integración a inventario y obras.
Maneja el ciclo completo: creación, aprobación, entrega y facturación.

MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}
            
        def sanitize_string(self, text):
            return str(text) if text else ""
            
        def sanitize_integer(self, value):
            return int(value) if value else 0
            
            @staticmethod
            def sanitize_string(data):
                return str(data).strip() if data else ""
                
            @staticmethod  
            def sanitize_dict(data_dict):
                if not isinstance(data_dict, dict):
                    return {}
                return {k: str(v).strip() if v else "" for k, v in data_dict.items()}

class PedidosModel:
    """Modelo para gestión completa de pedidos."""

    # Estados de pedidos
    ESTADOS = {
        "BORRADOR": "Borrador",
        "PENDIENTE": "Pendiente de Aprobación",
        "APROBADO": "Aprobado",
        "EN_PREPARACION": "En Preparación",
        "LISTO_ENTREGA": "Listo para Entrega",
        "EN_TRANSITO": "En Tránsito",
        "ENTREGADO": "Entregado",
        "CANCELADO": "Cancelado",
        "FACTURADO": "Facturado",
    }

    # Tipos de pedido
    TIPOS_PEDIDO = {
        "MATERIAL": "Material de Construcción",
        "HERRAMIENTA": "Herramientas",
        "SERVICIO": "Servicios",
        "VIDRIO": "Vidrios",
        "HERRAJE": "Herrajes",
        "MIXTO": "Mixto",
    }

    # Prioridades
    PRIORIDADES = {
        "BAJA": "Baja",
        "NORMAL": "Normal",
        "ALTA": "Alta",
        "URGENTE": "Urgente",
    }

    def __init__(self, db_connection=None):
        """Inicializa el modelo de pedidos."""
        self.db_connection = db_connection
        self.sanitizer = unified_sanitizer  # Para validación y sanitización
        self.sql_manager = SQLQueryManager()  # Para consultas SQL seguras
        
        # Validar conexión a BD
        if not self.db_connection:
            raise ValueError("Conexión a base de datos requerida")
            
        # Inicializar tablas
        self._crear_tablas_si_no_existen()
        self.create_tables()

    def _crear_tablas_si_no_existen(self):
        """Crea las tablas necesarias para pedidos usando SQL externo."""
        try:
            cursor = self.db_connection.cursor()
            
            # Ejecutar scripts SQL externos para crear tablas
            queries_tablas = [
                'create_pedidos_table',
                'create_pedidos_detalle_table', 
                'create_pedidos_historial_table',
                'create_pedidos_entregas_table'
            ]
            
            for query_name in queries_tablas:
                sql = self.sql_manager.get_query('pedidos', query_name)
                if sql:
                    cursor.execute(sql)
                    
            self.db_connection.commit()
            print("[PEDIDOS] Tablas verificadas/creadas exitosamente")
            
        except Exception as e:
            print(f"[PEDIDOS] Error creando tablas: {e}")
            if self.db_connection:
                self.db_connection.rollback()
    
    # Método legacy mantenido para compatibilidad
    def create_tables(self):
        """Método legacy - usar _crear_tablas_si_no_existen()."""
        return self._crear_tablas_si_no_existen()

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de tabla a validar

        Returns:
            Nombre de tabla validado

        Raises:
            ValueError: Si el nombre de tabla no es válido
        """
        import re

        # Solo permitir nombres alfanuméricos y underscore
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        # Lista blanca de tablas permitidas para pedidos
        allowed_tables = {
            "pedidos",
            "pedidos_detalle",
            "pedidos_historial",
            "clientes",
            "obras",
            "inventario_productos",
            "proveedores",
        }
        if table_name not in allowed_tables:
            raise ValueError(f"Tabla no permitida: {table_name}")

        return table_name

    def validar_pedido_duplicado(
        self, numero_pedido: str, excluir_id: Optional[int] = None
    ) -> bool:
        """
        Valida si un pedido ya existe (para evitar duplicados).

        Args:
            numero_pedido: Número de pedido a validar
            excluir_id: ID a excluir de la validación (para actualizaciones)

        Returns:
            bool: True si existe duplicado, False si no existe
        """
        try:
            if not self.db_connection:
                return False

            # Sanitizar la entrada
            numero_sanitizado = sanitize_string(
                str(numero_pedido).strip()
            )

            cursor = self.db_connection.cursor()
            try:
                if excluir_id:
                    # Para actualizaciones, excluir el ID actual
                    sql = self.sql_manager.get_query('pedidos', 'validar_pedido_duplicado_edicion')
                    cursor.execute(sql, (numero_sanitizado, excluir_id))
                else:
                    # Para nuevos pedidos  
                    sql = self.sql_manager.get_query('pedidos', 'validar_pedido_duplicado_creacion')
                    cursor.execute(sql, (numero_sanitizado,))

                result = cursor.fetchone()
                existe = result and result[0] > 0

                return bool(existe)

            finally:
                cursor.close()

        except Exception as e:
            print(f"[PEDIDOS] Error validando pedido duplicado: {e}")
            return False  # En caso de error, permitir la operación

    def generar_numero_pedido(self) -> str:
        """Genera un número único de pedido."""
        try:
            año_actual = datetime.now().year
            prefijo = f"PED-{año_actual}-"

            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    """
                    SELECT MAX(CAST(SUBSTRING(numero_pedido, LEN(?)+1, LEN(numero_pedido)) AS INT))
                    FROM pedidos 
                    WHERE numero_pedido LIKE ?
                """,
                    (prefijo, f"{prefijo}%"),
                )

                result = cursor.fetchone()
                ultimo_numero = result[0] if result and result[0] else 0
                nuevo_numero = ultimo_numero + 1

                return f"{prefijo}{nuevo_numero:05d}"
            else:
                # Fallback sin BD
                timestamp = datetime.now().strftime("%m%d%H%M")
                return f"PED-{año_actual}-{timestamp}"

        except Exception as e:
            print(f"[PEDIDOS] Error generando número: {e}")
            # Fallback con UUID
            return f"PED-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

    def validar_cliente_existe(self, cliente_id: int) -> bool:
        """Valida que un cliente existe en el sistema."""
        if not self.db_connection or not cliente_id:
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM clientes WHERE id = ? AND activo = 1",
                (cliente_id,),
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"[ERROR PEDIDOS] Error validando cliente: {e}")
            return False

    def validar_obra_existe(self, obra_id: int) -> bool:
        """Valida que una obra existe en el sistema."""
        if not self.db_connection or not obra_id:
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM obras WHERE id = ? AND activo = 1", (obra_id,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"[ERROR PEDIDOS] Error validando obra: {e}")
            return False

    def crear_pedido(self, datos_pedido: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo pedido con sus detalles con validación y sanitización completas."""
        if not self.db_connection:
            return None

        try:
            # Validar y sanitizar datos de entrada
            if not isinstance(datos_pedido, dict):
                raise ValueError("Los datos del pedido deben ser un diccionario")

            # Sanitizar datos críticos
            datos_sanitizados = self.data_sanitizer.sanitize_dict(datos_pedido)

            # Validar relaciones críticas
            cliente_id = datos_sanitizados.get("cliente_id")
            obra_id = datos_sanitizados.get("obra_id")

            if cliente_id and not self.validar_cliente_existe(cliente_id):
                raise ValueError(
                    f"Cliente con ID {cliente_id} no existe o está inactivo"
                )

            if obra_id and not self.validar_obra_existe(obra_id):
                raise ValueError(f"Obra con ID {obra_id} no existe o está inactiva")

            # Validar campos obligatorios
            tipo_pedido = datos_sanitizados.get("tipo_pedido", "MATERIAL")
            if tipo_pedido not in self.TIPOS_PEDIDO:
                raise ValueError(f"Tipo de pedido inválido: {tipo_pedido}")

            prioridad = datos_sanitizados.get("prioridad", "NORMAL")
            if prioridad not in self.PRIORIDADES:
                raise ValueError(f"Prioridad inválida: {prioridad}")

            cursor = self.db_connection.cursor()

            # Generar número de pedido
            numero_pedido = self.generar_numero_pedido()

            # Verificar que no existe duplicado
            if self.validar_pedido_duplicado(numero_pedido):
                numero_pedido = self.generar_numero_pedido()  # Regenerar si existe

            # Insertar pedido principal con datos sanitizados
            sql = self.sql_manager.get_query('pedidos', 'insertar_pedido_principal')
            cursor.execute(
                sql,
                (
                    numero_pedido,
                    datos_sanitizados.get("cliente_id"),
                    datos_sanitizados.get("obra_id"),
                    datos_sanitizados.get("fecha_entrega_solicitada"),
                    tipo_pedido,
                    prioridad,
                    datos_sanitizados.get("observaciones", ""),
                    datos_sanitizados.get("direccion_entrega", ""),
                    datos_sanitizados.get("responsable_entrega", ""),
                    datos_sanitizados.get("telefono_contacto", ""),
                    datos_sanitizados.get("usuario_creador", 1),
                ),
            )

            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]

            # Insertar detalles del pedido con validación
            detalles = datos_sanitizados.get("detalles", [])
            total_pedido = 0

            tabla_detalle = self._validate_table_name("pedidos_detalle")
            for detalle in detalles:
                # Validar y sanitizar cada detalle
                if not isinstance(detalle, dict):
                    continue

                detalle_sanitizado = self.data_sanitizer.sanitize_dict(detalle)

                cantidad = float(detalle_sanitizado.get("cantidad", 0))
                precio_unitario = float(detalle_sanitizado.get("precio_unitario", 0))
                descuento = float(detalle_sanitizado.get("descuento_item", 0))

                # Validaciones de negocio
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")
                if precio_unitario < 0:
                    raise ValueError("El precio unitario no puede ser negativo")

                subtotal = (cantidad * precio_unitario) - descuento
                total_pedido += subtotal

                cursor.execute(
                    self.sql_manager.get_query('pedidos', 'insertar_detalle_pedido'),
                    (
                        pedido_id,
                        detalle_sanitizado.get("producto_id"),
                        detalle_sanitizado.get("codigo_producto", ""),
                        detalle_sanitizado.get("descripcion", ""),
                        detalle_sanitizado.get("categoria", ""),
                        cantidad,
                        detalle_sanitizado.get("unidad_medida", "UND"),
                        precio_unitario,
                        descuento,
                        subtotal,
                        detalle_sanitizado.get("observaciones_item", ""),
                    ),
                )

            # Calcular impuestos y actualizar totales con datos sanitizados
            impuestos = total_pedido * 0.19  # IVA 19%
            descuento_general = float(datos_sanitizados.get("descuento", 0))
            total_final = total_pedido - descuento_general + impuestos

            cursor.execute(
                self.sql_manager.get_query('pedidos', 'actualizar_totales_pedido'),
                (total_pedido, descuento_general, impuestos, total_final, pedido_id),
            )

            # Registrar en historial
            self.registrar_cambio_estado(
                pedido_id, None, "BORRADOR", datos_sanitizados.get("usuario_creador", 1)
            )

            self.db_connection.commit()
            print(f"[PEDIDOS] Pedido {numero_pedido} creado exitosamente")
            return pedido_id

        except Exception as e:
            print(f"[PEDIDOS] Error creando pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def obtener_pedidos(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene lista de pedidos con filtros opcionales."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            where_clauses = ["p.activo = 1"]
            params = []

            if filtros:
                if filtros.get("estado"):
                    where_clauses.append("p.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("obra_id"):
                    where_clauses.append("p.obra_id = ?")
                    params.append(filtros["obra_id"])

                if filtros.get("fecha_desde"):
                    where_clauses.append("p.fecha_pedido >= ?")
                    params.append(filtros["fecha_desde"])

                if filtros.get("fecha_hasta"):
                    where_clauses.append("p.fecha_pedido <= ?")
                    params.append(filtros["fecha_hasta"])

                if filtros.get("busqueda"):
                    where_clauses.append("""
                        (p.numero_pedido LIKE ? OR 
                         p.observaciones LIKE ? OR
                         p.responsable_entrega LIKE ?)
                    """)
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            where_sql = " AND ".join(where_clauses)

            # Obtener consulta base y agregar filtros de manera segura
            query_base = self.sql_manager.get_query('pedidos', 'obtener_pedidos_base')
            
            # Reemplazar el WHERE base con nuestros filtros dinámicos
            query = query_base.replace(
                "WHERE p.activo = 1",
                f"WHERE {where_sql}"
            )

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]

            pedidos = []
            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedido["fecha_pedido"] = (
                    pedido["fecha_pedido"].strftime("%Y-%m-%d %H:%M")
                    if pedido["fecha_pedido"]
                    else ""
                )
                pedido["fecha_entrega_solicitada"] = (
                    pedido["fecha_entrega_solicitada"].strftime("%Y-%m-%d")
                    if pedido["fecha_entrega_solicitada"]
                    else ""
                )
                pedido["estado_texto"] = self.ESTADOS.get(
                    pedido["estado"], pedido["estado"]
                )
                pedido["tipo_texto"] = self.TIPOS_PEDIDO.get(
                    pedido["tipo_pedido"], pedido["tipo_pedido"]
                )
                pedido["prioridad_texto"] = self.PRIORIDADES.get(
                    pedido["prioridad"], pedido["prioridad"]
                )
                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo pedidos: {e}")
            return self._get_datos_demo()

    def obtener_pedido_por_id(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido específico con todos sus detalles."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Obtener datos del pedido
            cursor.execute(
                """
                SELECT * FROM pedidos WHERE id = ? AND activo = 1
            """,
                (pedido_id,),
            )

            pedido_data = cursor.fetchone()
            if not pedido_data:
                return None

            columns = [desc[0] for desc in cursor.description]
            pedido = dict(zip(columns, pedido_data))

            # Obtener detalles del pedido
            cursor.execute(
                """
                SELECT * FROM pedidos_detalle WHERE pedido_id = ?
                ORDER BY id
            """,
                (pedido_id,),
            )

            detalle_columns = [desc[0] for desc in cursor.description]
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(detalle_columns, row))
                detalles.append(detalle)

            pedido["detalles"] = detalles

            # Obtener historial
            cursor.execute(
                """
                SELECT * FROM pedidos_historial 
                WHERE pedido_id = ?
                ORDER BY fecha_cambio DESC
            """,
                (pedido_id,),
            )

            historial_columns = [desc[0] for desc in cursor.description]
            historial = []
            for row in cursor.fetchall():
                hist = dict(zip(historial_columns, row))
                historial.append(hist)

            pedido["historial"] = historial

            return pedido

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo pedido {pedido_id}: {e}")
            return None

    def actualizar_estado_pedido(
        self,
        pedido_id:int,
        nuevo_estado: str,
        usuario_id: int,
        observaciones: str = "",
    ) -> bool:
        """Actualiza el estado de un pedido."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Obtener estado actual
            cursor.execute("SELECT estado FROM pedidos WHERE id = ?", (pedido_id,))
            result = cursor.fetchone()
            if not result:
                return False

            estado_anterior = result[0]

            # Validar transición de estado
            if not self._validar_transicion_estado(estado_anterior, nuevo_estado):
                print(
                    f"[PEDIDOS] Transición inválida: {estado_anterior} -> {nuevo_estado}"
                )
                return False

            # Actualizar estado
            cursor.execute(
                """
                UPDATE pedidos 
                SET estado = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (nuevo_estado, pedido_id),
            )

            # Si se aprueba, registrar fecha y usuario
            if nuevo_estado == "APROBADO":
                cursor.execute(
                    """
                    UPDATE pedidos 
                    SET usuario_aprobador = ?, fecha_aprobacion = GETDATE()
                    WHERE id = ?
                """,
                    (usuario_id, pedido_id),
                )

            # Registrar en historial
            self.registrar_cambio_estado(
                pedido_id, estado_anterior, nuevo_estado, usuario_id, observaciones
            )

            self.db_connection.commit()
            return True

        except Exception as e:
            print(f"[PEDIDOS] Error actualizando estado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def registrar_cambio_estado(
        self,
        pedido_id: int,
        estado_anterior: Optional[str],
        estado_nuevo: str,
        usuario_id: int,
        observaciones: str = "",
    ):
        """Registra un cambio de estado en el historial."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO pedidos_historial (
                    pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones),
            )

        except Exception as e:
            print(f"[PEDIDOS] Error registrando historial: {e}")

    def _validar_transicion_estado(self, estado_actual: str, estado_nuevo: str) -> bool:
        """Valida si la transición de estado es válida."""
        transiciones_validas = {
            "BORRADOR": ["PENDIENTE", "CANCELADO"],
            "PENDIENTE": ["APROBADO", "CANCELADO"],
            "APROBADO": ["EN_PREPARACION", "CANCELADO"],
            "EN_PREPARACION": ["LISTO_ENTREGA", "CANCELADO"],
            "LISTO_ENTREGA": ["EN_TRANSITO", "ENTREGADO"],
            "EN_TRANSITO": ["ENTREGADO"],
            "ENTREGADO": ["FACTURADO"],
            "CANCELADO": [],  # Estado final
            "FACTURADO": [],  # Estado final
        }

        return estado_nuevo in transiciones_validas.get(estado_actual, [])

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de pedidos."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()

            stats = {}

            # Total pedidos
            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE activo = 1")
            stats["total_pedidos"] = cursor.fetchone()[0]

            # Por estado
            cursor.execute("""
                SELECT estado, COUNT(*) 
                FROM pedidos 
                WHERE activo = 1 
                GROUP BY estado
            """)
            stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Valor total
            cursor.execute(
                "SELECT SUM(total) FROM pedidos WHERE activo = 1 AND estado != 'CANCELADO'"
            )
            result = cursor.fetchone()
            stats["valor_total"] = float(result[0]) if result[0] else 0.0

            # Pedidos urgentes
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos 
                WHERE activo = 1 AND prioridad = 'URGENTE' AND estado NOT IN ('ENTREGADO', 'CANCELADO', 'FACTURADO')
            """)
            stats["urgentes_pendientes"] = cursor.fetchone()[0]

            # Pedidos del mes
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos 
                WHERE activo = 1 AND MONTH(fecha_pedido) = MONTH(GETDATE()) AND YEAR(fecha_pedido) = YEAR(GETDATE())
            """)
            stats["pedidos_mes"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def buscar_productos_inventario(self, busqueda: str) -> List[Dict[str, Any]]:
        """Busca productos en inventario para agregar a pedidos."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            cursor.execute(
                """
                SELECT TOP 20
                    id, codigo, descripcion, categoria, stock_actual, precio_unitario
                FROM inventario_perfiles 
                WHERE activo = 1 
                AND (codigo LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)
                ORDER BY descripcion
            """,
                (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"),
            )

            columns = [desc[0] for desc in cursor.description]
            productos = []

            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                productos.append(producto)

            return productos

        except Exception as e:
            print(f"[PEDIDOS] Error buscando productos: {e}")
            return []

    def _get_datos_demo(self) -> List[Dict[str, Any]]:
        """Datos demo cuando no hay conexión a BD."""
        return [
            {
                "id": 1,
                "numero_pedido": "PED-2025-00001",
                "fecha_pedido": "2025-01-15 10:30",
                "fecha_entrega_solicitada": "2025-01-20",
                "estado": "PENDIENTE",
                "estado_texto": "Pendiente de Aprobación",
                "tipo_pedido": "MATERIAL",
                "tipo_texto": "Material de Construcción",
                "prioridad": "NORMAL",
                "prioridad_texto": "Normal",
                "total": 1250.50,
                "responsable_entrega": "Juan Pérez",
                "obra_id": 1,
                "cantidad_items": 5,
                "total_cantidad": 25.0,
                "cantidad_pendiente": 25.0,
            },
            {
                "id": 2,
                "numero_pedido": "PED-2025-00002",
                "fecha_pedido": "2025-01-14 15:45",
                "fecha_entrega_solicitada": "2025-01-18",
                "estado": "APROBADO",
                "estado_texto": "Aprobado",
                "tipo_pedido": "HERRAJE",
                "tipo_texto": "Herrajes",
                "prioridad": "ALTA",
                "prioridad_texto": "Alta",
                "total": 850.75,
                "responsable_entrega": "María González",
                "obra_id": 2,
                "cantidad_items": 3,
                "total_cantidad": 15.0,
                "cantidad_pendiente": 0.0,
            },
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo cuando no hay conexión a BD."""
        return {
            "total_pedidos": 25,
            "por_estado": {
                "BORRADOR": 2,
                "PENDIENTE": 5,
                "APROBADO": 8,
                "EN_PREPARACION": 3,
                "ENTREGADO": 6,
                "CANCELADO": 1,
            },
            "valor_total": 45750.25,
            "urgentes_pendientes": 3,
            "pedidos_mes": 15,
        }

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de la tabla principal
        
        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filtros: Filtros adicionales a aplicar
            
        Returns:
            tuple: (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0
            
            cursor = self.db_connection.cursor()
            
            # Query base
            base_query = self._get_base_query()
            count_query = self._get_count_query()
            
            # Aplicar filtros si existen
            where_clause = ""
            params = []
            
            if filtros:
                where_conditions = []
                for campo, valor in filtros.items():
                    if valor:
                        where_conditions.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")
                
                if where_conditions:
                    where_clause = " WHERE " + " AND ".join(where_conditions)
            
            # Obtener total de registros
            full_count_query = count_query + where_clause
            cursor.execute(full_count_query, params)
            total_registros = cursor.fetchone()[0]
            
            # Obtener datos paginados
            paginated_query = f"{base_query}{where_clause} ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])
            
            datos = []
            for row in cursor.fetchall():
                datos.append(self._row_to_dict(row, cursor.description))
            
            return datos, total_registros
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo datos paginados: {e}")
            return [], 0
    
    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _, total = self.obtener_datos_paginados(offset=0, limit=1, filtros=filtros)
            return total
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0
    
    def _get_base_query(self):
        """Obtiene la query base para paginación usando SQL externo."""
        # White-list de tablas permitidas para paginación
        tabla_queries = {
            'pedidos': 'get_base_query_pedidos',
            'pedidos_detalle': 'get_base_query_pedidos_detalle',
            'pedidos_historial': 'get_base_query_pedidos_historial'
        }
        
        tabla_principal = getattr(self, 'tabla_principal', 'pedidos')
        if tabla_principal in tabla_queries:
            return self.sql_manager.get_query('pedidos', tabla_queries[tabla_principal])
        else:
            # Fallback seguro para tabla por defecto
            return self.sql_manager.get_query('pedidos', 'get_base_query_pedidos')
    
    def _get_count_query(self):
        """Obtiene la query de conteo usando SQL externo."""
        # White-list de tablas permitidas para conteo
        tabla_queries = {
            'pedidos': 'get_count_query_pedidos',
            'pedidos_detalle': 'get_count_query_pedidos_detalle', 
            'pedidos_historial': 'get_count_query_pedidos_historial'
        }
        
        tabla_principal = getattr(self, 'tabla_principal', 'pedidos')
        if tabla_principal in tabla_queries:
            return self.sql_manager.get_query('pedidos', tabla_queries[tabla_principal])
        else:
            # Fallback seguro para tabla por defecto
            return self.sql_manager.get_query('pedidos', 'get_count_query_pedidos')
    
    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
