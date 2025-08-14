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
from typing import Any, Dict, Tuple

from rexus.core.auth_manager import auth_required
from rexus.utils.xss_protection import XSSProtection

# Configurar logger
logger = logging.getLogger(__name__)

class HerrajesInventarioIntegration:
    """Servicio de integración entre Herrajes e Inventario."""

    def __init__(self, db_connection=None):
        """
        Inicializa el servicio de integración.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection

        # Tablas relacionadas
        self.tabla_herrajes = "herrajes"
        self.tabla_herrajes_inventario = "herrajes_inventario"
        self.tabla_inventario_general = "inventario_perfiles"
        self.tabla_movimientos = "historial"
        self.tabla_reservas = "reserva_materiales"

        if not self.db_connection:
            logger.warning("Sin conexión a BD - funciones limitadas")

    @auth_required
    def sincronizar_stock_herrajes(self) -> Tuple[bool, str, Dict]:
        """
        Sincroniza el stock de herrajes con el inventario general.

        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, estadísticas)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos", {}

        try:
            cursor = self.db_connection.cursor()
            stats = {
                'herrajes_sincronizados': 0,
                'herrajes_creados': 0,
                'herrajes_actualizados': 0,
                'errores': 0
            }

            # Obtener todos los herrajes activos
            cursor.execute("""
                SELECT h.id, h.codigo, h.descripcion, h.categoria, h.precio_unitario,
                       h.stock_actual, h.proveedor, h.unidad_medida, h.estado,
                       hi.stock_actual as stock_inventario, hi.ubicacion
                FROM herrajes h
                LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
                WHERE h.estado = 'ACTIVO'
            """)

            herrajes = cursor.fetchall()

            for herraje in herrajes:
                herraje_id, codigo, descripcion, categoria, precio, stock_herrajes, proveedor, unidad, estado, stock_inventario, ubicacion = herraje

                try:
                    # Verificar si existe en inventario general
                    cursor.execute("""
                        SELECT id, stock_actual, precio_unitario
                        FROM inventario_perfiles
                        WHERE codigo = ? AND categoria LIKE '%HERRAJES%'
                    """, (codigo,))

                    inventario_item = cursor.fetchone()

                    if inventario_item:
                        # Actualizar item existente en inventario general
                        inv_id, stock_inv, precio_inv = inventario_item

                        # Usar el stock más actualizado (de herrajes_inventario si existe)
                        stock_real = stock_inventario if stock_inventario is not None else stock_herrajes

                        cursor.execute("""
                            UPDATE inventario_perfiles
                            SET stock_actual = ?, precio_unitario = ?,
                                proveedor = ?, fecha_actualizacion = GETDATE(),
                                observaciones = 'Sincronizado desde Herrajes'
                            WHERE id = ?
                        """, (stock_real, precio, proveedor, inv_id))

                        stats['herrajes_actualizados'] += 1
                    else:
                        # Crear nuevo item en inventario general
                        cursor.execute("""
                            INSERT INTO inventario_perfiles
                            (codigo, descripcion, categoria, precio_unitario, stock_actual,
                             unidad_medida, proveedor, estado, ubicacion, observaciones)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            descripcion,
                            f"HERRAJES - {categoria}" if categoria else "HERRAJES",
                            precio,
                            stock_inventario if stock_inventario is not None else stock_herrajes,
                            unidad,
                            proveedor,
                            'ACTIVO',
                            ubicacion or 'Almacén Herrajes',
                            'Creado desde módulo Herrajes'
                        ))

                        stats['herrajes_creados'] += 1

                    # Sincronizar stock en herrajes_inventario si no existe
                    if stock_inventario is None:
                        cursor.execute("""
                            INSERT INTO herrajes_inventario (herraje_id, stock_actual, ubicacion)
                            VALUES (?, ?, ?)
                        """,
(herraje_id,
                            stock_herrajes,
                            ubicacion or 'Almacén Principal'))

                    stats['herrajes_sincronizados'] += 1

                except Exception as e:
                    logger.error(f"Error sincronizando herraje {codigo}: {e}")
                    stats['errores'] += 1
                    continue

            self.db_connection.commit()

            mensaje = f"""Sincronización completada:
• Herrajes procesados: {stats['herrajes_sincronizados']}
• Nuevos en inventario: {stats['herrajes_creados']}
• Actualizados: {stats['herrajes_actualizados']}
• Errores: {stats['errores']}"""

            return True, mensaje, stats

        except Exception as e:
            logger.error(f"Error en sincronización: {e}")
            return False, f"Error en sincronización: {str(e)}", {}

    @auth_required
    def transferir_herraje_a_inventario(self, herraje_id: int, cantidad: int,
                                       destino: str = "INVENTARIO_GENERAL") -> Tuple[bool, str]:
        """
        Transfiere herrajes del módulo de herrajes al inventario general.

        Args:
            herraje_id: ID del herraje a transferir
            cantidad: Cantidad a transferir
            destino: Destino de la transferencia

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar herraje y stock disponible
            cursor.execute("""
                SELECT h.codigo, h.descripcion, h.precio_unitario,
                       hi.stock_actual, hi.stock_reservado
                FROM herrajes h
                LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
                WHERE h.id = ? AND h.estado = 'ACTIVO'
            """, (herraje_id,))

            herraje = cursor.fetchone()
            if not herraje:
                return False, "Herraje no encontrado o inactivo"

            codigo, descripcion, precio, stock_actual, stock_reservado = herraje
            stock_disponible = (stock_actual or 0) - (stock_reservado or 0)

            if stock_disponible < cantidad:
                return False, f"Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {cantidad}"

            # Registrar movimiento de salida en herrajes
            cursor.execute("""
                INSERT INTO historial (tabla, operacion, registro_id, usuario,
                                     fecha, datos_anteriores, datos_nuevos, observaciones)
                VALUES ('herrajes_inventario', 'TRANSFERENCIA_OUT', ?,
                        USER_NAME(), GETDATE(), ?, ?, ?)
            """, (
                herraje_id,
                f"Stock: {stock_actual}",
                f"Stock: {stock_actual - cantidad}",
                f"Transferencia de {cantidad} unidades a {destino}"
            ))

            # Actualizar stock en herrajes_inventario
            cursor.execute("""
                UPDATE herrajes_inventario
                SET stock_actual = stock_actual - ?,
                    fecha_ultima_salida = GETDATE()
                WHERE herraje_id = ?
            """, (cantidad, herraje_id))

            # Buscar en inventario general
            cursor.execute("""
                SELECT id, stock_actual
                FROM inventario_perfiles
                WHERE codigo = ?
            """, (codigo,))

            inv_item = cursor.fetchone()

            if inv_item:
                # Actualizar stock en inventario general
                inv_id, stock_inv = inv_item
                cursor.execute("""
                    UPDATE inventario_perfiles
                    SET stock_actual = stock_actual + ?,
                        fecha_actualizacion = GETDATE()
                    WHERE id = ?
                """, (cantidad, inv_id))

                # Registrar movimiento de entrada
                cursor.execute("""
                    INSERT INTO historial (tabla, operacion, registro_id, usuario,
                                         fecha, datos_anteriores, datos_nuevos, observaciones)
                    VALUES ('inventario_perfiles', 'TRANSFERENCIA_IN', ?,
                            USER_NAME(), GETDATE(), ?, ?, ?)
                """, (
                    inv_id,
                    f"Stock: {stock_inv}",
                    f"Stock: {stock_inv + cantidad}",
                    f"Transferencia desde Herrajes: {descripcion}"
                ))

            self.db_connection.commit()
            return True, f"Transferencia exitosa: {cantidad} unidades de {descripcion}"

        except Exception as e:
            logger.error(f"Error en transferencia: {e}")
            return False, f"Error en transferencia: {str(e)}"

    @auth_required
    def crear_reserva_herraje(self, herraje_id: int, obra_id: int,
                             cantidad: int, observaciones: str = "") -> Tuple[bool, str]:
        """
        Crea una reserva de herraje para una obra específica.

        Args:
            herraje_id: ID del herraje
            obra_id: ID de la obra
            cantidad: Cantidad a reservar
            observaciones: Observaciones adicionales

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            # Sanitizar observaciones
            observaciones_limpias = XSSProtection.sanitize_text(observaciones) if observaciones else ""

            cursor = self.db_connection.cursor()

            # Verificar stock disponible
            cursor.execute("""
                SELECT h.codigo, h.descripcion, hi.stock_actual, hi.stock_reservado
                FROM herrajes h
                LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
                WHERE h.id = ? AND h.estado = 'ACTIVO'
            """, (herraje_id,))

            herraje = cursor.fetchone()
            if not herraje:
                return False, "Herraje no encontrado"

            codigo, descripcion, stock_actual, stock_reservado = herraje
            stock_disponible = (stock_actual or 0) - (stock_reservado or 0)

            if stock_disponible < cantidad:
                return False, f"Stock insuficiente para reserva. Disponible: {stock_disponible}"

            # Crear reserva
            cursor.execute("""
                INSERT INTO reserva_materiales
                (obra_id, codigo_material, descripcion, cantidad_reservada,
                 tipo_material, fecha_reserva, estado, observaciones)
                VALUES (?, ?, ?, ?, 'HERRAJES', GETDATE(), 'ACTIVA', ?)
            """,
(obra_id,
                codigo,
                descripcion,
                cantidad,
                observaciones_limpias))

            # Actualizar stock reservado
            cursor.execute("""
                UPDATE herrajes_inventario
                SET stock_reservado = ISNULL(stock_reservado, 0) + ?
                WHERE herraje_id = ?
            """, (cantidad, herraje_id))

            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial (tabla, operacion, registro_id, usuario,
                                     fecha, observaciones)
                VALUES ('herrajes_inventario', 'RESERVA', ?, USER_NAME(),
                        GETDATE(), ?)
            """, (herraje_id, f"Reserva de {cantidad} unidades para obra {obra_id}"))

            self.db_connection.commit()
            return True, f"Reserva creada: {cantidad} unidades de {descripcion}"

        except Exception as e:
            logger.error(f"Error creando reserva: {e}")
            return False, f"Error creando reserva: {str(e)}"

    def obtener_resumen_integracion(self) -> Dict[str, Any]:
        """
        Obtiene resumen del estado de integración entre herrajes e inventario.

        Returns:
            Dict con estadísticas de integración
        """
        if not self.db_connection:
            return {
                "herrajes_total": 0,
                "herrajes_en_inventario": 0,
                "reservas_activas": 0,
                "valor_total_herrajes": 0.0,
                "discrepancias": []
            }

        try:
            cursor = self.db_connection.cursor()
            resumen = {}

            # Total herrajes activos
            cursor.execute("SELECT COUNT(*) FROM herrajes WHERE estado = 'ACTIVO'")
            resumen["herrajes_total"] = cursor.fetchone()[0]

            # Herrajes en inventario general
            cursor.execute("""
                SELECT COUNT(*) FROM inventario_perfiles
                WHERE categoria LIKE '%HERRAJES%'
            """)
            resumen["herrajes_en_inventario"] = cursor.fetchone()[0]

            # Reservas activas
            cursor.execute("""
                SELECT COUNT(*) FROM reserva_materiales
                WHERE tipo_material = 'HERRAJES' AND estado = 'ACTIVA'
            """)
            resumen["reservas_activas"] = cursor.fetchone()[0]

            # Valor total herrajes
            cursor.execute("""
                SELECT SUM(h.precio_unitario * ISNULL(hi.stock_actual, 0))
                FROM herrajes h
                LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
                WHERE h.estado = 'ACTIVO'
            """)
            resultado = cursor.fetchone()[0]
            resumen["valor_total_herrajes"] = float(resultado or 0.0)

            # Discrepancias de stock
            cursor.execute("""
                SELECT h.codigo, h.descripcion, h.stock_actual as stock_herrajes,
                       hi.stock_actual as stock_inventario
                FROM herrajes h
                LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
                WHERE h.estado = 'ACTIVO'
                AND (h.stock_actual != ISNULL(hi.stock_actual, 0))
            """)

            discrepancias = []
            for row in cursor.fetchall():
                discrepancias.append({
                    "codigo": row[0],
                    "descripcion": row[1],
                    "stock_herrajes": row[2],
                    "stock_inventario": row[3] or 0
                })

            resumen["discrepancias"] = discrepancias

            return resumen

        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {
                "error": str(e),
                "herrajes_total": 0,
                "herrajes_en_inventario": 0,
                "reservas_activas": 0,
                "valor_total_herrajes": 0.0,
                "discrepancias": []
            }

    @auth_required
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
            logger.error(f"Error corrigiendo discrepancias: {e}")
            return False, f"Error corrigiendo discrepancias: {str(e)}", 0
