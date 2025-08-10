#!/usr/bin/env python3
"""
Generador de Datos Demo para Rexus.app

Este script genera datos realistas para todos los módulos de la aplicación,
útil para testing, desarrollo y presentaciones.
"""

import sys
import os
import random
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict, Any

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables de entorno cargadas")
except ImportError:
    print("[WARNING] python-dotenv no instalado")


class GeneradorDatosDemo:
    """Generador de datos demo para todos los módulos."""
    
    def __init__(self):
        """Inicializa el generador con datos base."""
        self.obras_creadas = []
        self.productos_creados = []
        self.usuarios_creados = []
        self.proveedores = [
            "Vidrios del Sur SA", "Herrajes Premium SRL", "Aluminios Modernos SA",
            "Cristales Industriales SA", "Accesorios del Vidrio SRL", "Técnica Vidrios SA",
            "Sistemas de Aluminio SA", "Vidriería Central SA", "Herrajes Especiales SRL"
        ]
        self.clientes = [
            "Constructora Delta SA", "Inmobiliaria Norte SRL", "Edificios Modernos SA",
            "Reformas Integrales SA", "Arquitectura Avanzada SRL", "Construcciones Sur SA",
            "Desarrollos Urbanos SA", "Obras Civiles SRL", "Ingeniería Total SA"
        ]
    
    def generar_todos_los_datos(self):
        """Genera datos para todos los módulos."""
        print("[ROCKET] Iniciando generación de datos demo...")
        
        try:
            # Conectar a la base de datos
            from src.core.database import UsersDatabaseConnection
            db = UsersDatabaseConnection()
            db.connect()
            print("[OK] Conexión a BD establecida")
            
            # Generar datos por módulo
            self.generar_usuarios_demo(db)
            self.generar_obras_demo(db)
            self.generar_inventario_demo(db)
            self.generar_compras_demo(db)
            self.generar_pedidos_demo(db)
            self.generar_herrajes_demo(db)
            self.generar_vidrios_demo(db)
            self.generar_logistica_demo(db)
            
            print("\n🎉 Generación de datos demo completada exitosamente!")
            print(f"[CHART] Resumen:")
            print(f"   - {len(self.usuarios_creados)} usuarios creados")
            print(f"   - {len(self.obras_creadas)} obras creadas")
            print(f"   - {len(self.productos_creados)} productos de inventario")
            
        except Exception as e:
            print(f"[ERROR] Error generando datos demo: {e}")
            import traceback
            traceback.print_exc()
    
    def generar_usuarios_demo(self, db):
        """Genera usuarios demo."""
        print("\n👥 Generando usuarios demo...")
        
        usuarios_demo = [
            {
                "usuario": "supervisor", "password": "supervisor", "rol": "SUPERVISOR",
                "nombre": "Carlos", "apellido": "Supervisor", "email": "supervisor@rexus.app"
            },
            {
                "usuario": "operador1", "password": "operador", "rol": "OPERADOR", 
                "nombre": "María", "apellido": "González", "email": "maria@rexus.app"
            },
            {
                "usuario": "operador2", "password": "operador", "rol": "OPERADOR",
                "nombre": "Juan", "apellido": "Pérez", "email": "juan@rexus.app"
            },
            {
                "usuario": "contador", "password": "contador", "rol": "CONTABILIDAD",
                "nombre": "Ana", "apellido": "Martínez", "email": "ana@rexus.app"
            },
            {
                "usuario": "inventario", "password": "inventario", "rol": "INVENTARIO",
                "nombre": "Luis", "apellido": "Rodríguez", "email": "luis@rexus.app"
            }
        ]
        
        for usuario_data in usuarios_demo:
            try:
                # Verificar si el usuario ya existe
                existing = db.execute_query(
                    "SELECT id FROM usuarios WHERE usuario = ?", 
                    (usuario_data["usuario"],)
                )
                
                if not existing:
                    import hashlib
                    password_hash = hashlib.sha256(usuario_data["password"].encode()).hexdigest()
                    
                    db.execute_non_query("""
                        INSERT INTO usuarios (usuario, password_hash, rol, estado, nombre, apellido, email)
                        VALUES (?, ?, ?, 'Activo', ?, ?, ?)
                    """, (
                        usuario_data["usuario"], password_hash, usuario_data["rol"],
                        usuario_data["nombre"], usuario_data["apellido"], usuario_data["email"]
                    ))
                    
                    self.usuarios_creados.append(usuario_data["usuario"])
                    print(f"   - Creado usuario: {usuario_data['usuario']} ({usuario_data['rol']})")
                
            except Exception as e:
                print(f"   - Error creando usuario {usuario_data['usuario']}: {e}")
    
    def generar_obras_demo(self, db):
        """Genera obras demo."""
        print("\n🏗️ Generando obras demo...")
        
        tipos_obra = ["Residencial", "Comercial", "Industrial", "Institucional"]
        estados = ["PLANIFICACION", "EN_PROCESO", "PAUSADA", "COMPLETADA"]
        
        for i in range(1, 16):  # 15 obras
            try:
                codigo = f"OBR-{2024}-{i:03d}"
                fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 180))
                fecha_fin = fecha_inicio + timedelta(days=random.randint(60, 300))
                
                obra_data = {
                    "codigo": codigo,
                    "nombre": f"Proyecto {random.choice(['Residencial', 'Comercial', 'Industrial'])} {i}",
                    "cliente": random.choice(self.clientes),
                    "direccion": f"Calle {random.randint(1, 60)} N° {random.randint(100, 9999)}, La Plata",
                    "telefono": f"+54 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "email": f"proyecto{i}@cliente.com",
                    "tipo_obra": random.choice(tipos_obra),
                    "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
                    "fecha_fin": fecha_fin.strftime('%Y-%m-%d'),
                    "estado": random.choice(estados),
                    "presupuesto": round(random.uniform(50000, 500000), 2),
                    "observaciones": f"Obra generada automáticamente para demo - Proyecto {i}",
                    "usuario_creacion": "admin"
                }
                
                # Verificar si la obra ya existe
                existing = db.execute_query("SELECT id FROM obras WHERE codigo = ?", (codigo,))
                
                if not existing:
                    db.execute_non_query("""
                        INSERT INTO obras (codigo, nombre, cliente, direccion, telefono, email, 
                                         tipo_obra, fecha_inicio, fecha_fin, estado, presupuesto, 
                                         observaciones, usuario_creacion, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        obra_data["codigo"], obra_data["nombre"], obra_data["cliente"],
                        obra_data["direccion"], obra_data["telefono"], obra_data["email"],
                        obra_data["tipo_obra"], obra_data["fecha_inicio"], obra_data["fecha_fin"],
                        obra_data["estado"], obra_data["presupuesto"], obra_data["observaciones"],
                        obra_data["usuario_creacion"]
                    ))
                    
                    self.obras_creadas.append(codigo)
                    print(f"   - Creada obra: {codigo} - {obra_data['nombre']}")
                
            except Exception as e:
                print(f"   - Error creando obra {i}: {e}")
    
    def generar_inventario_demo(self, db):
        """Genera productos de inventario demo."""
        print("\n📦 Generando productos de inventario demo...")
        
        productos_demo = [
            {"tipo": "Marco", "acabado": "Anodizado", "descripcion": "Marco de ventana 120x80cm"},
            {"tipo": "Marco", "acabado": "Natural", "descripcion": "Marco de puerta 200x90cm"},
            {"tipo": "Perfil", "acabado": "Anodizado", "descripcion": "Perfil estructural 6m"},
            {"tipo": "Accesorio", "acabado": "Cromado", "descripcion": "Manija de puerta estándar"},
            {"tipo": "Vidrio", "acabado": "Transparente", "descripcion": "Vidrio templado 6mm"},
            {"tipo": "Sellador", "acabado": "Transparente", "descripcion": "Sellador de silicona"},
            {"tipo": "Herraje", "acabado": "Galvanizado", "descripcion": "Bisagra de puerta pesada"},
            {"tipo": "Marco", "acabado": "Lacado", "descripcion": "Marco ventana oscilobatiente"},
            {"tipo": "Perfil", "acabado": "Natural", "descripcion": "Perfil de unión angular"},
            {"tipo": "Accesorio", "acabado": "Negro", "descripcion": "Cierre multipunto"},
        ]
        
        for i, producto_base in enumerate(productos_demo, 1):
            try:
                codigo = f"INV-{producto_base['tipo'][:3].upper()}-{i:04d}"
                
                producto_data = {
                    "codigo": codigo,
                    "descripcion": producto_base["descripcion"],
                    "tipo": producto_base["tipo"],
                    "acabado": producto_base["acabado"],
                    "unidad": random.choice(["UNIDAD", "METRO", "M2", "KG"]),
                    "importe": round(random.uniform(10, 500), 2),
                    "stock_actual": random.randint(5, 100),
                    "stock_minimo": random.randint(1, 10),
                    "proveedor": random.choice(self.proveedores),
                    "ubicacion": f"Sector {random.choice(['A', 'B', 'C'])}-{random.randint(1, 20)}",
                    "estado": "Activo"
                }
                
                # Verificar si el producto ya existe
                existing = db.execute_query("SELECT id FROM inventario_perfiles WHERE codigo = ?", (codigo,))
                
                if not existing:
                    db.execute_non_query("""
                        INSERT INTO inventario_perfiles (codigo, descripcion, tipo, acabado, unidad, 
                                                       importe, stock_actual, stock_minimo, proveedor, 
                                                       ubicacion, estado, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        producto_data["codigo"], producto_data["descripcion"], producto_data["tipo"],
                        producto_data["acabado"], producto_data["unidad"], producto_data["importe"],
                        producto_data["stock_actual"], producto_data["stock_minimo"], 
                        producto_data["proveedor"], producto_data["ubicacion"], producto_data["estado"]
                    ))
                    
                    self.productos_creados.append(codigo)
                    print(f"   - Creado producto: {codigo} - {producto_data['descripcion']}")
                
            except Exception as e:
                print(f"   - Error creando producto {i}: {e}")
    
    def generar_compras_demo(self, db):
        """Genera órdenes de compra demo."""
        print("\n🛒 Generando órdenes de compra demo...")
        
        estados_compra = ["PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]
        
        for i in range(1, 11):  # 10 órdenes
            try:
                numero_orden = f"OC-2024-{i:04d}"
                fecha_pedido = datetime.now() - timedelta(days=random.randint(5, 60))
                fecha_entrega = fecha_pedido + timedelta(days=random.randint(7, 30))
                
                orden_data = {
                    "numero_orden": numero_orden,
                    "proveedor": random.choice(self.proveedores),
                    "fecha_pedido": fecha_pedido.strftime('%Y-%m-%d'),
                    "fecha_entrega_estimada": fecha_entrega.strftime('%Y-%m-%d'),
                    "estado": random.choice(estados_compra),
                    "subtotal": round(random.uniform(1000, 25000), 2),
                    "descuento": round(random.uniform(0, 500), 2),
                    "impuestos": round(random.uniform(200, 2500), 2),
                    "total": 0,  # Se calculará
                    "observaciones": f"Orden de compra demo #{i}",
                    "usuario_creacion": "admin"
                }
                
                orden_data["total"] = orden_data["subtotal"] - orden_data["descuento"] + orden_data["impuestos"]
                
                # Verificar si la orden ya existe
                existing = db.execute_query("SELECT id FROM compras WHERE numero_orden = ?", (numero_orden,))
                
                if not existing:
                    db.execute_non_query("""
                        INSERT INTO compras (numero_orden, proveedor, fecha_pedido, fecha_entrega_estimada,
                                           estado, subtotal, descuento, impuestos, total, observaciones,
                                           usuario_creacion, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        orden_data["numero_orden"], orden_data["proveedor"], orden_data["fecha_pedido"],
                        orden_data["fecha_entrega_estimada"], orden_data["estado"], orden_data["subtotal"],
                        orden_data["descuento"], orden_data["impuestos"], orden_data["total"],
                        orden_data["observaciones"], orden_data["usuario_creacion"]
                    ))
                    
                    print(f"   - Creada orden: {numero_orden} - {orden_data['proveedor']}")
                
            except Exception as e:
                print(f"   - Error creando orden {i}: {e}")
    
    def generar_pedidos_demo(self, db):
        """Genera pedidos demo."""
        print("\n📋 Generando pedidos demo...")
        # Implementar según la estructura de la tabla pedidos
        print("   - Módulo de pedidos: implementación pendiente")
    
    def generar_herrajes_demo(self, db):
        """Genera herrajes demo."""
        print("\n🔧 Generando herrajes demo...")
        # Implementar según la estructura de la tabla herrajes
        print("   - Módulo de herrajes: implementación pendiente")
    
    def generar_vidrios_demo(self, db):
        """Genera vidrios demo."""
        print("\n🪟 Generando vidrios demo...")
        # Implementar según la estructura de la tabla vidrios
        print("   - Módulo de vidrios: implementación pendiente")
    
    def generar_logistica_demo(self, db):
        """Genera datos de logística demo."""
        print("\n🚚 Generando datos de logística demo...")
        # Implementar según la estructura de la tabla logística
        print("   - Módulo de logística: implementación pendiente")


def main():
    """Función principal."""
    print("=" * 60)
    print("🎯 GENERADOR DE DATOS DEMO - REXUS.APP")
    print("=" * 60)
    
    generador = GeneradorDatosDemo()
    generador.generar_todos_los_datos()
    
    print("\n" + "=" * 60)
    print("[CHECK] Proceso completado. Los datos demo están listos para usar.")
    print("💡 Ahora puede probar todos los módulos con datos realistas.")
    print("=" * 60)


if __name__ == "__main__":
    main()