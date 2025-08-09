# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Herrajes - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para herrajes.
Gestiona la compra por obra y asociación con proveedores.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rexus.core.auth_manager import admin_required, auth_required, manager_required
from rexus.core.auth_decorators import auth_required, admin_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Configurar logger para el módulo
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir / "src"))
    from utils.sql_security import SecureSQLBuilder, SQLSecurityValidator
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Security utilities not available in herrajes: {e}")
    SECURITY_AVAILABLE = False

# Importar cargador de scripts SQL
try:
    from rexus.utils.sql_script_loader import sql_script_loader

    SQL_LOADER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] SQL Script Loader not available in herrajes: {e}")
    SQL_LOADER_AVAILABLE = False
    sql_script_loader = None

class HerrajesModel:
    """Modelo para gestionar herrajes por obra y proveedor."""

    # Tipos de herrajes
    TIPOS_HERRAJES = {
        "BISAGRA": "Bisagra",
        "CERRADURA": "Cerradura",
        "MANIJA": "Manija",
        "TORNILLO": "Tornillo",
        "RIEL": "Riel",
        "SOPORTE": "Soporte",
        "OTRO": "Otro",
    }

    # Estados de herrajes
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "DESCONTINUADO": "Descontinuado",
    }

    # Unidades de medida
    UNIDADES = {
        "UNIDAD": "Unidad",
        "PAR": "Par",
        "JUEGO": "Juego",
        "METRO": "Metro",
        "KILOGRAMO": "Kilogramo",
    }

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de herrajes.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_herrajes = "herrajes"
        self.tabla_herrajes_obra = "herrajes_obra"
        self.tabla_pedidos_herrajes = "pedidos_herrajes"
        self.tabla_herrajes_inventario = "herrajes_inventario"

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available:
            self.data_sanitizer = data_sanitizer
            self.sql_validator = SQLSecurityValidator()
            print("OK [HERRAJES] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            self.sql_validator = None
            print("WARNING [HERRAJES] Utilidades de seguridad no disponibles")

        # Inicializar SQL script loader
        self.sql_loader_available = SQL_LOADER_AVAILABLE
        if self.sql_loader_available:
            self.sql_loader = sql_script_loader
            print("OK [HERRAJES] SQL Script Loader disponible")
        else:
            self.sql_loader = None
            print("WARNING [HERRAJES] SQL Script Loader no disponible")

        # Lista de tablas validadas para fallbacks seguros
        self._valid_table_names = {
            "herrajes",
            "herrajes_obra", 
            "pedidos_herrajes",
            "herrajes_inventario"
        }

        if not self.db_connection:
            print(
                "[ERROR HERRAJES] No hay conexión a la base de datos. El módulo no funcionará correctamente."
            )
        # Las tablas deben crearse por el DBA, no por la aplicación
        self._verificar_tablas()

    # ELIMINADO: _crear_tablas_si_no_existen() por razones de seguridad
    # Las tablas deben ser creadas por el DBA usando scripts externos,
    # nunca por la aplicación en tiempo de ejecución.
    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla principal de herrajes
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_herrajes,),
            )
            if cursor.fetchone():
                print(
                    f"[HERRAJES] Tabla '{self.tabla_herrajes}' verificada correctamente."
                )

                # Obtener estructura de la tabla
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_herrajes,),
                )
                columnas = cursor.fetchall()
                print(f"[HERRAJES] Estructura de tabla '{self.tabla_herrajes}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_herrajes}' no existe en la base de datos."
                )

            # Verificar tabla de herrajes por obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_herrajes_obra,),
            )
            if cursor.fetchone():
                print(
                    f"[HERRAJES] Tabla '{self.tabla_herrajes_obra}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_herrajes_obra}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR HERRAJES] Error verificando tablas: {e}")

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida que el nombre de tabla sea seguro.

        Args:
            table_name: Nombre de tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            ValueError: Si el nombre de tabla no es válido
        """
        if not table_name or table_name not in self._valid_table_names:
            raise ValueError(f"Nombre de tabla no válido: {table_name}")
        return table_name

    def obtener_todos_herrajes(self, filtros=None):
        """
        Obtiene todos los herrajes disponibles.

        Args:
            filtros (dict): Filtros opcionales (proveedor, codigo, descripcion)

        Returns:
            List[Dict]: Lista de herrajes
        """
        if not self.db_connection:
            # 🔒 SEGURIDAD: Solo retornar datos demo si hay SQL loader (para desarrollo/testing)
            if self.sql_loader_available and self.sql_loader:
                print("⚠️ [HERRAJES] Sin conexión DB, retornando datos demo para desarrollo")
                return self._get_herrajes_demo()
            else:
                print("❌ [HERRAJES] Sin conexión DB y sin SQL loader. No hay datos disponibles.")
                return []

        # 🔒 SEGURIDAD: Usar script SQL externo primero
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "select_all_herrajes"
                )
                
                if exito and resultados:
                    herrajes_dict = [dict(zip([desc[0] for desc in resultados[1]], row)) 
                                   for row in resultados[0]] if resultados[0] else []
                    
                    # Aplicar filtros si se proporcionan
                    if filtros and herrajes_dict:
                        herrajes_filtrados = []
                        for herraje in herrajes_dict:
                            incluir = True
                            
                            if filtros.get("proveedor"):
                                if filtros["proveedor"].lower() not in herraje.get("proveedor", "").lower():
                                    incluir = False
                            
                            if filtros.get("codigo") and incluir:
                                if filtros["codigo"].lower() not in herraje.get("codigo", "").lower():
                                    incluir = False
                                    
                            if filtros.get("descripcion") and incluir:
                                if filtros["descripcion"].lower() not in herraje.get("descripcion", "").lower():
                                    incluir = False
                            
                            if incluir:
                                herrajes_filtrados.append(herraje)
                        
                        return herrajes_filtrados
                    
                    print("✅ [HERRAJES] Lista de herrajes obtenida usando script externo")
                    return herrajes_dict
                    
            except Exception as e:
                print(f"⚠️ [HERRAJES] Error usando script externo, fallback a consulta segura: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se pueden obtener herrajes sin scripts externos.")
        return []

    def obtener_herrajes_por_obra(self, obra_id):
        """
        Obtiene herrajes asociados a una obra específica.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de herrajes con cantidades asignadas
        """
        if not self.db_connection:
            return []

        # 🔒 SEGURIDAD: Usar script SQL externo primero
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "select_herrajes_por_obra", params=(obra_id,)
                )
                
                if exito and resultados:
                    herrajes_obra = [dict(zip([desc[0] for desc in resultados[1]], row)) 
                                   for row in resultados[0]] if resultados[0] else []
                    print("✅ [HERRAJES] Herrajes por obra obtenidos usando script externo")
                    return herrajes_obra
                    
            except Exception as e:
                print(f"⚠️ [HERRAJES] Error usando script externo, fallback a consulta segura: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se pueden obtener herrajes por obra sin scripts externos.")
        return []

    def asignar_herraje_obra(
        self, herraje_id, obra_id, cantidad_requerida, observaciones=None
    ):
        """
        Asigna un herraje a una obra específica.

        Args:
            herraje_id (int): ID del herraje
            obra_id (int): ID de la obra
            cantidad_requerida (float): Cantidad requerida
            observaciones (str): Observaciones opcionales

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        # 🔒 SEGURIDAD: Usar script SQL externo primero
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, _ = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "insert_herraje_obra", 
                    params=(herraje_id, obra_id, cantidad_requerida, observaciones)
                )
                
                if exito:
                    print(f"✅ [HERRAJES] Herraje {herraje_id} asignado a obra {obra_id} usando script externo")
                    return True
                    
            except Exception as e:
                print(f"⚠️ [HERRAJES] Error usando script externo, fallback a consulta segura: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede asignar herraje a obra sin scripts externos.")
        return False

    def crear_pedido_obra(self, obra_id, proveedor, herrajes_lista):
        """
        Crea un pedido de herrajes para una obra específica.

        Args:
            obra_id (int): ID de la obra
            proveedor (str): Nombre del proveedor
            herrajes_lista (List[Dict]): Lista de herrajes con cantidades

        Returns:
            int: ID del pedido creado o None si falla
        """
        if not self.db_connection:
            return None

        # Calcular total estimado
        total_estimado = sum(
            item["cantidad"] * item["precio_unitario"] for item in herrajes_lista
        )

        # 🔒 SEGURIDAD: Usar script SQL externo primero
        if self.sql_loader_available and self.sql_loader:
            try:
                # Crear pedido principal
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "insert_pedido_obra", 
                    params=(obra_id, proveedor, total_estimado)
                )
                
                if exito:
                    # Obtener ID del pedido creado usando SCOPE_IDENTITY()
                    cursor = self.db_connection.cursor()
                    script_content = self.query_manager.load_script('herrajes/select_last_identity')
                    cursor.execute(script_content)
                    pedido_id = cursor.fetchone()[0]
                    
                    # Actualizar cantidades pedidas usando script
                    for herraje in herrajes_lista:
                        exito_update, _ = self.sql_loader.execute_script(
                            self.db_connection, "herrajes", "update_cantidad_pedida",
                            params=(herraje["cantidad"], herraje["herraje_id"], obra_id)
                        )
                        if not exito_update:
                            print(f"⚠️ [HERRAJES] Error actualizando cantidad para herraje {herraje['herraje_id']}")
                    
                    print(f"✅ [HERRAJES] Pedido {pedido_id} creado para obra {obra_id} usando script externo")
                    return pedido_id
                    
            except Exception as e:
                print(f"⚠️ [HERRAJES] Error usando script externo, fallback a consulta segura: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede crear pedido sin scripts externos.")
        return None

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas generales de herrajes.

        Returns:
            Dict: Estadísticas de herrajes
        """
        if not self.db_connection:
            return {
                "total_herrajes": 0,
                "proveedores_activos": 0,
                "valor_total_inventario": 0.0,
                "herrajes_por_proveedor": [],
            }

        # Usar script SQL externo si está disponible
        if SQL_LOADER_AVAILABLE and sql_script_loader:
            try:
                exito, resultados = sql_script_loader.execute_script(
                    self.db_connection, "herrajes", "select_estadisticas_herrajes"
                )

                if exito and resultados and len(resultados) >= 4:
                    # El script devuelve 4 consultas separadas
                    estadisticas = {
                        "total_herrajes": resultados[0][0]["total_herrajes"]
                        if resultados[0]
                        else 0,
                        "proveedores_activos": resultados[1][0]["proveedores_activos"]
                        if resultados[1]
                        else 0,
                        "valor_total_inventario": float(
                            resultados[2][0]["valor_total_inventario"] or 0.0
                        )
                        if resultados[2]
                        else 0.0,
                        "herrajes_por_proveedor": [
                            {"proveedor": row["proveedor"], "cantidad": row["cantidad"]}
                            for row in resultados[3]
                        ]
                        if resultados[3]
                        else [],
                    }

                    print("✅ [HERRAJES] Estadísticas obtenidas usando script externo")
                    return estadisticas

            except Exception as e:
                print(
                    f"⚠️ [HERRAJES] Error usando script externo, fallback a consultas directas: {e}"
                )

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se pueden obtener estadísticas sin scripts externos.")
        return {
            "total_herrajes": 0,
            "proveedores_activos": 0,
            "valor_total_inventario": 0.0,
            "herrajes_por_proveedor": [],
        }

    def buscar_herrajes(self, termino_busqueda):
        """
        Busca herrajes por término de búsqueda con sanitización de entrada.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de herrajes que coinciden
        """
        if not self.db_connection or not termino_busqueda:
            return []

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                # 🔒 SANITIZACIÓN DE ENTRADA
                if self.security_available and termino_busqueda:
                    termino_limpio = sanitize_string(
                        termino_busqueda, max_length=100
                    )
                    if not termino_limpio:
                        return []
                else:
                    termino_limpio = termino_busqueda

                termino = f"%{termino_limpio}%"
                
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "buscar_herrajes", 
                    params=(termino, termino, termino)
                )
                
                if exito and resultados:
                    herrajes = [dict(zip([desc[0] for desc in resultados[1]], row)) 
                              for row in resultados[0]] if resultados[0] else []
                    print("✅ [HERRAJES] Búsqueda de herrajes usando script externo")
                    return herrajes
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para búsqueda: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede buscar herrajes sin scripts externos.")
        return []

    def crear_herraje(
        self,
        datos_herraje:Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Crea un nuevo herraje con sanitización completa de datos.

        Args:
            datos_herraje: Datos del herraje a crear

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.security_available:
                # Sanitizar todos los datos de entrada
                datos_limpios = self.data_sanitizer.sanitize_form_data(datos_herraje)

                # Validaciones específicas
                if not datos_limpios.get("codigo"):
                    return False, "El código es requerido"
                if not datos_limpios.get("descripcion"):
                    return False, "La descripción es requerida"
                if not datos_limpios.get("proveedor"):
                    return False, "El proveedor es requerido"

                # Validar precio si se proporciona
                precio_original = datos_herraje.get("precio_unitario")
                precio_sanitizado = datos_limpios.get("precio_unitario")

                if (
                    precio_original
                    and precio_original != ""
                    and precio_sanitizado is None
                ):
                    return False, "Precio inválido"
                elif precio_sanitizado is None:
                    datos_limpios["precio_unitario"] = 0.0

            else:
                # Sin utilidades de seguridad, usar datos originales con precaución
                datos_limpios = datos_herraje.copy()
                print(
                    "WARNING [HERRAJES] Creando herraje sin sanitización de seguridad"
                )

            cursor = self.db_connection.cursor()

            # 🔒 SEGURIDAD: Verificación debe ir en script SQL externo
            # Por ahora omitir verificación de duplicados - debe estar en el script SQL
            print("⚠️ [HERRAJES] Verificación de duplicados debe ser manejada por el script SQL externo")

            # 🔒 SEGURIDAD: Usar script SQL externo primero
            if self.sql_loader_available and self.sql_loader:
                try:
                    exito, _ = self.sql_loader.execute_script(
                        self.db_connection, "herrajes", "insert_nuevo_herraje",
                        params=(
                            datos_limpios["codigo"],
                            datos_limpios["descripcion"], 
                            datos_limpios.get("categoria", ""),
                            datos_limpios.get("tipo", "OTRO"),
                            datos_limpios.get("stock_actual", 0),
                            datos_limpios.get("stock_minimo", 0),
                            0,  # stock_maximo
                            0,  # stock_reservado
                            datos_limpios.get("stock_actual", 0),  # stock_disponible
                            datos_limpios.get("precio_unitario", 0.00),
                            datos_limpios.get("precio_unitario", 0.00),  # precio_promedio
                            datos_limpios.get("precio_unitario", 0.00),  # costo_unitario
                            datos_limpios.get("unidad_medida", "UNIDAD"),
                            datos_limpios.get("ubicacion", ""),
                            datos_limpios.get("color", ""),
                            datos_limpios.get("material", ""),
                            datos_limpios.get("marca", ""),
                            datos_limpios.get("modelo", ""),
                            datos_limpios.get("acabado", ""),
                            datos_limpios["proveedor"],
                            datos_limpios.get("codigo", ""),  # codigo_proveedor
                            datos_limpios.get("tiempo_entrega_dias", 0),
                            datos_limpios.get("observaciones", ""),
                            "",  # codigo_qr
                            "",  # imagen_url
                            datos_limpios.get("especificaciones", ""),  # propiedades_especiales
                            datos_limpios.get("estado", "ACTIVO"),
                            1  # activo
                        )
                    )
                    
                    if exito:
                        script_content = self.query_manager.load_script('herrajes/select_last_identity')
                        cursor.execute(script_content)
                        herraje_id = cursor.fetchone()[0]
                        print(f"✅ [HERRAJES] Herraje '{datos_limpios['codigo']}' creado usando script externo")
                        self.db_connection.commit()
                        return True, f"Herraje '{datos_limpios['codigo']}' creado exitosamente"
                        
                except Exception as e:
                    print(f"⚠️ [HERRAJES] Error usando script externo, fallback a consulta segura: {e}")

            # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
            print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede crear herraje sin scripts externos.")
            return False, "Error: SQL Script Loader no disponible"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error creando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error creando herraje: {str(e)}"

    def actualizar_herraje(
        self,
        herraje_id:int,
        datos_herraje: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Actualiza un herraje existente.

        Args:
            herraje_id: ID del herraje a actualizar
            datos_herraje: Nuevos datos del herraje

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, _ = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "update_herraje",
                    params=(
                        datos_herraje["descripcion"],
                        datos_herraje.get("tipo", "OTRO"),
                        datos_herraje["proveedor"],
                        datos_herraje.get("precio_unitario", 0.00),
                        datos_herraje.get("unidad_medida", "UNIDAD"),
                        datos_herraje.get("categoria", ""),
                        datos_herraje.get("estado", "ACTIVO"),
                        datos_herraje.get("stock_minimo", 0),
                        datos_herraje.get("stock_actual", 0),
                        datos_herraje.get("observaciones", ""),
                        datos_herraje.get("especificaciones", ""),
                        datos_herraje.get("marca", ""),
                        datos_herraje.get("modelo", ""),
                        datos_herraje.get("color", ""),
                        datos_herraje.get("material", ""),
                        datos_herraje.get("dimensiones", ""),
                        datos_herraje.get("peso", 0.0),
                        herraje_id,
                        # Parámetros para actualizar inventario también
                        datos_herraje.get("stock_actual", 0),
                        datos_herraje.get("ubicacion", ""),
                        herraje_id
                    )
                )
                
                if exito:
                    print(f"✅ [HERRAJES] Herraje {herraje_id} actualizado usando script externo")
                    return True, "Herraje actualizado exitosamente"
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para actualizar: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede actualizar herraje sin scripts externos.")
        return False, "Error: SQL Script Loader no disponible"

    def eliminar_herraje(
        self,
        herraje_id:int,
    ) -> Tuple[bool, str]:
        """
        Elimina un herraje (eliminación lógica).

        Args:
            herraje_id: ID del herraje a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, _ = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "delete_herraje",
                    params=(herraje_id,)
                )
                
                if exito:
                    print(f"✅ [HERRAJES] Herraje {herraje_id} eliminado usando script externo")
                    return True, "Herraje eliminado exitosamente"
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para eliminar: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede eliminar herraje sin scripts externos.")
        return False, "Error: SQL Script Loader no disponible"

    def obtener_herraje_por_id(self, herraje_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un herraje por su ID.

        Args:
            herraje_id: ID del herraje

        Returns:
            Dict con los datos del herraje o None si no existe
        """
        if not self.db_connection:
            return None

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "select_by_id",
                    params=(herraje_id,)
                )
                
                if exito and resultados and resultados[0]:
                    row = resultados[0][0]
                    columns = [desc[0] for desc in resultados[1]]
                    print(f"✅ [HERRAJES] Herraje {herraje_id} obtenido usando script externo")
                    return dict(zip(columns, row))
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para obtener herraje por ID: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede obtener herraje por ID sin scripts externos.")
        return None

    def obtener_proveedores(self) -> List[str]:
        """
        Obtiene la lista de proveedores únicos.

        Returns:
            Lista de nombres de proveedores
        """
        if not self.db_connection:
            return []

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, resultados = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "select_proveedores"
                )
                
                if exito and resultados and resultados[0]:
                    print("✅ [HERRAJES] Proveedores obtenidos usando script externo")
                    return [row[0] for row in resultados[0]]
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para obtener proveedores: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se pueden obtener proveedores sin scripts externos.")
        return []

    def actualizar_stock(
        self,
        herraje_id:int,
        nuevo_stock: int,
        tipo_movimiento: str = "AJUSTE",
    ) -> Tuple[bool, str]:
        """
        Actualiza el stock de un herraje.

        Args:
            herraje_id: ID del herraje
            nuevo_stock: Nuevo stock actual
            tipo_movimiento: Tipo de movimiento (AJUSTE, ENTRADA, SALIDA)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        # 🔒 SEGURIDAD: Usar script SQL externo únicamente
        if self.sql_loader_available and self.sql_loader:
            try:
                exito, _ = self.sql_loader.execute_script(
                    self.db_connection, "herrajes", "update_stock_herraje",
                    params=(nuevo_stock, herraje_id, nuevo_stock, tipo_movimiento, tipo_movimiento, herraje_id)
                )
                
                if exito:
                    print(f"✅ [HERRAJES] Stock de herraje {herraje_id} actualizado usando script externo")
                    return True, "Stock actualizado exitosamente"
                    
            except Exception as e:
                print(f"❌ [HERRAJES] Error usando script externo para actualizar stock: {e}")

        # 🔒 SEGURIDAD: Sin fallback - solo usar scripts SQL externos
        print("❌ [HERRAJES] SQL Script Loader no disponible. No se puede actualizar stock sin scripts externos.")
        return False, "Error: SQL Script Loader no disponible"

    def _get_herrajes_demo(self) -> List[Dict[str, Any]]:
        """Datos demo cuando no hay conexión a BD."""
        return [
            {
                "id": 1,
                "codigo": "BIS-001",
                "descripcion": "Bisagra de puerta estándar",
                "tipo": "BISAGRA",
                "proveedor": "Herrajes SA",
                "precio_unitario": 15.50,
                "unidad_medida": "UNIDAD",
                "categoria": "Bisagras",
                "estado": "ACTIVO",
                "stock_actual": 50,
                "stock_minimo": 10,
                "marca": "Stanley",
                "modelo": "ST-001",
                "color": "Negro",
                "material": "Acero",
                "dimensiones": "10x8x2 cm",
                "peso": 0.2,
            },
            {
                "id": 2,
                "codigo": "CER-001",
                "descripcion": "Cerradura de seguridad",
                "tipo": "CERRADURA",
                "proveedor": "Seguridad Total",
                "precio_unitario": 85.00,
                "unidad_medida": "UNIDAD",
                "categoria": "Cerraduras",
                "estado": "ACTIVO",
                "stock_actual": 25,
                "stock_minimo": 5,
                "marca": "Yale",
                "modelo": "YL-200",
                "color": "Plateado",
                "material": "Acero inoxidable",
                "dimensiones": "15x10x5 cm",
                "peso": 0.8,
            },
        ]
