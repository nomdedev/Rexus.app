"""
MIT License

Copyright (c) 2025 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Rate Limiter - Sistema de limitación de velocidad para autenticación
================================================================

Sistema de rate limiting que protege contra ataques de fuerza bruta:
- Limita intentos de login por usuario
- Implementa bloqueo temporal progresivo 
- Registra actividad sospechosa
- Permite configuración flexible
"""

import datetime
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuración del rate limiter"""
    max_attempts: int = 5  # Máximo intentos permitidos
    base_lockout_minutes: int = 5  # Minutos base de bloqueo
    max_lockout_minutes: int = 120  # Máximo minutos de bloqueo
    progressive_multiplier: int = 2  # Multiplicador progresivo
    cleanup_hours: int = 24  # Horas para limpiar registros antiguos


class LoginRateLimiter:
    """
    Sistema de rate limiting para login que previene ataques de fuerza bruta
    
    Características:
    - Bloqueo temporal progresivo por usuario
    - Persistencia de datos entre sesiones
    - Limpieza automática de registros antiguos
    - Logging de actividad sospechosa
    - Configuración flexible
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Inicializa el rate limiter"""
        self.config = config or RateLimitConfig()
        self.data_file = Path("data/rate_limiter.json")
        self.attempts = {}  # {username: attempt_data}
        
        # Crear directorio data si no existe
        self.data_file.parent.mkdir(exist_ok=True)
        
        # Cargar datos persistidos
        self._load_data()
        
        # Limpiar registros antiguos
        self._cleanup_old_records()
    
    def _load_data(self):
        """Carga datos de intentos desde archivo JSON"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Convertir timestamps string de vuelta a datetime
                for username, attempt_data in data.items():
                    if 'locked_until' in attempt_data and attempt_data['locked_until']:
                        attempt_data['locked_until'] = datetime.datetime.fromisoformat(
                            attempt_data['locked_until']
                        )
                    if 'last_attempt' in attempt_data:
                        attempt_data['last_attempt'] = datetime.datetime.fromisoformat(
                            attempt_data['last_attempt']
                        )
                    if 'attempts' in attempt_data:
                        # Convertir lista de timestamps
                        attempt_data['attempts'] = [
                            datetime.datetime.fromisoformat(ts) 
                            for ts in attempt_data['attempts']
                        ]
                
                self.attempts = data
                
        except Exception as e:
            print(f"[WARNING] Error cargando rate limiter data: {e}")
            self.attempts = {}
    
    def _save_data(self):
        """Guarda datos de intentos en archivo JSON"""
        try:
            # Convertir datetime objects a strings para JSON
            data_to_save = {}
            for username, attempt_data in self.attempts.items():
                serialized_data = attempt_data.copy()
                
                if 'locked_until' in serialized_data and serialized_data['locked_until']:
                    serialized_data['locked_until'] = serialized_data['locked_until'].isoformat()
                
                if 'last_attempt' in serialized_data:
                    serialized_data['last_attempt'] = serialized_data['last_attempt'].isoformat()
                    
                if 'attempts' in serialized_data:
                    serialized_data['attempts'] = [
                        ts.isoformat() for ts in serialized_data['attempts']
                    ]
                
                data_to_save[username] = serialized_data
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[ERROR] Error guardando rate limiter data: {e}")
    
    def _cleanup_old_records(self):
        """Limpia registros antiguos basado en configuración"""
        try:
            cutoff_time = datetime.datetime.now() - datetime.timedelta(
                hours=self.config.cleanup_hours
            )
            
            users_to_remove = []
            for username, data in self.attempts.items():
                # Si el último intento es muy antiguo y no está bloqueado
                last_attempt = data.get('last_attempt')
                locked_until = data.get('locked_until')
                
                if last_attempt and last_attempt < cutoff_time:
                    if not locked_until or locked_until < datetime.datetime.now():
                        users_to_remove.append(username)
            
            # Remover registros antiguos
            for username in users_to_remove:
                del self.attempts[username]
            
            if users_to_remove:
                print(f"[INFO] Rate limiter: limpiados {len(users_to_remove)} registros antiguos")
                self._save_data()
                
        except Exception as e:
            print(f"[ERROR] Error limpiando registros antiguos: {e}")
    
    def is_blocked(self, username: str) -> Tuple[bool, Optional[datetime.datetime]]:
        """
        Verifica si un usuario está bloqueado
        
        Returns:
            Tuple[bool, Optional[datetime]]: (está_bloqueado, hasta_cuando)
        """
        if username not in self.attempts:
            return False, None
        
        attempt_data = self.attempts[username]
        locked_until = attempt_data.get('locked_until')
        
        if not locked_until:
            return False, None
        
        # Verificar si el bloqueo ya expiró
        now = datetime.datetime.now()
        if locked_until <= now:
            # Bloqueo expirado, limpiar
            attempt_data['locked_until'] = None
            attempt_data['consecutive_failures'] = 0
            self._save_data()
            return False, None
        
        return True, locked_until
    
    def record_failed_attempt(self, username: str):
        """
        Registra un intento fallido de login
        
        Args:
            username: Usuario que falló el login
        """
        now = datetime.datetime.now()
        
        if username not in self.attempts:
            self.attempts[username] = {
                'consecutive_failures': 0,
                'attempts': [],
                'last_attempt': now,
                'locked_until': None
            }
        
        attempt_data = self.attempts[username]
        
        # Registrar el intento
        attempt_data['consecutive_failures'] += 1
        attempt_data['last_attempt'] = now
        attempt_data['attempts'].append(now)
        
        # Limpiar intentos antiguos (más de 1 hora)
        cutoff = now - datetime.timedelta(hours=1)
        attempt_data['attempts'] = [
            ts for ts in attempt_data['attempts'] if ts > cutoff
        ]
        
        # Verificar si necesita bloqueo
        if attempt_data['consecutive_failures'] >= self.config.max_attempts:
            self._apply_lockout(username, attempt_data)
        
        # Guardar cambios
        self._save_data()
        
        # Log de seguridad
        self._log_security_event(username, "failed_attempt", attempt_data['consecutive_failures'])
    
    def record_successful_attempt(self, username: str):
        """
        Registra un intento exitoso de login
        
        Args:
            username: Usuario que logró autenticarse
        """
        if username in self.attempts:
            # Limpiar registros de fallos
            self.attempts[username] = {
                'consecutive_failures': 0,
                'attempts': [],
                'last_attempt': datetime.datetime.now(),
                'locked_until': None
            }
            
            self._save_data()
            
            # Log de seguridad si había fallos previos
            self._log_security_event(username, "successful_login_after_failures", 0)
    
    def _apply_lockout(self, username: str, attempt_data: Dict):
        """Aplica bloqueo temporal con escalación progresiva"""
        failures = attempt_data['consecutive_failures']
        
        # Calcular tiempo de bloqueo con escalación
        if failures <= self.config.max_attempts:
            lockout_minutes = self.config.base_lockout_minutes
        else:
            # Escalación progresiva: 5min, 10min, 20min, 40min, 80min, 120min (máx)
            escalation = failures - self.config.max_attempts
            lockout_minutes = min(
                self.config.base_lockout_minutes * (self.config.progressive_multiplier ** escalation),
                self.config.max_lockout_minutes
            )
        
        # Aplicar bloqueo
        locked_until = datetime.datetime.now() + datetime.timedelta(minutes=lockout_minutes)
        attempt_data['locked_until'] = locked_until
        
        # Log crítico de bloqueo
        self._log_security_event(username, "user_locked", lockout_minutes)
        
        print(f"[SECURITY] Usuario '{username}' bloqueado por {lockout_minutes} minutos "
              f"(fallos consecutivos: {failures})")
    
    def get_lockout_info(self, username: str) -> Dict:
        """
        Obtiene información del estado de bloqueo
        
        Returns:
            Dict con información de bloqueo y intentos
        """
        if username not in self.attempts:
            return {
                'is_blocked': False,
                'consecutive_failures': 0,
                'locked_until': None,
                'remaining_attempts': self.config.max_attempts,
                'recent_attempts': 0
            }
        
        attempt_data = self.attempts[username]
        is_blocked, locked_until = self.is_blocked(username)
        
        return {
            'is_blocked': is_blocked,
            'consecutive_failures': attempt_data.get('consecutive_failures', 0),
            'locked_until': locked_until,
            'remaining_attempts': max(0, self.config.max_attempts - attempt_data.get('consecutive_failures', 0)),
            'recent_attempts': len(attempt_data.get('attempts', []))
        }
    
    def _log_security_event(self, username: str, event_type: str, details):
        """Registra eventos de seguridad en auditoria"""
        try:
            from rexus.core.database import get_auditoria_connection
            
            conn = get_auditoria_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO auditoria (
                        fecha, usuario_id, accion, tabla_afectada, 
                        estado, justificativo
                    ) VALUES (
                        GETDATE(), 0, ?, 'login_attempts', 
                        'SECURITY', ?
                    )
                """, (
                    f"RATE_LIMIT_{event_type.upper()}",
                    f"Rate limiting for {username}: {event_type} - details: {details}"
                ))
                conn.commit()
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"[WARNING] Error logging security event: {e}")
    
    def reset_user_attempts(self, username: str, admin_user: str = "system"):
        """
        Resetea intentos de un usuario (solo para administradores)
        
        Args:
            username: Usuario a resetear
            admin_user: Usuario admin que realiza la acción
        """
        if username in self.attempts:
            del self.attempts[username]
            self._save_data()
            
            # Log de la acción administrativa
            self._log_security_event(admin_user, "admin_reset_attempts", f"Reset for user: {username}")
            
            print(f"[ADMIN] Intentos resetados para usuario '{username}' por '{admin_user}'")
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del rate limiter"""
        now = datetime.datetime.now()
        
        total_users = len(self.attempts)
        blocked_users = sum(1 for data in self.attempts.values() 
                          if data.get('locked_until') and data['locked_until'] > now)
        
        recent_attempts = 0
        for data in self.attempts.values():
            recent_attempts += len([
                ts for ts in data.get('attempts', [])
                if ts > now - datetime.timedelta(hours=1)
            ])
        
        return {
            'total_tracked_users': total_users,
            'currently_blocked': blocked_users,
            'recent_attempts_1h': recent_attempts,
            'config': {
                'max_attempts': self.config.max_attempts,
                'base_lockout_minutes': self.config.base_lockout_minutes,
                'max_lockout_minutes': self.config.max_lockout_minutes
            }
        }


# Instancia global del rate limiter
_rate_limiter_instance: Optional[LoginRateLimiter] = None


def get_rate_limiter() -> LoginRateLimiter:
    """Obtiene la instancia global del rate limiter"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = LoginRateLimiter()
    return _rate_limiter_instance


def initialize_rate_limiter(config: Optional[RateLimitConfig] = None):
    """Inicializa el rate limiter con configuración específica"""
    global _rate_limiter_instance
    _rate_limiter_instance = LoginRateLimiter(config)