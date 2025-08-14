"""
API REST para Rexus - Opcional
Versión: 2.0.0 - Enterprise Ready
"""

import re
import time
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from dataclasses import asdict
import threading

try:
    from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Mock básico de FastAPI y Pydantic
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class HTTPException(Exception):
        def __init__(self, status_code=500, detail="Internal Server Error"):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

    def Field(*args, **kwargs):
        return None

    def Depends(*args, **kwargs):
        return None

    class HTTPBearer:
        def __init__(self, *args, **kwargs):
            pass

    class HTTPAuthorizationCredentials:
        def __init__(self, scheme: str, credentials: str):
            self.scheme = scheme
            self.credentials = credentials

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from ..core.config import get_env_var, SECURITY_CONFIG
from ..core.logger import get_logger
from ..core.database_pool import database_transaction
from ..core.cache_manager import cache_manager
from ..core.backup_manager import backup_manager
from ..security.csrf_protection import init_csrf_protection, get_csrf_protection
from ..security.user_enumeration_protection import (
    init_user_enumeration_protection,
    get_user_enumeration_protection,
    record_login_attempt,
    get_response_delay,
    simulate_password_check
)
from ..security.password_manager import (
    init_password_manager,
    get_password_manager
)
from .validators import (
    InputSanitizer, ValidationError, PaginationModel,
    FilterModel, InventoryCreateModel, UserCreateModel, input_validator
)

logger = get_logger("api_server")

# Modelos Pydantic para la API
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_seconds: float

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class InventoryItem(BaseModel):
    id: Optional[int] = None
    codigo: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=200)
    cantidad: int = Field(..., ge=0)
    precio: float = Field(..., ge=0)
    categoria: Optional[str] = None

class InventoryResponse(BaseModel):
    items: List[InventoryItem]
    total: int
    page: int
    page_size: int

class APIStats(BaseModel):
    requests_total: int
    requests_per_minute: float
    average_response_time_ms: float
    active_connections: int
    cache_hit_rate: float

# Rate limiting simple
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
        self.lock = threading.RLock()

    def is_allowed(self, client_id: str) -> bool:
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Limpiar requests antiguos
            if client_id in self.requests:
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > window_start
                ]
            else:
                self.requests[client_id] = []

            # Verificar límite
            if len(self.requests[client_id]) >= self.max_requests:
                return False

            # Agregar nueva request
            self.requests[client_id].append(now)
            return True

