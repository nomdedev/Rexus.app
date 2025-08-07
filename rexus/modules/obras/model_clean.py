import datetime
from typing import Any, Dict, List, Optional

from rexus.core.auth_decorators import auth_required, admin_required
from rexus.utils.sql_script_loader import sql_script_loader

# Constantes
DB_ERROR_MESSAGE = "Sin conexión a la base de datos"

try:
    from rexus.utils.data_sanitizer import DataSanitizer
    data_sanitizer = DataSanitizer()
except ImportError:
    # Fallback robusto para DataSanitizer
    class DataSanitizer:
        def sanitize_html(self, html_text):
            if html_text is None:
                return ""
            import re
            s = str(html_text)
            for tag in ["script", "iframe", "object", "embed", "form", "input", "button", "meta", "link", "style"]:
                s = re.sub(f'<{tag}[^>]*>', '', s, flags=re.IGNORECASE)
                s = re.sub(f'</{tag}>', '', s, flags=re.IGNORECASE)
            for attr in ["onclick", "onload", "onerror", "onmouseover", "javascript:"]:
                s = re.sub(f'{attr}[^>]*', '', s, flags=re.IGNORECASE)
            return s.strip()
        def sanitize_text(self, text):
            if text is None:
                return ""
            s = str(text)
            # Elimina caracteres de control y limita longitud
            import re
            s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', s)
            if len(s) > 1000:
                s = s[:1000] + "..."
            return s.strip()

        def sanitize_sql_input(self, text):
            if text is None:
                return ""
            s = str(text)
            for char in ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]:
                s = s.replace(char, "")
            return s.strip()

        def clean_dict(self, data):
            if not isinstance(data, dict):
                return dict(data) if data else {}
            cleaned = {}
            for k, v in data.items():
                if isinstance(v, str):
                    cleaned[k] = self.sanitize_text(v)
                elif isinstance(v, dict):
                    cleaned[k] = self.clean_dict(v)
                elif isinstance(v, list):
                    cleaned[k] = [self.sanitize_text(i) if isinstance(i, str) else i for i in v]
                else:
                    cleaned[k] = v
            return cleaned

        def sanitize_string(self, value, max_length=None):
            s = self.sanitize_text(value)
            if max_length is not None:
                return s[:max_length]
            return s

        def sanitize_numeric(self, value, min_val=None, max_val=None):
            try:
                val = float(value)
                if min_val is not None:
                    val = max(val, min_val)
                if max_val is not None:
                    val = min(val, max_val)
                return val
            except Exception:
                return 0.0
        def sanitize_integer(self, value, min_val=None, max_val=None):
            try:
                val = int(value)
                if min_val is not None:
                    val = max(val, min_val)
                if max_val is not None:
                    val = min(val, max_val)
                return val
            except Exception:
                return 0
        def sanitize_dict(self, data_dict):
            return self.clean_dict(data_dict)
        def sanitize_list(self, data_list):
            return list(data_list) if data_list is not None else []
        def sanitize_bool(self, value):
            return bool(value)
        def sanitize(self, value):
            return value
    data_sanitizer = DataSanitizer()

class ObrasModel:
    def __init__(self, db_connection=None, data_sanitizer_instance=None):
        self.db_connection = db_connection
        self.tabla_obras = "obras"
        self.tabla_detalles_obra = "detalles_obra"
        self.sql_loader = sql_script_loader
        # Permitir inyectar un sanitizer para tests, si no usar el global
        self.data_sanitizer = data_sanitizer_instance if data_sanitizer_instance else data_sanitizer
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
            return

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla de obras
            script_content = self.sql_loader.load_script('obras/verificar_tabla_obras')
            cursor.execute(script_content, (self.tabla_obras,))
            if cursor.fetchone():
                print(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_obras}' no existe en la base de datos.")

            # Verificar tabla de detalles de obra
            try:
                script_content = self.sql_loader.load_script('obras/verificar_tabla_detalles')
                cursor.execute(script_content, (self.tabla_detalles_obra,))
                if cursor.fetchone():
                    print(f"[OBRAS] Tabla '{self.tabla_detalles_obra}' verificada correctamente.")
                else:
                    print(f"[ADVERTENCIA] La tabla '{self.tabla_detalles_obra}' no existe en la base de datos.")
            except Exception:
                # Script de verificación de detalles no existe, no es crítico
                pass

        except Exception as e:
            print(f"[ERROR OBRAS] Error verificando tablas: {e}")
        finally:
            if cursor:
                cursor.close()

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
                codigo_limpio = self.data_sanitizer.sanitize_string(codigo_limpio)
                codigo_limpio = self.data_sanitizer.sanitize_sql_input(codigo_limpio)

            cursor = self.db_connection.cursor()

            if id_obra_actual:
                script_content = self.sql_loader.load_script('obras/count_duplicados_codigo_exclude')
                cursor.execute(script_content, (codigo_limpio, id_obra_actual))
            else:
                script_content = self.sql_loader.load_script('obras/count_duplicados_codigo')
                cursor.execute(script_content, (codigo_limpio,))

            result = cursor.fetchone()
            if result is None:
                return False
            count = result[0]
            return count > 0

        except Exception as e:
            print(f"[ERROR OBRAS] Error validando obra duplicada: {e}")
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
            if presupuesto_original is not None and presupuesto_original != "":
                try:
                    presupuesto_limpio = float(presupuesto_original)
                    if presupuesto_limpio < 0:
                        return False, "El presupuesto no puede ser negativo"
                    datos_limpios["presupuesto_total"] = presupuesto_limpio
                except Exception:
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
                    val = self.data_sanitizer.sanitize_string(val, 128)
                    val = self.data_sanitizer.sanitize_sql_input(val)
                    val = self.data_sanitizer.sanitize_html(val)
                    for pattern in ["DROP TABLE", "UNION SELECT", "--", ";", "<script>", "</script>", "<iframe>", "</iframe>"]:
                        val = val.replace(pattern, "")
                    datos_limpios[campo] = val

            cursor = self.db_connection.cursor()

            # Verificar que no existe una obra con el mismo código
            script_content = self.sql_loader.load_script('obras/count_duplicados_codigo')
            cursor.execute(script_content, (datos_limpios.get("codigo"),))
            result = cursor.fetchone()
            if result and result[0] > 0:
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
                except Exception as rollback_error:
                    print(f"[ERROR OBRAS] Error en rollback: {rollback_error}")
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
                query = base_query.replace("WHERE activo = 1", f"WHERE activo = 1 {where_clause}")
            else:
                query = base_query

            cursor.execute(query, params)
            return cursor.fetchall()

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obras filtradas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def obtener_datos_paginados(self, offset=0, limit=10):
        """
        Obtiene datos paginados de obras.

        Args:
            offset: Desplazamiento
            limit: Límite de registros

        Returns:
            tuple: (lista_obras, total_count)
        """
        if not self.db_connection:
            return [], 0

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            
            # Query para datos paginados
            query = """
            SELECT * FROM obras 
            WHERE activo = 1 
            ORDER BY fecha_creacion DESC 
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            
            cursor.execute(query, (offset, limit))
            obras = cursor.fetchall()
            
            # Query para total count
            cursor.execute("SELECT COUNT(*) FROM obras WHERE activo = 1")
            total = cursor.fetchone()[0]
            
            return obras, total

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo datos paginados: {e}")
            return [], 0
        finally:
            if cursor:
                cursor.close()
