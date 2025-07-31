"""
Security Manager - Rexus.app
Handles security features like login attempt limiting, session management, etc.
"""

import datetime
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

class SecurityManager:
    """
    Manages security features including login attempt limiting,
    suspicious activity detection, and session security.
    """
    
    def __init__(self, max_attempts: int = 5, lockout_duration: int = 300):
        """
        Initialize security manager.
        
        Args:
            max_attempts: Maximum login attempts before lockout
            lockout_duration: Lockout duration in seconds (default 5 minutes)
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.logger = logging.getLogger(__name__)
        
        # Track failed login attempts by username and IP
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.ip_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Track locked accounts
        self.locked_accounts: Dict[str, datetime.datetime] = {}
        self.locked_ips: Dict[str, datetime.datetime] = {}
        
        # Session tracking
        self.active_sessions: Dict[str, Dict] = {}
        
        self.logger.info("SecurityManager initialized")
    
    def is_account_locked(self, username: str, ip_address: str = None) -> Tuple[bool, str]:
        """
        Check if an account or IP is currently locked.
        
        Args:
            username: Username to check
            ip_address: IP address to check (optional)
            
        Returns:
            Tuple[bool, str]: (is_locked, reason)
        """
        current_time = datetime.datetime.now()
        
        # Check if account is locked
        if username in self.locked_accounts:
            lock_time = self.locked_accounts[username]
            if (current_time - lock_time).total_seconds() < self.lockout_duration:
                remaining = self.lockout_duration - (current_time - lock_time).total_seconds()
                return True, f"Cuenta bloqueada. Intente en {int(remaining/60)} minutos"
            else:
                # Lockout expired, remove from locked accounts
                del self.locked_accounts[username]
                self.failed_attempts[username].clear()
        
        # Check if IP is locked
        if ip_address and ip_address in self.locked_ips:
            lock_time = self.locked_ips[ip_address]
            if (current_time - lock_time).total_seconds() < self.lockout_duration:
                remaining = self.lockout_duration - (current_time - lock_time).total_seconds()
                return True, f"IP bloqueada. Intente en {int(remaining/60)} minutos"
            else:
                # Lockout expired, remove from locked IPs
                del self.locked_ips[ip_address]
                self.ip_attempts[ip_address].clear()
        
        return False, ""
    
    def record_failed_attempt(self, username: str, ip_address: str = None) -> bool:
        """
        Record a failed login attempt and check if lockout is needed.
        
        Args:
            username: Username that failed
            ip_address: IP address of the attempt
            
        Returns:
            bool: True if account/IP should be locked
        """
        current_time = datetime.datetime.now()
        
        # Record failed attempt for username
        self.failed_attempts[username].append(current_time)
        
        # Record failed attempt for IP if provided
        if ip_address:
            self.ip_attempts[ip_address].append(current_time)
        
        # Check username attempts in the last hour
        recent_username_attempts = [
            attempt for attempt in self.failed_attempts[username]
            if (current_time - attempt).total_seconds() < 3600  # Last hour
        ]
        
        # Check IP attempts in the last hour
        recent_ip_attempts = []
        if ip_address:
            recent_ip_attempts = [
                attempt for attempt in self.ip_attempts[ip_address]
                if (current_time - attempt).total_seconds() < 3600  # Last hour
            ]
        
        should_lock = False
        
        # Lock account if too many attempts
        if len(recent_username_attempts) >= self.max_attempts:
            self.locked_accounts[username] = current_time
            should_lock = True
            self.logger.warning(f"Account locked due to failed attempts: {username}")
        
        # Lock IP if too many attempts
        if ip_address and len(recent_ip_attempts) >= self.max_attempts * 2:  # Higher threshold for IP
            self.locked_ips[ip_address] = current_time
            should_lock = True
            self.logger.warning(f"IP locked due to failed attempts: {ip_address}")
        
        return should_lock
    
    def record_successful_login(self, username: str, ip_address: str = None) -> None:
        """
        Record a successful login and clear failed attempts.
        
        Args:
            username: Username that logged in successfully
            ip_address: IP address of the successful login
        """
        # Clear failed attempts for this username
        if username in self.failed_attempts:
            self.failed_attempts[username].clear()
        
        # Remove account lock if it exists
        if username in self.locked_accounts:
            del self.locked_accounts[username]
        
        self.logger.info(f"Successful login recorded for: {username}")
    
    def create_session(self, username: str, user_id: int, ip_address: str = None) -> str:
        """
        Create a new user session.
        
        Args:
            username: Username
            user_id: User ID
            ip_address: IP address
            
        Returns:
            str: Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'username': username,
            'user_id': user_id,
            'ip_address': ip_address,
            'created_at': datetime.datetime.now(),
            'last_activity': datetime.datetime.now()
        }
        
        self.logger.info(f"Session created for user: {username}")
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str = None) -> Tuple[bool, Optional[Dict]]:
        """
        Validate an existing session.
        
        Args:
            session_id: Session ID to validate
            ip_address: Current IP address
            
        Returns:
            Tuple[bool, Optional[Dict]]: (is_valid, session_data)
        """
        if session_id not in self.active_sessions:
            return False, None
        
        session_data = self.active_sessions[session_id]
        current_time = datetime.datetime.now()
        
        # Check session timeout (8 hours)
        if (current_time - session_data['created_at']).total_seconds() > 28800:
            del self.active_sessions[session_id]
            self.logger.info(f"Session expired for user: {session_data['username']}")
            return False, None
        
        # Check inactivity timeout (2 hours)
        if (current_time - session_data['last_activity']).total_seconds() > 7200:
            del self.active_sessions[session_id]
            self.logger.info(f"Session timed out due to inactivity: {session_data['username']}")
            return False, None
        
        # Optional: Check IP consistency
        if ip_address and session_data.get('ip_address') != ip_address:
            self.logger.warning(f"IP mismatch for session: {session_data['username']}")
            # You might want to invalidate session or just log for now
        
        # Update last activity
        session_data['last_activity'] = current_time
        
        return True, session_data
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a user session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            bool: True if session was found and invalidated
        """
        if session_id in self.active_sessions:
            username = self.active_sessions[session_id]['username']
            del self.active_sessions[session_id]
            self.logger.info(f"Session invalidated for user: {username}")
            return True
        return False
    
    def get_security_stats(self) -> Dict:
        """
        Get security statistics.
        
        Returns:
            Dict: Security statistics
        """
        current_time = datetime.datetime.now()
        
        # Count active lockouts
        active_account_locks = len([
            username for username, lock_time in self.locked_accounts.items()
            if (current_time - lock_time).total_seconds() < self.lockout_duration
        ])
        
        active_ip_locks = len([
            ip for ip, lock_time in self.locked_ips.items()
            if (current_time - lock_time).total_seconds() < self.lockout_duration
        ])
        
        # Count recent failed attempts (last hour)
        recent_failed_attempts = 0
        for attempts in self.failed_attempts.values():
            recent_failed_attempts += len([
                attempt for attempt in attempts
                if (current_time - attempt).total_seconds() < 3600
            ])
        
        return {
            'active_sessions': len(self.active_sessions),
            'active_account_locks': active_account_locks,
            'active_ip_locks': active_ip_locks,
            'recent_failed_attempts': recent_failed_attempts,
            'total_tracked_accounts': len(self.failed_attempts),
            'total_tracked_ips': len(self.ip_attempts)
        }
    
    def cleanup_old_data(self) -> None:
        """
        Clean up old security data to prevent memory leaks.
        """
        current_time = datetime.datetime.now()
        
        # Remove old failed attempts (older than 24 hours)
        for username in list(self.failed_attempts.keys()):
            attempts = self.failed_attempts[username]
            # Keep only attempts from last 24 hours
            recent_attempts = deque([
                attempt for attempt in attempts
                if (current_time - attempt).total_seconds() < 86400
            ], maxlen=50)
            
            if recent_attempts:
                self.failed_attempts[username] = recent_attempts
            else:
                del self.failed_attempts[username]
        
        # Remove old IP attempts
        for ip in list(self.ip_attempts.keys()):
            attempts = self.ip_attempts[ip]
            recent_attempts = deque([
                attempt for attempt in attempts
                if (current_time - attempt).total_seconds() < 86400
            ], maxlen=100)
            
            if recent_attempts:
                self.ip_attempts[ip] = recent_attempts
            else:
                del self.ip_attempts[ip]
        
        # Remove expired locks
        expired_accounts = [
            username for username, lock_time in self.locked_accounts.items()
            if (current_time - lock_time).total_seconds() >= self.lockout_duration
        ]
        for username in expired_accounts:
            del self.locked_accounts[username]
        
        expired_ips = [
            ip for ip, lock_time in self.locked_ips.items()
            if (current_time - lock_time).total_seconds() >= self.lockout_duration
        ]
        for ip in expired_ips:
            del self.locked_ips[ip]
        
        self.logger.info("Security data cleanup completed")

# Global security manager instance
security_manager = SecurityManager()