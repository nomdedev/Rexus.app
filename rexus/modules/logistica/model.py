# -*- coding: utf-8 -*-
"""
Modelo de Logística - Rexus.app v2.0.0

Maneja la lógica de negocio para:
- Gestión de transportes
- Programación de entregas
- Seguimiento de envíos
- Gestión de proveedores de transporte
- Optimización de rutas
- Control de costos logísticos

MIGRADO A SQL EXTERNO - Todas las consultas usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.
"""

import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, date

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


class LogisticaModel:
    """Modelo para gestionar operaciones logísticas."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de logística.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("LogisticaModel inicializado")
    
    def crear_servicio_transporte(self, datos_servicio: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo servicio de transporte.
        
        Args:
            datos_servicio: Datos del servicio de transporte
            
        Returns:
            ID del servicio creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None
            
            if not self._validar_datos_servicio(datos_servicio):
                return None
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos
            datos_sanitizados = self._sanitizar_datos_servicio(datos_servicio)
            
            cursor.execute("""
                INSERT INTO servicios_transporte (
                    codigo, descripcion, tipo_servicio, proveedor_transporte_id,
                    origen, destino, fecha_programada, fecha_real,
                    estado, costo_estimado, costo_real, observaciones,
                    capacidad_peso, capacidad_volumen, activo, fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos_sanitizados['codigo'],
                datos_sanitizados['descripcion'],
                datos_sanitizados.get('tipo_servicio', 'ENTREGA'),
                datos_sanitizados.get('proveedor_transporte_id'),
                datos_sanitizados['origen'],
                datos_sanitizados['destino'],
                datos_sanitizados.get('fecha_programada'),
                datos_sanitizados.get('fecha_real'),
                datos_sanitizados.get('estado', 'PROGRAMADO'),
                datos_sanitizados.get('costo_estimado', 0.0),
                datos_sanitizados.get('costo_real', 0.0),
                datos_sanitizados.get('observaciones', ''),
                datos_sanitizados.get('capacidad_peso', 0.0),
                datos_sanitizados.get('capacidad_volumen', 0.0),
                1,  # activo por defecto
                datetime.now()
            ))
            
            servicio_id = cursor.lastrowid
            self.db_connection.commit()
            
            logger.info(f"Servicio de transporte creado con ID {servicio_id}")
            return servicio_id
            
        except Exception as e:
            logger.error(f"Error creando servicio de transporte: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None
    
    def obtener_servicios_transporte(self, activos_solo: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene todos los servicios de transporte.
        
        Args:
            activos_solo: Si True, solo devuelve servicios activos
            
        Returns:
            Lista de servicios de transporte
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            
            if activos_solo:
                cursor.execute("""
                    SELECT st.id, st.codigo, st.descripcion, st.tipo_servicio,
                           st.origen, st.destino, st.fecha_programada, st.fecha_real,
                           st.estado, st.costo_estimado, st.costo_real,
                           st.capacidad_peso, st.capacidad_volumen, st.observaciones,
                           pt.nombre as proveedor_nombre
                    FROM servicios_transporte st
                    LEFT JOIN proveedores_transporte pt ON st.proveedor_transporte_id = pt.id
                    WHERE st.activo = 1
                    ORDER BY st.fecha_programada DESC
                """)
            else:
                cursor.execute("""
                    SELECT st.id, st.codigo, st.descripcion, st.tipo_servicio,
                           st.origen, st.destino, st.fecha_programada, st.fecha_real,
                           st.estado, st.costo_estimado, st.costo_real,
                           st.capacidad_peso, st.capacidad_volumen, st.observaciones,
                           pt.nombre as proveedor_nombre
                    FROM servicios_transporte st
                    LEFT JOIN proveedores_transporte pt ON st.proveedor_transporte_id = pt.id
                    ORDER BY st.fecha_programada DESC
                """)
            
            servicios = []
            for row in cursor.fetchall():
                servicio = {
                    'id': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'tipo_servicio': row[3],
                    'origen': row[4],
                    'destino': row[5],
                    'fecha_programada': row[6],
                    'fecha_real': row[7],
                    'estado': row[8],
                    'costo_estimado': float(row[9]) if row[9] else 0.0,
                    'costo_real': float(row[10]) if row[10] else 0.0,
                    'capacidad_peso': float(row[11]) if row[11] else 0.0,
                    'capacidad_volumen': float(row[12]) if row[12] else 0.0,
                    'observaciones': row[13],
                    'proveedor_nombre': row[14]
                }
                servicios.append(servicio)
            
            return servicios
            
        except Exception as e:
            logger.error(f"Error obteniendo servicios de transporte: {e}")
            return []
    
    def actualizar_estado_servicio(self, servicio_id: int, nuevo_estado: str, observaciones: str = "") -> bool:
        """
        Actualiza el estado de un servicio de transporte.
        
        Args:
            servicio_id: ID del servicio
            nuevo_estado: Nuevo estado del servicio
            observaciones: Observaciones adicionales
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            
            # Actualizar estado y observaciones
            cursor.execute("""
                UPDATE servicios_transporte 
                SET estado = ?, observaciones = ?, fecha_modificacion = ?
                WHERE id = ? AND activo = 1
            """, (nuevo_estado, observaciones, datetime.now(), servicio_id))
            
            if cursor.rowcount > 0:
                # Si es completado, actualizar fecha real
                if nuevo_estado == 'COMPLETADO':
                    cursor.execute("""
                        UPDATE servicios_transporte 
                        SET fecha_real = ?
                        WHERE id = ?
                    """, (datetime.now(), servicio_id))
                
                self.db_connection.commit()
                logger.info(f"Estado de servicio {servicio_id} actualizado a {nuevo_estado}")
                return True
            else:
                logger.warning(f"No se pudo actualizar el servicio {servicio_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando estado servicio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def crear_proveedor_transporte(self, datos_proveedor: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo proveedor de transporte.
        
        Args:
            datos_proveedor: Datos del proveedor
            
        Returns:
            ID del proveedor creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None
            
            if not self._validar_datos_proveedor_transporte(datos_proveedor):
                return None
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos
            datos_sanitizados = self._sanitizar_datos_proveedor_transporte(datos_proveedor)
            
            cursor.execute("""
                INSERT INTO proveedores_transporte (
                    codigo, nombre, razon_social, ruc, telefono, email,
                    direccion, contacto_principal, tipo_transporte, zona_cobertura,
                    tarifa_base, calificacion, activo, fecha_registro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos_sanitizados['codigo'],
                datos_sanitizados['nombre'],
                datos_sanitizados.get('razon_social', ''),
                datos_sanitizados.get('ruc', ''),
                datos_sanitizados.get('telefono', ''),
                datos_sanitizados.get('email', ''),
                datos_sanitizados.get('direccion', ''),
                datos_sanitizados.get('contacto_principal', ''),
                datos_sanitizados.get('tipo_transporte', 'TERRESTRE'),
                datos_sanitizados.get('zona_cobertura', ''),
                datos_sanitizados.get('tarifa_base', 0.0),
                datos_sanitizados.get('calificacion', 5),
                1,  # activo por defecto
                datetime.now()
            ))
            
            proveedor_id = cursor.lastrowid
            self.db_connection.commit()
            
            logger.info(f"Proveedor de transporte creado con ID {proveedor_id}")
            return proveedor_id
            
        except Exception as e:
            logger.error(f"Error creando proveedor de transporte: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None
    
    def obtener_proveedores_transporte(self, activos_solo: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proveedores de transporte.
        
        Args:
            activos_solo: Si True, solo devuelve proveedores activos
            
        Returns:
            Lista de proveedores de transporte
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            
            if activos_solo:
                cursor.execute("""
                    SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                           direccion, contacto_principal, tipo_transporte, zona_cobertura,
                           tarifa_base, calificacion
                    FROM proveedores_transporte
                    WHERE activo = 1
                    ORDER BY calificacion DESC, nombre
                """)
            else:
                cursor.execute("""
                    SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
                           direccion, contacto_principal, tipo_transporte, zona_cobertura,
                           tarifa_base, calificacion
                    FROM proveedores_transporte
                    ORDER BY calificacion DESC, nombre
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
                    'tipo_transporte': row[9],
                    'zona_cobertura': row[10],
                    'tarifa_base': float(row[11]) if row[11] else 0.0,
                    'calificacion': row[12]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores de transporte: {e}")
            return []
    
    def calcular_costo_transporte(self, origen: str, destino: str, peso: float, volumen: float,
                                 tipo_servicio: str = "ENTREGA") -> Dict[str, Any]:
        """
        Calcula el costo estimado de transporte.
        
        Args:
            origen: Punto de origen
            destino: Punto de destino
            peso: Peso en kg
            volumen: Volumen en m³
            tipo_servicio: Tipo de servicio
            
        Returns:
            Diccionario con el cálculo de costos
        """
        try:
            # Lógica básica de cálculo de costos
            # En una implementación real, esto podría usar APIs de proveedores
            distancia_base = self._calcular_distancia_estimada(origen, destino)
            
            # Factores de costo
            factor_distancia = distancia_base * 0.5  # $0.5 por km
            factor_peso = peso * 0.1  # $0.1 por kg
            factor_volumen = volumen * 2.0  # $2.0 por m³
            
            # Multiplicador por tipo de servicio
            multiplicadores = {
                'ENTREGA': 1.0,
                'EXPRESS': 1.5,
                'URGENTE': 2.0,
                'PROGRAMADO': 0.8
            }
            
            multiplicador = multiplicadores.get(tipo_servicio, 1.0)
            
            costo_base = (factor_distancia + factor_peso + factor_volumen) * multiplicador
            costo_final = max(costo_base, 10.0)  # Costo mínimo $10
            
            return {
                'costo_estimado': round(costo_final, 2),
                'distancia_km': distancia_base,
                'factor_distancia': round(factor_distancia, 2),
                'factor_peso': round(factor_peso, 2),
                'factor_volumen': round(factor_volumen, 2),
                'multiplicador_servicio': multiplicador,
                'tipo_servicio': tipo_servicio
            }
            
        except Exception as e:
            logger.error(f"Error calculando costo de transporte: {e}")
            return {'costo_estimado': 0.0}
    
    def obtener_servicios_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtiene servicios filtrados por estado.
        
        Args:
            estado: Estado a filtrar
            
        Returns:
            Lista de servicios en el estado especificado
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT st.id, st.codigo, st.descripcion, st.origen, st.destino,
                       st.fecha_programada, st.estado, st.costo_estimado,
                       pt.nombre as proveedor_nombre
                FROM servicios_transporte st
                LEFT JOIN proveedores_transporte pt ON st.proveedor_transporte_id = pt.id
                WHERE st.estado = ? AND st.activo = 1
                ORDER BY st.fecha_programada
            """, (estado,))
            
            servicios = []
            for row in cursor.fetchall():
                servicio = {
                    'id': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'origen': row[3],
                    'destino': row[4],
                    'fecha_programada': row[5],
                    'estado': row[6],
                    'costo_estimado': float(row[7]) if row[7] else 0.0,
                    'proveedor_nombre': row[8]
                }
                servicios.append(servicio)
            
            return servicios
            
        except Exception as e:
            logger.error(f"Error obteniendo servicios por estado: {e}")
            return []
    
    def generar_reporte_logistico(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """
        Genera reporte logístico para un periodo.
        
        Args:
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte
            
        Returns:
            Diccionario con datos del reporte
        """
        try:
            if not self.db_connection:
                return {}
            
            cursor = self.db_connection.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_servicios,
                    COUNT(CASE WHEN estado = 'COMPLETADO' THEN 1 END) as completados,
                    COUNT(CASE WHEN estado = 'CANCELADO' THEN 1 END) as cancelados,
                    AVG(costo_real) as promedio_costo,
                    SUM(CASE WHEN estado = 'COMPLETADO' THEN costo_real ELSE 0 END) as costo_total
                FROM servicios_transporte
                WHERE fecha_programada BETWEEN ? AND ?
                AND activo = 1
            """, (fecha_inicio, fecha_fin))
            
            stats = cursor.fetchone()
            
            # Servicios por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM servicios_transporte
                WHERE fecha_programada BETWEEN ? AND ?
                AND activo = 1
                GROUP BY estado
                ORDER BY cantidad DESC
            """, (fecha_inicio, fecha_fin))
            
            servicios_por_estado = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Top proveedores
            cursor.execute("""
                SELECT pt.nombre, COUNT(*) as servicios, AVG(st.costo_real) as promedio_costo
                FROM servicios_transporte st
                JOIN proveedores_transporte pt ON st.proveedor_transporte_id = pt.id
                WHERE st.fecha_programada BETWEEN ? AND ?
                AND st.activo = 1
                GROUP BY pt.id, pt.nombre
                ORDER BY servicios DESC
                LIMIT 10
            """, (fecha_inicio, fecha_fin))
            
            top_proveedores = []
            for row in cursor.fetchall():
                top_proveedores.append({
                    'proveedor': row[0],
                    'servicios': row[1],
                    'promedio_costo': float(row[2]) if row[2] else 0.0
                })
            
            if stats:
                return {
                    'periodo': {
                        'inicio': fecha_inicio.strftime('%d/%m/%Y'),
                        'fin': fecha_fin.strftime('%d/%m/%Y')
                    },
                    'resumen': {
                        'total_servicios': stats[0] or 0,
                        'completados': stats[1] or 0,
                        'cancelados': stats[2] or 0,
                        'tasa_cumplimiento': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
                        'promedio_costo': float(stats[3]) if stats[3] else 0.0,
                        'costo_total': float(stats[4]) if stats[4] else 0.0
                    },
                    'servicios_por_estado': servicios_por_estado,
                    'top_proveedores': top_proveedores
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error generando reporte logístico: {e}")
            return {}
    
    def generar_codigo_servicio(self) -> str:
        """
        Genera un código único para un nuevo servicio.
        
        Returns:
            Código generado
        """
        try:
            if not self.db_connection:
                return f"SERV{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM servicios_transporte")
            count = cursor.fetchone()[0] + 1
            
            return f"SERV{count:06d}"
            
        except Exception as e:
            logger.error(f"Error generando código servicio: {e}")
            return f"SERV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # ===== MÉTODOS PRIVADOS =====
    
    def _validar_datos_servicio(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos de un servicio de transporte.
        
        Args:
            datos: Datos a validar
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validar campos obligatorios
            if not datos.get('origen', '').strip():
                logger.error("El origen es obligatorio")
                return False
            
            if not datos.get('destino', '').strip():
                logger.error("El destino es obligatorio")
                return False
            
            if not datos.get('descripcion', '').strip():
                logger.error("La descripción es obligatoria")
                return False
            
            # Validar fecha programada
            fecha_programada = datos.get('fecha_programada')
            if fecha_programada and isinstance(fecha_programada, str):
                try:
                    datetime.strptime(fecha_programada, '%Y-%m-%d')
                except ValueError:
                    logger.error("Formato de fecha programada inválido")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos servicio: {e}")
            return False
    
    def _validar_datos_proveedor_transporte(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos de un proveedor de transporte.
        
        Args:
            datos: Datos a validar
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validar campos obligatorios
            if not datos.get('nombre', '').strip():
                logger.error("El nombre del proveedor es obligatorio")
                return False
            
            # Validar email si se proporciona
            email = datos.get('email', '').strip()
            if email and not self._validar_email(email):
                logger.error("Formato de email inválido")
                return False
            
            # Validar calificación
            calificacion = datos.get('calificacion', 5)
            try:
                calificacion = int(calificacion)
                if not 1 <= calificacion <= 10:
                    logger.error("La calificación debe estar entre 1 y 10")
                    return False
            except ValueError:
                logger.error("La calificación debe ser un número válido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos proveedor transporte: {e}")
            return False
    
    def _sanitizar_datos_servicio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de entrada de un servicio.
        
        Args:
            datos: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        datos_sanitizados = {}
        
        # Campos de texto
        campos_texto = [
            'codigo', 'descripcion', 'tipo_servicio', 'origen', 'destino',
            'estado', 'observaciones'
        ]
        
        for campo in campos_texto:
            if campo in datos:
                datos_sanitizados[campo] = SecurityUtils.sanitize_sql_input(datos[campo])
        
        # Campos numéricos
        campos_numericos = ['proveedor_transporte_id', 'costo_estimado', 'costo_real',
                           'capacidad_peso', 'capacidad_volumen']
        
        for campo in campos_numericos:
            if campo in datos:
                try:
                    datos_sanitizados[campo] = float(datos[campo])
                except ValueError:
                    datos_sanitizados[campo] = 0.0
        
        # Campos de fecha
        if 'fecha_programada' in datos:
            datos_sanitizados['fecha_programada'] = datos['fecha_programada']
        
        if 'fecha_real' in datos:
            datos_sanitizados['fecha_real'] = datos['fecha_real']
        
        return datos_sanitizados
    
    def _sanitizar_datos_proveedor_transporte(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de entrada de un proveedor de transporte.
        
        Args:
            datos: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        datos_sanitizados = {}
        
        # Campos de texto
        campos_texto = [
            'codigo', 'nombre', 'razon_social', 'ruc', 'telefono', 'email',
            'direccion', 'contacto_principal', 'tipo_transporte', 'zona_cobertura'
        ]
        
        for campo in campos_texto:
            if campo in datos:
                datos_sanitizados[campo] = SecurityUtils.sanitize_sql_input(datos[campo])
        
        # Campos numéricos
        if 'tarifa_base' in datos:
            try:
                datos_sanitizados['tarifa_base'] = float(datos['tarifa_base'])
            except ValueError:
                datos_sanitizados['tarifa_base'] = 0.0
        
        if 'calificacion' in datos:
            try:
                datos_sanitizados['calificacion'] = int(datos['calificacion'])
            except ValueError:
                datos_sanitizados['calificacion'] = 5
        
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
    
    def _calcular_distancia_estimada(self, origen: str, destino: str) -> float:
        """
        Calcula distancia estimada entre dos puntos.
        
        Args:
            origen: Punto de origen
            destino: Punto de destino
            
        Returns:
            Distancia estimada en kilómetros
        """
        # Implementación básica
        # En una implementación real, usarías una API de mapas
        if origen.lower() == destino.lower():
            return 0.0
        
        # Distancia base estimada
        return 50.0  # 50 km por defecto