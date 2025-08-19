"""
Modelo de Herrajes - Rexus.app v2.0.0
Versión simplificada y funcional

Maneja la lógica de negocio y acceso a datos para herrajes.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HerrajesModel:
    """Modelo simplificado para gestión de herrajes"""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de herrajes.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_herrajes = "herrajes"
        self.tabla_herrajes_obra = "herrajes_obra"

        # Inicializar SQL Manager para consultas seguras
        from rexus.utils.sql_query_manager import SQLQueryManager
        self.sql_manager = SQLQueryManager()
        
        # Intentar establecer conexión automática si no se proporciona
        if not self.db_connection:
            try:
                from rexus.core.database import get_inventario_connection
                self.db_connection = get_inventario_connection()
                if self.db_connection:
                    logger.info("[HERRAJES] Conexión automática establecida exitosamente")
                else:
                    logger.warning("[ERROR HERRAJES] No se pudo establecer conexión automática")
            except Exception as e:
                logger.error(f"[ERROR HERRAJES] Error en conexión automática: {e}")

        if not self.db_connection:
            print("[ERROR HERRAJES] No hay conexión a la base de datos.")
        else:
            self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan."""
        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla herrajes
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'herrajes'
            """)
            herrajes_exists = cursor.fetchone()[0] > 0

            # Verificar tabla herrajes_obra
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'herrajes_obra'
            """)
            herrajes_obra_exists = cursor.fetchone()[0] > 0

            if herrajes_exists:
                print(f"[HERRAJES] Tabla '{self.tabla_herrajes}' verificada correctamente.")

                # Obtener estructura de la tabla
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'herrajes'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = cursor.fetchall()
                print(f"[HERRAJES] Estructura de tabla '{self.tabla_herrajes}':")
                for col_name, data_type in columns:
                    print(f"  - {col_name}: {data_type}")
            else:
                print(f"[WARNING HERRAJES] Tabla '{self.tabla_herrajes}' no existe.")

            if herrajes_obra_exists:
                print(f"[HERRAJES] Tabla '{self.tabla_herrajes_obra}' verificada correctamente.")
            else:
                print(f"[WARNING HERRAJES] Tabla '{self.tabla_herrajes_obra}' no existe.")

        except Exception as e:
            print(f"[ERROR HERRAJES] Error verificando tablas: {e}")

    def obtener_todos_herrajes(self, filtros=None) -> List[Dict]:
        """
        Obtiene todos los herrajes disponibles.

        Args:
            filtros (dict): Filtros opcionales

        Returns:
            List[Dict]: Lista de herrajes
        """
        if not self.db_connection:
            return self._get_herrajes_demo()

        try:
            cursor = self.db_connection.cursor()

            # Consulta base
            query = "SELECT * FROM herrajes WHERE activo = 1"
            params = []

            # Aplicar filtros
            if filtros:
                if filtros.get("proveedor"):
                    query += " AND proveedor LIKE ?"
                    params.append(f"%{filtros['proveedor']}%")

                if filtros.get("codigo"):
                    query += " AND codigo LIKE ?"
                    params.append(f"%{filtros['codigo']}%")

                if filtros.get("descripcion"):
                    query += " AND (nombre LIKE ? OR descripcion LIKE ?)"
                    params.extend([f"%{filtros['descripcion']}%", f"%{filtros['descripcion']}%"])

            query += " ORDER BY codigo"

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            resultados = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            herrajes_dict = [dict(zip(columns, row)) for row in resultados]

            print(f"OK [HERRAJES] Obtenidos {len(herrajes_dict)} herrajes")
            return herrajes_dict

        except Exception as e:
            logger.error(f"[HERRAJES] Error obteniendo herrajes: {e}")
            return self._get_herrajes_demo()

    def obtener_herrajes(self, filtros=None) -> List[Dict]:
        """Alias conveniente para obtener_todos_herrajes."""
        return self.obtener_todos_herrajes(filtros)

    def obtener_herrajes_por_obra(self, obra_id: int) -> List[Dict]:
        """
        Obtiene herrajes asociados a una obra específica.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de herrajes con cantidades asignadas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT h.*, ho.cantidad_requerida, ho.cantidad_instalada, ho.observaciones
                FROM herrajes h
                INNER JOIN herrajes_obra ho ON h.id = ho.herraje_id
                WHERE ho.obra_id = ?
                ORDER BY h.codigo
            """

            cursor.execute(query, (obra_id,))
            resultados = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            herrajes_obra = [dict(zip(columns, row)) for row in resultados]

            print(f"OK [HERRAJES] Obtenidos {len(herrajes_obra)} herrajes para obra {obra_id}")
            return herrajes_obra

        except Exception as e:
            logger.error(f"[HERRAJES] Error obteniendo herrajes por obra: {e}")
            return []

    def buscar_herrajes(self, termino: str) -> List[Dict]:
        """
        Busca herrajes por término general.

        Args:
            termino (str): Término de búsqueda

        Returns:
            List[Dict]: Lista de herrajes encontrados
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT * FROM herrajes
                WHERE activo = 1
                AND (
                    codigo LIKE ? OR
                    nombre LIKE ? OR
                    descripcion LIKE ? OR
                    proveedor LIKE ?
                )
                ORDER BY codigo
            """

            termino_like = f"%{termino}%"
            cursor.execute(query,
(termino_like,
                termino_like,
                termino_like,
                termino_like))

            resultados = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            herrajes_dict = [dict(zip(columns, row)) for row in resultados]

            print(f"OK [HERRAJES] Busqueda '{termino}': {len(herrajes_dict)} resultados")
            return herrajes_dict

        except Exception as e:
            logger.error(f"[HERRAJES] Error en búsqueda: {e}")
            return []

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas básicas de herrajes.

        Returns:
            Dict: Estadísticas básicas
        """
        if not self.db_connection:
            return {
                "total_herrajes": 0,
                "total_stock": 0,
                "herrajes_bajo_stock": 0,
                "proveedores_activos": 0
            }

        try:
            cursor = self.db_connection.cursor()

            # Total herrajes activos
            cursor.execute("SELECT COUNT(*) FROM herrajes WHERE activo = 1")
            total_herrajes = cursor.fetchone()[0]

            # Stock total
            cursor.execute("SELECT COALESCE(SUM(stock_actual), 0) FROM herrajes WHERE activo = 1")
            total_stock = cursor.fetchone()[0]

            # Herrajes bajo stock
            cursor.execute("SELECT COUNT(*) FROM herrajes WHERE activo = 1 AND stock_actual <= stock_minimo")
            herrajes_bajo_stock = cursor.fetchone()[0]

            # Proveedores activos
            cursor.execute("SELECT COUNT(DISTINCT proveedor) FROM herrajes WHERE activo = 1 AND proveedor IS NOT NULL")
            proveedores_activos = cursor.fetchone()[0]

            stats = {
                "total_herrajes": total_herrajes,
                "total_stock": int(total_stock) if total_stock else 0,
                "herrajes_bajo_stock": herrajes_bajo_stock,
                "proveedores_activos": proveedores_activos
            }

            print("OK [HERRAJES] Estadisticas obtenidas exitosamente")
            return stats

        except Exception as e:
            logger.error(f"[HERRAJES] Error obteniendo estadísticas: {e}")
            return {
                "total_herrajes": 0,
                "total_stock": 0,
                "herrajes_bajo_stock": 0,
                "proveedores_activos": 0
            }

    def _get_herrajes_demo(self) -> List[Dict]:
        """Datos de demostración para desarrollo."""
        return [
            {
                "id": 1,
                "codigo": "H001",
                "nombre": "Bisagra de Puerta",
                "descripcion": "Bisagra estándar para puertas de aluminio",
                "categoria": "Bisagras",
                "proveedor": "MetalTech SA",
                "precio_unitario": 25.50,
                "stock_actual": 150,
                "stock_minimo": 50,
                "unidad_medida": "unidad",
                "activo": True
            },
            {
                "id": 2,
                "codigo": "H002",
                "nombre": "Manija Cromada",
                "descripcion": "Manija cromada para ventanas",
                "categoria": "Manijas",
                "proveedor": "Cromados del Norte",
                "precio_unitario": 18.75,
                "stock_actual": 80,
                "stock_minimo": 30,
                "unidad_medida": "unidad",
                "activo": True
            },
            {
                "id": 3,
                "codigo": "H003",
                "nombre": "Cerradura Multipunto",
                "descripcion": "Sistema de cerradura de alta seguridad",
                "categoria": "Cerraduras",
                "proveedor": "Seguridad Total",
                "precio_unitario": 145.00,
                "stock_actual": 25,
                "stock_minimo": 10,
                "unidad_medida": "unidad",
                "activo": True
            }
        ]

    def crear_herraje(self, data: Dict) -> bool:
        """Crea un nuevo herraje en la base de datos."""
        try:
            if not self.db_connection:
                print("[ERROR HERRAJES] No hay conexión a la base de datos")
                return False

            cursor = self.db_connection.cursor()

            # Query de inserción
            query = """
                INSERT INTO herrajes (
                    codigo, nombre, descripcion, categoria, proveedor,
                    precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                data.get('codigo', ''),
                data.get('nombre', ''),
                data.get('descripcion', ''),
                data.get('categoria', ''),
                data.get('proveedor', ''),
                float(data.get('precio_unitario', 0)),
                int(data.get('stock_actual', 0)),
                int(data.get('stock_minimo', 0)),
                data.get('unidad_medida', 'unidad'),
                bool(data.get('activo', True))
            )

            cursor.execute(query, params)
            self.db_connection.commit()

            print(f"[HERRAJES] Herraje creado: {data.get('codigo')}")
            return True

        except Exception as e:
            print(f"[ERROR HERRAJES] Error creando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def actualizar_herraje(self, codigo: str, data: Dict) -> bool:
        """Actualiza un herraje existente."""
        try:
            if not self.db_connection:
                print("[ERROR HERRAJES] No hay conexión a la base de datos")
                return False

            cursor = self.db_connection.cursor()

            # Query de actualización
            query = """
                UPDATE herrajes SET
                    nombre = ?, descripcion = ?, categoria = ?, proveedor = ?,
                    precio_unitario = ?, stock_actual = ?, stock_minimo = ?,
                    unidad_medida = ?, activo = ?, fecha_actualizacion = GETDATE()
                WHERE codigo = ?
            """

            params = (
                data.get('nombre', ''),
                data.get('descripcion', ''),
                data.get('categoria', ''),
                data.get('proveedor', ''),
                float(data.get('precio_unitario', 0)),
                int(data.get('stock_actual', 0)),
                int(data.get('stock_minimo', 0)),
                data.get('unidad_medida', 'unidad'),
                bool(data.get('activo', True)),
                codigo
            )

            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            self.db_connection.commit()

            if rows_affected > 0:
                print(f"[HERRAJES] Herraje actualizado: {codigo}")
                return True
            else:
                print(f"[ERROR HERRAJES] No se encontró herraje con código: {codigo}")
                return False

        except Exception as e:
            print(f"[ERROR HERRAJES] Error actualizando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def eliminar_herraje(self, codigo: str) -> bool:
        """Elimina un herraje de la base de datos."""
        try:
            if not self.db_connection:
                print("[ERROR HERRAJES] No hay conexión a la base de datos")
                return False

            cursor = self.db_connection.cursor()

            # Verificar si el herraje existe
            cursor.execute("SELECT id FROM herrajes WHERE codigo = ?", (codigo,))
            if not cursor.fetchone():
                print(f"[ERROR HERRAJES] No se encontró herraje con código: {codigo}")
                return False

            # Eliminar registros relacionados primero (si existen)
            cursor.execute("DELETE FROM herrajes_obra WHERE herraje_id = (SELECT id FROM herrajes WHERE codigo = ?)", (codigo,))

            # Eliminar el herraje
            cursor.execute("DELETE FROM herrajes WHERE codigo = ?", (codigo,))
            rows_affected = cursor.rowcount
            self.db_connection.commit()

            if rows_affected > 0:
                print(f"[HERRAJES] Herraje eliminado: {codigo}")
                return True
            else:
                print(f"[ERROR HERRAJES] No se pudo eliminar herraje: {codigo}")
                return False

        except Exception as e:
            print(f"[ERROR HERRAJES] Error eliminando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_herraje_por_codigo(self, codigo: str) -> Optional[Dict]:
        """Obtiene un herraje específico por su código."""
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT codigo, nombre, descripcion, categoria, proveedor,
                       precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
                FROM herrajes
                WHERE codigo = ? AND activo = 1
            """, (codigo,))

            row = cursor.fetchone()
            if row:
                return {
                    "codigo": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "categoria": row[3],
                    "proveedor": row[4],
                    "precio_unitario": float(row[5]) if row[5] else 0.0,
                    "stock_actual": int(row[6]) if row[6] else 0,
                    "stock_minimo": int(row[7]) if row[7] else 0,
                    "unidad_medida": row[8] or "unidad",
                    "activo": bool(row[9])
                }
            return None

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herraje por código: {e}")
            return None

    # === MÉTODOS DE PAGINACIÓN ===

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de herrajes.

        Args:
            offset: Registro inicial
            limit: Cantidad de registros
            filtros: Filtros adicionales

        Returns:
            tuple: (datos, total_registros)
        """
        if not self.db_connection:
            # Fallback con datos demo
            datos_demo = self._get_herrajes_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

        try:
            cursor = self.db_connection.cursor()

            # Query principal con paginación
            query = """
                SELECT codigo, nombre, descripcion, categoria, proveedor,
                       precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
                FROM herrajes
                WHERE activo = 1
            """
            
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('categoria') and filtros['categoria'] not in ['Todos', '📂 Todas las categorías']:
                    # Limpiar el emoji si existe
                    categoria = filtros['categoria']
                    if ' ' in categoria and categoria.startswith('📂'):
                        categoria = categoria.split(' ', 1)[1]
                    query += " AND categoria LIKE ?"
                    params.append(f"%{categoria}%")
                
                if filtros.get('busqueda'):
                    query += " AND (codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            # Query de conteo
            count_query = query.replace(
                "SELECT codigo, nombre, descripcion, categoria, proveedor, precio_unitario, stock_actual, stock_minimo, unidad_medida, activo",
                "SELECT COUNT(*)"
            )
            
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()[0]

            # Query principal con paginación
            query += " ORDER BY codigo OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            params.extend([offset, limit])
            
            cursor.execute(query, params)
            datos = []
            
            for row in cursor.fetchall():
                datos.append({
                    "codigo": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "categoria": row[3],
                    "tipo": row[3],  # Alias para compatibilidad
                    "proveedor": row[4],
                    "precio_unitario": float(row[5]) if row[5] else 0.0,
                    "stock_actual": int(row[6]) if row[6] else 0,
                    "stock": int(row[6]) if row[6] else 0,  # Alias para compatibilidad
                    "stock_minimo": int(row[7]) if row[7] else 0,
                    "unidad_medida": row[8] or "unidad",
                    "activo": bool(row[9])
                })

            return datos, total_registros

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo datos paginados: {e}")
            # Fallback con datos demo en caso de error
            datos_demo = self._get_herrajes_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

    def obtener_total_registros(self, filtros=None):
        """
        Obtiene el total de registros de herrajes.

        Args:
            filtros: Filtros aplicados

        Returns:
            int: Total de registros
        """
        if not self.db_connection:
            return len(self._get_herrajes_demo())

        try:
            cursor = self.db_connection.cursor()
            
            query = "SELECT COUNT(*) FROM herrajes WHERE activo = 1"
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('categoria') and filtros['categoria'] not in ['Todos', '📂 Todas las categorías']:
                    categoria = filtros['categoria']
                    if ' ' in categoria and categoria.startswith('📂'):
                        categoria = categoria.split(' ', 1)[1]
                    query += " AND categoria LIKE ?"
                    params.append(f"%{categoria}%")
                
                if filtros.get('busqueda'):
                    query += " AND (codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo total de registros: {e}")
            return len(self._get_herrajes_demo())

    def _get_herrajes_demo(self):
        """Datos demo para cuando no hay conexión a base de datos."""
        return [
            {
                "codigo": "BIS-001",
                "nombre": "Bisagra Estándar 3\"",
                "categoria": "Bisagras",
                "tipo": "Bisagras",
                "proveedor": "Herrajes del Norte",
                "precio_unitario": 1250.00,
                "stock_actual": 150,
                "stock": 150,
                "activo": True
            },
            {
                "codigo": "CER-001", 
                "nombre": "Cerradura Multipunto",
                "categoria": "Cerraduras",
                "tipo": "Cerraduras",
                "proveedor": "Seguridad Total",
                "precio_unitario": 8500.00,
                "stock_actual": 25,
                "stock": 25,
                "activo": True
            },
            {
                "codigo": "MAN-001",
                "nombre": "Manija Acero Inoxidable",
                "categoria": "Manijas",
                "tipo": "Manijas", 
                "proveedor": "Diseño Moderno",
                "precio_unitario": 3200.00,
                "stock_actual": 75,
                "stock": 75,
                "activo": True
            },
            {
                "codigo": "TOR-001",
                "nombre": "Tornillo Autoperforante 4x40",
                "categoria": "Tornillería",
                "tipo": "Tornillería",
                "proveedor": "Ferretería Central",
                "precio_unitario": 25.00,
                "stock_actual": 0,
                "stock": 0,
                "activo": True
            }
        ]
