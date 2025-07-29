"""
API REST para Rexus - Opcional
Versión: 2.0.0 - Enterprise Ready
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import asyncio
import threading

try:
    from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from ..core.config import get_env_var, SECURITY_CONFIG
from ..core.logger import get_logger
from ..core.database_pool import get_database_pool, database_transaction
from ..core.cache_manager import cache_manager
from ..core.backup_manager import backup_manager

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
        
        logger.info("RexusAPI inicializada")
    
    def _setup_middleware(self):
        """Configurar middleware de la API"""
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
        
        # Autenticación
        if JWT_AVAILABLE:
            @self.app.post("/auth/token", response_model=TokenResponse, tags=["Authentication"])
            async def login(username: str, password: str):
                """Obtener token de acceso"""
                # Verificar credenciales (implementar según necesidades)
                if not self._verify_credentials(username, password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Credenciales inválidas"
                    )
                
                # Generar token
                token_data = {
                    "sub": username,
                    "exp": datetime.utcnow() + timedelta(hours=24),
                    "iat": datetime.utcnow()
                }
                
                token = jwt.encode(
                    token_data,
                    SECURITY_CONFIG["jwt_secret"],
                    algorithm="HS256"
                )
                
                return TokenResponse(
                    access_token=token,
                    expires_in=86400  # 24 horas
                )
        
        # Inventario endpoints
        @self.app.get("/api/v1/inventory", response_model=InventoryResponse, tags=["Inventory"])
        async def get_inventory(
            page: int = 1,
            page_size: int = 50,
            categoria: Optional[str] = None,
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Obtener lista de inventario con paginación"""
            try:
                # Cache key
                cache_key = f"inventory:page:{page}:size:{page_size}:cat:{categoria}"
                cached_result = cache_manager.get(cache_key)
                
                if cached_result:
                    return cached_result
                
                # Query a BD
                offset = (page - 1) * page_size
                
                with database_transaction("inventario") as conn:
                    # Query principal
                    where_clause = "WHERE categoria = ?" if categoria else ""
                    params = (categoria,) if categoria else ()
                    
                    query = """
                        SELECT id, codigo, descripcion, cantidad, precio, categoria
                        FROM inventario
                        """ + where_clause + """
                        ORDER BY codigo
                        OFFSET ? ROWS
                        FETCH NEXT ? ROWS ONLY
                    """
                    
                    cursor = conn.execute(query, params + (offset, page_size))
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
                    
                    # Count total
                    # Use secure string concatenation instead of f-string
                    count_query = "SELECT COUNT(*) FROM inventario " + where_clause
                    cursor = conn.execute(count_query, params)
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
            item: InventoryItem,
            current_user: dict = Depends(self._get_current_user) if JWT_AVAILABLE else None
        ):
            """Crear nuevo item de inventario"""
            try:
                with database_transaction("inventario") as conn:
                    query = """
                        INSERT INTO inventario (codigo, descripcion, cantidad, precio, categoria)
                        OUTPUT INSERTED.id
                        VALUES (?, ?, ?, ?, ?)
                    """
                    
                    cursor = conn.execute(query, (
                        item.codigo,
                        item.descripcion,
                        item.cantidad,
                        item.precio,
                        item.categoria
                    ))
                    
                    new_id = cursor.fetchone()[0]
                    item.id = new_id
                
                # Invalidar cache
                cache_manager.delete("inventory:*")
                
                # Log de auditoría
                logger.audit(
                    action="inventory_create",
                    user=current_user.get("sub") if current_user else "api_user",
                    resource=f"inventory:{new_id}",
                    result="success",
                    extra={"item_code": item.codigo}
                )
                
                return item
                
            except Exception as e:
                logger.error("Error creando item", extra={"error": str(e)})
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
    
    def _verify_credentials(self, username: str, password: str) -> bool:
        """Verificar credenciales de usuario (implementar según necesidades)"""
        # Implementación básica - en producción usar hash real
        test_users = {
            "admin": "admin123",
            "api_user": "api123"
        }
        
        return test_users.get(username) == password
    
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
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
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