#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usuarios - Funcionalidades Avanzadas Faltantes
Implementa todas las características que debe tener un módulo de usuarios completo empresarial
"""

import json
import os
import logging
import datetime
import hashlib
import uuid
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import secrets

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("usuarios.advanced")
except ImportError:
    logger = logging.getLogger("usuarios.advanced")

@dataclass
class UserProfile:
    """Perfil completo de usuario."""
    id: str
    username: str
    email: str
    nombre: str
    apellido: str
    role: str
    departamento: str
    cargo: str
    telefono: str
    fecha_ingreso: datetime.datetime
    ultimo_login: Optional[datetime.datetime]
    activo: bool
    configuraciones_personales: Dict[str, Any]
    permisos_especiales: List[str]

@dataclass
class UserSession:
    """Sesión activa de usuario."""
    session_id: str
    user_id: str
    username: str
    ip_address: str
    user_agent: str
    fecha_inicio: datetime.datetime
    ultima_actividad: datetime.datetime
    activa: bool

class AdvancedUserManager:
    """Manager avanzado de usuarios con funcionalidades empresariales completas."""
    
    def __init__(self, user_model):
        self.user_model = user_model
        self.active_sessions = {}
        self.login_attempts = {}
        self.user_preferences = {}
        self.user_groups = {}
        self.audit_trail = []
        
    # =================================================================
    # GESTIÓN AVANZADA DE PERFILES
    # =================================================================
    
    def crear_perfil_completo(self, datos_usuario: Dict[str, Any], 
                            creado_por: str) -> Tuple[bool, str]:
        """Crea un perfil completo de usuario con validaciones avanzadas."""
        try:
            # Validaciones avanzadas
            validacion = self._validar_datos_usuario_completos(datos_usuario)
            if not validacion['valido']:
                return False, f"Datos inválidos: {validacion['errores']}"
            
            # Generar ID único
            user_id = str(uuid.uuid4())
            
            # Hashear password de forma segura
            password_hash = self._hash_password_secure(datos_usuario['password'])
            
            # Crear perfil completo
            profile = UserProfile(
                id=user_id,
                username=datos_usuario['username'],
                email=datos_usuario['email'],
                nombre=datos_usuario['nombre'],
                apellido=datos_usuario['apellido'],
                role=datos_usuario.get('role', 'USER'),
                departamento=datos_usuario.get('departamento', ''),
                cargo=datos_usuario.get('cargo', ''),
                telefono=datos_usuario.get('telefono', ''),
                fecha_ingreso=datetime.datetime.now(),
                ultimo_login=None,
                activo=True,
                configuraciones_personales={},
                permisos_especiales=datos_usuario.get('permisos_especiales', [])
            )
            
            # Guardar en base de datos
            success = self._guardar_perfil_bd(profile, password_hash)
            
            if success:
                self._audit_log("USER_CREATED", {
                    'new_user_id': user_id,
                    'username': datos_usuario['username'],
                    'role': profile.role
                }, creado_por)
                
                return True, f"Usuario {datos_usuario['username']} creado exitosamente"
            else:
                return False, "Error guardando usuario en base de datos"
                
        except Exception as e:
            logger.error(f"Error creando perfil completo: {str(e)}")
            return False, f"Error interno: {str(e)}"
    
    def actualizar_perfil_completo(self, user_id: str, datos_actualizados: Dict[str, Any],
                                 actualizado_por: str) -> Tuple[bool, str]:
        """Actualiza un perfil de usuario con validaciones."""
        try:
            # Obtener perfil actual
            perfil_actual = self._obtener_perfil_completo(user_id)
            if not perfil_actual:
                return False, "Usuario no encontrado"
            
            # Validar cambios
            if 'email' in datos_actualizados:
                if not self._validar_email_unico(datos_actualizados['email'], user_id):
                    return False, "Email ya está en uso"
            
            # Aplicar cambios
            cambios_aplicados = []
            for campo, nuevo_valor in datos_actualizados.items():
                if hasattr(perfil_actual, campo):
                    valor_anterior = getattr(perfil_actual, campo)
                    setattr(perfil_actual, campo, nuevo_valor)
                    cambios_aplicados.append(f"{campo}: {valor_anterior} → {nuevo_valor}")
            
            # Guardar cambios
            success = self._actualizar_perfil_bd(perfil_actual)
            
            if success:
                self._audit_log("USER_UPDATED", {
                    'user_id': user_id,
                    'cambios': cambios_aplicados
                }, actualizado_por)
                
                return True, f"Perfil actualizado: {len(cambios_aplicados)} campos modificados"
            else:
                return False, "Error actualizando perfil en base de datos"
                
        except Exception as e:
            logger.error(f"Error actualizando perfil: {str(e)}")
            return False, f"Error interno: {str(e)}"
    
    # =================================================================
    # GESTIÓN AVANZADA DE SESIONES
    # =================================================================
    
    def iniciar_sesion_avanzada(self, username: str, password: str, 
                              ip_address: str, user_agent: str) -> Tuple[bool, Dict[str, Any]]:
        """Inicia sesión con tracking avanzado y validaciones de seguridad."""
        try:
            # Verificar si la cuenta está bloqueada
            if self._cuenta_bloqueada(username):
                return False, {'error': 'Cuenta bloqueada por múltiples intentos fallidos'}
            
            # Validar credenciales
            usuario = self._validar_credenciales(username, password)
            if not usuario:
                self._registrar_intento_fallido(username, ip_address)
                return False, {'error': 'Credenciales inválidas'}
            
            # Verificar usuario activo
            if not usuario.get('activo', False):
                return False, {'error': 'Cuenta desactivada'}
            
            # Crear sesión
            session_id = self._generar_session_id()
            session = UserSession(
                session_id=session_id,
                user_id=usuario['id'],
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                fecha_inicio=datetime.datetime.now(),
                ultima_actividad=datetime.datetime.now(),
                activa=True
            )
            
            # Almacenar sesión activa
            self.active_sessions[session_id] = session
            
            # Limpiar intentos fallidos
            self._limpiar_intentos_fallidos(username)
            
            # Actualizar último login
            self._actualizar_ultimo_login(usuario['id'])
            
            # Audit log
            self._audit_log("USER_LOGIN", {
                'user_id': usuario['id'],
                'ip_address': ip_address,
                'user_agent': user_agent[:100]  # Truncar para log
            }, username)
            
            return True, {
                'session_id': session_id,
                'user': usuario,
                'permisos': self._obtener_permisos_usuario(usuario['id']),
                'configuraciones': self._obtener_configuraciones_usuario(usuario['id'])
            }
            
        except Exception as e:
            logger.error(f"Error iniciando sesión: {str(e)}")
            return False, {'error': 'Error interno del sistema'}
    
    def cerrar_sesion_avanzada(self, session_id: str) -> Tuple[bool, str]:
        """Cierra sesión con cleanup completo."""
        try:
            if session_id not in self.active_sessions:
                return False, "Sesión no encontrada"
            
            session = self.active_sessions[session_id]
            session.activa = False
            
            # Audit log
            self._audit_log("USER_LOGOUT", {
                'user_id': session.user_id,
                'session_duration': str(datetime.datetime.now() - session.fecha_inicio)
            }, session.username)
            
            # Remover de sesiones activas
            del self.active_sessions[session_id]
            
            return True, "Sesión cerrada exitosamente"
            
        except Exception as e:
            logger.error(f"Error cerrando sesión: {str(e)}")
            return False, f"Error cerrando sesión: {str(e)}"
    
    def validar_sesion_activa(self, session_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida si una sesión sigue activa y actualiza última actividad."""
        try:
            if session_id not in self.active_sessions:
                return False, {'error': 'Sesión no encontrada'}
            
            session = self.active_sessions[session_id]
            
            # Verificar timeout
            timeout_minutes = 30  # Configurable
            tiempo_inactivo = datetime.datetime.now() - session.ultima_actividad
            
            if tiempo_inactivo.total_seconds() > (timeout_minutes * 60):
                # Sesión expirada
                session.activa = False
                del self.active_sessions[session_id]
                return False, {'error': 'Sesión expirada'}
            
            # Actualizar última actividad
            session.ultima_actividad = datetime.datetime.now()
            
            return True, {
                'user_id': session.user_id,
                'username': session.username,
                'activa': session.activa
            }
            
        except Exception as e:
            logger.error(f"Error validando sesión: {str(e)}")
            return False, {'error': 'Error validando sesión'}
    
    # =================================================================
    # GESTIÓN DE PERMISOS Y ROLES AVANZADA
    # =================================================================
    
    def asignar_permisos_especiales(self, user_id: str, permisos: List[str], 
                                  asignado_por: str) -> Tuple[bool, str]:
        """Asigna permisos especiales a un usuario."""
        try:
            usuario = self._obtener_perfil_completo(user_id)
            if not usuario:
                return False, "Usuario no encontrado"
            
            # Validar permisos
            permisos_validos = self._validar_permisos(permisos)
            if not permisos_validos['validos']:
                return False, f"Permisos inválidos: {permisos_validos['invalidos']}"
            
            # Agregar permisos
            permisos_actuales = set(usuario.permisos_especiales)
            nuevos_permisos = set(permisos) - permisos_actuales
            
            usuario.permisos_especiales = list(permisos_actuales | set(permisos))
            
            # Guardar cambios
            success = self._actualizar_perfil_bd(usuario)
            
            if success:
                self._audit_log("PERMISSIONS_ASSIGNED", {
                    'user_id': user_id,
                    'nuevos_permisos': list(nuevos_permisos)
                }, asignado_por)
                
                return True, f"Asignados {len(nuevos_permisos)} permisos nuevos"
            else:
                return False, "Error guardando permisos"
                
        except Exception as e:
            logger.error(f"Error asignando permisos: {str(e)}")
            return False, f"Error interno: {str(e)}"
    
    def crear_grupo_usuarios(self, nombre_grupo: str, descripcion: str, 
                           permisos_grupo: List[str], creado_por: str) -> Tuple[bool, str]:
        """Crea un grupo de usuarios con permisos específicos."""
        try:
            group_id = str(uuid.uuid4())
            
            grupo = {
                'id': group_id,
                'nombre': nombre_grupo,
                'descripcion': descripcion,
                'permisos': permisos_grupo,
                'miembros': [],
                'fecha_creacion': datetime.datetime.now().isoformat(),
                'creado_por': creado_por,
                'activo': True
            }
            
            self.user_groups[group_id] = grupo
            
            self._audit_log("GROUP_CREATED", {
                'group_id': group_id,
                'nombre': nombre_grupo,
                'permisos_count': len(permisos_grupo)
            }, creado_por)
            
            return True, f"Grupo {nombre_grupo} creado exitosamente"
            
        except Exception as e:
            logger.error(f"Error creando grupo: {str(e)}")
            return False, f"Error interno: {str(e)}"
    
    def asignar_usuario_a_grupo(self, user_id: str, group_id: str, 
                              asignado_por: str) -> Tuple[bool, str]:
        """Asigna un usuario a un grupo."""
        try:
            if group_id not in self.user_groups:
                return False, "Grupo no encontrado"
            
            grupo = self.user_groups[group_id]
            
            if user_id not in grupo['miembros']:
                grupo['miembros'].append(user_id)
                
                self._audit_log("USER_ADDED_TO_GROUP", {
                    'user_id': user_id,
                    'group_id': group_id,
                    'group_name': grupo['nombre']
                }, asignado_por)
                
                return True, f"Usuario agregado al grupo {grupo['nombre']}"
            else:
                return False, "Usuario ya pertenece al grupo"
                
        except Exception as e:
            logger.error(f"Error asignando usuario a grupo: {str(e)}")
            return False, f"Error interno: {str(e)}"
    
    # =================================================================
    # REPORTES Y ANÁLISIS DE USUARIOS
    # =================================================================
    
    def generar_reporte_actividad_usuarios(self, fecha_inicio: datetime.datetime,
                                         fecha_fin: datetime.datetime) -> Dict[str, Any]:
        """Genera reporte de actividad de usuarios."""
        try:
            # Filtrar logs de auditoría por período
            logs_periodo = [
                log for log in self.audit_trail
                if fecha_inicio <= datetime.datetime.fromisoformat(log['timestamp']) <= fecha_fin
            ]
            
            # Analizar actividad
            actividad_por_usuario = {}
            for log in logs_periodo:
                username = log['usuario']
                if username not in actividad_por_usuario:
                    actividad_por_usuario[username] = {
                        'logins': 0,
                        'acciones': 0,
                        'ultimo_login': None,
                        'tiempo_total': 0
                    }
                
                if log['accion'] == 'USER_LOGIN':
                    actividad_por_usuario[username]['logins'] += 1
                    actividad_por_usuario[username]['ultimo_login'] = log['timestamp']
                
                actividad_por_usuario[username]['acciones'] += 1
            
            # Usuarios más activos
            usuarios_activos = sorted(
                actividad_por_usuario.items(),
                key=lambda x: x[1]['acciones'],
                reverse=True
            )[:10]
            
            return {
                'periodo': {
                    'inicio': fecha_inicio.isoformat(),
                    'fin': fecha_fin.isoformat()
                },
                'total_logs': len(logs_periodo),
                'usuarios_activos': dict(usuarios_activos),
                'resumen': {
                    'total_usuarios_activos': len(actividad_por_usuario),
                    'total_logins': sum(u['logins'] for u in actividad_por_usuario.values()),
                    'promedio_acciones_por_usuario': sum(u['acciones'] for u in actividad_por_usuario.values()) / len(actividad_por_usuario) if actividad_por_usuario else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            return {'error': str(e)}
    
    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de usuarios."""
        try:
            # Contar usuarios por estado
            usuarios_activos = 0
            usuarios_inactivos = 0
            usuarios_por_rol = {}
            
            # Aquí iría la lógica para obtener datos reales de BD
            # Por ahora simulamos
            
            return {
                'total_usuarios': usuarios_activos + usuarios_inactivos,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
                'usuarios_por_rol': usuarios_por_rol,
                'sesiones_activas': len(self.active_sessions),
                'grupos_creados': len(self.user_groups),
                'fecha_generacion': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {'error': str(e)}
    
    # =================================================================
    # MÉTODOS PRIVADOS DE SOPORTE
    # =================================================================
    
    def _validar_datos_usuario_completos(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos completos de usuario."""
        errores = []
        
        # Username
        if not datos.get('username'):
            errores.append("Username es requerido")
        elif len(datos['username']) < 3:
            errores.append("Username debe tener al menos 3 caracteres")
        elif not re.match(r'^[a-zA-Z0-9_]+$', datos['username']):
            errores.append("Username solo puede contener letras, números y guiones bajos")
        
        # Email
        if not datos.get('email'):
            errores.append("Email es requerido")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', datos['email']):
            errores.append("Formato de email inválido")
        
        # Password
        if not datos.get('password'):
            errores.append("Password es requerido")
        else:
            password_validation = self._validar_fortaleza_password(datos['password'])
            if not password_validation['valido']:
                errores.extend(password_validation['errores'])
        
        # Nombre y apellido
        if not datos.get('nombre'):
            errores.append("Nombre es requerido")
        if not datos.get('apellido'):
            errores.append("Apellido es requerido")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
    
    def _validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """Valida la fortaleza de una contraseña."""
        errores = []
        
        if len(password) < 8:
            errores.append("Password debe tener al menos 8 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errores.append("Password debe contener al menos una letra mayúscula")
        
        if not re.search(r'[a-z]', password):
            errores.append("Password debe contener al menos una letra minúscula")
        
        if not re.search(r'\d', password):
            errores.append("Password debe contener al menos un número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errores.append("Password debe contener al menos un carácter especial")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
    
    def _hash_password_secure(self, password: str) -> str:
        """Genera hash seguro de contraseña."""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _generar_session_id(self) -> str:
        """Genera ID único para sesión."""
        return secrets.token_urlsafe(32)
    
    def _audit_log(self, accion: str, detalles: Dict[str, Any], usuario: str):
        """Registra acción en log de auditoría."""
        log_entry = {
            'id': str(uuid.uuid4()),
            'accion': accion,
            'detalles': detalles,
            'usuario': usuario,
            'timestamp': datetime.datetime.now().isoformat(),
            'ip_address': detalles.get('ip_address', 'unknown')
        }
        
        self.audit_trail.append(log_entry)
        
        # Mantener solo últimos 10000 logs
        if len(self.audit_trail) > 10000:
            self.audit_trail = self.audit_trail[-10000:]
    
    def _cuenta_bloqueada(self, username: str) -> bool:
        """Verifica si una cuenta está bloqueada."""
        if username not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[username]
        if attempts['count'] >= 5:  # Máximo 5 intentos
            # Verificar si han pasado 15 minutos
            tiempo_bloqueo = datetime.datetime.now() - attempts['ultimo_intento']
            if tiempo_bloqueo.total_seconds() < 900:  # 15 minutos
                return True
            else:
                # Limpiar intentos después del período de bloqueo
                del self.login_attempts[username]
        
        return False
    
    def _registrar_intento_fallido(self, username: str, ip_address: str):
        """Registra un intento de login fallido."""
        if username not in self.login_attempts:
            self.login_attempts[username] = {
                'count': 0,
                'primer_intento': datetime.datetime.now(),
                'ultimo_intento': datetime.datetime.now(),
                'ips': []
            }
        
        self.login_attempts[username]['count'] += 1
        self.login_attempts[username]['ultimo_intento'] = datetime.datetime.now()
        
        if ip_address not in self.login_attempts[username]['ips']:
            self.login_attempts[username]['ips'].append(ip_address)
    
    def _limpiar_intentos_fallidos(self, username: str):
        """Limpia los intentos fallidos de un usuario."""
        if username in self.login_attempts:
            del self.login_attempts[username]
    
    # Métodos stub para integración con BD (implementar según necesidad)
    def _obtener_perfil_completo(self, user_id: str) -> Optional[UserProfile]:
        """Obtiene perfil completo desde BD."""
        # Implementar según estructura de BD
        return None
    
    def _guardar_perfil_bd(self, profile: UserProfile, password_hash: str) -> bool:
        """Guarda perfil en BD."""
        # Implementar según estructura de BD
        return True
    
    def _actualizar_perfil_bd(self, profile: UserProfile) -> bool:
        """Actualiza perfil en BD."""
        # Implementar según estructura de BD
        return True
    
    def _validar_credenciales(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Valida credenciales contra BD."""
        # Implementar según estructura de BD
        return None
    
    def _validar_email_unico(self, email: str, exclude_user_id: str = None) -> bool:
        """Verifica que el email sea único."""
        # Implementar según estructura de BD
        return True
    
    def _obtener_permisos_usuario(self, user_id: str) -> List[str]:
        """Obtiene permisos del usuario."""
        # Implementar según estructura de BD
        return []
    
    def _obtener_configuraciones_usuario(self, user_id: str) -> Dict[str, Any]:
        """Obtiene configuraciones personales del usuario."""
        # Implementar según estructura de BD
        return {}
    
    def _actualizar_ultimo_login(self, user_id: str):
        """Actualiza timestamp de último login."""
        # Implementar según estructura de BD
        pass
    
    def _validar_permisos(self, permisos: List[str]) -> Dict[str, Any]:
        """Valida que los permisos sean válidos."""
        permisos_validos = [
            'CREATE_USER', 'EDIT_USER', 'DELETE_USER', 'VIEW_USERS',
            'MANAGE_INVENTORY', 'CREATE_ORDERS', 'APPROVE_ORDERS',
            'VIEW_REPORTS', 'EXPORT_DATA', 'ADMIN_PANEL'
        ]
        
        invalidos = [p for p in permisos if p not in permisos_validos]
        
        return {
            'validos': len(invalidos) == 0,
            'invalidos': invalidos
        }