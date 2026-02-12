"""
Modelo de Vidrios - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para vidrios.
Gestiona la compra por obra y asociación con proveedores.
Incluye utilidades de seguridad integradas.
"""

# Importaciones estándar
import logging
from typing import Dict, Any, Optional, List, Tuple

# Constantes del módulo
NO_CONNECTION_MSG = "No hay conexión a la base de datos"
DB_ERROR_MSG = "Error en la base de datos"
INVALID_DATA_MSG = "Datos inválidos"

# Importar utilidades requeridas
from rexus.utils.sql_script_loader import sql_script_loader
from rexus.utils.unified_sanitizer import sanitize_string

# Importar sistema unificado de sanitización
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer as data_sanitizer
    SANITIZER_AVAILABLE = True
    print("OK [VIDRIOS] Sistema unificado de sanitización cargado")
except ImportError:
    try:
        from rexus.utils.data_sanitizer import DataSanitizer
        data_sanitizer = DataSanitizer()
        SANITIZER_AVAILABLE = True
        print("OK [VIDRIOS] DataSanitizer legacy cargado")
    except ImportError:
        SANITIZER_AVAILABLE = False
        data_sanitizer = None

# Configuración de logging
logger = logging.getLogger(__name__)


class VidriosModel:
    """Modelo principal para gestión de vidrios"""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de vidrios.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_vidrios = "vidrios"
        self.tabla_vidrios_obra = "vidrios_obra"
        
        if self.db_connection:
            self._verificar_tablas()
    
    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan"""
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar tabla principal
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = '{self.tabla_vidrios}'
            """)
            
            if cursor.fetchone()[0] > 0:
                logger.info(f"OK [VIDRIOS] Tabla '{self.tabla_vidrios}' verificada correctamente.")
            else:
                logger.warning(f"ADVERTENCIA: La tabla '{self.tabla_vidrios}' no existe en la base de datos.")
                
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Verificando tablas: {e}")
    
    def _sanitizar_entrada_segura(self, value: Any, tipo: str = 'string', **kwargs) -> Any:
        """
        Sanitiza una entrada de forma segura usando el sistema unificado.
        
        Args:
            value: Valor a sanitizar
            tipo: Tipo de dato ('string', 'numeric', 'email', etc.)
            **kwargs: Parámetros adicionales
            
        Returns:
            Valor sanitizado
        """
        if not SANITIZER_AVAILABLE:
            # Fallback simple
            if tipo == 'string':
                return str(value).strip() if value else ""
            elif tipo == 'numeric':
                try:
                    return float(value) if value else 0.0
                except:
                    return 0.0
            else:
                return value
        
        try:
            if tipo == 'string':
                return data_sanitizer.sanitize_string(value, max_length=kwargs.get('max_length', 255))
            elif tipo == 'numeric':
                return data_sanitizer.sanitize_numeric(value, min_val=kwargs.get('min_val'), max_val=kwargs.get('max_val'))
            elif tipo == 'email':
                return data_sanitizer.sanitize_email(value)
            elif tipo == 'integer':
                return data_sanitizer.sanitize_integer(value, kwargs.get('min_val'), kwargs.get('max_val'))
            else:
                return value
        except Exception as e:
            logger.error(f"[ERROR VIDRIOS] Error en sanitización: {e}")
            # Fallback en caso de error
            return self._sanitizar_entrada_segura(value, tipo, **kwargs)
    
    def _sanitizar_datos_vidrio(self, datos_vidrio: dict) -> dict:
        """
        Sanitiza todos los datos de un vidrio.
        
        Args:
            datos_vidrio: Diccionario con datos del vidrio
            
        Returns:
            Diccionario con datos sanitizados
        """
        if not isinstance(datos_vidrio, dict):
            raise ValueError("datos_vidrio debe ser un diccionario")
        
        datos_limpios = {}
        
        # Sanitizar campos de texto
        datos_limpios["codigo"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("codigo", ""), 'string', max_length=50
        )
        
        datos_limpios["descripcion"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("descripcion", ""), 'string', max_length=500
        )
        
        datos_limpios["tipo"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("tipo", ""), 'string', max_length=100
        )
        
        datos_limpios["proveedor"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("proveedor", ""), 'string', max_length=200
        )
        
        datos_limpios["color"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("color", ""), 'string', max_length=100
        )
        
        datos_limpios["tratamiento"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("tratamiento", ""), 'string', max_length=100
        )
        
        datos_limpios["dimensiones_especiales"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("dimensiones_especiales", ""), 'string', max_length=200
        )
        
        datos_limpios["estado"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("estado", "activo"), 'string', max_length=20
        )
        
        datos_limpios["observaciones"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("observaciones", ""), 'string', max_length=1000
        )
        
        # Sanitizar campos numéricos
        datos_limpios["espesor"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("espesor", 0), 'numeric', min_val=0, max_val=100
        )
        
        # Sanitizar campos de precio
        for campo_precio in ["precio_unitario", "precio_metro2", "precio_compra"]:
            if campo_precio in datos_vidrio:
                precio_limpio = self._sanitizar_entrada_segura(
                    datos_vidrio[campo_precio], 'numeric', min_val=0
                )
                datos_limpios[campo_precio] = precio_limpio
        
        return datos_limpios
    
    def crear_vidrio(self, datos_vidrio: dict) -> Tuple[bool, str, Optional[int]]:
        """
        Crea un nuevo vidrio en el sistema.
        
        Args:
            datos_vidrio: Diccionario con datos del vidrio
            
        Returns:
            Tuple con (éxito, mensaje, id_vidrio)
        """
        if not self.db_connection:
            return False, NO_CONNECTION_MSG, None
        
        try:
            # Sanitizar datos
            datos_sanitizados = self._sanitizar_datos_vidrio(datos_vidrio)
            
            # Validar datos requeridos
            if not datos_sanitizados.get("codigo"):
                return False, "El código del vidrio es requerido", None
            
            if not datos_sanitizados.get("descripcion"):
                return False, "La descripción del vidrio es requerida", None
            
            # Verificar si ya existe
            if self.verificar_vidrio_existe(datos_sanitizados["codigo"]):
                return False, f"Ya existe un vidrio con código '{datos_sanitizados['codigo']}'", None
            
            # Insertar vidrio
            cursor = self.db_connection.cursor()
            
            query = f"""
                INSERT INTO {self.tabla_vidrios} 
                (codigo, descripcion, tipo, proveedor, color, tratamiento, 
                 dimensiones_especiales, espesor, precio_unitario, precio_metro2, 
                 precio_compra, estado, observaciones, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """
            
            valores = (
                datos_sanitizados["codigo"],
                datos_sanitizados["descripcion"],
                datos_sanitizados["tipo"],
                datos_sanitizados["proveedor"],
                datos_sanitizados["color"],
                datos_sanitizados["tratamiento"],
                datos_sanitizados["dimensiones_especiales"],
                datos_sanitizados["espesor"],
                datos_sanitizados.get("precio_unitario", 0),
                datos_sanitizados.get("precio_metro2", 0),
                datos_sanitizados.get("precio_compra", 0),
                datos_sanitizados["estado"],
                datos_sanitizados["observaciones"]
            )
            
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            # Obtener ID del vidrio insertado
            cursor.execute("SELECT @@IDENTITY")
            id_vidrio = cursor.fetchone()[0]
            
            logger.info(f"OK [VIDRIOS] Vidrio creado: {datos_sanitizados['codigo']} (ID: {id_vidrio})")
            
            return True, f"Vidrio '{datos_sanitizados['codigo']}' creado correctamente", id_vidrio
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"{DB_ERROR_MSG}: {str(e)}", None
    
    def verificar_vidrio_existe(self, codigo: str) -> bool:
        """
        Verifica si un vidrio existe por su código.
        
        Args:
            codigo: Código del vidrio a verificar
            
        Returns:
            True si existe, False si no
        """
        if not self.db_connection or not codigo:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_vidrios} WHERE codigo = ?", (codigo,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Verificando existencia: {e}")
            return False
    
    def obtener_vidrio_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un vidrio por su código.
        
        Args:
            codigo: Código del vidrio
            
        Returns:
            Diccionario con datos del vidrio o None si no existe
        """
        if not self.db_connection or not codigo:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM {self.tabla_vidrios} WHERE codigo = ?", (codigo,))
            
            row = cursor.fetchone()
            if row:
                # Convertir a diccionario
                columnas = [desc[0] for desc in cursor.description]
                return dict(zip(columnas, row))
            
            return None
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo vidrio por código: {e}")
            return None
    
    def obtener_todos_vidrios(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene todos los vidrios del sistema.
        
        Args:
            solo_activos: Si es True, solo devuelve vidrios activos
            
        Returns:
            Lista de diccionarios con datos de vidrios
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            query = f"SELECT * FROM {self.tabla_vidrios}"
            if solo_activos:
                query += " WHERE estado = 'activo'"
            query += " ORDER BY codigo"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if rows:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, row)) for row in rows]
            
            return []
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo todos los vidrios: {e}")
            return []
    
    def actualizar_vidrio(self, codigo: str, datos_actualizacion: dict) -> Tuple[bool, str]:
        """
        Actualiza los datos de un vidrio.
        
        Args:
            codigo: Código del vidrio a actualizar
            datos_actualizacion: Diccionario con datos a actualizar
            
        Returns:
            Tuple con (éxito, mensaje)
        """
        if not self.db_connection or not codigo:
            return False, NO_CONNECTION_MSG
        
        try:
            # Verificar que el vidrio existe
            if not self.verificar_vidrio_existe(codigo):
                return False, f"No existe un vidrio con código '{codigo}'"
            
            # Sanitizar datos
            datos_sanitizados = self._sanitizar_datos_vidrio(datos_actualizacion)
            
            # Construir query de actualización
            campos_actualizar = []
            valores = []
            
            for campo, valor in datos_sanitizados.items():
                if campo != "codigo":  # No actualizar el código
                    campos_actualizar.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos_actualizar:
                return False, "No hay campos válidos para actualizar"
            
            # Agregar fecha de actualización
            campos_actualizar.append("fecha_actualizacion = GETDATE()")
            
            # Agregar código al WHERE
            valores.append(codigo)
            
            query = f"""
                UPDATE {self.tabla_vidrios}
                SET {', '.join(campos_actualizar)}
                WHERE codigo = ?
            """
            
            cursor = self.db_connection.cursor()
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            logger.info(f"OK [VIDRIOS] Vidrio actualizado: {codigo}")
            return True, f"Vidrio '{codigo}' actualizado correctamente"
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Actualizando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"{DB_ERROR_MSG}: {str(e)}"
    
    def eliminar_vidrio(self, codigo: str, eliminacion_logica: bool = True) -> Tuple[bool, str]:
        """
        Elimina un vidrio del sistema.
        
        Args:
            codigo: Código del vidrio a eliminar
            eliminacion_logica: Si es True, solo marca como inactivo
            
        Returns:
            Tuple con (éxito, mensaje)
        """
        if not self.db_connection or not codigo:
            return False, NO_CONNECTION_MSG
        
        try:
            # Verificar que el vidrio existe
            if not self.verificar_vidrio_existe(codigo):
                return False, f"No existe un vidrio con código '{codigo}'"
            
            cursor = self.db_connection.cursor()
            
            if eliminacion_logica:
                # Eliminación lógica
                cursor.execute(f"""
                    UPDATE {self.tabla_vidrios}
                    SET estado = 'inactivo', fecha_actualizacion = GETDATE()
                    WHERE codigo = ?
                """, (codigo,))
                mensaje = f"Vidrio '{codigo}' marcado como inactivo"
            else:
                # Eliminación física
                cursor.execute(f"DELETE FROM {self.tabla_vidrios} WHERE codigo = ?", (codigo,))
                mensaje = f"Vidrio '{codigo}' eliminado permanentemente"
            
            self.db_connection.commit()
            logger.info(f"OK [VIDRIOS] {mensaje}")
            
            return True, mensaje
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Eliminando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"{DB_ERROR_MSG}: {str(e)}"


# Clase de compatibilidad para mantener la interfaz anterior
class ModeloVidrios(VidriosModel):
    """Clase de compatibilidad para el modelo de vidrios"""
    pass
