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
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
        "BACKUP": "Backup",
        "INTEGRACIONES": "Integraciones",
    }

    # Configuraciones por defecto
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
        self.tabla_configuracion = "configuracion_sistema"
        self.config_file = Path("config/rexus_config.json")
        self.config_cache = {}

        # Crear directorio de configuración si no existe
        self.config_file.parent.mkdir(exist_ok=True)

        # Inicializar configuración
        self._verificar_tablas()
        self._cargar_configuracion_inicial()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos. NO CREA TABLAS."""
        if not self.db_connection:
            print("[CONFIGURACION] Sin conexión BD - usando archivo de configuración")
            return

        try:
            cursor = self.db_connection.cursor()
            
            # Verificar si la tabla existe
            cursor.execute(
                "SELECT COUNT(*) FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_configuracion,),
            )
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                print(f"[CONFIGURACION] Tabla '{self.tabla_configuracion}' verificada correctamente.")
            else:
                print(f"[CONFIGURACION] AVISO: Tabla '{self.tabla_configuracion}' no existe - usando configuración de archivos")
                self.db_connection = None  # Deshabilitar BD y usar archivo
                
            cursor.close()

        except Exception as e:
            print(f"[CONFIGURACION] Error verificando tablas: {e} - usando configuración de archivos")
            self.db_connection = None  # Fallback a archivo

    def _cargar_configuracion_inicial(self):
        """Carga la configuración inicial en la base de datos."""
        if not self.db_connection:
            self._cargar_desde_archivo()
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar si ya hay configuraciones
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_configuracion}")
            result = cursor.fetchone()
            count = result[0] if result else 0

            if count == 0:
                print("[CONFIGURACION] Insertando configuraciones por defecto...")
                # Insertar configuraciones por defecto
                for clave, valor in self.CONFIG_DEFAULTS.items():
                    categoria = self._obtener_categoria_por_clave(clave)
                    descripcion = self._obtener_descripcion_por_clave(clave)
                    tipo_dato = self._obtener_tipo_dato_por_valor(valor)

                    cursor.execute(
                        f"""
                        INSERT INTO {self.tabla_configuracion} 
                        (clave, valor, descripcion, tipo, categoria)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (clave, valor, descripcion, tipo_dato, categoria),
                    )

                self.db_connection.commit()
                print("[CONFIGURACION] Configuración inicial cargada en BD")
            else:
                print(f"[CONFIGURACION] {count} configuraciones ya existentes en BD")

            cursor.close()

            # Cargar configuración en cache
            self._cargar_cache()

        except Exception as e:
            print(f"[CONFIGURACION] Error cargando configuración inicial: {e} - usando archivo")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            # Fallback a archivo
            self.db_connection = None
            self._cargar_desde_archivo()

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
            print(f"[ERROR CONFIGURACION] Error cargando desde archivo: {e}")
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
            
            # Verificar si la columna 'activo' existe
            try:
                cursor.execute(f"SELECT clave, valor FROM {self.tabla_configuracion} WHERE activo = 1")
            except:
                # Si falla, la tabla podría no tener columna 'activo'
                cursor.execute(f"SELECT clave, valor FROM {self.tabla_configuracion}")

            self.config_cache = {}
            rows = cursor.fetchall()
            for row in rows:
                self.config_cache[row[0]] = row[1]
                
            cursor.close()
            print(f"[CONFIGURACION] Cache cargado con {len(self.config_cache)} configuraciones")

        except Exception as e:
            print(f"[CONFIGURACION] Error cargando cache: {e} - usando configuración por defecto")
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
            # Convertir valor a string para almacenamiento
            valor_str = str(valor)

            if self.db_connection:
                cursor = self.db_connection.cursor()

                try:
                    # Verificar si existe
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {self.tabla_configuracion} WHERE clave = ?",
                        (clave,),
                    )
                    result = cursor.fetchone()
                    existe = result[0] > 0 if result else False

                    if existe:
                        # Actualizar
                        try:
                            cursor.execute(
                                f"""
                                UPDATE {self.tabla_configuracion}
                                SET valor = ?, fecha_modificacion = GETDATE()
                                WHERE clave = ?
                            """,
                                (valor_str, clave),
                            )
                        except:
                            # Si no existe fecha_modificacion, usar versión simple
                            cursor.execute(
                                f"""
                                UPDATE {self.tabla_configuracion}
                                SET valor = ?
                                WHERE clave = ?
                            """,
                                (valor_str, clave),
                            )
                    else:
                        # Insertar
                        categoria = self._obtener_categoria_por_clave(clave)
                        descripcion = self._obtener_descripcion_por_clave(clave)
                        tipo_dato = self._obtener_tipo_dato_por_valor(valor_str)

                        cursor.execute(
                            f"""
                            INSERT INTO {self.tabla_configuracion}
                            (clave, valor, descripcion, tipo, categoria)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (clave, valor_str, descripcion, tipo_dato, categoria),
                        )

                    self.db_connection.commit()
                    
                finally:
                    cursor.close()

            # Actualizar cache
            self.config_cache[clave] = valor_str

            # Guardar en archivo si no hay BD
            if not self.db_connection:
                self._guardar_en_archivo()

            return True, f"Configuración '{clave}' actualizada exitosamente"

        except Exception as e:
            print(f"[CONFIGURACION] Error estableciendo valor: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
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
                    FROM {self.tabla_configuracion}
                    WHERE categoria = ? AND activo = 1
                    ORDER BY clave
                """,
                    (categoria,),
                )
            except:
                # Si falla, usar sin columna activo
                cursor.execute(
                    f"""
                    SELECT clave, valor, descripcion, tipo
                    FROM {self.tabla_configuracion}
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
                    FROM {self.tabla_configuracion}
                    WHERE activo = 1
                    ORDER BY categoria, clave
                """)
            except:
                try:
                    # Sin fecha_modificacion ni activo
                    cursor.execute(f"""
                        SELECT clave, valor, descripcion, tipo, categoria
                        FROM {self.tabla_configuracion}
                        ORDER BY categoria, clave
                    """)
                except:
                    # Solo columnas básicas
                    cursor.execute(f"""
                        SELECT clave, valor
                        FROM {self.tabla_configuracion}
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

    def exportar_configuracion(self, archivo: str) -> Tuple[bool, str]:
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
                json.dump(configuraciones, f, indent=2, ensure_ascii=False, default=str)

            return True, f"Configuración exportada a '{archivo}'"

        except Exception as e:
            print(f"[ERROR CONFIGURACION] Error exportando configuración: {e}")
            return False, f"Error exportando configuración: {str(e)}"

    def importar_configuracion(
        self, archivo: str, usuario: str = "SISTEMA"
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
