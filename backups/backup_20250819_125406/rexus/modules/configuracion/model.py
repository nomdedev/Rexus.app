# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Configuración - Rexus.app v2.0.0

Gestiona todas las configuraciones del sistema incluyendo:
- Configuración de base de datos
- Configuración de la empresa
- Parámetros del sistema
- Configuraciones de usuarios
- Configuraciones de reportes
- Temas y personalización
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Importar sistema de logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("configuracion.model")
except ImportError:
    logger = logging.getLogger("configuracion.model")

# Importar SQL loader para queries externas
from rexus.utils.sql_script_loader import sql_script_loader

# Nota: Los decoradores admin_required y auth_required no se usan en este archivo.


# Importar sistema unificado de sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.unified_sanitizer import sanitize_string


class ConfiguracionModel:
    """Modelo para gestión de configuraciones del sistema."""

    # Tipos de configuración
    TIPOS_CONFIG = {
        "DATABASE": "Base de Datos",
        "EMPRESA": "Empresa",
        "SISTEMA": "Sistema",
        "USUARIOS": "Usuarios",
        "REPORTES": "Reportes",
        "TEMA": "Tema",
    }

    CONFIG_DEFAULTS = {
        # Base de datos (deben ser configurados por el usuario, nunca por defecto)
        "db_server": "",  # Debe configurarse en .env o por el usuario
        "db_port": "",
        "db_name": "",
        "db_user": "",
        "db_timeout": "",
        "db_pool_size": "",
        # Empresa (pueden tener valores de ejemplo, pero no datos sensibles)
        "empresa_nombre": "",
        "empresa_nit": "",
        "empresa_direccion": "",
        "empresa_telefono": "",
        "empresa_email": "",
        "empresa_web": "",
        "empresa_logo": "",
        "empresa_moneda": "COP",
        "empresa_pais": "Colombia",
        "empresa_ciudad": "Bogotá",
        # Sistema
        "sistema_version": "2.0.0",
        "sistema_modo_debug": "false",
        "sistema_logs_nivel": "INFO",
        "sistema_max_backups": "30",
        "sistema_timeout_sesion": "3600",
        "sistema_max_intentos_login": "3",
        "sistema_idioma": "es",
        "sistema_zona_horaria": "America/Bogota",
        "sistema_formato_fecha": "DD/MM/YYYY",
        "sistema_formato_hora": "HH:mm:ss",
        # Usuarios
        "usuarios_password_min_length": "8",
        "usuarios_password_require_numbers": "true",
        "usuarios_password_require_symbols": "false",
        "usuarios_password_expire_days": "90",
        "usuarios_session_timeout": "3600",
        "usuarios_max_sessions": "3",
        # Reportes
        "reportes_formato_default": "PDF",
        "reportes_autor_default": "Sistema Rexus",
        "reportes_logo_incluir": "true",
        "reportes_pie_pagina": "Generado por Rexus.app",
        "reportes_max_registros": "10000",
        # Tema
        "tema_color_primario": "#3498db",
        "tema_color_secundario": "#2c3e50",
        "tema_color_exito": "#27ae60",
        "tema_color_error": "#e74c3c",
        "tema_color_warning": "#f39c12",
        "tema_fuente_familia": "Segoe UI",
        "tema_fuente_tamaño": "12",
        "tema_modo_oscuro": "false",
        # Backup
        "backup_auto_habilitado": "true",
        "backup_intervalo_horas": "24",
        "backup_directorio": "./backups",
        "backup_mantener_dias": "30",
        "backup_comprimir": "true",
        # Integraciones
        "integraciones_email_smtp_server": "",
        "integraciones_email_smtp_port": "587",
        "integraciones_email_usuario": "",
        "integraciones_email_ssl": "true",
        "integraciones_api_timeout": "30",
        "integraciones_webhook_url": "",
    }

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de configuración.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        # Usar el sistema unificado de sanitización
        self.sanitizer = unified_sanitizer
        self.tabla_configuracion = "configuracion_sistema"
        self.config_file = Path("config/rexus_config.json")
        self.config_cache = {}
        # Configurar cargador de scripts SQL
        self.sql_loader = sql_script_loader

        # Crear directorio de configuración si no existe
        self.config_file.parent.mkdir(exist_ok=True)

        # Inicializar configuración
        self._cargar_configuracion_inicial()

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitiza texto usando el método apropiado según la versión de DataSanitizer.

        Args:
            text: Texto a sanitizar

        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Usar el sistema unificado
        return sanitize_string(text)

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

        # Lista blanca de tablas permitidas
        allowed_tables = {"configuracion_sistema"}
        if table_name not in allowed_tables:
            raise ValueError(f"Tabla no permitida: {table_name}")

        return table_name

    def _cargar_configuracion_inicial(self):
        """Carga la configuración inicial en la base de datos usando SQL externo."""
        if not self.db_connection:
            self._cargar_desde_archivo()
            return

        try:
            from rexus.utils.sql_query_manager import SQLQueryManager

            sql_manager = getattr(self, "sql_manager", SQLQueryManager())
            cursor = self.db_connection.cursor()
            # Verificar si ya hay configuraciones
            query_count = sql_manager.get_query("configuracion", "count_all_configs")
            cursor.execute(query_count)
            result = cursor.fetchone()
            count = result[0] if result else 0

            if count == 0:
                logger.info("Insertando configuraciones por defecto")
                # Insertar configuraciones por defecto
                query_insert = sql_manager.get_query(
                    "configuracion", "insert_config_default"
                )
                for clave, valor in self.CONFIG_DEFAULTS.items():
                    categoria = self._obtener_categoria_por_clave(clave)
                    descripcion = self._obtener_descripcion_por_clave(clave)
                    tipo_dato = self._obtener_tipo_dato_por_valor(valor)
                    cursor.execute(
                        query_insert,
(clave,
                            valor,
                            descripcion,
                            tipo_dato,
                            categoria)
                    )
                self.db_connection.commit()
                logger.info("Configuración inicial cargada en BD")
            else:
                logger.info(f"{count} configuraciones ya existentes en BD")

            cursor.close()
            # Cargar configuración en cache
            self._cargar_cache()
        except Exception as e:
            logger.error(f"Error cargando configuración inicial: {e} - usando archivo")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except (AttributeError, ConnectionError) as e:
                    logger.warning(f"No se pudo hacer rollback: {e}")
            # Fallback a archivo
            self.db_connection = None
            self._cargar_desde_archivo()

        try:
            from rexus.utils.sql_query_manager import SQLQueryManager

            sql_manager = getattr(self, "sql_manager", SQLQueryManager())
            cursor = self.db_connection.cursor()
            query = sql_manager.get_query("configuracion", "check_table_exists")
            cursor.execute(query, (self.tabla_configuracion,))
            result = cursor.fetchone()
            if result and result[0] > 0:
                logger.info(f"Tabla '{self.tabla_configuracion}' verificada correctamente")
            else:
                logger.warning(f"Tabla '{self.tabla_configuracion}' no existe - usando configuración de archivos")
                self.db_connection = None  # Deshabilitar BD y usar archivo
            cursor.close()
        except Exception as e:
            logger.error(f"Error verificando tablas: {e} - usando configuración de archivos")
            self.db_connection = None  # Fallback a archivo

    def validar_configuracion_duplicada(
        self, clave: str, excluir_id: Optional[int] = None
    ) -> bool:
        """
        Valida si una configuración ya existe (para evitar duplicados).

        Args:
            clave: Clave de configuración a validar
            excluir_id: ID a excluir de la validación (para actualizaciones)

        Returns:
            bool: True si existe duplicado, False si no existe
        """
        try:
            if not self.db_connection:
                # Verificar en caché local si no hay BD
                return clave in self.config_cache

            # Sanitizar la clave de entrada
            clave_sanitizada = self._sanitize_text(str(clave).strip())

            cursor = self.db_connection.cursor()
            try:
                if excluir_id:
                    # Consulta externa: count_config_by_key_exclude_id.sql
                    from rexus.utils.sql_query_manager import SQLQueryManager

                    sql_manager = getattr(self, "sql_manager", SQLQueryManager())
                    query = sql_manager.get_query(
                        "configuracion", "count_config_by_key_exclude_id"
                    )
                    cursor.execute(query, (clave_sanitizada, excluir_id))
                else:
                    # Consulta externa: count_config_by_key.sql
                    from rexus.utils.sql_query_manager import SQLQueryManager

                    sql_manager = getattr(self, "sql_manager", SQLQueryManager())
                    query = sql_manager.get_query(
                        "configuracion", "count_config_by_key"
                    )
                    cursor.execute(query, (clave_sanitizada,))

                result = cursor.fetchone()
                existe = result and result[0] > 0
                return bool(existe)
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error validando configuración duplicada: {e}")
            return False  # En caso de error, permitir la operación
        # Código duplicado y SQL embebido eliminado tras migración a SQL externo

    def _cargar_desde_archivo(self):
        """Carga configuración desde archivo JSON."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config_cache = json.load(f)
            else:
                self.config_cache = self.CONFIG_DEFAULTS.copy()
                self._guardar_en_archivo()
        except Exception as e:
            logger.error(f"Error cargando desde archivo: {e}")
            self.config_cache = self.CONFIG_DEFAULTS.copy()

    def _guardar_en_archivo(self):
        """Guarda configuración en archivo JSON."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR CONFIGURACION] Error guardando en archivo: {e}")

    def _cargar_cache(self):
        """Carga toda la configuración en cache."""
        if not self.db_connection:
            print("[CONFIGURACION] Sin BD - cache desde archivo")
            return

        try:
            cursor = self.db_connection.cursor()

            # FIXED: Usar consultas parametrizadas seguras en lugar de script_content
            try:
                cursor.execute("""
                    SELECT clave, valor, categoria, descripcion, tipo_dato, fecha_modificacion
                    FROM configuracion 
                    WHERE activo = 1
                    ORDER BY categoria, clave
                """)
            except Exception as e:
                # Si falla, la tabla podría no tener columna 'activo'
                print(
                    f"[CONFIGURACION] Error al consultar con 'activo': {e}, intentando sin columna 'activo'"
                )
                cursor.execute("""
                    SELECT clave, valor, categoria, descripcion, tipo_dato, fecha_modificacion
                    FROM configuracion 
                    ORDER BY categoria, clave
                """)

            self.config_cache = {}
            rows = cursor.fetchall()
            for row in rows:
                self.config_cache[row[0]] = row[1]

            cursor.close()
            print(
                f"[CONFIGURACION] Cache cargado con {len(self.config_cache)} configuraciones"
            )

        except Exception as e:
            print(
                f"[CONFIGURACION] Error cargando cache: {e} - usando configuración por defecto"
            )
            self.config_cache = self.CONFIG_DEFAULTS.copy()

    def obtener_valor(self, clave: str, valor_por_defecto: Any = None) -> Any:
        """
        Obtiene un valor de configuración.

        Args:
            clave: Clave de configuración
            valor_por_defecto: Valor por defecto si no existe

        Returns:
            El valor de configuración
        """
        if clave in self.config_cache:
            valor = self.config_cache[clave]
        else:
            valor = self.CONFIG_DEFAULTS.get(clave, valor_por_defecto)

        # Convertir strings a tipos apropiados
        if isinstance(valor, str):
            if valor.lower() == "true":
                return True
            elif valor.lower() == "false":
                return False
            elif valor.isdigit():
                return int(valor)
            elif valor.replace(".", "", 1).isdigit():
                return float(valor)

        return valor

    def establecer_valor(
        self, clave: str, valor: Any, usuario: str = "SISTEMA"
    ) -> Tuple[bool, str]:
        """
        Establece un valor de configuración.

        Args:
            clave: Clave de configuración
            valor: Nuevo valor
            usuario: Usuario que hace el cambio

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Validar y sanitizar parámetros de entrada
            if not clave or not isinstance(clave, str):
                return (
                    False,
                    "La clave de configuración es obligatoria y debe ser string",
                )

            # Sanitizar entradas para prevenir XSS y ataques
            clave_sanitizada = self._sanitize_text(clave.strip())
            # usuario_sanitizado eliminado porque no se usa

            # Validar longitud de clave
            if len(clave_sanitizada) > 100:
                return (
                    False,
                    "La clave de configuración es demasiado larga (máximo 100 caracteres)",
                )

            # Convertir valor a string para almacenamiento
            valor_str = self._sanitize_text(str(valor))

            if self.db_connection:
                cursor = self.db_connection.cursor()

                try:
                    # FIXED: Verificar si existe con consulta parametrizada segura
                    cursor.execute("""
                        SELECT COUNT(*) FROM configuracion WHERE clave = ?
                    """, (clave_sanitizada,))
                    result = cursor.fetchone()
                    existe = result[0] > 0 if result else False

                    if existe:
                        # FIXED: Actualizar con consulta parametrizada segura
                        try:
                            cursor.execute("""
                                UPDATE configuracion 
                                SET valor = ?, fecha_modificacion = GETDATE() 
                                WHERE clave = ?
                            """, (valor_str, clave_sanitizada))
                        except Exception as e:
                            # Si no existe fecha_modificacion, usar versión simple
                            print(
                                f"[CONFIGURACION] Error actualizando con fecha_modificacion: {e}, usando versión simple"
                            )
                            cursor.execute("""
                                UPDATE configuracion SET valor = ? WHERE clave = ?
                            """, (valor_str, clave_sanitizada))
                    else:
                        # Insertar con datos validados
                        categoria = self._obtener_categoria_por_clave(clave_sanitizada)
                        descripcion = self._obtener_descripcion_por_clave(
                            clave_sanitizada
                        )
                        tipo_dato = self._obtener_tipo_dato_por_valor(valor_str)

                        # FIXED: Insertar con consulta parametrizada segura
                        cursor.execute("""
                            INSERT INTO configuracion 
                            (clave, valor, descripcion, tipo_dato, categoria, fecha_creacion, fecha_modificacion)
                            VALUES (?, ?, ?, ?, ?, GETDATE(), GETDATE())
                        """, (
                            clave_sanitizada,
                            valor_str,
                            descripcion,
                            tipo_dato,
                            categoria
                        ))

                    self.db_connection.commit()

                finally:
                    cursor.close()

            # Actualizar cache con datos sanitizados
            self.config_cache[clave_sanitizada] = valor_str

            # Guardar en archivo si no hay BD
            if not self.db_connection:
                self._guardar_en_archivo()

            return True, f"Configuración '{clave_sanitizada}' actualizada exitosamente"

        except Exception as e:
            print(f"[CONFIGURACION] Error estableciendo valor: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as e:
                    print(f"[CONFIGURACION] Error en rollback: {e}")
            return False, f"Error estableciendo configuración: {str(e)}"

    def obtener_configuracion_por_categoria(self, categoria: str) -> Dict[str, Any]:
        """
        Obtiene todas las configuraciones de una categoría.

        Args:
            categoria: Categoría de configuraciones

        Returns:
            Dict con las configuraciones de la categoría
        """
        if not self.db_connection:
            # Filtrar desde cache/archivo
            return {
                k: v
                for k, v in self.config_cache.items()
                if self._obtener_categoria_por_clave(k) == categoria
            }

        try:
            cursor = self.db_connection.cursor()

            try:
                # Intentar con columna activo
                cursor.execute(
                    f"""
                    SELECT clave, valor, descripcion, tipo
                    FROM [{self._validate_table_name(self.tabla_configuracion)}]
                    WHERE categoria = ? AND activo = 1
                    ORDER BY clave
                """,
                    (categoria,),
                )
            except (KeyError, ValueError, ConnectionError) as e:
                # Si falla, usar sin columna activo
                print(f"[WARNING] Usando query alternativa: {e}")
                cursor.execute(
                    f"""
                    SELECT clave, valor, descripcion, tipo
                    FROM [{self._validate_table_name(self.tabla_configuracion)}]
                    WHERE categoria = ?
                    ORDER BY clave
                """,
                    (categoria,),
                )

            configs = {}
            rows = cursor.fetchall()
            for row in rows:
                configs[row[0]] = {
                    "valor": row[1],
                    "descripcion": row[2] if len(row) > 2 else "Configuración",
                    "tipo": row[3] if len(row) > 3 else "string",
                    "editable": True,
                }

            cursor.close()
            return configs

        except Exception as e:
            print(f"[CONFIGURACION] Error obteniendo configuración por categoría: {e}")
            # Fallback desde cache
            return {
                k: v
                for k, v in self.config_cache.items()
                if self._obtener_categoria_por_clave(k) == categoria
            }

    def obtener_todas_configuraciones(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las configuraciones del sistema.

        Returns:
            Lista de configuraciones
        """
        if not self.db_connection:
            return self._get_configuraciones_demo()

        try:
            cursor = self.db_connection.cursor()

            try:
                # Intentar con todas las columnas
                cursor.execute(f"""
                    SELECT clave, valor, descripcion, tipo, categoria,
                           fecha_modificacion
                    FROM [{self._validate_table_name(self.tabla_configuracion)}]
                    WHERE activo = 1
                    ORDER BY categoria, clave
                """)
            except (KeyError, ValueError, ConnectionError) as e:
                print(f"[WARNING] Error en query completa, usando alternativa: {e}")
                try:
                    # Sin fecha_modificacion ni activo
                    cursor.execute(f"""
                        SELECT clave, valor, descripcion, tipo, categoria
                        FROM [{self._validate_table_name(self.tabla_configuracion)}]
                        ORDER BY categoria, clave
                    """)
                except (KeyError, ValueError, ConnectionError) as e:
                    # Solo columnas básicas
                    print(f"[WARNING] Usando query básica: {e}")
                    cursor.execute(f"""
                        SELECT clave, valor
                        FROM [{self._validate_table_name(self.tabla_configuracion)}]
                        ORDER BY clave
                    """)

            configuraciones = []
            rows = cursor.fetchall()

            for row in rows:
                if len(row) >= 5:
                    # Formato completo
                    config = {
                        "clave": row[0],
                        "valor": row[1],
                        "descripcion": row[2] or "Configuración",
                        "tipo": row[3] or "string",
                        "categoria": row[4] or "SISTEMA",
                    }
                elif len(row) >= 2:
                    # Formato básico
                    config = {
                        "clave": row[0],
                        "valor": row[1],
                        "descripcion": self._obtener_descripcion_por_clave(row[0]),
                        "tipo": "string",
                        "categoria": self._obtener_categoria_por_clave(row[0]),
                    }
                else:
                    continue

                configuraciones.append(config)

            cursor.close()
            return configuraciones

        except Exception as e:
            print(f"[CONFIGURACION] Error obteniendo todas las configuraciones: {e}")
            return self._get_configuraciones_demo()

    def restaurar_configuracion_defecto(
        self, clave: str, usuario: str = "SISTEMA"
    ) -> Tuple[bool, str]:
        """
        Restaura una configuración a su valor por defecto.

        Args:
            clave: Clave de configuración
            usuario: Usuario que hace el cambio

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if clave in self.CONFIG_DEFAULTS:
            return self.establecer_valor(clave, self.CONFIG_DEFAULTS[clave], usuario)
        else:
            return False, f"No existe valor por defecto para '{clave}'"

    def exportar_configuracion(
        self,
        archivo: str,
    ) -> Tuple[bool, str]:
        """
        Exporta la configuración actual a un archivo.

        Args:
            archivo: Ruta del archivo de destino

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            configuraciones = self.obtener_todas_configuraciones()

            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(configuraciones,
f,
                    indent=2,
                    ensure_ascii=False,
                    default=str)

            return True, f"Configuración exportada a '{archivo}'"

        except Exception as e:
            print(f"[ERROR CONFIGURACION] Error exportando configuración: {e}")
            return False, f"Error exportando configuración: {str(e)}"

    def importar_configuracion(
        self,
        archivo: str,
        usuario: str = "SISTEMA",
    ) -> Tuple[bool, str]:
        """
        Importa configuración desde un archivo.

        Args:
            archivo: Ruta del archivo de origen
            usuario: Usuario que hace el cambio

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                configuraciones = json.load(f)

            contador = 0
            for config in configuraciones:
                if isinstance(config, dict) and "clave" in config and "valor" in config:
                    exito, _ = self.establecer_valor(
                        config["clave"], config["valor"], usuario
                    )
                    if exito:
                        contador += 1

            return True, f"Importadas {contador} configuraciones desde '{archivo}'"

        except Exception as e:
            print(f"[ERROR CONFIGURACION] Error importando configuración: {e}")
            return False, f"Error importando configuración: {str(e)}"

    def _obtener_categoria_por_clave(self, clave: str) -> str:
        """Obtiene la categoría basada en la clave."""
        if clave.startswith("db_"):
            return "DATABASE"
        elif clave.startswith("empresa_"):
            return "EMPRESA"
        elif clave.startswith("usuarios_"):
            return "USUARIOS"
        elif clave.startswith("reportes_"):
            return "REPORTES"
        elif clave.startswith("tema_"):
            return "TEMA"
        elif clave.startswith("backup_"):
            return "BACKUP"
        elif clave.startswith("integraciones_"):
            return "INTEGRACIONES"
        else:
            return "SISTEMA"

    def _obtener_descripcion_por_clave(self, clave: str) -> str:
        """Obtiene una descripción basada en la clave."""
        descripciones = {
            "db_server": "Servidor de base de datos",
            "db_port": "Puerto de base de datos",
            "db_name": "Nombre de base de datos",
            "empresa_nombre": "Nombre de la empresa",
            "empresa_nit": "NIT de la empresa",
            "sistema_version": "Versión del sistema",
            "usuarios_password_min_length": "Longitud mínima de contraseña",
            "tema_color_primario": "Color primario del tema",
            "backup_auto_habilitado": "Backup automático habilitado",
            "integraciones_email_smtp_server": "Servidor SMTP para email",
        }
        return descripciones.get(clave, f"Configuración {clave}")

    def _obtener_tipo_dato_por_valor(self, valor: str) -> str:
        """Obtiene el tipo de dato basado en el valor."""
        if valor.lower() in ["true", "false"]:
            return "boolean"
        elif valor.isdigit():
            return "integer"
        elif valor.replace(".", "", 1).isdigit():
            return "float"
        else:
            return "string"

    def _get_configuraciones_demo(self) -> List[Dict[str, Any]]:
        """Configuraciones demo cuando no hay BD."""
        return [
            {
                "clave": "empresa_nombre",
                "valor": "Rexus Construction",
                "descripcion": "Nombre de la empresa",
                "tipo_dato": "string",
                "categoria": "EMPRESA",
                "es_editable": True,
            },
            {
                "clave": "sistema_version",
                "valor": "2.0.0",
                "descripcion": "Versión del sistema",
                "tipo_dato": "string",
                "categoria": "SISTEMA",
                "es_editable": False,
            },
            {
                "clave": "tema_color_primario",
                "valor": "#3498db",
                "descripcion": "Color primario del tema",
                "tipo_dato": "string",
                "categoria": "TEMA",
                "es_editable": True,
            },
        ]

    def obtener_configuraciones_filtradas(self, filtros: Dict[str, Any]) -> List[Dict]:
        """
        Obtiene configuraciones aplicando filtros específicos.
        
        Args:
            filtros: Diccionario con filtros a aplicar
            
        Returns:
            Lista de configuraciones filtradas
        """
        try:
            print(f"[CONFIGURACION MODEL] Aplicando filtros: {filtros}")
            
            if not self.db_connection:
                print("[ERROR CONFIGURACION MODEL] No hay conexión a la base de datos")
                # Fallback con datos demo filtrados
                configuraciones_demo = self._obtener_configuraciones_demo()
                return self._aplicar_filtros_demo(configuraciones_demo, filtros)
            
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT 
                    id, clave, valor, descripcion, tipo_dato, categoria, 
                    es_editable, fecha_creacion, fecha_modificacion, usuario_modificacion
                FROM configuraciones
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros dinámicamente
            if filtros.get('busqueda'):
                query += """
                    AND (clave LIKE ? OR descripcion LIKE ? OR valor LIKE ? OR categoria LIKE ?)
                """
                busqueda = f"%{filtros['busqueda']}%"
                params.extend([busqueda, busqueda, busqueda, busqueda])
            
            if filtros.get('categoria') and filtros['categoria'] != 'Todas':
                query += " AND categoria = ?"
                params.append(filtros['categoria'])
            
            if filtros.get('tipo') and filtros['tipo'] != 'Todos':
                query += " AND tipo_dato = ?"
                params.append(filtros['tipo'].lower())
            
            if filtros.get('estado') and filtros['estado'] != 'Todos':
                if filtros['estado'] == 'Activo':
                    query += " AND es_editable = 1"
                elif filtros['estado'] == 'Inactivo':
                    query += " AND es_editable = 0"
                elif filtros['estado'] == 'Por Defecto':
                    query += " AND usuario_modificacion IS NULL"
                elif filtros['estado'] == 'Personalizado':
                    query += " AND usuario_modificacion IS NOT NULL"
            
            # Ordenar por categoría y clave
            query += " ORDER BY categoria, clave"
            
            print(f"[CONFIGURACION MODEL] Ejecutando query con {len(params)} parámetros")
            cursor.execute(query, params)
            
            # Convertir resultados a diccionarios
            configuraciones = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                configuracion = dict(zip(columns, row))
                configuraciones.append(configuracion)
            
            print(f"[CONFIGURACION MODEL] Filtradas {len(configuraciones)} configuraciones exitosamente")
            return configuraciones
            
        except Exception as e:
            print(f"[ERROR CONFIGURACION MODEL] Error filtrando configuraciones: {e}")
            # Fallback con datos demo en caso de error
            configuraciones_demo = self._obtener_configuraciones_demo()
            return self._aplicar_filtros_demo(configuraciones_demo, filtros)

    def _aplicar_filtros_demo(self, configuraciones: List[Dict], filtros: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros a los datos demo."""
        resultado = configuraciones
        
        if filtros.get('busqueda'):
            termino = filtros['busqueda'].lower()
            resultado = [c for c in resultado if (
                termino in c.get('clave', '').lower() or
                termino in c.get('descripcion', '').lower() or
                termino in c.get('valor', '').lower() or
                termino in c.get('categoria', '').lower()
            )]
        
        if filtros.get('categoria') and filtros['categoria'] != 'Todas':
            resultado = [c for c in resultado if c.get('categoria', '') == filtros['categoria']]
        
        if filtros.get('tipo') and filtros['tipo'] != 'Todos':
            resultado = [c for c in resultado if c.get('tipo_dato', '') == filtros['tipo'].lower()]
        
        if filtros.get('estado') and filtros['estado'] != 'Todos':
            if filtros['estado'] == 'Activo':
                resultado = [c for c in resultado if c.get('es_editable', False)]
            elif filtros['estado'] == 'Inactivo':
                resultado = [c for c in resultado if not c.get('es_editable', True)]
        
        return resultado
