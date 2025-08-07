from rexus.core.auth_decorators import auth_required, admin_required, permission_required

# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Obras - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para obras.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Importar utilidades requeridas
from rexus.utils.sql_script_loader import sql_script_loader
try:
    from rexus.utils.data_sanitizer import DataSanitizer
    data_sanitizer = DataSanitizer()
except ImportError:
    # Fallback básico si no está disponible
    class DataSanitizer:
        def sanitize_string(self, value, max_length=None): return str(value) if value else ""
        def sanitize_numeric(self, value, min_val=None, max_val=None): return float(value) if value else 0.0
        def sanitize_integer(self, value, min_val=None, max_val=None): return int(value) if value else 0
        def sanitize_dict(self, data_dict): return dict(data_dict)
    data_sanitizer = DataSanitizer()

class ObrasModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_obras = "obras"
        self.tabla_detalles_obra = "detalles_obra"

        # Configurar cargador de scripts SQL y sanitización
        self.sql_loader = sql_script_loader
        self.data_sanitizer = data_sanitizer

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
            # Sanitizar datos
            codigo_limpio = codigo_obra.strip().upper()
            if self.data_sanitizer:
                codigo_limpio = self.data_sanitizer.sanitize_string(codigo_limpio)

            cursor = self.db_connection.cursor()

            if id_obra_actual:
                # Para edición, excluir la obra actual
                script_content = self.sql_loader.load_script('obras/count_duplicados_codigo_exclude')
                cursor.execute(script_content, (codigo_limpio, id_obra_actual))
            else:
                # Para nueva obra
                script_content = self.sql_loader.load_script('obras/count_duplicados_codigo')
                cursor.execute(script_content, (codigo_limpio,))

            count = cursor.fetchone()[0]
            return count > 0

        except Exception as e:
            print(f"[ERROR OBRAS] Error validando obra duplicada: {e}")
            return False

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla de obras
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_obras,),
            )
            if cursor.fetchone():
                print(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")

                # Mostrar estructura
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_obras,),
                )
                columnas = cursor.fetchall()
                print(f"[OBRAS] Estructura de tabla '{self.tabla_obras}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_obras}' no existe en la base de datos."
                )

            # Verificar tabla de detalles de obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_detalles_obra,),
            )
            if cursor.fetchone():
                print(
                    f"[OBRAS] Tabla '{self.tabla_detalles_obra}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_detalles_obra}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR OBRAS] Error verificando tablas: {e}")
        finally:
            if cursor:
                cursor.close()

    @auth_required
    def crear_obra(
        self,
        datos_obra:Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Crea una nueva obra en el sistema con sanitización completa de datos.

        Args:
            datos_obra: Diccionario con los datos de la obra

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

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
            presupuesto_original = datos_obra.get("presupuesto_total")
            if presupuesto_original and presupuesto_original != "":
                try:
                    presupuesto_limpio = float(presupuesto_original)
                    if presupuesto_limpio < 0:
                        return False, "El presupuesto no puede ser negativo"
                    datos_limpios["presupuesto_total"] = presupuesto_limpio
                except (ValueError, TypeError):
                    return False, "Presupuesto inválido"
            else:
                datos_limpios["presupuesto_total"] = 0.0

            cursor = self.db_connection.cursor()

            # Verificar que no existe una obra con el mismo código
            script_content = self.sql_loader.load_script('obras/count_duplicados_codigo')
            cursor.execute(script_content, (datos_limpios.get("codigo"),))
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    f"Ya existe una obra con el código {datos_limpios.get('codigo')}",
                )

            # Insertar obra con datos sanitizados
            script_content = self.sql_loader.load_script('obras/insert_obra')
            cursor.execute(script_content, (
                datos_limpios.get("codigo"),
                datos_limpios.get("nombre"),
                datos_limpios.get("descripcion", ""),
                datos_limpios.get("cliente"),
                datos_limpios.get("direccion", ""),
                datos_limpios.get("telefono_contacto", ""),
                datos_limpios.get("email_contacto", ""),
                datos_limpios.get("fecha_inicio"),
                datos_limpios.get("fecha_fin_estimada"),
                datos_limpios.get("presupuesto_total", 0),
                datos_limpios.get("estado", "PLANIFICACION"),
                datos_limpios.get("tipo_obra", "CONSTRUCCION"),
                datos_limpios.get("prioridad", "MEDIA"),
                datos_limpios.get("responsable"),
                datos_limpios.get("observaciones", ""),
                datos_limpios.get("usuario_creacion", "SISTEMA"),
            ))

            self.db_connection.commit()

            print(f"[OBRAS] Obra creada exitosamente: {datos_limpios.get('codigo')}")
            return True, f"Obra {datos_limpios.get('codigo')} creada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error creando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error creando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def obtener_todas_obras(self):
        """Obtiene todas las obras de la base de datos como lista de diccionarios."""
        cursor = None
        try:
            cursor = self.db_connection.cursor()
            script_content = self.sql_loader.load_script('obras/select_all_obras')
            cursor.execute(script_content)
            rows = cursor.fetchall()
            columnas = [column[0] for column in cursor.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            print(f"Error obteniendo obras: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su ID."""
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            script_content = self.sql_loader.load_script('obras/select_obra_por_id')
            cursor.execute(script_content, (obra_id,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Error obteniendo obra {obra_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def obtener_obra_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su código."""
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            script_content = self.sql_loader.load_script('obras/select_obra_por_codigo')
            cursor.execute(script_content, (codigo,))

            row = cursor.fetchone()
            if row:
                columnas = [column[0] for column in cursor.description]
                return dict(zip(columnas, row))
            return None

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obra: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    @auth_required
    def actualizar_obra(
        self,
        obra_id:int,
        datos_obra: Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Actualiza los datos de una obra.

        Args:
            obra_id: ID de la obra a actualizar
            datos_obra: Diccionario con los nuevos datos

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            script_content = self.sql_loader.load_script('obras/update_obra')
            cursor.execute(script_content, (
                datos_obra.get("nombre"),
                datos_obra.get("descripcion"),
                datos_obra.get("cliente"),
                datos_obra.get("direccion"),
                datos_obra.get("telefono_contacto"),
                datos_obra.get("email_contacto"),
                datos_obra.get("fecha_fin_estimada"),
                datos_obra.get("presupuesto_total"),
                datos_obra.get("estado"),
                datos_obra.get("tipo_obra"),
                datos_obra.get("prioridad"),
                datos_obra.get("responsable"),
                datos_obra.get("observaciones"),
                datos_obra.get("usuario_modificacion", "SISTEMA"),
                obra_id,
            ))

            if cursor.rowcount > 0:
                self.db_connection.commit()
                return True, "Obra actualizada exitosamente"
            else:
                return False, "No se encontró la obra a actualizar"

        except Exception as e:
            print(f"[ERROR OBRAS] Error actualizando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error actualizando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    @auth_required
    def cambiar_estado_obra(
        self,
        obra_id:int,
        nuevo_estado: str,
        usuario: str = "SISTEMA",
    ) -> tuple[bool, str]:
        """
        Cambia el estado de una obra.

        Args:
            obra_id: ID de la obra
            nuevo_estado: Nuevo estado (PLANIFICACION, EN_PROCESO, PAUSADA, FINALIZADA, CANCELADA)
            usuario: Usuario que realiza el cambio

        Returns:
            tuple: (éxito, mensaje)
        """
        estados_validos = [
            "PLANIFICACION",
            "EN_PROCESO",
            "PAUSADA",
            "FINALIZADA",
            "CANCELADA",
        ]

        if nuevo_estado not in estados_validos:
            return (
                False,
                f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}",
            )

        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Obtener estado actual
            script_content = self.sql_loader.load_script('obras/select_estado_obra')
            cursor.execute(script_content, (obra_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Obra no encontrada"

            estado_actual = resultado[0]

            # Actualizar estado
            script_content = self.sql_loader.load_script('obras/update_estado_obra')
            cursor.execute(script_content, (nuevo_estado, usuario, obra_id))
            self.db_connection.commit()

            # Si se finaliza la obra, actualizar fecha de finalización
            if nuevo_estado == "FINALIZADA":
                script_content = self.sql_loader.load_script('obras/update_fecha_finalizacion')
                cursor.execute(script_content, (obra_id,))
                self.db_connection.commit()

            return True, f"Estado cambiado de {estado_actual} a {nuevo_estado}"

        except Exception as e:
            print(f"[ERROR OBRAS] Error cambiando estado: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error cambiando estado: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def obtener_obras_filtradas(
        self,
        estado: str = "",
        responsable: str = "",
        fecha_inicio: Optional[datetime.date] = None,
        fecha_fin: Optional[datetime.date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene obras con filtros aplicados.

        Args:
            estado: Filtrar por estado específico
            responsable: Filtrar por responsable
            fecha_inicio: Filtrar desde fecha
            fecha_fin: Filtrar hasta fecha

        Returns:
            List: Lista de obras que cumplen los filtros
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]  # Condición base
            params = []

            if estado:
                conditions.append("estado = ?")
                params.append(estado)

            if responsable:
                conditions.append("responsable LIKE ?")
                params.append(f"%{responsable}%")

            if fecha_inicio:
                conditions.append("fecha_inicio >= ?")
                params.append(fecha_inicio)

            if fecha_fin:
                conditions.append("fecha_inicio <= ?")
                params.append(fecha_fin)

            # Usar script SQL externo con filtros dinámicos
            script_content = self.sql_loader.load_script('obras/select_obras_filtradas')
            where_clause = " AND ".join(conditions)
            query = script_content.replace("WHERE 1=1", f"WHERE {where_clause}")
            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            obras = []

            for row in cursor.fetchall():
                obra = dict(zip(columnas, row))
                obras.append(obra)

            return obras

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obras filtradas: {e}")
            return []

    def obtener_estadisticas_obras(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de obras."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # Total de obras
            script_content = self.sql_loader.load_script('obras/select_estadisticas_obras')
            cursor.execute(script_content)
            estadisticas["total_obras"] = cursor.fetchone()[0]

            # Obras por estado
            script_content = self.sql_loader.load_script('obras/select_estadisticas_por_estado')
            cursor.execute(script_content)
            estadisticas["obras_por_estado"] = [
                {"estado": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            # Obras activas (en proceso y planificación)
            script_content = self.sql_loader.load_script('obras/select_obras_activas')
            cursor.execute(script_content)
            estadisticas["obras_activas"] = cursor.fetchone()[0]

            # Presupuesto total
            script_content = self.sql_loader.load_script('obras/select_presupuesto_total')
            cursor.execute(script_content)
            resultado = cursor.fetchone()[0]
            estadisticas["presupuesto_total"] = resultado if resultado else 0

            # Obras por responsable
            script_content = self.sql_loader.load_script('obras/select_estadisticas_por_responsable')
            cursor.execute(script_content)
            estadisticas["obras_por_responsable"] = [
                {"responsable": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            return estadisticas

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo estadísticas: {e}")
            return {}

    @admin_required
    def eliminar_obra(
        self,
        obra_id:int,
        usuario: str = "SISTEMA",
    ) -> tuple[bool, str]:
        """
        Elimina una obra del sistema (solo si no tiene movimientos asociados).

        Args:
            obra_id: ID de la obra a eliminar
            usuario: Usuario que realiza la eliminación

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar si la obra existe
            script_content = self.sql_loader.load_script('obras/select_info_obra')
            cursor.execute(script_content, (obra_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Obra no encontrada"

            codigo_obra, estado = resultado

            # Verificar si tiene detalles asociados
            script_content = self.sql_loader.load_script('obras/count_detalles_obra')
            cursor.execute(script_content, (obra_id,))
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    "No se puede eliminar la obra porque tiene detalles asociados",
                )

            # Solo permitir eliminar obras en estado PLANIFICACION o CANCELADA
            if estado not in ["PLANIFICACION", "CANCELADA"]:
                return False, f"No se puede eliminar una obra en estado {estado}"

            # Eliminar la obra
            script_content = self.sql_loader.load_script('obras/delete_obra')
            cursor.execute(script_content, (obra_id,))
            self.db_connection.commit()

            return True, f"Obra {codigo_obra} eliminada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error eliminando obra: {e}")
            return False, f"Error eliminando obra: {str(e)}"

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
        """Obtiene la query base para paginación (debe ser implementado por cada modelo)"""
        # Esta es una implementación genérica
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        return f"SELECT * FROM {tabla_principal}"
    
    def _get_count_query(self):
        """Obtiene la query de conteo (debe ser implementado por cada modelo)"""
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        return f"SELECT COUNT(*) FROM {tabla_principal}"
    
    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
