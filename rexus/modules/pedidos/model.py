"""
Modelo de Pedidos - Rexus.app v2.0.0

Gestión completa de pedidos con integración a inventario y obras.
Maneja el ciclo completo: creación, aprobación, entrega y facturación.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any


class PedidosModel:
    """Modelo para gestión completa de pedidos."""
    
    # Estados de pedidos
    ESTADOS = {
        'BORRADOR': 'Borrador',
        'PENDIENTE': 'Pendiente de Aprobación', 
        'APROBADO': 'Aprobado',
        'EN_PREPARACION': 'En Preparación',
        'LISTO_ENTREGA': 'Listo para Entrega',
        'EN_TRANSITO': 'En Tránsito',
        'ENTREGADO': 'Entregado',
        'CANCELADO': 'Cancelado',
        'FACTURADO': 'Facturado'
    }
    
    # Tipos de pedido
    TIPOS_PEDIDO = {
        'MATERIAL': 'Material de Construcción',
        'HERRAMIENTA': 'Herramientas',
        'SERVICIO': 'Servicios',
        'VIDRIO': 'Vidrios',
        'HERRAJE': 'Herrajes',
        'MIXTO': 'Mixto'
    }
    
    # Prioridades
    PRIORIDADES = {
        'BAJA': 'Baja',
        'NORMAL': 'Normal', 
        'ALTA': 'Alta',
        'URGENTE': 'Urgente'
    }

    def __init__(self, db_connection=None):
        """Inicializa el modelo de pedidos."""
        self.db_connection = db_connection
        self.create_tables()

    def create_tables(self):
        """Crea las tablas necesarias para pedidos."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla principal de pedidos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos' AND xtype='U')
                CREATE TABLE pedidos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    numero_pedido NVARCHAR(50) UNIQUE NOT NULL,
                    cliente_id INT,
                    obra_id INT,
                    fecha_pedido DATETIME NOT NULL DEFAULT GETDATE(),
                    fecha_entrega_solicitada DATETIME,
                    fecha_entrega_real DATETIME,
                    estado NVARCHAR(50) NOT NULL DEFAULT 'BORRADOR',
                    tipo_pedido NVARCHAR(50) NOT NULL DEFAULT 'MATERIAL',
                    prioridad NVARCHAR(20) NOT NULL DEFAULT 'NORMAL',
                    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
                    descuento DECIMAL(12,2) NOT NULL DEFAULT 0,
                    impuestos DECIMAL(12,2) NOT NULL DEFAULT 0,
                    total DECIMAL(12,2) NOT NULL DEFAULT 0,
                    observaciones NTEXT,
                    direccion_entrega NTEXT,
                    responsable_entrega NVARCHAR(100),
                    telefono_contacto NVARCHAR(50),
                    usuario_creador INT,
                    usuario_aprobador INT,
                    fecha_aprobacion DATETIME,
                    motivo_cancelacion NTEXT,
                    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
                    fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
                    activo BIT NOT NULL DEFAULT 1
                )
            """)
            
            # Tabla de detalle de pedidos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_detalle' AND xtype='U')
                CREATE TABLE pedidos_detalle (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    pedido_id INT NOT NULL,
                    producto_id INT,
                    codigo_producto NVARCHAR(50),
                    descripcion NVARCHAR(255) NOT NULL,
                    categoria NVARCHAR(100),
                    cantidad DECIMAL(10,3) NOT NULL,
                    unidad_medida NVARCHAR(20) NOT NULL DEFAULT 'UND',
                    precio_unitario DECIMAL(12,2) NOT NULL,
                    descuento_item DECIMAL(12,2) NOT NULL DEFAULT 0,
                    subtotal_item DECIMAL(12,2) NOT NULL,
                    observaciones_item NTEXT,
                    cantidad_entregada DECIMAL(10,3) NOT NULL DEFAULT 0,
                    cantidad_pendiente AS (cantidad - cantidad_entregada) PERSISTED,
                    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de historial de estados
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_historial' AND xtype='U')
                CREATE TABLE pedidos_historial (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    pedido_id INT NOT NULL,
                    estado_anterior NVARCHAR(50),
                    estado_nuevo NVARCHAR(50) NOT NULL,
                    fecha_cambio DATETIME NOT NULL DEFAULT GETDATE(),
                    usuario_id INT,
                    observaciones NTEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de entregas
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_entregas' AND xtype='U')
                CREATE TABLE pedidos_entregas (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    pedido_id INT NOT NULL,
                    numero_entrega NVARCHAR(50) NOT NULL,
                    fecha_entrega DATETIME NOT NULL,
                    responsable_entrega NVARCHAR(100),
                    quien_recibe NVARCHAR(100),
                    observaciones NTEXT,
                    total_entregado DECIMAL(12,2) NOT NULL DEFAULT 0,
                    documento_transporte NVARCHAR(100),
                    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
                )
            """)
            
            # Índices para optimización
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_numero ON pedidos(numero_pedido)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_obra ON pedidos(obra_id)")
            
            self.db_connection.commit()
            print("[PEDIDOS] Tablas creadas exitosamente")
            
        except Exception as e:
            print(f"[PEDIDOS] Error creando tablas: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def generar_numero_pedido(self) -> str:
        """Genera un número único de pedido."""
        try:
            año_actual = datetime.now().year
            prefijo = f"PED-{año_actual}-"
            
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTRING(numero_pedido, LEN(?)+1, LEN(numero_pedido)) AS INT))
                    FROM pedidos 
                    WHERE numero_pedido LIKE ?
                """, (prefijo, f"{prefijo}%"))
                
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

    def crear_pedido(self, datos_pedido: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo pedido con sus detalles."""
        if not self.db_connection:
            return None
            
        try:
            cursor = self.db_connection.cursor()
            
            # Generar número de pedido
            numero_pedido = self.generar_numero_pedido()
            
            # Insertar pedido principal
            cursor.execute("""
                INSERT INTO pedidos (
                    numero_pedido, cliente_id, obra_id, fecha_entrega_solicitada,
                    tipo_pedido, prioridad, observaciones, direccion_entrega,
                    responsable_entrega, telefono_contacto, usuario_creador
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_pedido,
                datos_pedido.get('cliente_id'),
                datos_pedido.get('obra_id'),
                datos_pedido.get('fecha_entrega_solicitada'),
                datos_pedido.get('tipo_pedido', 'MATERIAL'),
                datos_pedido.get('prioridad', 'NORMAL'),
                datos_pedido.get('observaciones', ''),
                datos_pedido.get('direccion_entrega', ''),
                datos_pedido.get('responsable_entrega', ''),
                datos_pedido.get('telefono_contacto', ''),
                datos_pedido.get('usuario_creador', 1)
            ))
            
            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]
            
            # Insertar detalles del pedido
            detalles = datos_pedido.get('detalles', [])
            total_pedido = 0
            
            for detalle in detalles:
                cantidad = float(detalle.get('cantidad', 0))
                precio_unitario = float(detalle.get('precio_unitario', 0))
                descuento = float(detalle.get('descuento_item', 0))
                subtotal = (cantidad * precio_unitario) - descuento
                total_pedido += subtotal
                
                cursor.execute("""
                    INSERT INTO pedidos_detalle (
                        pedido_id, producto_id, codigo_producto, descripcion,
                        categoria, cantidad, unidad_medida, precio_unitario,
                        descuento_item, subtotal_item, observaciones_item
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pedido_id,
                    detalle.get('producto_id'),
                    detalle.get('codigo_producto', ''),
                    detalle.get('descripcion', ''),
                    detalle.get('categoria', ''),
                    cantidad,
                    detalle.get('unidad_medida', 'UND'),
                    precio_unitario,
                    descuento,
                    subtotal,
                    detalle.get('observaciones_item', '')
                ))
            
            # Calcular impuestos y actualizar totales
            impuestos = total_pedido * 0.19  # IVA 19%
            descuento_general = float(datos_pedido.get('descuento', 0))
            total_final = total_pedido - descuento_general + impuestos
            
            cursor.execute("""
                UPDATE pedidos 
                SET subtotal = ?, descuento = ?, impuestos = ?, total = ?
                WHERE id = ?
            """, (total_pedido, descuento_general, impuestos, total_final, pedido_id))
            
            # Registrar en historial
            self.registrar_cambio_estado(pedido_id, None, 'BORRADOR', 
                                       datos_pedido.get('usuario_creador', 1))
            
            self.db_connection.commit()
            print(f"[PEDIDOS] Pedido {numero_pedido} creado exitosamente")
            return pedido_id
            
        except Exception as e:
            print(f"[PEDIDOS] Error creando pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def obtener_pedidos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene lista de pedidos con filtros opcionales."""
        if not self.db_connection:
            return []
            
        try:
            cursor = self.db_connection.cursor()
            
            where_clauses = ["p.activo = 1"]
            params = []
            
            if filtros:
                if filtros.get('estado'):
                    where_clauses.append("p.estado = ?")
                    params.append(filtros['estado'])
                    
                if filtros.get('obra_id'):
                    where_clauses.append("p.obra_id = ?")
                    params.append(filtros['obra_id'])
                    
                if filtros.get('fecha_desde'):
                    where_clauses.append("p.fecha_pedido >= ?")
                    params.append(filtros['fecha_desde'])
                    
                if filtros.get('fecha_hasta'):
                    where_clauses.append("p.fecha_pedido <= ?")
                    params.append(filtros['fecha_hasta'])
                    
                if filtros.get('busqueda'):
                    where_clauses.append("""
                        (p.numero_pedido LIKE ? OR 
                         p.observaciones LIKE ? OR
                         p.responsable_entrega LIKE ?)
                    """)
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])
            
            where_sql = " AND ".join(where_clauses)
            
            query = f"""
                SELECT 
                    p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                    p.estado, p.tipo_pedido, p.prioridad, p.total, p.observaciones,
                    p.responsable_entrega, p.obra_id,
                    COUNT(pd.id) as cantidad_items,
                    SUM(pd.cantidad) as total_cantidad,
                    SUM(CASE WHEN pd.cantidad_pendiente > 0 THEN pd.cantidad_pendiente ELSE 0 END) as cantidad_pendiente
                FROM pedidos p
                LEFT JOIN pedidos_detalle pd ON p.id = pd.pedido_id
                WHERE {where_sql}
                GROUP BY p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                         p.estado, p.tipo_pedido, p.prioridad, p.total, p.observaciones,
                         p.responsable_entrega, p.obra_id
                ORDER BY p.fecha_pedido DESC
            """
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            
            pedidos = []
            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedido['fecha_pedido'] = pedido['fecha_pedido'].strftime('%Y-%m-%d %H:%M') if pedido['fecha_pedido'] else ''
                pedido['fecha_entrega_solicitada'] = pedido['fecha_entrega_solicitada'].strftime('%Y-%m-%d') if pedido['fecha_entrega_solicitada'] else ''
                pedido['estado_texto'] = self.ESTADOS.get(pedido['estado'], pedido['estado'])
                pedido['tipo_texto'] = self.TIPOS_PEDIDO.get(pedido['tipo_pedido'], pedido['tipo_pedido'])
                pedido['prioridad_texto'] = self.PRIORIDADES.get(pedido['prioridad'], pedido['prioridad'])
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
            cursor.execute("""
                SELECT * FROM pedidos WHERE id = ? AND activo = 1
            """, (pedido_id,))
            
            pedido_data = cursor.fetchone()
            if not pedido_data:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            pedido = dict(zip(columns, pedido_data))
            
            # Obtener detalles del pedido
            cursor.execute("""
                SELECT * FROM pedidos_detalle WHERE pedido_id = ?
                ORDER BY id
            """, (pedido_id,))
            
            detalle_columns = [desc[0] for desc in cursor.description]
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(detalle_columns, row))
                detalles.append(detalle)
            
            pedido['detalles'] = detalles
            
            # Obtener historial
            cursor.execute("""
                SELECT * FROM pedidos_historial 
                WHERE pedido_id = ?
                ORDER BY fecha_cambio DESC
            """, (pedido_id,))
            
            historial_columns = [desc[0] for desc in cursor.description]
            historial = []
            for row in cursor.fetchall():
                hist = dict(zip(historial_columns, row))
                historial.append(hist)
            
            pedido['historial'] = historial
            
            return pedido
            
        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo pedido {pedido_id}: {e}")
            return None

    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str, 
                                usuario_id: int, observaciones: str = "") -> bool:
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
                print(f"[PEDIDOS] Transición inválida: {estado_anterior} -> {nuevo_estado}")
                return False
            
            # Actualizar estado
            cursor.execute("""
                UPDATE pedidos 
                SET estado = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (nuevo_estado, pedido_id))
            
            # Si se aprueba, registrar fecha y usuario
            if nuevo_estado == 'APROBADO':
                cursor.execute("""
                    UPDATE pedidos 
                    SET usuario_aprobador = ?, fecha_aprobacion = GETDATE()
                    WHERE id = ?
                """, (usuario_id, pedido_id))
            
            # Registrar en historial
            self.registrar_cambio_estado(pedido_id, estado_anterior, nuevo_estado, 
                                       usuario_id, observaciones)
            
            self.db_connection.commit()
            return True
            
        except Exception as e:
            print(f"[PEDIDOS] Error actualizando estado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def registrar_cambio_estado(self, pedido_id: int, estado_anterior: Optional[str], 
                              estado_nuevo: str, usuario_id: int, observaciones: str = ""):
        """Registra un cambio de estado en el historial."""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO pedidos_historial (
                    pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones
                ) VALUES (?, ?, ?, ?, ?)
            """, (pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones))
            
        except Exception as e:
            print(f"[PEDIDOS] Error registrando historial: {e}")

    def _validar_transicion_estado(self, estado_actual: str, estado_nuevo: str) -> bool:
        """Valida si la transición de estado es válida."""
        transiciones_validas = {
            'BORRADOR': ['PENDIENTE', 'CANCELADO'],
            'PENDIENTE': ['APROBADO', 'CANCELADO'],
            'APROBADO': ['EN_PREPARACION', 'CANCELADO'],
            'EN_PREPARACION': ['LISTO_ENTREGA', 'CANCELADO'],
            'LISTO_ENTREGA': ['EN_TRANSITO', 'ENTREGADO'],
            'EN_TRANSITO': ['ENTREGADO'],
            'ENTREGADO': ['FACTURADO'],
            'CANCELADO': [],  # Estado final
            'FACTURADO': []   # Estado final
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
            stats['total_pedidos'] = cursor.fetchone()[0]
            
            # Por estado
            cursor.execute("""
                SELECT estado, COUNT(*) 
                FROM pedidos 
                WHERE activo = 1 
                GROUP BY estado
            """)
            stats['por_estado'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Valor total
            cursor.execute("SELECT SUM(total) FROM pedidos WHERE activo = 1 AND estado != 'CANCELADO'")
            result = cursor.fetchone()
            stats['valor_total'] = float(result[0]) if result[0] else 0.0
            
            # Pedidos urgentes
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos 
                WHERE activo = 1 AND prioridad = 'URGENTE' AND estado NOT IN ('ENTREGADO', 'CANCELADO', 'FACTURADO')
            """)
            stats['urgentes_pendientes'] = cursor.fetchone()[0]
            
            # Pedidos del mes
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos 
                WHERE activo = 1 AND MONTH(fecha_pedido) = MONTH(GETDATE()) AND YEAR(fecha_pedido) = YEAR(GETDATE())
            """)
            stats['pedidos_mes'] = cursor.fetchone()[0]
            
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
            
            cursor.execute("""
                SELECT TOP 20
                    id, codigo, descripcion, categoria, stock_actual, precio_unitario
                FROM inventario_perfiles 
                WHERE activo = 1 
                AND (codigo LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)
                ORDER BY descripcion
            """, (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"))
            
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
                'id': 1,
                'numero_pedido': 'PED-2025-00001',
                'fecha_pedido': '2025-01-15 10:30',
                'fecha_entrega_solicitada': '2025-01-20',
                'estado': 'PENDIENTE',
                'estado_texto': 'Pendiente de Aprobación',
                'tipo_pedido': 'MATERIAL',
                'tipo_texto': 'Material de Construcción',
                'prioridad': 'NORMAL',
                'prioridad_texto': 'Normal',
                'total': 1250.50,
                'responsable_entrega': 'Juan Pérez',
                'obra_id': 1,
                'cantidad_items': 5,
                'total_cantidad': 25.0,
                'cantidad_pendiente': 25.0
            },
            {
                'id': 2,
                'numero_pedido': 'PED-2025-00002',
                'fecha_pedido': '2025-01-14 15:45',
                'fecha_entrega_solicitada': '2025-01-18',
                'estado': 'APROBADO',
                'estado_texto': 'Aprobado',
                'tipo_pedido': 'HERRAJE',
                'tipo_texto': 'Herrajes',
                'prioridad': 'ALTA',
                'prioridad_texto': 'Alta',
                'total': 850.75,
                'responsable_entrega': 'María González',
                'obra_id': 2,
                'cantidad_items': 3,
                'total_cantidad': 15.0,
                'cantidad_pendiente': 0.0
            }
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo cuando no hay conexión a BD."""
        return {
            'total_pedidos': 25,
            'por_estado': {
                'BORRADOR': 2,
                'PENDIENTE': 5,
                'APROBADO': 8,
                'EN_PREPARACION': 3,
                'ENTREGADO': 6,
                'CANCELADO': 1
            },
            'valor_total': 45750.25,
            'urgentes_pendientes': 3,
            'pedidos_mes': 15
        }