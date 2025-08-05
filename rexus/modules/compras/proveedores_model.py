"""
Modelo de Proveedores

Maneja la gestión de proveedores para el módulo de compras.
"""

from typing import Any, Dict, List, Optional
from rexus.utils.security import SecurityUtils


class ProveedoresModel:
    """Modelo para gestionar proveedores."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de proveedores.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_proveedores = "proveedores"
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        """Verifica que la tabla de proveedores exista."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_proveedores,),
            )
            if cursor.fetchone():
                print(f"[PROVEEDORES] Tabla '{self.tabla_proveedores}' verificada.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_proveedores}' no existe.")

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error verificando tabla: {e}")

    def crear_proveedor(
        self,
        nombre: str,
        razon_social: str = "",
        ruc: str = "",
        telefono: str = "",
        email: str = "",
        direccion: str = "",
        contacto_principal: str = "",
        categoria: str = "",
        estado: str = "ACTIVO",
        observaciones: str = "",
        usuario_creacion: str = ""
    ) -> bool:
        """
        Crea un nuevo proveedor.

        Args:
            nombre: Nombre comercial del proveedor
            razon_social: Razón social oficial
            ruc: RUC/CUIT del proveedor
            telefono: Teléfono de contacto
            email: Email de contacto
            direccion: Dirección física
            contacto_principal: Nombre del contacto principal
            categoria: Categoría de productos que provee
            estado: Estado del proveedor (ACTIVO, INACTIVO)
            observaciones: Observaciones adicionales
            usuario_creacion: Usuario que crea el proveedor

        Returns:
            bool: True si se creó exitosamente
        """
        if not self.db_connection:
            print("[WARN PROVEEDORES] Sin conexión BD")
            return False

        try:
            # Sanitizar todos los datos de entrada
            nombre_sanitizado = SecurityUtils.sanitize_sql_input(nombre)
            razon_social_sanitizada = SecurityUtils.sanitize_sql_input(razon_social)
            ruc_sanitizado = SecurityUtils.sanitize_sql_input(ruc)
            telefono_sanitizado = SecurityUtils.sanitize_sql_input(telefono)
            email_sanitizado = SecurityUtils.sanitize_sql_input(email)
            direccion_sanitizada = SecurityUtils.sanitize_sql_input(direccion)
            contacto_sanitizado = SecurityUtils.sanitize_sql_input(contacto_principal)
            categoria_sanitizada = SecurityUtils.sanitize_sql_input(categoria)
            observaciones_sanitizadas = SecurityUtils.sanitize_sql_input(observaciones)
            usuario_sanitizado = SecurityUtils.sanitize_sql_input(usuario_creacion)

            # Validar email si se proporciona
            if email and not SecurityUtils.validate_email(email):
                print("[ERROR PROVEEDORES] Email inválido")
                return False

            cursor = self.db_connection.cursor()

            # Verificar si ya existe un proveedor con el mismo nombre o RUC
            cursor.execute(
                "SELECT id FROM proveedores WHERE nombre = ? OR (ruc = ? AND ruc != '')",
                (nombre_sanitizado, ruc_sanitizado)
            )
            if cursor.fetchone():
                print(f"[ERROR PROVEEDORES] Ya existe un proveedor con nombre '{nombre}' o RUC '{ruc}'")
                return False

            sql_insert = """
            INSERT INTO proveedores
            (nombre, razon_social, ruc, telefono, email, direccion, 
             contacto_principal, categoria, estado, observaciones, 
             usuario_creacion, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """

            cursor.execute(
                sql_insert,
                (
                    nombre_sanitizado,
                    razon_social_sanitizada,
                    ruc_sanitizado,
                    telefono_sanitizado,
                    email_sanitizado,
                    direccion_sanitizada,
                    contacto_sanitizado,
                    categoria_sanitizada,
                    estado,
                    observaciones_sanitizadas,
                    usuario_sanitizado,
                ),
            )

            self.db_connection.commit()
            print(f"[PROVEEDORES] Proveedor creado: {nombre}")
            return True

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error creando proveedor: {e}")
            return False

    def obtener_todos_proveedores(self) -> List[Dict]:
        """
        Obtiene todos los proveedores.

        Returns:
            List[Dict]: Lista de proveedores
        """
        if not self.db_connection:
            return self._get_proveedores_demo()

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT 
                p.id, p.nombre, p.razon_social, p.ruc, p.telefono, p.email,
                p.direccion, p.contacto_principal, p.categoria, p.estado,
                p.observaciones, p.usuario_creacion, p.fecha_creacion,
                p.fecha_actualizacion,
                COUNT(c.id) as total_ordenes,
                ISNULL(SUM(
                    ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                            FROM detalle_compras dc
                            WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                ), 0) as monto_total_compras
            FROM proveedores p
            LEFT JOIN compras c ON p.nombre = c.proveedor
            GROUP BY p.id, p.nombre, p.razon_social, p.ruc, p.telefono, p.email,
                     p.direccion, p.contacto_principal, p.categoria, p.estado,
                     p.observaciones, p.usuario_creacion, p.fecha_creacion,
                     p.fecha_actualizacion
            ORDER BY p.nombre ASC
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            proveedores = []

            for row in rows:
                proveedor = dict(zip(columns, row))
                proveedores.append(proveedor)

            print(f"[PROVEEDORES] Obtenidos {len(proveedores)} proveedores")
            return proveedores

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error obteniendo proveedores: {e}")
            return self._get_proveedores_demo()

    def obtener_proveedor_por_id(self, proveedor_id: int) -> Optional[Dict]:
        """
        Obtiene un proveedor por su ID.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Dict o None: Datos del proveedor
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT 
                id, nombre, razon_social, ruc, telefono, email, direccion,
                contacto_principal, categoria, estado, observaciones,
                usuario_creacion, fecha_creacion, fecha_actualizacion
            FROM proveedores
            WHERE id = ?
            """

            cursor.execute(sql_select, (proveedor_id,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                proveedor = dict(zip(columns, row))
                return proveedor

            return None

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error obteniendo proveedor {proveedor_id}: {e}")
            return None

    def actualizar_proveedor(
        self,
        proveedor_id: int,
        nombre: str = None,
        razon_social: str = None,
        ruc: str = None,
        telefono: str = None,
        email: str = None,
        direccion: str = None,
        contacto_principal: str = None,
        categoria: str = None,
        estado: str = None,
        observaciones: str = None
    ) -> bool:
        """
        Actualiza un proveedor existente.

        Args:
            proveedor_id: ID del proveedor
            Resto de parámetros opcionales para actualizar

        Returns:
            bool: True si se actualizó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Construir query dinámico solo con campos a actualizar
            updates = []
            params = []

            if nombre is not None:
                updates.append("nombre = ?")
                params.append(SecurityUtils.sanitize_sql_input(nombre))

            if razon_social is not None:
                updates.append("razon_social = ?")
                params.append(SecurityUtils.sanitize_sql_input(razon_social))

            if ruc is not None:
                updates.append("ruc = ?")
                params.append(SecurityUtils.sanitize_sql_input(ruc))

            if telefono is not None:
                updates.append("telefono = ?")
                params.append(SecurityUtils.sanitize_sql_input(telefono))

            if email is not None:
                # Validar email si se proporciona
                if email and not SecurityUtils.validate_email(email):
                    print("[ERROR PROVEEDORES] Email inválido en actualización")
                    return False
                updates.append("email = ?")
                params.append(SecurityUtils.sanitize_sql_input(email))

            if direccion is not None:
                updates.append("direccion = ?")
                params.append(SecurityUtils.sanitize_sql_input(direccion))

            if contacto_principal is not None:
                updates.append("contacto_principal = ?")
                params.append(SecurityUtils.sanitize_sql_input(contacto_principal))

            if categoria is not None:
                updates.append("categoria = ?")
                params.append(SecurityUtils.sanitize_sql_input(categoria))

            if estado is not None:
                updates.append("estado = ?")
                params.append(estado)

            if observaciones is not None:
                updates.append("observaciones = ?")
                params.append(SecurityUtils.sanitize_sql_input(observaciones))

            if not updates:
                return False

            updates.append("fecha_actualizacion = GETDATE()")
            params.append(proveedor_id)

            sql_update = f"""
            UPDATE proveedores 
            SET {', '.join(updates)}
            WHERE id = ?
            """

            cursor.execute(sql_update, params)
            self.db_connection.commit()

            print(f"[PROVEEDORES] Proveedor {proveedor_id} actualizado")
            return True

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error actualizando proveedor: {e}")
            return False

    def buscar_proveedores(
        self,
        nombre: str = "",
        categoria: str = "",
        estado: str = "",
        ruc: str = ""
    ) -> List[Dict]:
        """
        Busca proveedores con filtros.

        Args:
            nombre: Filtrar por nombre
            categoria: Filtrar por categoría
            estado: Filtrar por estado
            ruc: Filtrar por RUC

        Returns:
            List[Dict]: Lista de proveedores filtrados
        """
        if not self.db_connection:
            return self._get_proveedores_demo()

        try:
            cursor = self.db_connection.cursor()

            # Construir query con filtros
            conditions = []
            params = []

            if nombre:
                conditions.append("nombre LIKE ?")
                params.append(f"%{SecurityUtils.sanitize_sql_input(nombre)}%")

            if categoria:
                conditions.append("categoria LIKE ?")
                params.append(f"%{SecurityUtils.sanitize_sql_input(categoria)}%")

            if estado:
                conditions.append("estado = ?")
                params.append(estado)

            if ruc:
                conditions.append("ruc LIKE ?")
                params.append(f"%{SecurityUtils.sanitize_sql_input(ruc)}%")

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            sql_select = f"""
            SELECT 
                id, nombre, razon_social, ruc, telefono, email, direccion,
                contacto_principal, categoria, estado, observaciones,
                usuario_creacion, fecha_creacion, fecha_actualizacion
            FROM proveedores
            {where_clause}
            ORDER BY nombre ASC
            """

            cursor.execute(sql_select, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            proveedores = []

            for row in rows:
                proveedor = dict(zip(columns, row))
                proveedores.append(proveedor)

            print(f"[PROVEEDORES] Búsqueda retornó {len(proveedores)} proveedores")
            return proveedores

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error en búsqueda: {e}")
            return []

    def obtener_estadisticas_proveedor(self, proveedor_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas detalladas de un proveedor.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Dict: Estadísticas del proveedor
        """
        if not self.db_connection:
            return self._get_estadisticas_proveedor_demo(proveedor_id)

        try:
            cursor = self.db_connection.cursor()

            # Obtener datos básicos del proveedor
            cursor.execute(
                "SELECT nombre, categoria, estado FROM proveedores WHERE id = ?",
                (proveedor_id,)
            )
            proveedor_row = cursor.fetchone()

            if not proveedor_row:
                return {}

            nombre_proveedor = proveedor_row[0]

            # Estadísticas de compras
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_ordenes,
                    COUNT(CASE WHEN estado = 'PENDIENTE' THEN 1 END) as ordenes_pendientes,
                    COUNT(CASE WHEN estado = 'APROBADA' THEN 1 END) as ordenes_aprobadas,
                    COUNT(CASE WHEN estado = 'RECIBIDA' THEN 1 END) as ordenes_recibidas,
                    COUNT(CASE WHEN estado = 'CANCELADA' THEN 1 END) as ordenes_canceladas
                FROM compras
                WHERE proveedor = ?
            """, (nombre_proveedor,))

            stats_row = cursor.fetchone()

            # Montos totales
            cursor.execute("""
                SELECT 
                    ISNULL(SUM(
                        ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                                FROM detalle_compras dc
                                WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                    ), 0) as monto_total,
                    AVG(
                        ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                                FROM detalle_compras dc
                                WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                    ) as promedio_orden
                FROM compras c
                WHERE c.proveedor = ?
            """, (nombre_proveedor,))

            monto_row = cursor.fetchone()

            # Productos más comprados a este proveedor
            cursor.execute("""
                SELECT TOP 5
                    dc.descripcion,
                    SUM(dc.cantidad) as cantidad_total,
                    AVG(dc.precio_unitario) as precio_promedio
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
                WHERE c.proveedor = ?
                GROUP BY dc.descripcion
                ORDER BY cantidad_total DESC
            """, (nombre_proveedor,))

            productos_top = cursor.fetchall()

            return {
                "proveedor_id": proveedor_id,
                "nombre": nombre_proveedor,
                "categoria": proveedor_row[1],
                "estado": proveedor_row[2],
                "total_ordenes": stats_row[0] if stats_row else 0,
                "ordenes_pendientes": stats_row[1] if stats_row else 0,
                "ordenes_aprobadas": stats_row[2] if stats_row else 0,
                "ordenes_recibidas": stats_row[3] if stats_row else 0,
                "ordenes_canceladas": stats_row[4] if stats_row else 0,
                "monto_total": monto_row[0] if monto_row else 0.0,
                "promedio_orden": monto_row[1] if monto_row else 0.0,
                "productos_top": [
                    {
                        "descripcion": p[0],
                        "cantidad_total": p[1],
                        "precio_promedio": p[2]
                    }
                    for p in productos_top
                ]
            }

        except Exception as e:
            print(f"[ERROR PROVEEDORES] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_proveedor_demo(proveedor_id)

    def obtener_proveedores_activos(self) -> List[Dict]:
        """
        Obtiene solo los proveedores activos.

        Returns:
            List[Dict]: Lista de proveedores activos
        """
        return self.buscar_proveedores(estado="ACTIVO")

    def cambiar_estado_proveedor(self, proveedor_id: int, nuevo_estado: str) -> bool:
        """
        Cambia el estado de un proveedor.

        Args:
            proveedor_id: ID del proveedor
            nuevo_estado: Nuevo estado (ACTIVO, INACTIVO)

        Returns:
            bool: True si se cambió exitosamente
        """
        return self.actualizar_proveedor(proveedor_id, estado=nuevo_estado)

    def _get_proveedores_demo(self) -> List[Dict]:
        """Proveedores demo para testing."""
        return [
            {
                "id": 1,
                "nombre": "Materiales del Sur",
                "razon_social": "Materiales del Sur S.A.",
                "ruc": "20123456789",
                "telefono": "+54 11 4000-1000",
                "email": "ventas@materialesdelsur.com",
                "direccion": "Av. Industrial 1234, Buenos Aires",
                "contacto_principal": "Juan Pérez",
                "categoria": "Materiales de Construcción",
                "estado": "ACTIVO",
                "observaciones": "Proveedor principal de perfiles",
                "total_ordenes": 25,
                "monto_total_compras": 156789.50
            },
            {
                "id": 2,
                "nombre": "Vidrios y Cristales SA",
                "razon_social": "Vidrios y Cristales S.A.",
                "ruc": "20987654321",
                "telefono": "+54 11 4000-2000",
                "email": "pedidos@vidriosycristales.com",
                "direccion": "Calle del Vidrio 567, CABA",
                "contacto_principal": "María González",
                "categoria": "Vidrios y Cristales",
                "estado": "ACTIVO",
                "observaciones": "Especialistas en vidrio templado",
                "total_ordenes": 18,
                "monto_total_compras": 89234.75
            },
            {
                "id": 3,
                "nombre": "Herrajes Industriales",
                "razon_social": "Herrajes Industriales LTDA",
                "ruc": "20456789123",
                "telefono": "+54 11 4000-3000",
                "email": "info@herrajes.com",
                "direccion": "Parque Industrial Norte, Lote 45",
                "contacto_principal": "Carlos Rodriguez",
                "categoria": "Herrajes y Accesorios",
                "estado": "ACTIVO",
                "observaciones": "Herrajes de alta calidad",
                "total_ordenes": 12,
                "monto_total_compras": 45678.25
            }
        ]

    def _get_estadisticas_proveedor_demo(self, proveedor_id: int) -> Dict[str, Any]:
        """Estadísticas demo de proveedor."""
        return {
            "proveedor_id": proveedor_id,
            "nombre": "Materiales del Sur",
            "categoria": "Materiales de Construcción",
            "estado": "ACTIVO",
            "total_ordenes": 25,
            "ordenes_pendientes": 3,
            "ordenes_aprobadas": 5,
            "ordenes_recibidas": 15,
            "ordenes_canceladas": 2,
            "monto_total": 156789.50,
            "promedio_orden": 6271.58,
            "productos_top": [
                {"descripcion": "Perfil Aluminio 20x20", "cantidad_total": 500, "precio_promedio": 12.50},
                {"descripcion": "Perfil Aluminio 30x30", "cantidad_total": 250, "precio_promedio": 18.75},
                {"descripcion": "Perfil Aluminio 40x40", "cantidad_total": 150, "precio_promedio": 25.00}
            ]
        }