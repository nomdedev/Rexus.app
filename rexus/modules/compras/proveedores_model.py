# -*- coding: utf-8 -*-
"""
Modelo de Proveedores para Compras - Rexus.app v2.0.0

Maneja la gestión completa de proveedores para el módulo de compras.
Incluye CRUD, validaciones, y funcionalidades de calificación de proveedores.
"""

import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

# Configurar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

try:
    from ...utils.security_utils import SecurityUtils
except ImportError:
    class SecurityUtils:
        @staticmethod
        def sanitize_sql_input(text):
            if not text:
                return ""
            return str(text).replace("'", "''")


class ProveedoresModel:
    """Modelo para gestionar proveedores del módulo de compras."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de proveedores.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("ProveedoresModel inicializado")
    
    def crear_proveedor(self, datos_proveedor: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo proveedor.
        
        Args:
            datos_proveedor: Datos del proveedor
            
        Returns:
            ID del proveedor creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None
            
            # Validar datos requeridos
            if not self._validar_datos_proveedor(datos_proveedor):
                return None
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos de entrada
            datos_sanitizados = self._sanitizar_datos_proveedor(datos_proveedor)
            
            cursor.execute("""
                INSERT INTO proveedores (
                    codigo, nombre, razon_social, ruc, telefono, email, 
                    direccion, contacto_principal, calificacion, activo,
                    fecha_registro, observaciones, tipo_proveedor,
                    condiciones_pago, descuento_comercial
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos_sanitizados['codigo'],
                datos_sanitizados['nombre'],
                datos_sanitizados['razon_social'],
                datos_sanitizados['ruc'],
                datos_sanitizados.get('telefono', ''),
                datos_sanitizados.get('email', ''),
                datos_sanitizados.get('direccion', ''),
                datos_sanitizados.get('contacto_principal', ''),
                datos_sanitizados.get('calificacion', 5),
                1,  # activo por defecto
                datetime.now(),
                datos_sanitizados.get('observaciones', ''),
                datos_sanitizados.get('tipo_proveedor', 'GENERAL'),
                datos_sanitizados.get('condiciones_pago', '30 días'),
                datos_sanitizados.get('descuento_comercial', 0.0)
            ))
            
            proveedor_id = cursor.lastrowid
            self.db_connection.commit()
            
            logger.info(f"Proveedor creado con ID {proveedor_id}")
            return proveedor_id
            
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None
    
    def obtener_proveedor(self, proveedor_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de un proveedor específico.
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Diccionario con datos del proveedor o None si no existe
        """
        try:
            if not self.db_connection:
                return None
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                       direccion, contacto_principal, calificacion, activo,
                       fecha_registro, observaciones, tipo_proveedor,
                       condiciones_pago, descuento_comercial
                FROM proveedores
                WHERE id = ? AND activo = 1
            """, (proveedor_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'codigo': result[1],
                    'nombre': result[2],
                    'razon_social': result[3],
                    'ruc': result[4],
                    'telefono': result[5],
                    'email': result[6],
                    'direccion': result[7],
                    'contacto_principal': result[8],
                    'calificacion': result[9],
                    'activo': result[10],
                    'fecha_registro': result[11],
                    'observaciones': result[12],
                    'tipo_proveedor': result[13],
                    'condiciones_pago': result[14],
                    'descuento_comercial': float(result[15]) if result[15] else 0.0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
            return None
    
    def obtener_proveedores(self, activos_solo: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proveedores.
        
        Args:
            activos_solo: Si True, solo devuelve proveedores activos
            
        Returns:
            Lista de proveedores
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            
            if activos_solo:
                cursor.execute("""
                    SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                           direccion, contacto_principal, calificacion, activo,
                           fecha_registro, observaciones, tipo_proveedor,
                           condiciones_pago, descuento_comercial
                    FROM proveedores
                    WHERE activo = 1
                    ORDER BY nombre
                """)
            else:
                cursor.execute("""
                    SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                           direccion, contacto_principal, calificacion, activo,
                           fecha_registro, observaciones, tipo_proveedor,
                           condiciones_pago, descuento_comercial
                    FROM proveedores
                    ORDER BY nombre
                """)
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'razon_social': row[3],
                    'ruc': row[4],
                    'telefono': row[5],
                    'email': row[6],
                    'direccion': row[7],
                    'contacto_principal': row[8],
                    'calificacion': row[9],
                    'activo': row[10],
                    'fecha_registro': row[11],
                    'observaciones': row[12],
                    'tipo_proveedor': row[13],
                    'condiciones_pago': row[14],
                    'descuento_comercial': float(row[15]) if row[15] else 0.0
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            return []
    
    def actualizar_proveedor(self, proveedor_id: int, datos_proveedor: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un proveedor.
        
        Args:
            proveedor_id: ID del proveedor
            datos_proveedor: Nuevos datos del proveedor
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            # Validar datos
            if not self._validar_datos_proveedor(datos_proveedor, proveedor_id):
                return False
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos de entrada
            datos_sanitizados = self._sanitizar_datos_proveedor(datos_proveedor)
            
            cursor.execute("""
                UPDATE proveedores 
                SET nombre = ?, razon_social = ?, ruc = ?, telefono = ?, 
                    email = ?, direccion = ?, contacto_principal = ?,
                    observaciones = ?, tipo_proveedor = ?, condiciones_pago = ?,
                    descuento_comercial = ?
                WHERE id = ? AND activo = 1
            """, (
                datos_sanitizados['nombre'],
                datos_sanitizados['razon_social'],
                datos_sanitizados['ruc'],
                datos_sanitizados.get('telefono', ''),
                datos_sanitizados.get('email', ''),
                datos_sanitizados.get('direccion', ''),
                datos_sanitizados.get('contacto_principal', ''),
                datos_sanitizados.get('observaciones', ''),
                datos_sanitizados.get('tipo_proveedor', 'GENERAL'),
                datos_sanitizados.get('condiciones_pago', '30 días'),
                datos_sanitizados.get('descuento_comercial', 0.0),
                proveedor_id
            ))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                logger.info(f"Proveedor {proveedor_id} actualizado exitosamente")
                return True
            else:
                logger.warning(f"No se pudo actualizar el proveedor {proveedor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando proveedor: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        """
        Elimina (desactiva) un proveedor.
        
        Args:
            proveedor_id: ID del proveedor a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            # Verificar que el proveedor no tenga órdenes pendientes
            if self._proveedor_tiene_ordenes_pendientes(proveedor_id):
                logger.warning(f"No se puede eliminar proveedor {proveedor_id}: tiene órdenes pendientes")
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE proveedores 
                SET activo = 0 
                WHERE id = ?
            """, (proveedor_id,))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                logger.info(f"Proveedor {proveedor_id} eliminado exitosamente")
                return True
            else:
                logger.warning(f"No se pudo eliminar el proveedor {proveedor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando proveedor: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def buscar_proveedores(self, termino: str) -> List[Dict[str, Any]]:
        """
        Busca proveedores por nombre, razón social o RUC.
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de proveedores que coinciden
        """
        try:
            if not self.db_connection:
                return []
            
            if not termino or len(termino.strip()) < 2:
                return []
            
            cursor = self.db_connection.cursor()
            termino_sanitizado = SecurityUtils.sanitize_sql_input(termino)
            termino_busqueda = f"%{termino_sanitizado}%"
            
            cursor.execute("""
                SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                       direccion, contacto_principal, calificacion
                FROM proveedores
                WHERE activo = 1 
                AND (nombre LIKE ? OR razon_social LIKE ? OR ruc LIKE ?)
                ORDER BY nombre
                LIMIT 50
            """, (termino_busqueda, termino_busqueda, termino_busqueda))
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'razon_social': row[3],
                    'ruc': row[4],
                    'telefono': row[5],
                    'email': row[6],
                    'direccion': row[7],
                    'contacto_principal': row[8],
                    'calificacion': row[9]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error buscando proveedores: {e}")
            return []
    
    def obtener_proveedores_por_tipo(self, tipo_proveedor: str) -> List[Dict[str, Any]]:
        """
        Obtiene proveedores filtrados por tipo.
        
        Args:
            tipo_proveedor: Tipo de proveedor a filtrar
            
        Returns:
            Lista de proveedores del tipo especificado
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, codigo, nombre, razon_social, ruc, calificacion
                FROM proveedores
                WHERE activo = 1 AND tipo_proveedor = ?
                ORDER BY calificacion DESC, nombre
            """, (tipo_proveedor,))
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'razon_social': row[3],
                    'ruc': row[4],
                    'calificacion': row[5]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores por tipo: {e}")
            return []
    
    def actualizar_calificacion_proveedor(self, proveedor_id: int, calificacion: float) -> bool:
        """
        Actualiza la calificación de un proveedor.
        
        Args:
            proveedor_id: ID del proveedor
            calificacion: Nueva calificación (1-10)
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            # Validar calificación
            if not 1 <= calificacion <= 10:
                logger.error("La calificación debe estar entre 1 y 10")
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE proveedores 
                SET calificacion = ? 
                WHERE id = ? AND activo = 1
            """, (calificacion, proveedor_id))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                logger.info(f"Calificación del proveedor {proveedor_id} actualizada a {calificacion}")
                return True
            else:
                logger.warning(f"No se pudo actualizar calificación del proveedor {proveedor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando calificación: {e}")
            return False
    
    def obtener_estadisticas_proveedor(self, proveedor_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un proveedor.
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            if not self.db_connection:
                return {}
            
            cursor = self.db_connection.cursor()
            
            # Estadísticas de órdenes
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_ordenes,
                    COUNT(CASE WHEN estado = 'COMPLETADA' THEN 1 END) as ordenes_completadas,
                    COUNT(CASE WHEN estado = 'CANCELADA' THEN 1 END) as ordenes_canceladas,
                    AVG(CASE WHEN estado = 'COMPLETADA' THEN total END) as promedio_orden,
                    SUM(CASE WHEN estado = 'COMPLETADA' THEN total ELSE 0 END) as total_comprado
                FROM ordenes_compra
                WHERE proveedor_id = ?
                AND fecha_creacion >= datetime('now', '-12 months')
            """, (proveedor_id,))
            
            stats = cursor.fetchone()
            if stats:
                return {
                    'total_ordenes': stats[0] or 0,
                    'ordenes_completadas': stats[1] or 0,
                    'ordenes_canceladas': stats[2] or 0,
                    'promedio_orden': float(stats[3]) if stats[3] else 0.0,
                    'total_comprado': float(stats[4]) if stats[4] else 0.0,
                    'tasa_cumplimiento': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de proveedor: {e}")
            return {}
    
    def generar_codigo_proveedor(self) -> str:
        """
        Genera un código único para un nuevo proveedor.
        
        Returns:
            Código generado
        """
        try:
            if not self.db_connection:
                return f"PROV{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM proveedores")
            count = cursor.fetchone()[0] + 1
            
            return f"PROV{count:06d}"
            
        except Exception as e:
            logger.error(f"Error generando código proveedor: {e}")
            return f"PROV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def codigo_proveedor_existe(self, codigo: str, excluir_id: int = None) -> bool:
        """
        Verifica si un código de proveedor ya existe.
        
        Args:
            codigo: Código a verificar
            excluir_id: ID de proveedor a excluir de la verificación
            
        Returns:
            True si el código existe
        """
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            
            if excluir_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM proveedores 
                    WHERE codigo = ? AND id != ?
                """, (codigo, excluir_id))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM proveedores 
                    WHERE codigo = ?
                """, (codigo,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando código proveedor: {e}")
            return False
    
    def ruc_proveedor_existe(self, ruc: str, excluir_id: int = None) -> bool:
        """
        Verifica si un RUC de proveedor ya existe.
        
        Args:
            ruc: RUC a verificar
            excluir_id: ID de proveedor a excluir de la verificación
            
        Returns:
            True si el RUC existe
        """
        try:
            if not self.db_connection or not ruc:
                return False
            
            cursor = self.db_connection.cursor()
            
            if excluir_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM proveedores 
                    WHERE ruc = ? AND id != ? AND activo = 1
                """, (ruc, excluir_id))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM proveedores 
                    WHERE ruc = ? AND activo = 1
                """, (ruc,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando RUC proveedor: {e}")
            return False
    
    # ===== MÉTODOS PRIVADOS =====
    
    def _validar_datos_proveedor(self, datos: Dict[str, Any], proveedor_id: int = None) -> bool:
        """
        Valida los datos de un proveedor.
        
        Args:
            datos: Datos a validar
            proveedor_id: ID del proveedor (para actualizaciones)
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validar campos obligatorios
            if not datos.get('nombre', '').strip():
                logger.error("El nombre del proveedor es obligatorio")
                return False
            
            if not datos.get('razon_social', '').strip():
                logger.error("La razón social es obligatoria")
                return False
            
            if not datos.get('ruc', '').strip():
                logger.error("El RUC es obligatorio")
                return False
            
            # Validar RUC único
            ruc = datos['ruc'].strip()
            if self.ruc_proveedor_existe(ruc, proveedor_id):
                logger.error(f"Ya existe un proveedor con RUC {ruc}")
                return False
            
            # Validar código único (si se proporciona)
            codigo = datos.get('codigo', '').strip()
            if codigo and self.codigo_proveedor_existe(codigo, proveedor_id):
                logger.error(f"Ya existe un proveedor con código {codigo}")
                return False
            
            # Validar email (si se proporciona)
            email = datos.get('email', '').strip()
            if email and not self._validar_email(email):
                logger.error("El formato del email es inválido")
                return False
            
            # Validar calificación
            calificacion = datos.get('calificacion', 5)
            try:
                calificacion = float(calificacion)
                if not 1 <= calificacion <= 10:
                    logger.error("La calificación debe estar entre 1 y 10")
                    return False
            except ValueError:
                logger.error("La calificación debe ser un número válido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos proveedor: {e}")
            return False
    
    def _sanitizar_datos_proveedor(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de entrada de un proveedor.
        
        Args:
            datos: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        datos_sanitizados = {}
        
        # Campos de texto
        campos_texto = [
            'codigo', 'nombre', 'razon_social', 'ruc', 'telefono', 
            'email', 'direccion', 'contacto_principal', 'observaciones',
            'tipo_proveedor', 'condiciones_pago'
        ]
        
        for campo in campos_texto:
            if campo in datos:
                datos_sanitizados[campo] = SecurityUtils.sanitize_sql_input(datos[campo])
        
        # Campos numéricos
        if 'calificacion' in datos:
            try:
                datos_sanitizados['calificacion'] = float(datos['calificacion'])
            except ValueError:
                datos_sanitizados['calificacion'] = 5.0
        
        if 'descuento_comercial' in datos:
            try:
                datos_sanitizados['descuento_comercial'] = float(datos['descuento_comercial'])
            except ValueError:
                datos_sanitizados['descuento_comercial'] = 0.0
        
        return datos_sanitizados
    
    def _validar_email(self, email: str) -> bool:
        """
        Valida el formato de un email.
        
        Args:
            email: Email a validar
            
        Returns:
            True si el formato es válido
        """
        import re
        
        if not email:
            return True  # Email es opcional
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def _proveedor_tiene_ordenes_pendientes(self, proveedor_id: int) -> bool:
        """
        Verifica si un proveedor tiene órdenes pendientes.
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            True si tiene órdenes pendientes
        """
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ordenes_compra
                WHERE proveedor_id = ? 
                AND estado IN ('BORRADOR', 'ENVIADA', 'CONFIRMADA', 'PARCIAL')
            """, (proveedor_id,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando órdenes pendientes: {e}")
            return False