class RexusAPI:
    """
    API REST para Rexus con autenticación, rate limiting y documentación automática
    """

    def __init__(self):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI no está disponible. Instala con: pip install fastapi uvicorn")

        if not JWT_AVAILABLE:
            logger.warning("JWT no disponible. Autenticación deshabilitada.")

        self.app = FastAPI(
            title="Rexus API",
            description="API REST para el sistema de gestión empresarial Rexus",
            version="2.0.0",
            docs_url="/docs" if get_env_var("API_ENABLED", False, var_type=bool) else None,
            redoc_url="/redoc" if get_env_var("API_ENABLED", False, var_type=bool) else None
        )

        # Estado de la API
        self.start_time = datetime.now()
        self.request_count = 0
        self.response_times = []
        self.rate_limiter = RateLimiter()

        # Configurar middleware
        self._setup_middleware()

        # Configurar rutas
        self._setup_routes()

        # Security
        self.security = HTTPBearer() if JWT_AVAILABLE else None

        # Inicializar protección CSRF
        try:
            init_csrf_protection(SECURITY_CONFIG.get("secret_key", "fallback_key"))
            logger.info("Protección CSRF inicializada")
        except Exception as e:
            logger.error(f"Error inicializando protección CSRF: {e}")

        # Inicializar protección contra enumeración de usuarios
        try:
            init_user_enumeration_protection()
            logger.info("Protección contra enumeración de usuarios inicializada")
        except Exception as e:
            logger.error(f"Error inicializando protección de enumeración: {e}")

        # Inicializar gestor de contraseñas
        try:
            init_password_manager()
            logger.info("Gestor de contraseñas inicializado")
        except Exception as e:
            logger.error(f"Error inicializando gestor de contraseñas: {e}")

        logger.info("RexusAPI inicializada")

    def _setup_middleware(self):
        """Configurar middleware de la API"""

        # Middleware de validación de entrada (primero)
        @self.app.middleware("http")
        async def input_validation_middleware(request: Request, call_next):
            """Middleware de validación y seguridad global."""
            from ..utils.secure_logger import log_security_event, log_info

            try:
                # Validar tamaño del request
                content_length = request.headers.get("content-length")
                if content_length:
                    input_validator.validate_request_size(int(content_length))

                # Leer y validar contenido si es POST/PUT/PATCH
                if request.method in ["POST", "PUT", "PATCH"]:
                    body = await request.body()
                    if body:
                        body_str = body.decode('utf-8', errors='ignore')
                        input_validator.scan_for_attacks(body_str)

                # Log de request
                log_info(f"API {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")

                # Procesar request
                response = await call_next(request)
                return response

            except ValidationError as e:
                log_security_event("INPUT_VALIDATION_FAILED", "MEDIUM", str(e.detail))
                return JSONResponse(
                    status_code=422,
                    content=e.detail
                )
            except Exception as e:
                log_security_event("MIDDLEWARE_ERROR", "HIGH", str(e))
                return JSONResponse(
                    status_code=500,
                    content={"error": "internal_server_error", "message": "Error de validación interno"}
                )

        # CORS
        cors_origins = get_env_var("API_CORS_ORIGINS", "http://localhost:3000").split(",")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        # Trusted hosts
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*"]  # Configurar según necesidades
        )

        # Middleware CSRF para métodos que modifican datos
        @self.app.middleware("http")
        async def csrf_protection_middleware(request: Request, call_next):
            """Middleware de protección CSRF para métodos POST/PUT/DELETE."""
            from ..utils.secure_logger import log_security_event

            # Solo verificar CSRF en métodos que modifican datos
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                try:
                    # Obtener token CSRF del header
                    csrf_token = request.headers.get("X-CSRF-Token")

                    if not csrf_token:
                        log_security_event("CSRF_TOKEN_MISSING", "MEDIUM", f"Method: {request.method}, Path: {request.url.path}")
                        return JSONResponse(
                            status_code=403,
                            content={"error": "csrf_token_required", "message": "Token CSRF requerido"}
                        )

                    # Obtener información del usuario (si está autenticado)
                    user_id = "anonymous"
                    auth_header = request.headers.get("Authorization")

                    if auth_header and JWT_AVAILABLE:
                        try:
                            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                            payload = jwt.decode(
                                token,
                                SECURITY_CONFIG["jwt_secret"],
                                algorithms=["HS256"]
                            )
                            user_id = payload.get("sub", "anonymous")
                        except Exception:
                            pass  # Mantener user_id como anonymous si falla

                    # Validar token CSRF
                    csrf_protection = get_csrf_protection()
                    is_valid, error_message = csrf_protection.validate_token_for_user(
                        csrf_token, user_id, consume=True
                    )

                    if not is_valid:
                        log_security_event("CSRF_TOKEN_INVALID", "HIGH",
                                          f"User: {user_id}, Error: {error_message}")
                        return JSONResponse(
                            status_code=403,
                            content={"error": "csrf_token_invalid", "message": error_message}
                        )

                except Exception as e:
                    log_security_event("CSRF_MIDDLEWARE_ERROR", "HIGH", str(e))
                    return JSONResponse(
                        status_code=500,
                        content={"error": "csrf_validation_error", "message": "Error validando CSRF"}
                    )

            return await call_next(request)

        # Middleware personalizado para logging y métricas
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            start_time = time.time()

            # Rate limiting
            client_ip = request.client.host
            if not self.rate_limiter.is_allowed(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"}
                )

            # Procesar request
            response = await call_next(request)

            # Métricas
            process_time = time.time() - start_time
            self.request_count += 1
            self.response_times.append(process_time)

            # Mantener solo las últimas 1000 response times
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]

            # Log
            logger.info("API Request", extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "status_code": response.status_code,
                "response_time_ms": round(process_time * 1000, 2)
            })

            # Headers de respuesta
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(self.request_count)

            return response

    def _setup_routes(self):
        """Configurar todas las rutas de la API"""

        # CSRF Token endpoint
        @self.app.get("/csrf-token", tags=["Security"])
        async def get_csrf_token(current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None):
            """Generar token CSRF para el usuario actual"""
            try:
                user_id = current_user.get('sub', 'anonymous') if current_user else 'anonymous'
                session_id = current_user.get('session_id') if current_user else None

                csrf_protection = get_csrf_protection()
                token = csrf_protection.generate_token_for_user(user_id, session_id)

                return {
                    "csrf_token": token,
                    "expires_in": 3600,  # 1 hora
                    "user_id": user_id
                }
            except Exception as e:
                from ..utils.secure_logger import log_error
                log_error(f"Error generando token CSRF: {str(e)}")
                raise HTTPException(status_code=500, detail="Error generando token CSRF")

        # Health check
        @self.app.get("/health", response_model=HealthResponse, tags=["System"])
        async def health_check():
            """Verificar estado de salud de la API"""
            uptime = (datetime.now() - self.start_time).total_seconds()

            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="2.0.0",
                uptime_seconds=uptime
            )

        # Autenticación con validación exhaustiva
        if JWT_AVAILABLE:
            @self.app.post("/auth/token", response_model=TokenResponse, tags=["Authentication"])
            async def login(username: str = Body(..., min_length=3, max_length=50),
                          password: str = Body(..., min_length=6, max_length=100)):
                """Obtener token de acceso con validación de seguridad"""
                from ..utils.secure_logger import log_security_event, log_user_action

                try:
                    # Rate limiting específico para login
                    client_ip = "unknown"

                    # Sanitizar entrada
                    safe_username = InputSanitizer.sanitize_string(username, max_length=50)

                    # Validar formato de username
                    if not re.match(r'^[a-zA-Z0-9._-]+$', safe_username):
                        log_security_event("INVALID_USERNAME_FORMAT", "MEDIUM", f"Username: {safe_username[:10]}...")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Formato de usuario inválido"
                        )

                    # Validar longitud de password
                    if len(password) < 6 or len(password) > 100:
                        log_security_event("INVALID_PASSWORD_LENGTH", "LOW", f"Username: {safe_username}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Longitud de contraseña inválida"
                        )

                    # Obtener IP del cliente
                    client_ip = request.client.host if hasattr(request, 'client') and \
                        request.client else "unknown"

                    # Verificar credenciales con protección contra enumeración
                    credentials_valid, user_exists = self._verify_credentials(safe_username,
                                                                             password,
                                                                             client_ip)

                    if not credentials_valid:
                        # Usar mensaje genérico para evitar revelación de información
                        error_message = get_user_enumeration_protection().get_generic_error_message()
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=error_message
                        )

                    # Log de login exitoso
                    log_user_action(safe_username, "LOGIN_SUCCESS", {"method": "API_TOKEN"})

                    # Generar token con información adicional
                    token_data = {
                        "sub": safe_username,
                        "exp": datetime.utcnow() + timedelta(hours=SECURITY_CONFIG.get("jwt_expiration_hours", 24)),
                        "iat": datetime.utcnow(),
                        "type": "access_token",
                        "version": "1.0"
                    }

                    token = jwt.encode(
                        token_data,
                        SECURITY_CONFIG["jwt_secret"],
                        algorithm="HS256"
                    )

                    return TokenResponse(
                        access_token=token,
                        expires_in=SECURITY_CONFIG.get("jwt_expiration_hours", 24) * 3600
                    )

                except HTTPException:
                    raise  # Re-raise HTTP exceptions as-is
                except Exception as e:
                    log_security_event("LOGIN_ERROR", "HIGH", str(e))
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error interno de autenticación"
                    )

        # Inventario endpoints
        @self.app.get("/api/v1/inventory", response_model=InventoryResponse, tags=["Inventory"])
        async def get_inventory(
            pagination: PaginationModel = Depends(),
            filters: FilterModel = Depends(),
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Obtener lista de inventario con paginación y filtros validados"""
            try:
                # Log de acceso seguro
                from ..utils.secure_logger import log_data_access
                username = current_user.get('sub', 'anonymous') if current_user else 'anonymous'
                log_data_access(username, 'inventario', 'READ')

                # Validar y sanitizar parámetros
                page, page_size = InputSanitizer.validate_pagination(pagination.page, pagination.page_size)

                # Sanitizar filtros
                safe_filters = {}
                if filters.categoria:
                    safe_filters['categoria'] = InputSanitizer.sanitize_string(filters.categoria, max_length=100)
                if filters.search:
                    safe_filters['search'] = InputSanitizer.sanitize_string(filters.search, max_length=255)

                # Cache key seguro (sin datos sensibles)
                cache_key = f"inventory:p:{page}:s:{page_size}:f:{hash(str(safe_filters))}"
                cached_result = cache_manager.get(cache_key)

                if cached_result:
                    return cached_result

                # Query a BD
                offset = (page - 1) * page_size

                with database_transaction("inventario") as conn:
                    # Construir query con filtros seguros
                    where_conditions = []
                    params = []

                    if safe_filters.get('categoria'):
                        where_conditions.append("categoria = ?")
                        params.append(safe_filters['categoria'])

                    if safe_filters.get('search'):
                        where_conditions.append("(codigo LIKE ? OR descripcion LIKE ?)")
                        search_pattern = f"%{safe_filters['search']}%"
                        params.extend([search_pattern, search_pattern])

                    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

                    query = f"""
                        SELECT id, codigo, descripcion, cantidad, precio, categoria
                        FROM inventario
                        {where_clause}
                        ORDER BY codigo
                        OFFSET ? ROWS
                        FETCH NEXT ? ROWS ONLY
                    """

                    cursor = conn.execute(query, params + [offset, page_size])
                    items = []

                    for row in cursor.fetchall():
                        items.append(InventoryItem(
                            id=row[0],
                            codigo=row[1],
                            descripcion=row[2],
                            cantidad=row[3],
                            precio=float(row[4]),
                            categoria=row[5]
                        ))

                    # Count total con mismos filtros
                    count_query = f"SELECT COUNT(*) FROM inventario {where_clause}"
                    count_params = params[:-2] if where_conditions else []  # Excluir offset y page_size
                    cursor = conn.execute(count_query, count_params)
                    total = cursor.fetchone()[0]

                result = InventoryResponse(
                    items=items,
                    total=total,
                    page=page,
                    page_size=page_size
                )

                # Cache por 5 minutos
                cache_manager.set(cache_key, result, timeout=300)

                return result

            except Exception as e:
                logger.error("Error obteniendo inventario", extra={"error": str(e)})
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.app.post("/api/v1/inventory", response_model=InventoryItem, tags=["Inventory"])
        async def create_inventory_item(
            item: InventoryCreateModel,
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Crear nuevo item de inventario con validación exhaustiva"""
            try:
                # Log de acceso seguro
                from ..utils.secure_logger import log_data_access, log_user_action
                username = current_user.get('sub', 'anonymous') if current_user else 'anonymous'
                log_data_access(username, 'inventario', 'CREATE')

                # Sanitizar todos los campos
                safe_nombre = InputSanitizer.sanitize_string(item.nombre, max_length=255)
                safe_categoria = InputSanitizer.sanitize_string(item.categoria, max_length=100)

                # Validaciones adicionales de negocio
                if float(item.precio) < 0 or float(item.precio) > 999999999.99:
                    raise ValidationError("Precio fuera del rango permitido", "precio")

                if item.stock < 0 or item.stock > 999999:
                    raise ValidationError("Stock fuera del rango permitido", "stock")

                with database_transaction("inventario") as conn:
                    # Verificar si el código ya existe
                    check_query = "SELECT COUNT(*) FROM inventario WHERE codigo = ?"
                    cursor = conn.execute(check_query, (safe_codigo,))
                    if cursor.fetchone()[0] > 0:
                        raise ValidationError("El código ya existe", "codigo")

                    # Insertar nuevo item
                    query = """
                        INSERT INTO inventario (codigo,
descripcion,
                            cantidad,
                            precio,
                            categoria)
                        OUTPUT INSERTED.id
                        VALUES (?, ?, ?, ?, ?)
                    """

                    cursor = conn.execute(query, (
                        safe_codigo,
                        safe_nombre,  # Usar nombre como descripción
                        item.stock,   # Usar stock como cantidad
                        float(item.precio),
                        safe_categoria
                    ))

                    new_id = cursor.fetchone()[0]

                    # Crear respuesta compatible
                    created_item = InventoryItem(
                        id=new_id,
                        codigo=safe_codigo,
                        descripcion=safe_nombre,
                        cantidad=item.stock,
                        precio=float(item.precio),
                        categoria=safe_categoria
                    )

                # Invalidar cache
                cache_manager.delete("inventory:*")

                # Log de auditoría seguro
                log_user_action(
                    username,
                    "inventory_create",
                    {"item_id": new_id, "item_code": safe_codigo, "category": safe_categoria}
                )

                return created_item

            except ValidationError:
                raise  # Re-raise validation errors as-is
            except Exception as e:
                from ..utils.secure_logger import log_error
                log_error(f"Error creando item de inventario: {str(e)}")
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        # Usuarios endpoints con validación exhaustiva
        @self.app.post("/api/v1/users", response_model=dict, tags=["Users"])
        async def create_user(
            user: UserCreateModel,
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Crear nuevo usuario con validación exhaustiva"""
            try:
                from ..utils.secure_logger import log_data_access, log_user_action, log_security_event
                username = current_user.get('sub', 'anonymous') if current_user else 'anonymous'

                # Validar permisos de administrador (en producción)
                if current_user and current_user.get('sub') != 'admin':
                    log_security_event("UNAUTHORIZED_USER_CREATE", "HIGH", f"User: {username}")
                    raise HTTPException(status_code=403, detail="Permisos insuficientes")

                # Log de acceso
                log_data_access(username, 'usuarios', 'CREATE')

                # Sanitizar todos los campos de entrada
                safe_username = InputSanitizer.sanitize_string(user.username, max_length=50)
                safe_email = InputSanitizer.sanitize_string(user.email, max_length=255)
                safe_nombre = InputSanitizer.sanitize_string(user.nombre, max_length=100)
                safe_apellido = InputSanitizer.sanitize_string(user.apellido, max_length=100)
                safe_departamento = InputSanitizer.sanitize_string(user.departamento, max_length=100) if user.departamento else None

                # Validaciones adicionales de negocio
                if len(safe_username) < 3:
                    raise ValidationError("Username debe tener al menos 3 caracteres", "username")

                # Verificar que el email no exista
                with database_transaction("users") as conn:
                    check_query = "SELECT COUNT(*) FROM usuarios WHERE email = ? OR username = ?"
                    cursor = conn.execute(check_query, (safe_email, safe_username))
                    if cursor.fetchone()[0] > 0:
                        raise ValidationError("Usuario o email ya existe", "duplicate")

                    # Crear usuario (password será generada/enviada por separado)
                    insert_query = """
                        INSERT INTO usuarios (username, email, nombre, apellido, rol, departamento, activo, fecha_creacion)
                        OUTPUT INSERTED.id
                        VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
                    """

                    cursor = conn.execute(insert_query, (
                        safe_username,
                        safe_email,
                        safe_nombre,
                        safe_apellido,
                        user.rol,
                        safe_departamento
                    ))

                    new_user_id = cursor.fetchone()[0]

                # Log de auditoría
                log_user_action(
                    username,
                    "user_create",
                    {"new_user_id": new_user_id, "new_username": safe_username, "role": user.rol}
                )

                return {
                    "message": "Usuario creado exitosamente",
                    "user_id": new_user_id,
                    "username": safe_username
                }

            except ValidationError:
                raise  # Re-raise validation errors as-is
            except HTTPException:
                raise  # Re-raise HTTP exceptions as-is
            except Exception as e:
                from ..utils.secure_logger import log_error
                log_error(f"Error creando usuario: {str(e)}")
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        # Estadísticas
        @self.app.get("/api/v1/stats", response_model=APIStats, tags=["System"])
        async def get_api_stats(
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Obtener estadísticas de la API"""
            cache_stats = cache_manager.get_stats()

            avg_response_time = (
                sum(self.response_times) / len(self.response_times) * 1000
                if self.response_times else 0
            )

            # Requests por minuto (últimos 60 segundos)
            recent_requests = len([
                t for t in self.response_times
                if time.time() - t < 60
            ])

            return APIStats(
                requests_total=self.request_count,
                requests_per_minute=recent_requests,
                average_response_time_ms=round(avg_response_time, 2),
                active_connections=0,  # Implementar si necesario
                cache_hit_rate=cache_stats.get("hit_rate", 0.0)
            )

        # Backup endpoints
        @self.app.post("/api/v1/backup/run", tags=["System"])
        async def run_backup(
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Ejecutar backup manual"""
            try:
                results = backup_manager.backup_all()

                return {
                    "message": "Backup ejecutado",
                    "results": [asdict(result) for result in results]
                }
            except Exception as e:
                logger.error("Error ejecutando backup", extra={"error": str(e)})
                raise HTTPException(status_code=500, detail="Error ejecutando backup")

        @self.app.get("/api/v1/backup/status", tags=["System"])
        async def get_backup_status(
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Obtener estado del sistema de backup"""
            try:
                return backup_manager.get_backup_status()
            except Exception as e:
                logger.error("Error obteniendo estado de backup", extra={"error": str(e)})
                raise HTTPException(status_code=500, detail="Error obteniendo estado")

    def _verify_credentials(self,
username: str,
        password: str,
        ip_address: str = "unknown") -> Tuple[bool,
        bool]:
        """
        Verificar credenciales con protección contra enumeración y timing attacks.

        Args:
            username: Nombre de usuario sanitizado
            password: Contraseña
            ip_address: Dirección IP del cliente

        Returns:
            Tuple[bool, bool]: (credenciales_válidas, usuario_existe)
        """
        try:
            from ..utils.secure_logger import log_security_event
            import time

            start_time = time.time()
            user_exists = False
            credentials_valid = False

            # Verificar si IP puede hacer intentos
            enum_protection = get_user_enumeration_protection()
            ip_allowed, error_msg = enum_protection.is_ip_allowed(ip_address)

            if not ip_allowed:
                log_security_event("IP_BLOCKED_LOGIN_ATTEMPT", "HIGH",
                                  f"IP: {ip_address}, User: {username}")
                # Simular verificación para timing consistency
                simulate_password_check(username)
                return False, False

            # Verificar credenciales usando el gestor de contraseñas
            import os
            if os.getenv('APP_ENV', 'development') == 'development':
                # Credenciales de desarrollo desde variables de entorno
                password_mgr = get_password_manager()

                # Obtener credenciales de desarrollo desde el entorno (NO hardcodeadas)
                admin_password = os.getenv("API_ADMIN_PASSWORD")
                api_password = os.getenv("API_USER_PASSWORD")

                if not admin_password or not api_password:
                    log_security_event("MISSING_CREDENTIALS", "HIGH",
                                     "Variables de entorno API_ADMIN_PASSWORD y API_USER_PASSWORD no definidas")
                    return False, False

                dev_users = {
                    "admin": password_mgr.hash_password(admin_password),
                    "api_user": password_mgr.hash_password(api_password)
                }

                user_exists = username in dev_users

                if user_exists:
                    credentials_valid = password_mgr.verify_password(password, dev_users[username])
                else:
                    # Simular verificación para usuarios inexistentes
                    simulate_password_check(username)

            else:
                # En producción, consultar base de datos
                try:
                    password_mgr = get_password_manager()

                    with database_transaction("users") as conn:
                        query = "SELECT password_hash, activo FROM usuarios WHERE username = ?"
                        cursor = conn.execute(query, (username,))
                        result = cursor.fetchone()

                        user_exists = result is not None

                        if user_exists:
                            stored_hash, activo = result
                            if activo:
                                # Verificar contraseña usando el gestor seguro
                                credentials_valid = password_mgr.verify_password(password, stored_hash)
                            else:
                                credentials_valid = False
                                log_security_event("LOGIN_USER_DISABLED", "MEDIUM", f"Username: {username}")
                        else:
                            # Simular verificación para usuarios inexistentes
                            simulate_password_check(username)

                except Exception as e:
                    log_security_event("LOGIN_DB_ERROR", "HIGH", str(e))
                    # Simular verificación en caso de error
                    simulate_password_check(username)

            # Registrar intento en sistema de protección
            record_login_attempt(ip_address,
username,
                credentials_valid,
                user_exists)

            # Aplicar delay consistente para prevenir timing attacks
            required_delay = get_response_delay(username, user_exists)
            elapsed_time = time.time() - start_time
            remaining_delay = max(0, required_delay - elapsed_time)

            if remaining_delay > 0:
                time.sleep(remaining_delay)

            # Log del resultado
            if credentials_valid:
                log_security_event("LOGIN_SUCCESS", "INFO",
                                  f"Username: {username}, IP: {ip_address}")
            else:
                result_type = "USER_NOT_EXISTS" if not user_exists else "INVALID_PASSWORD"
                log_security_event(f"LOGIN_FAILED_{result_type}", "MEDIUM",
                                  f"Username: {username}, IP: {ip_address}")

            return credentials_valid, user_exists

        except Exception as e:
            from ..utils.secure_logger import log_error
            log_error(f"Error verificando credenciales: {str(e)}")
            # Simular verificación en caso de error crítico
            simulate_password_check(username)
            return False, False

    async def _get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Obtener usuario actual desde token JWT"""
        if not JWT_AVAILABLE:
            return {"sub": "anonymous"}

        try:
            payload = jwt.decode(
                credentials.credentials,
                SECURITY_CONFIG["jwt_secret"],
                algorithms=["HS256"]
            )

            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

    def run(self,
host: str = "0.0.0.0",
        port: int = 8000,
        debug: bool = False):
        """Ejecutar servidor API"""
        logger.info("Iniciando servidor API", extra={
            "host": host,
            "port": port,
            "debug": debug
        })

        uvicorn.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            access_log=False  # Usamos nuestro logging personalizado
        )

# Funciones de conveniencia
def create_api_server() -> RexusAPI:
    """Crear instancia del servidor API"""
    return RexusAPI()

def run_api_server():
    """Ejecutar servidor API con configuración desde variables de entorno"""
    if not get_env_var("API_ENABLED", False, var_type=bool):
        logger.info("API deshabilitada por configuración")
        return

    api = create_api_server()
    api.run(
        host=get_env_var("API_HOST", "0.0.0.0"),
        port=get_env_var("API_PORT", 8000, var_type=int),
        debug=get_env_var("APP_DEBUG", False, var_type=bool)
    )

# Ejecutar como script independiente
if __name__ == "__main__":
    run_api_server()
