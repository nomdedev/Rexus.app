"""
Modelo de Compras - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de compras.
Incluye gestión de órdenes, proveedores y seguimiento de gastos.
"""

import datetime
import json
import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar utilidades de sanitización
try:
    from ...utils.data_sanitizer import sanitize_string, validate_input
    SANITIZER_AVAILABLE = True
except ImportError:
    logger.warning("Sanitizador no disponible, usando métodos básicos")
    SANITIZER_AVAILABLE = False
    
    def sanitize_string(s):
        return str(s).replace("'", "''").replace(";", "") if s else ""
    
    def validate_input(s, input_type="string"):
        return bool(s and len(str(s)) < 1000)


class ComprasModel:
    """Modelo para gestionar el sistema de compras."""
    
    def __init__(self, db_connection=None):
        """
        Inicializar modelo de compras.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("ComprasModel inicializado")
    
    def crear_tablas(self):
        """Crea las tablas necesarias para el módulo de compras."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            
            # Tabla de proveedores
            create_proveedores_table = """
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    contacto TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    ruc TEXT,
                    categoria TEXT DEFAULT 'GENERAL',
                    activo BOOLEAN DEFAULT 1,
                    limite_credito DECIMAL(15,2) DEFAULT 0.00,
                    plazo_pago INTEGER DEFAULT 30,
                    descuento_habitual DECIMAL(5,2) DEFAULT 0.00,
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            # Tabla de órdenes de compra
            create_ordenes_table = """
                CREATE TABLE IF NOT EXISTS ordenes_compra (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_orden TEXT UNIQUE NOT NULL,
                    proveedor_id INTEGER NOT NULL,
                    fecha_orden DATE NOT NULL,
                    fecha_entrega DATE,
                    estado TEXT DEFAULT 'BORRADOR',
                    subtotal DECIMAL(15,2) DEFAULT 0.00,
                    descuento DECIMAL(15,2) DEFAULT 0.00,
                    impuestos DECIMAL(15,2) DEFAULT 0.00,
                    total DECIMAL(15,2) DEFAULT 0.00,
                    observaciones TEXT,
                    usuario_creador TEXT,
                    usuario_aprobador TEXT,
                    fecha_aprobacion DATETIME,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
                )
            """
            
            # Tabla de detalles de órdenes
            create_detalles_table = """
                CREATE TABLE IF NOT EXISTS ordenes_compra_detalles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orden_id INTEGER NOT NULL,
                    producto_id INTEGER,
                    codigo_producto TEXT,
                    descripcion TEXT NOT NULL,
                    cantidad DECIMAL(10,3) NOT NULL,
                    precio_unitario DECIMAL(15,2) NOT NULL,
                    descuento_porcentaje DECIMAL(5,2) DEFAULT 0.00,
                    descuento_monto DECIMAL(15,2) DEFAULT 0.00,
                    subtotal DECIMAL(15,2) NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orden_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE
                )
            """
            
            # Tabla de seguimiento de órdenes
            create_seguimiento_table = """
                CREATE TABLE IF NOT EXISTS ordenes_seguimiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orden_id INTEGER NOT NULL,
                    estado_anterior TEXT,
                    estado_nuevo TEXT NOT NULL,
                    comentario TEXT,
                    usuario TEXT,
                    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orden_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE
                )
            """
            
            # Tabla de recepciones
            create_recepciones_table = """
                CREATE TABLE IF NOT EXISTS recepciones_compra (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orden_id INTEGER NOT NULL,
                    numero_recepcion TEXT UNIQUE NOT NULL,
                    fecha_recepcion DATE NOT NULL,
                    usuario_receptor TEXT,
                    estado TEXT DEFAULT 'PARCIAL',
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orden_id) REFERENCES ordenes_compra(id)
                )
            """
            
            # Ejecutar creación de tablas
            cursor.execute(create_proveedores_table)
            cursor.execute(create_ordenes_table)
            cursor.execute(create_detalles_table)
            cursor.execute(create_seguimiento_table)
            cursor.execute(create_recepciones_table)
            
            # Crear índices para optimizar consultas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ordenes_proveedor ON ordenes_compra(proveedor_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes_compra(fecha_orden)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes_compra(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_detalles_orden ON ordenes_compra_detalles(orden_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_seguimiento_orden ON ordenes_seguimiento(orden_id)")
            
            self.db_connection.commit()
            
            logger.debug("Tablas de compras creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tablas de compras: {e}")
            return False
    
    # MÉTODOS DE PROVEEDORES
    
    def crear_proveedor(self, datos_proveedor: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo proveedor.
        
        Args:
            datos_proveedor: Datos del proveedor
            
        Returns:
            ID del proveedor creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None
            
            # Sanitizar datos
            nombre = sanitize_string(datos_proveedor.get('nombre', ''))
            contacto = sanitize_string(datos_proveedor.get('contacto', ''))
            codigo = sanitize_string(datos_proveedor.get('codigo', ''))
            
            if not nombre or not contacto:
                logger.error("Nombre y contacto son requeridos")
                return None
            
            cursor = self.db_connection.cursor()
            
            # Generar código si no se proporciona
            if not codigo:
                cursor.execute("SELECT COUNT(*) FROM proveedores")
                count = cursor.fetchone()[0] + 1
                codigo = f"PROV{count:04d}"
            
            cursor.execute("""
                INSERT INTO proveedores 
                (codigo, nombre, contacto, telefono, email, direccion, ruc, 
                 categoria, limite_credito, plazo_pago, descuento_habitual, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo,
                nombre,
                contacto,
                datos_proveedor.get('telefono', ''),
                datos_proveedor.get('email', ''),
                datos_proveedor.get('direccion', ''),
                datos_proveedor.get('ruc', ''),
                datos_proveedor.get('categoria', 'GENERAL'),
                Decimal(str(datos_proveedor.get('limite_credito', 0))),
                int(datos_proveedor.get('plazo_pago', 30)),
                Decimal(str(datos_proveedor.get('descuento_habitual', 0))),
                datos_proveedor.get('observaciones', '')
            ))
            
            self.db_connection.commit()
            proveedor_id = cursor.lastrowid
            
            logger.info(f"Proveedor {nombre} creado con ID {proveedor_id}")
            return proveedor_id
            
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            return None
    
    def obtener_todos_proveedores(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proveedores.
        
        Returns:
            Lista de proveedores
        """
        try:
            if not self.db_connection:
                return self._obtener_proveedores_demo()
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, codigo, nombre, contacto, telefono, email, direccion,
                       ruc, categoria, activo, limite_credito, plazo_pago,
                       descuento_habitual, observaciones, fecha_creacion
                FROM proveedores 
                ORDER BY nombre
            """)
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'contacto': row[3],
                    'telefono': row[4],
                    'email': row[5],
                    'direccion': row[6],
                    'ruc': row[7],
                    'categoria': row[8],
                    'activo': bool(row[9]),
                    'limite_credito': float(row[10]) if row[10] else 0.0,
                    'plazo_pago': row[11],
                    'descuento_habitual': float(row[12]) if row[12] else 0.0,
                    'observaciones': row[13],
                    'fecha_creacion': row[14]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            return self._obtener_proveedores_demo()
    
    def obtener_proveedores_filtrados(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtiene proveedores aplicando filtros.
        
        Args:
            filtros: Filtros a aplicar
            
        Returns:
            Lista de proveedores filtrados
        """
        try:
            if not self.db_connection:
                return self._obtener_proveedores_demo()
            
            cursor = self.db_connection.cursor()
            
            query = """
                SELECT id, codigo, nombre, contacto, telefono, email, direccion,
                       ruc, categoria, activo, limite_credito, plazo_pago,
                       descuento_habitual, observaciones, fecha_creacion
                FROM proveedores 
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros
            if filtros.get('nombre'):
                query += " AND nombre LIKE ?"
                params.append(f"%{sanitize_string(filtros['nombre'])}%")
            
            if filtros.get('categoria'):
                query += " AND categoria = ?"
                params.append(sanitize_string(filtros['categoria']))
            
            if filtros.get('activo') is not None:
                query += " AND activo = ?"
                params.append(filtros['activo'])
            
            query += " ORDER BY nombre"
            
            cursor.execute(query, params)
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'contacto': row[3],
                    'telefono': row[4],
                    'email': row[5],
                    'direccion': row[6],
                    'ruc': row[7],
                    'categoria': row[8],
                    'activo': bool(row[9]),
                    'limite_credito': float(row[10]) if row[10] else 0.0,
                    'plazo_pago': row[11],
                    'descuento_habitual': float(row[12]) if row[12] else 0.0,
                    'observaciones': row[13],
                    'fecha_creacion': row[14]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores filtrados: {e}")
            return []
    
    # MÉTODOS DE ÓRDENES DE COMPRA
    
    def crear_orden_compra(self, datos_orden: Dict[str, Any]) -> Optional[int]:
        """
        Crea una nueva orden de compra.
        
        Args:
            datos_orden: Datos de la orden
            
        Returns:
            ID de la orden creada o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None
            
            cursor = self.db_connection.cursor()
            
            # Generar número de orden
            cursor.execute("SELECT COUNT(*) FROM ordenes_compra")
            count = cursor.fetchone()[0] + 1
            numero_orden = f"OC{count:06d}"
            
            # Calcular totales
            detalles = datos_orden.get('detalles', [])
            subtotal = Decimal('0.00')
            
            for detalle in detalles:
                cantidad = Decimal(str(detalle.get('cantidad', 0)))
                precio = Decimal(str(detalle.get('precio_unitario', 0)))
                descuento = Decimal(str(detalle.get('descuento_monto', 0)))
                subtotal += (cantidad * precio) - descuento
            
            descuento_orden = Decimal(str(datos_orden.get('descuento', 0)))
            impuestos = Decimal(str(datos_orden.get('impuestos', 0)))
            total = subtotal - descuento_orden + impuestos
            
            # Crear orden
            cursor.execute("""
                INSERT INTO ordenes_compra 
                (numero_orden, proveedor_id, fecha_orden, fecha_entrega, estado,
                 subtotal, descuento, impuestos, total, observaciones, usuario_creador)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_orden,
                datos_orden.get('proveedor_id'),
                datos_orden.get('fecha_orden'),
                datos_orden.get('fecha_entrega'),
                'BORRADOR',
                subtotal,
                descuento_orden,
                impuestos,
                total,
                datos_orden.get('observaciones', ''),
                datos_orden.get('usuario_creador', 'SISTEMA')
            ))
            
            orden_id = cursor.lastrowid
            
            # Crear detalles
            for detalle in detalles:
                cantidad = Decimal(str(detalle.get('cantidad', 0)))
                precio = Decimal(str(detalle.get('precio_unitario', 0)))
                descuento_porc = Decimal(str(detalle.get('descuento_porcentaje', 0)))
                descuento_monto = (cantidad * precio * descuento_porc / 100)
                subtotal_detalle = (cantidad * precio) - descuento_monto
                
                cursor.execute("""
                    INSERT INTO ordenes_compra_detalles 
                    (orden_id, producto_id, codigo_producto, descripcion, cantidad,
                     precio_unitario, descuento_porcentaje, descuento_monto, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    orden_id,
                    detalle.get('producto_id'),
                    detalle.get('codigo_producto', ''),
                    sanitize_string(detalle.get('descripcion', '')),
                    cantidad,
                    precio,
                    descuento_porc,
                    descuento_monto,
                    subtotal_detalle
                ))
            
            # Registrar en seguimiento
            cursor.execute("""
                INSERT INTO ordenes_seguimiento 
                (orden_id, estado_nuevo, comentario, usuario)
                VALUES (?, ?, ?, ?)
            """, (orden_id, 'BORRADOR', 'Orden creada', datos_orden.get('usuario_creador', 'SISTEMA')))
            
            self.db_connection.commit()
            
            logger.info(f"Orden de compra {numero_orden} creada con ID {orden_id}")
            return orden_id
            
        except Exception as e:
            logger.error(f"Error creando orden de compra: {e}")
            return None
    
    def obtener_todas_ordenes(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las órdenes de compra.
        
        Returns:
            Lista de órdenes
        """
        try:
            if not self.db_connection:
                return self._obtener_ordenes_demo()
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT o.id, o.numero_orden, o.proveedor_id, p.nombre as proveedor_nombre,
                       o.fecha_orden, o.fecha_entrega, o.estado, o.subtotal, o.descuento,
                       o.impuestos, o.total, o.observaciones, o.usuario_creador,
                       o.fecha_creacion, o.fecha_aprobacion
                FROM ordenes_compra o
                LEFT JOIN proveedores p ON o.proveedor_id = p.id
                ORDER BY o.fecha_orden DESC, o.id DESC
            """)
            
            ordenes = []
            for row in cursor.fetchall():
                orden = {
                    'id': row[0],
                    'numero_orden': row[1],
                    'proveedor_id': row[2],
                    'proveedor_nombre': row[3],
                    'fecha_orden': row[4],
                    'fecha_entrega': row[5],
                    'estado': row[6],
                    'subtotal': float(row[7]) if row[7] else 0.0,
                    'descuento': float(row[8]) if row[8] else 0.0,
                    'impuestos': float(row[9]) if row[9] else 0.0,
                    'total': float(row[10]) if row[10] else 0.0,
                    'observaciones': row[11],
                    'usuario_creador': row[12],
                    'fecha_creacion': row[13],
                    'fecha_aprobacion': row[14]
                }
                ordenes.append(orden)
            
            return ordenes
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes: {e}")
            return self._obtener_ordenes_demo()
    
    def obtener_ordenes_filtradas(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtiene órdenes aplicando filtros.
        
        Args:
            filtros: Filtros a aplicar
            
        Returns:
            Lista de órdenes filtradas
        """
        try:
            if not self.db_connection:
                return self._obtener_ordenes_demo()
            
            cursor = self.db_connection.cursor()
            
            query = """
                SELECT o.id, o.numero_orden, o.proveedor_id, p.nombre as proveedor_nombre,
                       o.fecha_orden, o.fecha_entrega, o.estado, o.subtotal, o.descuento,
                       o.impuestos, o.total, o.observaciones, o.usuario_creador,
                       o.fecha_creacion, o.fecha_aprobacion
                FROM ordenes_compra o
                LEFT JOIN proveedores p ON o.proveedor_id = p.id
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros
            if filtros.get('estado'):
                query += " AND o.estado = ?"
                params.append(filtros['estado'])
            
            if filtros.get('proveedor_id'):
                query += " AND o.proveedor_id = ?"
                params.append(filtros['proveedor_id'])
            
            if filtros.get('fecha_desde'):
                query += " AND o.fecha_orden >= ?"
                params.append(filtros['fecha_desde'])
            
            if filtros.get('fecha_hasta'):
                query += " AND o.fecha_orden <= ?"
                params.append(filtros['fecha_hasta'])
            
            if filtros.get('numero_orden'):
                query += " AND o.numero_orden LIKE ?"
                params.append(f"%{sanitize_string(filtros['numero_orden'])}%")
            
            query += " ORDER BY o.fecha_orden DESC, o.id DESC"
            
            cursor.execute(query, params)
            
            ordenes = []
            for row in cursor.fetchall():
                orden = {
                    'id': row[0],
                    'numero_orden': row[1],
                    'proveedor_id': row[2],
                    'proveedor_nombre': row[3],
                    'fecha_orden': row[4],
                    'fecha_entrega': row[5],
                    'estado': row[6],
                    'subtotal': float(row[7]) if row[7] else 0.0,
                    'descuento': float(row[8]) if row[8] else 0.0,
                    'impuestos': float(row[9]) if row[9] else 0.0,
                    'total': float(row[10]) if row[10] else 0.0,
                    'observaciones': row[11],
                    'usuario_creador': row[12],
                    'fecha_creacion': row[13],
                    'fecha_aprobacion': row[14]
                }
                ordenes.append(orden)
            
            return ordenes
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes filtradas: {e}")
            return []
    
    def aprobar_orden_compra(self, orden_id: int, usuario_aprobador: str) -> bool:
        """
        Aprueba una orden de compra.
        
        Args:
            orden_id: ID de la orden
            usuario_aprobador: Usuario que aprueba
            
        Returns:
            True si se aprobó exitosamente
        """
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            
            # Actualizar estado de la orden
            cursor.execute("""
                UPDATE ordenes_compra 
                SET estado = 'APROBADA', 
                    usuario_aprobador = ?, 
                    fecha_aprobacion = ?,
                    fecha_modificacion = ?
                WHERE id = ? AND estado = 'BORRADOR'
            """, (usuario_aprobador, datetime.datetime.now(), datetime.datetime.now(), orden_id))
            
            if cursor.rowcount > 0:
                # Registrar en seguimiento
                cursor.execute("""
                    INSERT INTO ordenes_seguimiento 
                    (orden_id, estado_anterior, estado_nuevo, comentario, usuario)
                    VALUES (?, ?, ?, ?, ?)
                """, (orden_id, 'BORRADOR', 'APROBADA', f'Orden aprobada por {usuario_aprobador}', usuario_aprobador))
                
                self.db_connection.commit()
                logger.info(f"Orden {orden_id} aprobada por {usuario_aprobador}")
                return True
            else:
                logger.warning(f"No se pudo aprobar la orden {orden_id} - estado incorrecto")
                return False
            
        except Exception as e:
            logger.error(f"Error aprobando orden: {e}")
            return False
    
    def cancelar_orden_compra(self, orden_id: int, motivo: str) -> bool:
        """
        Cancela una orden de compra.
        
        Args:
            orden_id: ID de la orden
            motivo: Motivo de cancelación
            
        Returns:
            True si se canceló exitosamente
        """
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            
            # Obtener estado actual
            cursor.execute("SELECT estado FROM ordenes_compra WHERE id = ?", (orden_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Orden {orden_id} no encontrada")
                return False
            
            estado_anterior = result[0]
            
            # Actualizar estado
            cursor.execute("""
                UPDATE ordenes_compra 
                SET estado = 'CANCELADA', fecha_modificacion = ?
                WHERE id = ? AND estado IN ('BORRADOR', 'APROBADA')
            """, (datetime.datetime.now(), orden_id))
            
            if cursor.rowcount > 0:
                # Registrar en seguimiento
                cursor.execute("""
                    INSERT INTO ordenes_seguimiento 
                    (orden_id, estado_anterior, estado_nuevo, comentario, usuario)
                    VALUES (?, ?, ?, ?, ?)
                """, (orden_id, estado_anterior, 'CANCELADA', f'Cancelada: {motivo}', 'SISTEMA'))
                
                self.db_connection.commit()
                logger.info(f"Orden {orden_id} cancelada")
                return True
            else:
                logger.warning(f"No se pudo cancelar la orden {orden_id} - estado incorrecto")
                return False
            
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False
    
    def obtener_estadisticas_compras(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del módulo de compras.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            if not self.db_connection:
                return self._obtener_estadisticas_demo()
            
            cursor = self.db_connection.cursor()
            
            # Total de órdenes
            cursor.execute("SELECT COUNT(*) FROM ordenes_compra")
            total_ordenes = cursor.fetchone()[0]
            
            # Órdenes por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as count 
                FROM ordenes_compra 
                GROUP BY estado
            """)
            ordenes_por_estado = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total gastado este mes
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM ordenes_compra 
                WHERE strftime('%Y-%m', fecha_orden) = strftime('%Y-%m', 'now')
                AND estado IN ('APROBADA', 'RECIBIDA')
            """)
            gasto_mes_actual = float(cursor.fetchone()[0])
            
            # Proveedores activos
            cursor.execute("SELECT COUNT(*) FROM proveedores WHERE activo = 1")
            proveedores_activos = cursor.fetchone()[0]
            
            # Órdenes pendientes
            cursor.execute("SELECT COUNT(*) FROM ordenes_compra WHERE estado = 'BORRADOR'")
            ordenes_pendientes = cursor.fetchone()[0]
            
            estadisticas = {
                'total_ordenes': total_ordenes,
                'ordenes_por_estado': ordenes_por_estado,
                'gasto_mes_actual': gasto_mes_actual,
                'proveedores_activos': proveedores_activos,
                'ordenes_pendientes': ordenes_pendientes,
                'ultima_actualizacion': datetime.datetime.now().isoformat()
            }
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de compras: {e}")
            return self._obtener_estadisticas_demo()
    
    # MÉTODOS DEMO
    
    def _obtener_proveedores_demo(self) -> List[Dict[str, Any]]:
        """Datos demo para proveedores."""
        return [
            {
                'id': 1,
                'codigo': 'PROV001',
                'nombre': 'Proveedor Demo 1',
                'contacto': 'Juan Pérez',
                'telefono': '123-456-789',
                'email': 'contacto@proveedor1.com',
                'direccion': 'Av. Demo 123',
                'ruc': '12345678901',
                'categoria': 'MATERIALES',
                'activo': True,
                'limite_credito': 50000.00,
                'plazo_pago': 30,
                'descuento_habitual': 5.00,
                'observaciones': 'Proveedor de materiales de construcción',
                'fecha_creacion': datetime.datetime.now().isoformat()
            }
        ]
    
    def _obtener_ordenes_demo(self) -> List[Dict[str, Any]]:
        """Datos demo para órdenes."""
        return [
            {
                'id': 1,
                'numero_orden': 'OC000001',
                'proveedor_id': 1,
                'proveedor_nombre': 'Proveedor Demo 1',
                'fecha_orden': datetime.date.today().isoformat(),
                'fecha_entrega': None,
                'estado': 'BORRADOR',
                'subtotal': 1000.00,
                'descuento': 50.00,
                'impuestos': 171.00,
                'total': 1121.00,
                'observaciones': 'Orden de prueba',
                'usuario_creador': 'SISTEMA',
                'fecha_creacion': datetime.datetime.now().isoformat(),
                'fecha_aprobacion': None
            }
        ]
    
    def _obtener_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo."""
        return {
            'total_ordenes': 25,
            'ordenes_por_estado': {
                'BORRADOR': 5,
                'APROBADA': 15,
                'RECIBIDA': 3,
                'CANCELADA': 2
            },
            'gasto_mes_actual': 125000.00,
            'proveedores_activos': 8,
            'ordenes_pendientes': 5,
            'ultima_actualizacion': datetime.datetime.now().isoformat()
        }