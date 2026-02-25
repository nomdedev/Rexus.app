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
                numeric_val = data_sanitizer.sanitize_numeric(value)
                if numeric_val is None:
                    return 0.0

                min_val = kwargs.get('min_val')
                max_val = kwargs.get('max_val')

                if min_val is not None and numeric_val < min_val:
                    numeric_val = min_val
                if max_val is not None and numeric_val > max_val:
                    numeric_val = max_val

                return float(numeric_val)
            elif tipo == 'email':
                return data_sanitizer.sanitize_email(value)
            elif tipo == 'integer':
                return data_sanitizer.sanitize_integer(value, kwargs.get('min_val'), kwargs.get('max_val'))
            else:
                return value
        except Exception as e:
            logger.error(f"[ERROR VIDRIOS] Error en sanitización: {e}")
            # Fallback en caso de error (sin recursión)
            if tipo == 'string':
                return str(value).strip() if value else ""
            if tipo in ('numeric', 'integer'):
                try:
                    return float(value) if tipo == 'numeric' else int(float(value))
                except Exception:
                    return 0.0 if tipo == 'numeric' else 0
            return value
    
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
    
    def crear_vidrio(self, datos_vidrio: dict):
        """
        Crea un nuevo vidrio en el sistema.
        
        Args:
            datos_vidrio: Diccionario con datos del vidrio
            
        Returns:
            Tuple con (éxito, mensaje, id_vidrio)
        """
        if not self.db_connection:
            return False
        
        try:
            # Sanitizar datos
            datos_sanitizados = self._sanitizar_datos_vidrio(datos_vidrio)
            
            # Validar datos requeridos
            if not datos_sanitizados.get("codigo"):
                return False
            
            if not datos_sanitizados.get("descripcion"):
                return False
            
            # Verificar si ya existe
            if self.verificar_vidrio_existe(datos_sanitizados["codigo"]):
                return False
            
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
            
            return id_vidrio
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
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
    
    def actualizar_vidrio(self, codigo: str, datos_actualizacion: dict) -> bool:
        """
        Actualiza los datos de un vidrio.
        
        Args:
            codigo: Código del vidrio a actualizar
            datos_actualizacion: Diccionario con datos a actualizar
            
        Returns:
            bool
        """
        if not self.db_connection or not codigo:
            return False
        
        try:
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
                return False
            
            # Agregar fecha de actualización
            campos_actualizar.append("fecha_actualizacion = GETDATE()")
            
            # Agregar código al WHERE
            valores.append(codigo)

            campo_where = "codigo"
            if isinstance(codigo, int):
                campo_where = "id"
            
            query = f"""
                UPDATE {self.tabla_vidrios}
                SET {', '.join(campos_actualizar)}
                WHERE {campo_where} = ?
            """
            
            cursor = self.db_connection.cursor()
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            logger.info(f"OK [VIDRIOS] Vidrio actualizado: {codigo}")
            return True
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Actualizando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def eliminar_vidrio(self, codigo: str, eliminacion_logica: bool = True) -> bool:
        """
        Elimina un vidrio del sistema.
        
        Args:
            codigo: Código del vidrio a eliminar
            eliminacion_logica: Si es True, solo marca como inactivo
            
        Returns:
            bool
        """
        if not self.db_connection or not codigo:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            campo_where = "codigo"
            if isinstance(codigo, int):
                campo_where = "id"
            
            if eliminacion_logica:
                # Eliminación lógica
                cursor.execute(f"""
                    UPDATE {self.tabla_vidrios}
                    SET estado = 'inactivo', fecha_actualizacion = GETDATE()
                    WHERE {campo_where} = ?
                """, (codigo,))
                mensaje = f"Vidrio '{codigo}' marcado como inactivo"
            else:
                # Eliminación física
                cursor.execute(f"DELETE FROM {self.tabla_vidrios} WHERE {campo_where} = ?", (codigo,))
                mensaje = f"Vidrio '{codigo}' eliminado permanentemente"
            
            self.db_connection.commit()
            logger.info(f"OK [VIDRIOS] {mensaje}")
            
            return True
            
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Eliminando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_vidrios(self) -> List[Dict[str, Any]]:
        """Compatibilidad legacy: obtiene listado de vidrios."""
        return self.obtener_todos_vidrios(solo_activos=False)

    def obtener_vidrio_por_id(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """Compatibilidad legacy: obtiene un vidrio por ID."""
        if not self.db_connection:
            return None
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM {self.tabla_vidrios} WHERE id = ?", (vidrio_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [desc[0] for desc in cursor.description]
            return dict(zip(columnas, row))
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo vidrio por ID: {e}")
            return None

    def obtener_vidrios_por_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Compatibilidad legacy: obtiene vidrios por obra."""
        if not self.db_connection:
            return []
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM {self.tabla_vidrios} WHERE obra_id = ?", (obra_id,))
            rows = cursor.fetchall()
            if not rows:
                return []
            if cursor.description:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, row)) for row in rows]
            return rows
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo vidrios por obra: {e}")
            return []

    def calcular_area_vidrio(self, ancho_mm: float, alto_mm: float) -> float:
        """Calcula área en m2 a partir de dimensiones en mm."""
        try:
            ancho = float(ancho_mm)
            alto = float(alto_mm)
            if ancho <= 0 or alto <= 0:
                return 0
            return round((ancho / 1000.0) * (alto / 1000.0), 2)
        except Exception:
            return 0

    def obtener_tipos_vidrio(self) -> List[str]:
        """Compatibilidad legacy: obtiene tipos de vidrio únicos."""
        if not self.db_connection:
            return []
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT DISTINCT tipo FROM {self.tabla_vidrios} ORDER BY tipo")
            rows = cursor.fetchall() or []
            return [row[0] for row in rows if row and row[0] is not None]
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo tipos de vidrio: {e}")
            return []

    def validar_datos_vidrio(self, datos_vidrio: dict) -> bool:
        """Compatibilidad legacy: valida datos mínimos de un vidrio."""
        if not isinstance(datos_vidrio, dict):
            return False
        if not datos_vidrio.get('tipo'):
            return False
        for campo in ('espesor', 'ancho', 'alto'):
            if campo in datos_vidrio:
                try:
                    if float(datos_vidrio[campo]) <= 0:
                        return False
                except Exception:
                    return False
        return True

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Compatibilidad legacy: retorna estadísticas agregadas de vidrios."""
        if not self.db_connection:
            return {
                'total_vidrios': 0,
                'area_total': 0,
                'espesor_promedio': 0,
                'precio_promedio': 0,
            }
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                f"SELECT COUNT(*), SUM(1.0), AVG(espesor), AVG(precio_unitario) FROM {self.tabla_vidrios}"
            )
            row = cursor.fetchone() or (0, 0, 0, 0)
            return {
                'total_vidrios': row[0] or 0,
                'area_total': row[1] or 0,
                'espesor_promedio': row[2] or 0,
                'precio_promedio': row[3] or 0,
            }
        except Exception as e:
            logger.error(f"ERROR [VIDRIOS] Obteniendo estadísticas: {e}")
            return {
                'total_vidrios': 0,
                'area_total': 0,
                'espesor_promedio': 0,
                'precio_promedio': 0,
            }


# Clase de compatibilidad para mantener la interfaz anterior
class ModeloVidrios(VidriosModel):
    """Clase de compatibilidad para el modelo de vidrios"""
    pass
