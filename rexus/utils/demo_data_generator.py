"""
Generador de datos demo para Rexus.app

Este módulo proporciona datos de ejemplo realistas para todos los módulos
de la aplicación, útil para testing y demostración.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict, Any


class DemoDataGenerator:
    """Generador de datos demo para todos los módulos."""

    # Datos base para generación
    NOMBRES = ["Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "Miguel", "Isabel", "José", "Laura"]
    APELLIDOS = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez", "Cruz", "Flores"]

    DIRECCIONES_LA_PLATA = [
        "Calle 7 entre 47 y 48, La Plata",
        "Av. 13 y 60, La Plata",
        "Calle 50 entre 15 y 16, Berisso",
        "Calle 25 entre 3 y 4, Gonnet",
        "Av. 122 y 82, Los Hornos",
        "Calle 1 y 57, Tolosa",
        "Calle 10 y 38, City Bell",
        "Av. 44 y 150, Villa Elisa",
        "Calle 520 y 15, Melchor Romero",
        "Calle 2 y 64, Ringuelet"
    ]

    TIPOS_VIDRIO = ["Templado", "Laminado", "Float", "Espejo", "Doble Vidriado Hermético"]
    ACABADOS_VIDRIO = ["Natural", "Bronceado", "Reflectivo", "Satinado", "Serigrafía"]

    TIPOS_HERRAJE = ["Bisagra", "Cerradura", "Manija", "Tirador", "Pestillo", "Corredera"]

    ESTADOS_OBRA = ["Planificada", "En Proceso", "Pausada", "Finalizada", "Cancelada"]
    ESTADOS_PEDIDO = ["Borrador", "Pendiente", "Aprobado", "En Preparación", "Entregado"]
    ESTADOS_ENTREGA = ["Programada", "En Preparación", "En Tránsito", "Entregada"]

    @staticmethod
    def generar_inventario_demo() -> List[Dict[str, Any]]:
        """Genera datos demo para el módulo de inventario."""
        productos = []

        # Generar vidrios
        for i in range(50):
            producto = {
                'id': i + 1,
                'codigo': f"VID-{1000 + i}",
                'descripcion': f"Vidrio {random.choice(DemoDataGenerator.TIPOS_VIDRIO)} {random.randint(4, 12)}mm",
                'tipo': 'Vidrio',
                'acabado': random.choice(DemoDataGenerator.ACABADOS_VIDRIO),
                'stock': random.randint(5, 100),
                'stock_minimo': random.randint(10, 20),
                'importe': round(random.uniform(50, 500), 2),
                'unidad': 'm²',
                'proveedor': f"Proveedor {random.choice(['A', 'B', 'C'])}",
                'fecha_actualizacion': datetime.now() - timedelta(days=random.randint(0, 30))
            }
            productos.append(producto)

        # Generar herrajes
        for i in range(30):
            producto = {
                'id': i + 51,
                'codigo': f"HER-{2000 + i}",
                'descripcion': f"{random.choice(DemoDataGenerator.TIPOS_HERRAJE)} {random.choice(['Estándar', 'Premium', 'Industrial'])}",
                'tipo': 'Herraje',
                'acabado': random.choice(['Aluminio',
'Acero',
                    'Bronce',
                    'Negro']),
                'stock': random.randint(10, 200),
                'stock_minimo': random.randint(15, 25),
                'importe': round(random.uniform(20, 150), 2),
                'unidad': 'unidad',
                'proveedor': f"Herrajes {random.choice(['Del Sur', 'Premium', 'Industriales'])}",
                'fecha_actualizacion': datetime.now() - timedelta(days=random.randint(0, 30))
            }
            productos.append(producto)

        return productos

    @staticmethod
    def generar_obras_demo() -> List[Dict[str, Any]]:
        """Genera datos demo para el módulo de obras."""
        obras = []

        for i in range(15):
            fecha_inicio = datetime.now() - timedelta(days=random.randint(0, 60))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(15, 90))

            obra = {
                'id': i + 1,
                'numero_obra': f"OBR-{2025}-{1000 + i}",
                'nombre': f"Obra {random.choice(['Residencial', 'Comercial', 'Industrial'])} {i + 1}",
                'cliente': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'direccion': random.choice(DemoDataGenerator.DIRECCIONES_LA_PLATA),
                'fecha_inicio': fecha_inicio,
                'fecha_fin_estimada': fecha_fin,
                'estado': random.choice(DemoDataGenerator.ESTADOS_OBRA),
                'presupuesto': round(random.uniform(50000, 500000), 2),
                'responsable': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'descripcion': f"Proyecto de {random.choice(['construcción', 'remodelación', 'ampliación'])} con instalación de {random.choice(['ventanas', 'fachadas', 'cerramientos'])}",
                'telefono': f"221-{random.randint(1000000, 9999999)}"
            }
            obras.append(obra)

        return obras

    @staticmethod
    def generar_pedidos_demo() -> List[Dict[str, Any]]:
        """Genera datos demo para el módulo de pedidos."""
        pedidos = []

        for i in range(20):
            fecha_pedido = datetime.now() - timedelta(days=random.randint(0, 30))
            fecha_entrega = fecha_pedido + timedelta(days=random.randint(5, 15))

            pedido = {
                'id': i + 1,
                'numero_pedido': f"PED-{fecha_pedido.year}-{10000 + i}",
                'cliente': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'fecha_pedido': fecha_pedido,
                'fecha_entrega_solicitada': fecha_entrega,
                'estado': random.choice(DemoDataGenerator.ESTADOS_PEDIDO),
                'total': round(random.uniform(5000, 50000), 2),
                'direccion_entrega': random.choice(DemoDataGenerator.DIRECCIONES_LA_PLATA),
                'responsable_entrega': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'telefono_contacto': f"221-{random.randint(1000000, 9999999)}",
                'observaciones': f"Pedido de {random.choice(['ventanas', 'puertas', 'herrajes', 'vidrios especiales'])}",
                'prioridad': random.choice(['Normal', 'Alta', 'Urgente'])
            }
            pedidos.append(pedido)

        return pedidos

    @staticmethod
    def generar_logistica_demo() -> Dict[str, List[Dict[str, Any]]]:
        """Genera datos demo para el módulo de logística."""
        # Entregas
        entregas = []
        for i in range(12):
            fecha_programada = datetime.now() + timedelta(days=random.randint(0, 15))

            entrega = {
                'id': i + 1,
                'fecha_programada': fecha_programada,
                'direccion': random.choice(DemoDataGenerator.DIRECCIONES_LA_PLATA),
                'estado': random.choice(DemoDataGenerator.ESTADOS_ENTREGA),
                'contacto': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'telefono': f"221-{random.randint(1000000, 9999999)}",
                'observaciones': f"Entrega de {random.choice(['vidrios', 'herrajes', 'materiales varios'])}"
            }
            entregas.append(entrega)

        # Servicios
        servicios = []
        for i in range(10):
            fecha_programada = datetime.now() + timedelta(days=random.randint(0, 10))

            servicio = {
                'id': i + 1,
                'tipo': random.choice(['Instalación',
'Reparación',
                    'Mantenimiento',
                    'Medición']),
                'cliente': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}",
                'direccion': random.choice(DemoDataGenerator.DIRECCIONES_LA_PLATA),
                'fecha_programada': fecha_programada,
                'hora': f"{random.randint(8, 17)}:{random.choice(['00', '30'])}",
                'estado': random.choice(['Programado',
'En Proceso',
                    'Completado',
                    'Cancelado']),
                'tecnico': f"{random.choice(DemoDataGenerator.NOMBRES)} {random.choice(DemoDataGenerator.APELLIDOS)}"
            }
            servicios.append(servicio)

        return {'entregas': entregas, 'servicios': servicios}

    @staticmethod
    def generar_usuarios_demo() -> List[Dict[str, Any]]:
        """Genera datos demo para el módulo de usuarios."""
        usuarios = []
        roles = ['ADMIN', 'GERENTE', 'VENDEDOR', 'TECNICO', 'USUARIO']

        for i in range(8):
            nombre = random.choice(DemoDataGenerator.NOMBRES)
            apellido = random.choice(DemoDataGenerator.APELLIDOS)

            usuario = {
                'id': i + 1,
                'username': f"{nombre.lower()}.{apellido.lower()}",
                'nombre': nombre,
                'apellido': apellido,
                'email': f"{nombre.lower()}.{apellido.lower()}@rexus.com",
                'rol': random.choice(roles),
                'estado': 'ACTIVO' if random.random() > 0.1 else 'INACTIVO',
                'fecha_creacion': datetime.now() - timedelta(days=random.randint(30, 365)),
                'ultimo_acceso': datetime.now() - timedelta(days=random.randint(0, 7))
            }
            usuarios.append(usuario)

        return usuarios

    @staticmethod
    def generar_compras_demo() -> List[Dict[str, Any]]:
        """Genera datos demo para el módulo de compras."""
        compras = []
        proveedores = ['Vidrios del Sur', 'Herrajes Premium', 'Aluminios La Plata', 'Cristales Industriales']

        for i in range(15):
            fecha_pedido = datetime.now() - timedelta(days=random.randint(0, 45))
            fecha_entrega = fecha_pedido + timedelta(days=random.randint(7, 21))

            compra = {
                'id': i + 1,
                'numero_orden': f"OC-{fecha_pedido.year}-{5000 + i}",
                'proveedor': random.choice(proveedores),
                'fecha_pedido': fecha_pedido,
                'fecha_entrega_estimada': fecha_entrega,
                'estado': random.choice(['Pendiente',
'Confirmada',
                    'En Tránsito',
                    'Recibida',
                    'Cancelada']),
                'total': round(random.uniform(10000, 100000), 2),
                'descuento': round(random.uniform(0, 10), 2),
                'observaciones': f"Compra de {random.choice(['vidrios', 'herrajes', 'materiales', 'insumos'])} para stock",
                'usuario_creacion': random.choice(['admin', 'compras.manager', 'juan.garcia'])
            }
            compras.append(compra)

        return compras

    @staticmethod
    def obtener_todos_los_datos_demo() -> Dict[str, Any]:
        """Obtiene todos los datos demo para todos los módulos."""
        return {
            'inventario': DemoDataGenerator.generar_inventario_demo(),
            'obras': DemoDataGenerator.generar_obras_demo(),
            'pedidos': DemoDataGenerator.generar_pedidos_demo(),
            'logistica': DemoDataGenerator.generar_logistica_demo(),
            'usuarios': DemoDataGenerator.generar_usuarios_demo(),
            'compras': DemoDataGenerator.generar_compras_demo()
        }

    @staticmethod
    def es_modo_demo() -> bool:
        """Determina si la aplicación debe funcionar en modo demo."""
        # Se puede basar en variables de entorno o archivo de configuración
        import os
        return os.environ.get('REXUS_MODO_DEMO', 'false').lower() == 'true'
