import logging
from typing import Any, Dict, Optional
from sqlite3 import IntegrityError

from rexus.utils.sql_script_loader import sql_script_loader
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.core.query_optimizer import cached_query, track_performance, prevent_n_plus_one, paginated
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.app_logger import get_logger

# [LOCK] MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
# para prevenir inyección SQL y mejorar mantenibilidad.

# Configurar logger para el módulo
logger = get_logger(__name__)

# Constantes
DB_ERROR_MESSAGE = "Sin conexión a la base de datos"

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    data_sanitizer = unified_sanitizer
except ImportError:
    # Fallback básico
    class FallbackSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}
        def sanitize_string(self, text):
            return str(text) if text else ""
        def sanitize_integer(self, value, min_val=None, max_val=None):
            try:
                val = int(value)
                if min_val is not None:
                    val = max(val, min_val)
                if max_val is not None:
                    val = min(val, max_val)
                return val
            except (ValueError, TypeError):
                return 0
        def sanitize_sql_input(self, text):
            return str(text).replace("'", "").replace('"', '') if text else ""
        def sanitize_html(self, text):
            return str(text) if text else ""
    data_sanitizer = FallbackSanitizer()

class ObrasModel:
    """
    Modelo para gestionar obras.

    MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
    para prevenir inyección SQL y mejorar mantenibilidad.
    """

    def __init__(self, db_connection=None, data_sanitizer_instance=None):
        self.db_connection = db_connection
        # [LOCK] Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()  # Para consultas SQL seguras
        self.tabla_obras = "obras"
        self.tabla_detalles_obra = "detalles_obra"
        self.sql_loader = sql_script_loader
        # Permitir inyectar un sanitizer para tests, si no usar el global
        self.data_sanitizer = data_sanitizer_instance if data_sanitizer_instance else data_sanitizer
        
        # Intentar establecer conexión automática si no se proporciona
        if not self.db_connection:
            try:
                from rexus.core.database import get_inventario_connection
                self.db_connection = get_inventario_connection()
                if self.db_connection:
                    logger.info("[OBRAS] Conexión automática establecida exitosamente")
                else:
                    logger.warning("[ERROR OBRAS] No se pudo establecer conexión automática")
            except Exception as e:
                logger.error(f"[ERROR OBRAS] Error en conexión automática: {e}")
        
        self._verificar_tablas()

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de la tabla a validar

        Returns:
            str: Nombre de tabla validado
        """
        # Lista blanca de tablas permitidas
        allowed_tables = {'obras', 'detalles_obra'}
        if table_name not in allowed_tables:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            logger.info("[OBRAS] Sin conexión a BD - omitiendo verificación de tablas")
            return

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla de obras con query más compatible
            try:
                # Usar query más compatible que funcione con diferentes motores de BD
                sql_verificar = self.sql_manager.get_query('obras', 'verificar_tabla_sqlite')
                cursor.execute(sql_verificar, (self.tabla_obras,))
                if cursor.fetchone():
                    logger.info(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")
                else:
                    logger.info(f"[INFO] La tabla '{self.tabla_obras}' no existe - se creará cuando sea necesaria.")
            except (AttributeError, RuntimeError, ConnectionError):
                # Si SQLite no funciona, intentar con SQL Server/otros
                try:
                    sql_sql_server = self.sql_manager.get_query('obras', 'verificar_tabla_sql_server')
                    cursor.execute(sql_sql_server, (self.tabla_obras,))
                    if cursor.fetchone():
                        logger.info(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")
                    else:
                        logger.info(f"[INFO] La tabla '{self.tabla_obras}' no existe - se creará cuando sea necesaria.")
                except (AttributeError, RuntimeError, ConnectionError) as e:
                    logger.info(f"[INFO] No se pudo verificar tabla '{self.tabla_obras}' - continuando sin verificación: {e}")

            # Verificar tabla de detalles de obra (opcional)
            try:
                sql_verificar = self.sql_manager.get_query('obras', 'verificar_tabla_sqlite')
                cursor.execute(sql_verificar, (self.tabla_detalles_obra,))
                if cursor.fetchone():
                    logger.info(f"[OBRAS] Tabla '{self.tabla_detalles_obra}' verificada correctamente.")
            except (AttributeError, RuntimeError, ConnectionError) as e:
                try:
                    sql_sql_server = self.sql_manager.get_query('obras', 'verificar_tabla_sql_server')
                    cursor.execute(sql_sql_server, (self.tabla_detalles_obra,))
                    if cursor.fetchone():
                        logger.info(f"[OBRAS] Tabla '{self.tabla_detalles_obra}' verificada correctamente.")
                except (AttributeError, RuntimeError, ConnectionError) as e2:
                    logger.info(f"[ERROR OBRAS] Error en rollback: {e2}")

        except (AttributeError, RuntimeError, ConnectionError) as e:
            # Error en verificación no debe bloquear el módulo
            logger.info(f"[INFO OBRAS] Verificación de tablas omitida: {e}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except (AttributeError, RuntimeError, ConnectionError) as e2:
                    logger.info(f"[ERROR OBRAS] Error en rollback: {e2}")

    def validar_obra_duplicada(
        self, codigo_obra: str, id_obra_actual: Optional[int] = None
    ) -> bool:
        """
        Valida si existe una obra duplicada por código.

        Args:
            codigo_obra: Código de obra a verificar
            id_obra_actual: ID de la obra actual (para edición)

        Returns:
            bool: True si existe duplicado, False si no
        """
        if not self.db_connection or not codigo_obra:
            return False

        try:
            # Sanitizar datos y prevenir SQLi
            codigo_limpio = codigo_obra.strip().upper()
            if self.data_sanitizer:
                codigo_limpio = sanitize_string(codigo_limpio)
                codigo_limpio = self.data_sanitizer.sanitize_sql_input(codigo_limpio)

            cursor = self.db_connection.cursor()

            # Usar SQLQueryManager para consultas seguras
            if id_obra_actual:
                sql_query = self.sql_manager.get_query('obras', 'count_duplicados_codigo_exclude')
                cursor.execute(sql_query, (codigo_limpio, id_obra_actual))
            else:
                sql_query = self.sql_manager.get_query('obras', 'count_duplicados_codigo')
                cursor.execute(sql_query, (codigo_limpio,))

            result = cursor.fetchone()
            if result is None:
                return False
            count = result[0]
            return count > 0

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.info(f"[ERROR OBRAS] Error validando obra duplicada: {e}")
            return False

    def crear_obra(self, datos_obra):
        """Crea una nueva obra en la base de datos."""
        if not self.db_connection:
            return False, DB_ERROR_MESSAGE

        cursor = None
        try:
            # Sanitizar y validar datos
            datos_limpios = self.data_sanitizer.sanitize_dict(datos_obra)

            # Validaciones específicas
            if not datos_limpios.get("codigo"):
                return False, "El código de obra es requerido"
            if not datos_limpios.get("nombre"):
                return False, "El nombre de obra es requerido"
            if not datos_limpios.get("cliente"):
                return False, "El cliente es requerido"

            # Validar presupuesto
            presupuesto_original = datos_limpios.get("presupuesto_total")
            if presupuesto_original is not None and \
                presupuesto_original != "":
                try:
                    presupuesto_limpio = float(presupuesto_original)
                    if presupuesto_limpio < 0:
                        return False, "El presupuesto no puede ser negativo"
                    datos_limpios["presupuesto_total"] = presupuesto_limpio
                except (ValueError, TypeError):
                    return False, "El presupuesto debe ser un número válido"
            else:
                datos_limpios["presupuesto_total"] = 0.0

            # Validar longitud de código
            if len(str(datos_limpios.get("codigo", ""))) > 32:
                return False, "El código de obra es demasiado largo"

            # Validar nombre vacío
            if str(datos_limpios.get("nombre", "")).strip() == "":
                return False, "El nombre de obra no puede estar vacío"

            # Reforzar sanitización de campos críticos (SQLi y XSS)
            for campo in ["codigo", "nombre", "cliente", "descripcion"]:
                if campo in datos_limpios:
                    val = datos_limpios[campo]
                    val = sanitize_string(val, 128)
                    val = self.data_sanitizer.sanitize_sql_input(val)
                    val = self.data_sanitizer.sanitize_html(val)
                    for pattern in ["DROP TABLE", "UNION SELECT", "--", ";", "<script>", "</script>", "<iframe>", "</iframe>"]:
                        val = val.replace(pattern, "")
                    datos_limpios[campo] = val

            cursor = self.db_connection.cursor()

            # Verificar que no existe una obra con el mismo código usando SQLQueryManager
            sql_duplicados = self.sql_manager.get_query('obras', 'count_duplicados_codigo')
            cursor.execute(sql_duplicados, (datos_limpios.get("codigo"),))
            result = cursor.fetchone()
            if result and result[0] > 0:
                return (
                    False,
                    f"Ya existe una obra con el código {datos_limpios.get('codigo')}",
                )

            # Insertar obra usando SQLQueryManager
            sql_insert = self.sql_manager.get_query('obras', 'insert_obra')
            cursor.execute(sql_insert, (
                datos_limpios.get("codigo"),
                datos_limpios.get("nombre"),
                datos_limpios.get("descripcion", ""),
                datos_limpios.get("cliente"),
                datos_limpios.get("direccion", ""),
                datos_limpios.get("telefono_contacto", ""),
                datos_limpios.get("fecha_inicio"),
                datos_limpios.get("fecha_fin_estimada"),
                datos_limpios.get("presupuesto_total", 0),
                datos_limpios.get("estado", "PLANIFICACION"),
                datos_limpios.get("tipo_obra", "RESIDENCIAL"),
                datos_limpios.get("prioridad", "MEDIA"),
                datos_limpios.get("responsable"),
                datos_limpios.get("observaciones", ""),
                datos_limpios.get("usuario_creacion", "SISTEMA")
            ))

            self.db_connection.commit()

            # Log de auditoria
            logger.info(f"Obra creada exitosamente: {datos_limpios.get('codigo')} por usuario {datos_limpios.get('usuario_creacion', 'SISTEMA')}")
            logger.info(f"[OBRAS] Obra creada exitosamente: {datos_limpios.get('codigo')}")

            return True, f"Obra {datos_limpios.get('codigo')} creada exitosamente"

        except (AttributeError, RuntimeError, ConnectionError, ValueError, IntegrityError) as e:
            logger.info(f"[ERROR OBRAS] Error creando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except (AttributeError, RuntimeError) as rollback_error:
                    logger.info(f"[ERROR OBRAS] Error en rollback: {rollback_error}")
            return False, f"Error creando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def obtener_obra_por_codigo(self, codigo: str):
        """
        Obtiene una obra por su código.

        Args:
            codigo: Código de la obra

        Returns:
            dict: Datos de la obra o None si no existe
        """
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            # Usar SQLQueryManager para consulta segura
            sql_obra_codigo = self.sql_manager.get_query('obras', 'select_obra_por_codigo')
            cursor.execute(sql_obra_codigo, (codigo,))

            row = cursor.fetchone()
            if row:
                columnas = [column[0] for column in cursor.description]
                return dict(zip(columnas, row))
            return None

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo obra: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def obtener_obras_filtradas(self, filtros=None, orden_por="fecha_creacion"):
        """
        Obtiene obras filtradas según criterios.

        Args:
            filtros: Diccionario con filtros
            orden_por: Campo por el cual ordenar

        Returns:
            list: Lista de obras
        """
        if not self.db_connection:
            return []

        if filtros is None:
            filtros = {}

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Construir query con filtros
            base_query = self.sql_loader.load_script('obras/select_all_obras')
            where_conditions = []
            params = []

            for campo, valor in filtros.items():
                if valor and valor.strip():
                    # Sanitizar valores de filtro
                    valor_limpio = self.data_sanitizer.sanitize_sql_input(valor)
                    where_conditions.append(f"{campo} LIKE ?")
                    params.append(f"%{valor_limpio}%")


            if where_conditions:
                where_clause = " AND " + " AND ".join(where_conditions)
                if base_query and hasattr(base_query, 'replace'):
                    query = base_query.replace("WHERE activo = 1", f"WHERE activo = 1 {where_clause}")
                else:
                    logger.info("[ERROR OBRAS] base_query es None o no es un string")
                    return []
            else:
                query = base_query

            cursor.execute(query, params)
            return cursor.fetchall()

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo obras filtradas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def obtener_datos_paginados(self,
page=1,
        page_size=50,
        search_term="",
        filters=None):
        """
        Obtiene datos paginados de obras con búsqueda y filtros optimizados.

        Args:
            page: Número de página (1-based)
            page_size: Registros por página
            search_term: Término de búsqueda
            filters: Filtros adicionales

        Returns:
            dict: Resultado con datos, total, página actual, etc.
        """
        if not self.db_connection:
            return {
                'data': [],
                'total_records': 0,
                'current_page': page,
                'page_size': page_size,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False
            }

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Calcular offset
            offset = (page - 1) * page_size

            # Determinar si es búsqueda o listado normal
            if search_term and search_term.strip():
                # Búsqueda paginada
                sql_data = self.sql_manager.get_query('obras', 'buscar_obras_paginadas')
                search_param = f"%{search_term.strip()}%"

                # Ejecutar búsqueda (la query espera múltiples parámetros de search_term)
                cursor.execute(sql_data, (
                    search_param, search_param, search_param, search_param, search_param,  # Para relevancia
                    search_param, search_param, search_param, search_param, search_param, search_param,  # Para WHERE
                    page_size, offset
                ))

                # Contar total de búsqueda usando SQLQueryManager
                sql_count = self.sql_manager.get_query('obras', 'count_obras_activas')
                cursor.execute(sql_count, (search_param, search_param, search_param,
                                         search_param, search_param, search_param))
                total_count = cursor.fetchone()[0]

            else:
                # Listado normal paginado
                sql_data = self.sql_manager.get_query('obras', 'obtener_obras_paginadas')
                cursor.execute(sql_data, (page_size, offset))

                # Contar total
                sql_count = self.sql_manager.get_query('obras', 'contar_obras_activas')
                cursor.execute(sql_count)
                total_count = cursor.fetchone()[0]

            # Obtener datos
            rows = cursor.fetchall()

            # Convertir a diccionarios
            obras = []
            if rows:
                columns = [column[0] for column in cursor.description]
                obras = [dict(zip(columns, row)) for row in rows]

            # Calcular información de paginación
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

            return {
                'data': obras,
                'total_records': total_count,
                'current_page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'start_record': offset + 1 if obras else 0,
                'end_record': min(offset + len(obras), total_count)
            }

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo datos paginados: {e}")
            return {
                'data': [],
                'total_records': 0,
                'current_page': page,
                'page_size': page_size,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False
            }
        finally:
            if cursor:
                cursor.close()

    @cached_query(cache_key="todas_obras", ttl=300)
    @track_performance
    @paginated(page_size=50)
    def obtener_todas_obras(self, limit=None, offset=0):
        """
        Obtiene todas las obras activas con paginación y cache.

        Args:
            limit: Límite de resultados (agregado por decorator)
            offset: Offset para paginación (agregado por decorator)

        Returns:
            list: Lista de obras paginadas
        """
        if not self.db_connection:
            return []

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Query optimizada con paginación usando SQLQueryManager
            query = self.sql_manager.get_query('obras', 'select_obras_activas')

            cursor.execute(query, (offset, limit or 50))
            obras = cursor.fetchall()

            return obras

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo todas las obras: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    @cached_query(ttl=600)
    @track_performance
    @prevent_n_plus_one(batch_key="obras_by_id")
    def obtener_obra_por_id(self, obra_id: int):
        """
        Obtiene una obra por su ID con cache y prevención N+1.

        Args:
            obra_id: ID de la obra

        Returns:
            dict: Datos de la obra o None si no existe
        """
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Query optimizada usando SQLQueryManager
            query = self.sql_manager.get_query('obras', 'select_obra_por_id')

            cursor.execute(query, (obra_id,))
            row = cursor.fetchone()

            if row:
                # Para manejar tanto datos reales como mocks
                try:
                    columnas = [column[0] for column in cursor.description]
                    return dict(zip(columnas, row))
                except (AttributeError, TypeError):
                    # Mock o datos sin descripción
                    if len(row) >= 5:
                        return {
                            'id': row[0],
                            'codigo_obra': row[1],
                            'nombre': row[2],
                            'cliente': row[3],
                            'presupuesto_inicial': row[4]
                        }
                    return {'id': obra_id, 'data': row}
            return None

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo obra por ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def actualizar_obra(self,
obra_id: int,
        datos_actualizados: Dict[str,
        Any]):
        """Actualiza una obra existente."""
        if not self.db_connection:
            return False, DB_ERROR_MESSAGE

        cursor = None
        try:
            # Sanitizar datos
            datos_limpios = self.data_sanitizer.sanitize_dict(datos_actualizados)

            # Validar ID
            try:
                obra_id_limpio = int(obra_id)
                if obra_id_limpio <= 0:
                    return False, "ID de obra inválido"
            except (ValueError, TypeError):
                return False, "ID de obra inválido"

            cursor = self.db_connection.cursor()

            # Verificar que la obra existe
            sql_verificacion = self.sql_manager.get_query('obras', 'verificar_obra_existe')
            cursor.execute(sql_verificacion, (obra_id_limpio,))
            if not cursor.fetchone():
                return False, "La obra no existe o está inactiva"

            # Actualizar obra usando SQLQueryManager
            sql = self.sql_manager.get_query('obras', 'update_obra')
            params = (
                datos_limpios.get('nombre'),
                datos_limpios.get('descripcion'),
                datos_limpios.get('direccion'),
                datos_limpios.get('cliente'),
                datos_limpios.get('estado'),
                datos_limpios.get('fecha_inicio'),
                datos_limpios.get('fecha_fin_estimada'),
                datos_limpios.get('presupuesto_total'),
                datos_limpios.get('presupuesto_utilizado'),
                datos_limpios.get('observaciones'),
                obra_id_limpio
            )
            cursor.execute(sql, params)

            if cursor.rowcount == 0:
                return False, "No se pudo actualizar la obra"

            self.db_connection.commit()
            return True, f"Obra actualizada exitosamente"

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error actualizando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as e2:
                    logger.info(f"[ERROR OBRAS] Error en rollback: {e2}")
            return False, f"Error actualizando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def eliminar_obra(self, obra_id: int, usuario_eliminacion: str):
        """Elimina lógicamente una obra (soft delete)."""
        if not self.db_connection:
            return False, DB_ERROR_MESSAGE

        cursor = None
        try:
            # Sanitizar datos
            try:
                obra_id_limpio = int(obra_id)
                if obra_id_limpio <= 0:
                    return False, "ID de obra inválido"
            except (ValueError, TypeError):
                return False, "ID de obra inválido"

            usuario_limpio = str(usuario_eliminacion)[:50] if usuario_eliminacion else ""

            if not usuario_limpio:
                return False, "Usuario de eliminación es requerido"

            cursor = self.db_connection.cursor()

            # Verificar que la obra existe
            sql = self.sql_manager.get_query('obras', 'obtener_codigo_obra')
            cursor.execute(sql, (obra_id_limpio,))
            result = cursor.fetchone()
            if not result:
                return False, "La obra no existe o ya está eliminada"

            codigo_obra = result[0]

            # Soft delete
            sql = self.sql_manager.get_query('obras', 'desactivar_obra')
            cursor.execute(sql, (obra_id_limpio,))

            if cursor.rowcount == 0:
                return False, "No se pudo eliminar la obra"

            self.db_connection.commit()
            return True, f"Obra {codigo_obra} eliminada exitosamente"

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error eliminando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as e2:
                    logger.info(f"[ERROR OBRAS] Error en rollback: {e2}")
            return False, f"Error eliminando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def cambiar_estado_obra(self,
obra_id: int,
        nuevo_estado: str,
        usuario_cambio: str):
        """Cambia el estado de una obra."""
        if not self.db_connection:
            return False, DB_ERROR_MESSAGE

        cursor = None
        try:
            # Sanitizar datos
            try:
                obra_id_limpio = int(obra_id)
                if obra_id_limpio <= 0:
                    return False, "ID de obra inválido"
            except (ValueError, TypeError):
                return False, "ID de obra inválido"

            estado_limpio = str(nuevo_estado)[:20] if nuevo_estado else ""
            usuario_limpio = str(usuario_cambio)[:50] if usuario_cambio else ""

            estados_validos = ['PLANIFICACION', 'EN_PROCESO', 'PAUSADA', 'FINALIZADA', 'CANCELADA']
            if estado_limpio not in estados_validos:
                return False, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"

            cursor = self.db_connection.cursor()

            # Actualizar estado
            sql = self.sql_manager.get_query('obras', 'actualizar_estado_obra')
            cursor.execute(sql, (estado_limpio, obra_id_limpio))

            if cursor.rowcount == 0:
                return False, "No se pudo cambiar el estado de la obra"

            self.db_connection.commit()
            return True, f"Estado cambiado a {estado_limpio}"

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error cambiando estado: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as e2:
                    logger.info(f"[ERROR OBRAS] Error al hacer rollback: {e2}")
            return False, f"Error cambiando estado: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    @cached_query(cache_key="estadisticas_obras", ttl=900)
    @track_performance
    def obtener_estadisticas_obras(self):
        """Obtiene estadísticas generales de obras con cache de 15 minutos."""
        if not self.db_connection:
            return {}

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # Query optimizada usando SQLQueryManager
            sql_stats = self.sql_manager.get_query('obras', 'select_estadisticas_completas_obras')
            cursor.execute(sql_stats)

            row = cursor.fetchone()
            if row:
                estadisticas = {
                    'total_obras': row[0] or 0,
                    'obras_activas': row[1] or 0,
                    'obras_finalizadas': row[2] or 0,
                    'obras_pendientes': row[3] or 0,
                    'presupuesto_promedio': round(row[4] or 0, 2),
                    'presupuesto_total_acumulado': round(row[5] or 0, 2)
                }

            # Presupuesto total
            sql = self.sql_manager.get_query('obras', 'calcular_presupuesto_total')
            cursor.execute(sql)
            result = cursor.fetchone()[0]
            estadisticas['presupuesto_total'] = float(result) if result else 0.0

            return estadisticas

        except Exception as e:
            logger.info(f"[ERROR OBRAS] Error obteniendo estadísticas: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
