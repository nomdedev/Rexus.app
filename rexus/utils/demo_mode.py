"""
Modo Demo para Rexus.app

Sistema que proporciona datos falsos cuando no hay conexión a BD
o cuando se habilita explícitamente el modo demo.
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class DemoDataProvider:
    """Proveedor de datos demo para todos los módulos."""

    def __init__(self):
        """Inicializa el proveedor con datos base."""
        self.demo_mode_enabled = self._check_demo_mode()
        self._init_base_data()

    def _check_demo_mode(self) -> bool:
        """Verifica si el modo demo está habilitado."""
        return os.getenv('REXUS_MODO_DEMO',
'false').lower() in ['true',
            '1',
            'yes',
            'on']

    def _init_base_data(self):
        """Inicializa datos base para generar datos demo."""
        self.proveedores = [
            "Vidrios del Sur SA", "Herrajes Premium SRL", "Aluminios Modernos SA",
            "Cristales Industriales SA", "Accesorios del Vidrio SRL", "Técnica Vidrios SA"
        ]

        self.clientes = [
            "Constructora Delta SA", "Inmobiliaria Norte SRL", "Edificios Modernos SA",
            "Reformas Integrales SA", "Arquitectura Avanzada SRL", "Construcciones Sur SA"
        ]

        self.direcciones_laplata = [
            "Calle 7 entre 47 y 48, La Plata", "Av. 13 y 60, La Plata",
            "Calle 50 entre 15 y 16, Berisso", "Calle 25 entre 3 y 4, Gonnet",
            "Av. 122 y 82, Los Hornos", "Calle 1 y 57, Tolosa"
        ]

    def is_demo_mode(self) -> bool:
        """Retorna si el modo demo está activo."""
        return self.demo_mode_enabled

    def get_demo_usuarios(self) -> List[Dict[str, Any]]:
        """Retorna usuarios demo."""
        return [
            {
                "id": 1, "username": "admin", "nombre": "Administrador", "apellido": "Sistema",
                "email": "admin@rexus.app", "rol": "ADMIN", "estado": "Activo",
                "ultimo_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_creacion": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            },
            {
                "id": 2, "username": "supervisor", "nombre": "Carlos", "apellido": "Supervisor",
                "email": "supervisor@rexus.app", "rol": "SUPERVISOR", "estado": "Activo",
                "ultimo_login": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_creacion": (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d')
            },
            {
                "id": 3, "username": "operador1", "nombre": "María", "apellido": "González",
                "email": "maria@rexus.app", "rol": "OPERADOR", "estado": "Activo",
                "ultimo_login": (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_creacion": (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
            },
            {
                "id": 4, "username": "contador", "nombre": "Ana", "apellido": "Martínez",
                "email": "ana@rexus.app", "rol": "CONTABILIDAD", "estado": "Activo",
                "ultimo_login": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_creacion": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
            }
        ]

    def get_demo_obras(self) -> List[Dict[str, Any]]:
        """Retorna obras demo."""
        obras = []
        estados = ["PLANIFICACION", "EN_PROCESO", "PAUSADA", "COMPLETADA"]
        tipos = ["Residencial", "Comercial", "Industrial", "Institucional"]

        for i in range(1, 21):  # 20 obras demo
            fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 180))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(60, 300))

            obra = {
                "id": i,
                "codigo": f"OBR-2024-{i:03d}",
                "nombre": f"Proyecto {random.choice(tipos)} {i}",
                "cliente": random.choice(self.clientes),
                "direccion": random.choice(self.direcciones_laplata),
                "telefono": f"+54 221 {random.randint(400, 499)}-{random.randint(1000, 9999)}",
                "email": f"proyecto{i}@cliente.com",
                "tipo_obra": random.choice(tipos),
                "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_fin": fecha_fin.strftime('%Y-%m-%d'),
                "estado": random.choice(estados),
                "presupuesto": round(random.uniform(50000, 500000), 2),
                "observaciones": f"Obra de ejemplo para demostración - Proyecto {i}",
                "usuario_creacion": "admin",
                "fecha_creacion": fecha_inicio.strftime('%Y-%m-%d')
            }
            obras.append(obra)

        return obras

    def get_demo_inventario(self) -> List[Dict[str, Any]]:
        """Retorna productos de inventario demo."""
        productos = []
        tipos = ["Marco", "Perfil", "Accesorio", "Vidrio", "Sellador", "Herraje"]
        acabados = ["Anodizado", "Natural", "Lacado", "Cromado", "Galvanizado", "Transparente"]
        unidades = ["UNIDAD", "METRO", "M2", "KG"]

        descripciones = {
            "Marco": ["Marco de ventana", "Marco de puerta", "Marco oscilobatiente"],
            "Perfil": ["Perfil estructural", "Perfil de unión", "Perfil angular"],
            "Accesorio": ["Manija", "Cierre", "Cerradura", "Bisagra"],
            "Vidrio": ["Vidrio templado", "Vidrio laminado", "Vidrio común"],
            "Sellador": ["Sellador de silicona", "Sellador estructural", "Sellador secundario"],
            "Herraje": ["Bisagra pesada", "Cerrojo", "Tornillería"]
        }

        for i in range(1, 51):  # 50 productos demo
            tipo = random.choice(tipos)
            descripcion_base = random.choice(descripciones[tipo])

            producto = {
                "id": i,
                "codigo": f"INV-{tipo[:3].upper()}-{i:04d}",
                "descripcion": f"{descripcion_base} {random.randint(50, 300)}cm",
                "tipo": tipo,
                "acabado": random.choice(acabados),
                "unidad": random.choice(unidades),
                "importe": round(random.uniform(10, 500), 2),
                "stock_actual": random.randint(0, 150),
                "stock_minimo": random.randint(5, 25),
                "proveedor": random.choice(self.proveedores),
                "ubicacion": f"Sector {random.choice(['A',
'B',
                    'C'])}-{random.randint(1,
                    30)}",
                "estado": "Activo",
                "fecha_creacion": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')
            }
            productos.append(producto)

        return productos

    def get_demo_compras(self) -> List[Dict[str, Any]]:
        """Retorna órdenes de compra demo."""
        compras = []
        estados = ["PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]

        for i in range(1, 16):  # 15 órdenes demo
            fecha_pedido = datetime.now() - timedelta(days=random.randint(5, 60))
            fecha_entrega = fecha_pedido + timedelta(days=random.randint(7, 30))

            subtotal = round(random.uniform(1000, 25000), 2)
            descuento = round(random.uniform(0, subtotal * 0.1), 2)
            impuestos = round(subtotal * 0.21, 2)  # IVA 21%
            total = subtotal - descuento + impuestos

            compra = {
                "id": i,
                "numero_orden": f"OC-2024-{i:04d}",
                "proveedor": random.choice(self.proveedores),
                "fecha_pedido": fecha_pedido.strftime('%Y-%m-%d'),
                "fecha_entrega_estimada": fecha_entrega.strftime('%Y-%m-%d'),
                "estado": random.choice(estados),
                "subtotal": subtotal,
                "descuento": descuento,
                "impuestos": impuestos,
                "total": total,
                "observaciones": f"Orden de compra de ejemplo #{i}",
                "usuario_creacion": "admin",
                "fecha_creacion": fecha_pedido.strftime('%Y-%m-%d')
            }
            compras.append(compra)

        return compras

    def get_demo_logistica(self) -> List[Dict[str, Any]]:
        """Retorna datos de logística demo."""
        entregas = []
        estados = ["Programada", "En Tránsito", "Entregada", "Cancelada"]

        for i in range(1, 26):  # 25 entregas demo
            fecha_programada = datetime.now() + timedelta(days=random.randint(-15, 30))

            entrega = {
                "id": i,
                "codigo": f"ENT-{i:04d}",
                "fecha_programada": fecha_programada.strftime('%Y-%m-%d'),
                "direccion_entrega": random.choice(self.direcciones_laplata),
                "estado": random.choice(estados),
                "contacto": f"Cliente {i}",
                "telefono": f"+54 221 {random.randint(400, 499)}-{random.randint(1000, 9999)}",
                "observaciones": f"Entrega de materiales para obra - Demo {i}",
                "usuario_creacion": "admin",
                "fecha_creacion": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            }
            entregas.append(entrega)

        return entregas

    def get_demo_estadisticas(self, modulo: str) -> Dict[str, Any]:
        """Retorna estadísticas demo para un módulo específico."""
        base_stats = {
            "inventario": {
                "total_productos": 50,
                "productos_activos": 47,
                "productos_bajo_stock": 8,
                "valor_total_inventario": 45750.00,
                "productos_sin_stock": 3,
                "categorias_activas": 6
            },
            "obras": {
                "total_obras": 20,
                "obras_activas": 12,
                "obras_completadas": 6,
                "obras_pausadas": 2,
                "presupuesto_total": 2456000.00,
                "obras_mes_actual": 3
            },
            "compras": {
                "total_ordenes": 15,
                "ordenes_pendientes": 4,
                "ordenes_aprobadas": 6,
                "ordenes_recibidas": 4,
                "ordenes_canceladas": 1,
                "monto_total": 187500.00
            },
            "usuarios": {
                "total_usuarios": 4,
                "usuarios_activos": 4,
                "usuarios_inactivos": 0,
                "logins_hoy": 8,
                "ultimo_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "logistica": {
                "entregas_programadas": 8,
                "entregas_en_transito": 3,
                "entregas_completadas": 12,
                "entregas_canceladas": 2,
                "eficiencia_entregas": 92.5
            }
        }

        return base_stats.get(modulo, {})

    def authenticate_demo_user(self,
username: str,
        password: str) -> Optional[Dict[str,
        Any]]:
        """Autentica un usuario en modo demo."""
        if not self.is_demo_mode():
            return None

        # Credenciales demo válidas
        # Obtener credenciales desde variables de entorno
        from rexus.utils.env_manager import get_demo_credentials
        env_credentials = get_demo_credentials()

        demo_credentials = {
            "admin": {"password": env_credentials.get("admin"), "role": "ADMIN"},
            "supervisor": {"password": env_credentials.get("supervisor"), "role": "SUPERVISOR"},
            "operador": {"password": env_credentials.get("operador"), "role": "OPERADOR"},
            "contador": {"password": env_credentials.get("contador"), "role": "CONTABILIDAD"}
        }

        # Validar que todas las credenciales estén disponibles
        for user, creds in demo_credentials.items():
            if not creds["password"]:
                print(f"[SECURITY WARNING] Credenciales demo para '{user}' no definidas en variables de entorno")
                return False

        if username in demo_credentials and \
            demo_credentials[username]["password"] == password:
            usuarios_demo = self.get_demo_usuarios()
            user_data = next((u for u in usuarios_demo if u["username"] == username), None)

            if user_data:
                # Actualizar último login
                user_data["ultimo_login"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return user_data

        return None


# Instancia global del proveedor demo
demo_provider = DemoDataProvider()


def get_demo_data(modulo: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Función de conveniencia para obtener datos demo de cualquier módulo.

    Args:
        modulo: Nombre del módulo (usuarios, obras, inventario, etc.)
        **kwargs: Parámetros adicionales para filtros

    Returns:
        Lista de datos demo para el módulo especificado
    """
    if not demo_provider.is_demo_mode():
        return []

    method_map = {
        "usuarios": demo_provider.get_demo_usuarios,
        "obras": demo_provider.get_demo_obras,
        "inventario": demo_provider.get_demo_inventario,
        "compras": demo_provider.get_demo_compras,
        "logistica": demo_provider.get_demo_logistica
    }

    method = method_map.get(modulo)
    if method:
        data = method()

        # Aplicar filtros básicos si se proporcionan
        if "limit" in kwargs:
            data = data[:kwargs["limit"]]

        if "estado" in kwargs:
            data = [item for item in data if item.get("estado") == kwargs["estado"]]

        return data

    return []


def is_demo_mode_active() -> bool:
    """Verifica si el modo demo está activo."""
    return demo_provider.is_demo_mode()


def enable_demo_mode():
    """Habilita el modo demo."""
    os.environ['REXUS_MODO_DEMO'] = 'true'
    demo_provider.demo_mode_enabled = True


def disable_demo_mode():
    """Deshabilita el modo demo."""
    os.environ['REXUS_MODO_DEMO'] = 'false'
    demo_provider.demo_mode_enabled = False
