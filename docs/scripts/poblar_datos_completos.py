#!/usr/bin/env python3
"""
Script para poblar todas las tablas con datos de prueba completos
para poder seguir el flujo de una obra completa en Rexus.app
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import random
import hashlib

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.database import InventarioDatabaseConnection, UsersDatabaseConnection, AuditoriaDatabaseConnection


class DataPopulator:
    """Clase para poblar datos de prueba en todas las bases de datos"""
    
    def __init__(self):
        self.db_inventario = None
        self.db_users = None
        self.db_auditoria = None
        self.connect_to_databases()
        
    def connect_to_databases(self):
        """Conecta a las tres bases de datos"""
        try:
            self.db_inventario = InventarioDatabaseConnection()
            self.db_users = UsersDatabaseConnection()
            self.db_auditoria = AuditoriaDatabaseConnection()
            print("OK - Conexion a bases de datos establecida")
        except Exception as e:
            print(f"ERROR - Error conectando a BD: {e}")
            self.db_inventario = None
            self.db_users = None
            self.db_auditoria = None
    
    def create_tables_inventario(self):
        """Crea las tablas de la base de datos inventario"""
        if not self.db_inventario:
            return False
        
        try:
            # Obras
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='obras')
                CREATE TABLE obras (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(300) NOT NULL,
                    cliente VARCHAR(200) NOT NULL,
                    contacto_cliente VARCHAR(100),
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(400),
                    ciudad VARCHAR(100),
                    fecha_inicio DATE,
                    fecha_fin_estimada DATE,
                    fecha_fin_real DATE,
                    estado VARCHAR(50) DEFAULT 'Planificada',
                    presupuesto DECIMAL(15,2),
                    costo_real DECIMAL(15,2),
                    porcentaje_avance DECIMAL(5,2) DEFAULT 0,
                    observaciones TEXT,
                    supervisor VARCHAR(100),
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Inventario general
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='inventario')
                CREATE TABLE inventario (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(300) NOT NULL,
                    descripcion TEXT,
                    categoria VARCHAR(100),
                    subcategoria VARCHAR(100),
                    unidad VARCHAR(20),
                    precio_unitario DECIMAL(10,2),
                    stock_actual INT DEFAULT 0,
                    stock_minimo INT DEFAULT 0,
                    stock_maximo INT DEFAULT 0,
                    proveedor VARCHAR(200),
                    ubicacion VARCHAR(100),
                    fecha_vencimiento DATE,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Herrajes
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='herrajes')
                CREATE TABLE herrajes (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(300) NOT NULL,
                    tipo VARCHAR(100),
                    subtipo VARCHAR(100),
                    marca VARCHAR(100),
                    modelo VARCHAR(100),
                    precio DECIMAL(10,2),
                    stock INT DEFAULT 0,
                    stock_minimo INT DEFAULT 0,
                    proveedor VARCHAR(200),
                    ubicacion VARCHAR(100),
                    garantia_meses INT,
                    especificaciones TEXT,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Vidrios
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='vidrios')
                CREATE TABLE vidrios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    tipo VARCHAR(100) NOT NULL,
                    subtipo VARCHAR(100),
                    espesor DECIMAL(5,2),
                    ancho DECIMAL(8,2),
                    alto DECIMAL(8,2),
                    color VARCHAR(50),
                    precio_m2 DECIMAL(10,2),
                    stock_m2 DECIMAL(10,2) DEFAULT 0,
                    stock_minimo_m2 DECIMAL(10,2) DEFAULT 0,
                    proveedor VARCHAR(200),
                    ubicacion VARCHAR(100),
                    caracteristicas TEXT,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Empleados
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='empleados')
                CREATE TABLE empleados (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    dni VARCHAR(20) UNIQUE,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(300),
                    ciudad VARCHAR(100),
                    cargo VARCHAR(100),
                    departamento VARCHAR(100),
                    salario DECIMAL(10,2),
                    fecha_ingreso DATE,
                    fecha_salida DATE,
                    estado VARCHAR(20) DEFAULT 'Activo',
                    supervisor VARCHAR(100),
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Equipos
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='equipos')
                CREATE TABLE equipos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(300) NOT NULL,
                    tipo VARCHAR(100),
                    categoria VARCHAR(100),
                    marca VARCHAR(100),
                    modelo VARCHAR(100),
                    numero_serie VARCHAR(100),
                    fecha_compra DATE,
                    valor_compra DECIMAL(12,2),
                    valor_actual DECIMAL(12,2),
                    estado VARCHAR(50) DEFAULT 'Operativo',
                    ubicacion VARCHAR(100),
                    responsable VARCHAR(100),
                    proveedor VARCHAR(200),
                    garantia_hasta DATE,
                    fecha_ultimo_mantenimiento DATE,
                    proximo_mantenimiento DATE,
                    observaciones TEXT,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Pedidos
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='pedidos')
                CREATE TABLE pedidos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    numero_pedido VARCHAR(50) NOT NULL UNIQUE,
                    obra_id INT,
                    proveedor VARCHAR(200),
                    contacto_proveedor VARCHAR(100),
                    telefono_proveedor VARCHAR(20),
                    fecha_pedido DATE,
                    fecha_entrega_estimada DATE,
                    fecha_entrega_real DATE,
                    estado VARCHAR(50) DEFAULT 'Pendiente',
                    subtotal DECIMAL(12,2),
                    impuestos DECIMAL(12,2),
                    total DECIMAL(12,2),
                    descuento DECIMAL(12,2) DEFAULT 0,
                    forma_pago VARCHAR(50),
                    condiciones TEXT,
                    observaciones TEXT,
                    usuario_solicita VARCHAR(50),
                    aprobado_por VARCHAR(50),
                    fecha_aprobacion DATETIME,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (obra_id) REFERENCES obras(id)
                )
            """)
            
            # Detalle de pedidos
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='detalle_pedidos')
                CREATE TABLE detalle_pedidos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    pedido_id INT NOT NULL,
                    producto_codigo VARCHAR(50),
                    producto_nombre VARCHAR(300),
                    cantidad DECIMAL(10,2),
                    precio_unitario DECIMAL(10,2),
                    subtotal DECIMAL(12,2),
                    entregado BIT DEFAULT 0,
                    fecha_entrega DATE,
                    observaciones TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Materiales por obra
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='materiales_obra')
                CREATE TABLE materiales_obra (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    obra_id INT NOT NULL,
                    material_id INT NOT NULL,
                    tipo_material VARCHAR(50) NOT NULL,
                    cantidad_requerida DECIMAL(10,2),
                    cantidad_asignada DECIMAL(10,2) DEFAULT 0,
                    cantidad_consumida DECIMAL(10,2) DEFAULT 0,
                    precio_unitario DECIMAL(10,2),
                    costo_total DECIMAL(12,2),
                    fecha_asignacion DATETIME DEFAULT GETDATE(),
                    fecha_consumo DATETIME,
                    observaciones TEXT,
                    FOREIGN KEY (obra_id) REFERENCES obras(id)
                )
            """)
            
            # Proveedores
            self.db_inventario.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='proveedores')
                CREATE TABLE proveedores (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    nombre VARCHAR(200) NOT NULL,
                    contacto VARCHAR(100),
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(300),
                    ciudad VARCHAR(100),
                    ruc VARCHAR(20),
                    categoria VARCHAR(100),
                    calificacion INT DEFAULT 5,
                    condiciones_pago VARCHAR(100),
                    dias_credito INT DEFAULT 0,
                    activo BIT DEFAULT 1,
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            print("OK - Tablas de inventario creadas/verificadas")
            return True
            
        except Exception as e:
            print(f"ERROR - Error creando tablas inventario: {e}")
            return False
    
    def create_tables_users(self):
        """Crea las tablas de la base de datos users"""
        if not self.db_users:
            return False
        
        try:
            # Usuarios
            self.db_users.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='usuarios')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    telefono VARCHAR(20),
                    rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
                    departamento VARCHAR(100),
                    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
                    ultimo_login DATETIME,
                    intentos_fallidos INT DEFAULT 0,
                    bloqueado BIT DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Permisos
            self.db_users.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='permisos')
                CREATE TABLE permisos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    modulo VARCHAR(50) NOT NULL,
                    permiso VARCHAR(50) NOT NULL,
                    concedido BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Sesiones
            self.db_users.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='sesiones')
                CREATE TABLE sesiones (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    token VARCHAR(255) NOT NULL,
                    fecha_inicio DATETIME DEFAULT GETDATE(),
                    fecha_expiracion DATETIME,
                    activa BIT DEFAULT 1,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            print("OK - Tablas de usuarios creadas/verificadas")
            return True
            
        except Exception as e:
            print(f"ERROR - Error creando tablas usuarios: {e}")
            return False
    
    def create_tables_auditoria(self):
        """Crea las tablas de la base de datos auditoria"""
        if not self.db_auditoria:
            return False
        
        try:
            # Auditoría general
            self.db_auditoria.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='auditoria')
                CREATE TABLE auditoria (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL,
                    accion VARCHAR(100) NOT NULL,
                    tabla_afectada VARCHAR(100),
                    registro_id INT,
                    valores_anteriores TEXT,
                    valores_nuevos TEXT,
                    fecha DATETIME DEFAULT GETDATE(),
                    ip_address VARCHAR(45),
                    detalles TEXT
                )
            """)
            
            # Log de accesos
            self.db_auditoria.execute_non_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='log_accesos')
                CREATE TABLE log_accesos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL,
                    accion VARCHAR(50) NOT NULL,
                    exitoso BIT DEFAULT 1,
                    fecha DATETIME DEFAULT GETDATE(),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    mensaje TEXT
                )
            """)
            
            print("OK - Tablas de auditoría creadas/verificadas")
            return True
            
        except Exception as e:
            print(f"ERROR - Error creando tablas auditoría: {e}")
            return False
    
    def populate_users(self):
        """Pobla la base de datos de usuarios"""
        try:
            # Verificar si ya hay usuarios
            result = self.db_users.execute_query("SELECT COUNT(*) FROM usuarios")
            if result and result[0][0] > 0:
                print("INFO - Usuarios ya existen")
                return
            
            usuarios = [
                ('admin', 'admin123', 'Administrador', 'Sistema', 'admin@rexus.com', '555-0001', 'admin', 'Sistemas'),
                ('supervisor', 'super123', 'Juan Carlos', 'Supervisor', 'supervisor@rexus.com', '555-0002', 'supervisor', 'Obras'),
                ('arquitecto', 'arq123', 'María Elena', 'Arquitecta', 'arquitecto@rexus.com', '555-0003', 'usuario', 'Diseño'),
                ('ingeniero', 'ing123', 'Pedro José', 'Ingeniero', 'ingeniero@rexus.com', '555-0004', 'usuario', 'Ingeniería'),
                ('compras', 'comp123', 'Ana María', 'Compras', 'compras@rexus.com', '555-0005', 'usuario', 'Compras'),
                ('almacen', 'alm123', 'Carlos Eduardo', 'Almacenero', 'almacen@rexus.com', '555-0006', 'usuario', 'Almacén'),
                ('vendedor', 'vend123', 'Laura Patricia', 'Vendedora', 'vendedor@rexus.com', '555-0007', 'usuario', 'Ventas'),
                ('contador', 'cont123', 'Roberto Miguel', 'Contador', 'contador@rexus.com', '555-0008', 'usuario', 'Contabilidad'),
            ]
            
            for usuario, password, nombre, apellido, email, telefono, rol, departamento in usuarios:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                self.db_users.execute_non_query("""
                    INSERT INTO usuarios (usuario, password_hash, nombre, apellido, email, telefono, rol, departamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (usuario, password_hash, nombre, apellido, email, telefono, rol, departamento))
            
            print(f"OK - Creados {len(usuarios)} usuarios")
            
        except Exception as e:
            print(f"ERROR - Error poblando usuarios: {e}")
    
    def populate_proveedores(self):
        """Pobla la tabla de proveedores"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores")
            if result and result[0][0] > 0:
                print("INFO - Proveedores ya existen")
                return
            
            proveedores = [
                ('PROV001', 'Cementos Nacionales S.A.', 'Jorge Ramírez', '555-1001', 'ventas@cementos.com', 'Av. Industrial 123', 'Capital', '12345678901', 'Cemento', 5, 'Contado/30 días', 30),
                ('PROV002', 'Áridos del Sur Ltda.', 'María González', '555-1002', 'info@aridos.com', 'Ruta 5 Km 25', 'Sur', '12345678902', 'Agregados', 4, '15 días', 15),
                ('PROV003', 'Siderúrgica Nacional', 'Carlos Pérez', '555-1003', 'pedidos@sider.com', 'Zona Industrial B', 'Norte', '12345678903', 'Hierro', 5, '45 días', 45),
                ('PROV004', 'Vidrios del Centro', 'Ana Martínez', '555-1004', 'ventas@vidrios.com', 'Calle Central 456', 'Centro', '12345678904', 'Vidrios', 4, '30 días', 30),
                ('PROV005', 'Herrajes Premium', 'Luis Rodríguez', '555-1005', 'info@herrajes.com', 'Av. Principal 789', 'Este', '12345678905', 'Herrajes', 5, 'Contado', 0),
                ('PROV006', 'Pinturas Profesionales', 'Carmen Silva', '555-1006', 'pedidos@pinturas.com', 'Sector Comercial 321', 'Oeste', '12345678906', 'Pinturas', 4, '30 días', 30),
                ('PROV007', 'Tuberías Técnicas', 'Roberto García', '555-1007', 'ventas@tuberias.com', 'Polígono Industrial', 'Norte', '12345678907', 'Fontanería', 5, '60 días', 60),
                ('PROV008', 'Eléctricos Modernos', 'Patricia López', '555-1008', 'info@electricos.com', 'Calle Eléctrica 654', 'Sur', '12345678908', 'Eléctricos', 4, '45 días', 45),
                ('PROV009', 'Maderas del Bosque', 'Diego Fernández', '555-1009', 'ventas@maderas.com', 'Zona Forestal 987', 'Este', '12345678909', 'Madera', 5, '30 días', 30),
                ('PROV010', 'Bloques Constructivos', 'Elena Torres', '555-1010', 'pedidos@bloques.com', 'Sector Industrial C', 'Centro', '12345678910', 'Mampostería', 4, '15 días', 15),
            ]
            
            for datos in proveedores:
                self.db_inventario.execute_non_query("""
                    INSERT INTO proveedores (codigo, nombre, contacto, telefono, email, direccion, ciudad, ruc, categoria, calificacion, condiciones_pago, dias_credito)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos)
            
            print(f"OK - Creados {len(proveedores)} proveedores")
            
        except Exception as e:
            print(f"ERROR - Error poblando proveedores: {e}")
    
    def populate_obras(self):
        """Pobla la tabla de obras con datos realistas"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM obras")
            if result and result[0][0] > 0:
                print("INFO - Obras ya existen")
                return
            
            obras = [
                ('OBR001', 'Edificio Residencial "Torres del Parque"', 'Constructora ABC S.A.', 'Ing. Miguel Torres', '555-2001', 'torres@abc.com', 'Av. Principal 1250, Torre A', 'Capital', '2024-01-15', '2024-12-15', 'En Proceso', 2500000.00, 45.5, 'Edificio de 12 pisos, 48 apartamentos', 'supervisor'),
                ('OBR002', 'Casa Moderna "Villa Esperanza"', 'Familia Rodríguez García', 'Sr. Carlos Rodríguez', '555-2002', 'carlos.rodriguez@email.com', 'Urbanización Los Pinos, Lote 15', 'Norte', '2024-02-01', '2024-08-30', 'Activa', 450000.00, 65.0, 'Casa de 3 pisos, 4 habitaciones, piscina', 'arquitecto'),
                ('OBR003', 'Complejo Comercial "Plaza Central"', 'Inversiones Comerciales Norte', 'Dra. Ana Martínez', '555-2003', 'proyectos@icnorte.com', 'Av. Comercial 2500, Sector Centro', 'Centro', '2024-03-01', '2025-02-28', 'Planificada', 3800000.00, 15.0, 'Centro comercial 3 niveles, 150 locales', 'ingeniero'),
                ('OBR004', 'Oficinas Corporativas "Business Hub"', 'TechCorp Internacional S.A.', 'Lic. Roberto Silva', '555-2004', 'infraestructura@techcorp.com', 'Zona Empresarial, Edificio Tech', 'Este', '2024-01-10', '2024-10-15', 'Activa', 1200000.00, 75.0, 'Oficinas modernas, 8 pisos', 'supervisor'),
                ('OBR005', 'Renovación Escuela "San José"', 'Ministerio de Educación', 'Arq. Patricia González', '555-2005', 'obras@minedu.gov', 'Sector Educativo, Calle 123', 'Sur', '2024-02-15', '2024-07-30', 'Finalizada', 650000.00, 100.0, 'Renovación completa, 20 aulas', 'arquitecto'),
                ('OBR006', 'Condominio "Jardines del Valle"', 'Desarrollos Inmobiliarios SA', 'Ing. Luis Pérez', '555-2006', 'proyectos@desarrollos.com', 'Valle Verde, Fase 1', 'Oeste', '2024-04-01', '2025-03-31', 'Planificada', 5200000.00, 5.0, 'Condominio cerrado, 80 casas', 'ingeniero'),
                ('OBR007', 'Centro Médico "Salud Integral"', 'Fundación Salud para Todos', 'Dr. Mario Hernández', '555-2007', 'construccion@salud.org', 'Av. Médica 500', 'Norte', '2024-03-15', '2024-11-30', 'En Proceso', 980000.00, 35.0, 'Clínica de 4 pisos, 50 consultorios', 'supervisor'),
                ('OBR008', 'Warehouse "Logística Total"', 'Distribuidora Nacional Ltda.', 'Ing. Carmen López', '555-2008', 'logistica@distribuidora.com', 'Parque Industrial, Nave 5', 'Este', '2024-05-01', '2024-09-30', 'Activa', 750000.00, 55.0, 'Bodega industrial, 5000 m²', 'ingeniero'),
            ]
            
            for datos in obras:
                codigo, nombre, cliente, contacto, telefono, email, direccion, ciudad, fecha_inicio, fecha_fin, estado, presupuesto, avance, observaciones, supervisor = datos
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO obras (codigo, nombre, cliente, contacto_cliente, telefono, email, direccion, ciudad, fecha_inicio, fecha_fin_estimada, estado, presupuesto, porcentaje_avance, observaciones, supervisor)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, cliente, contacto, telefono, email, direccion, ciudad, fecha_inicio, fecha_fin, estado, presupuesto, avance, observaciones, supervisor))
            
            print(f"OK - Creadas {len(obras)} obras")
            
        except Exception as e:
            print(f"ERROR - Error poblando obras: {e}")
    
    def populate_inventario(self):
        """Pobla la tabla de inventario con materiales completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM inventario")
            if result and result[0][0] > 0:
                print("INFO - Inventario ya existe")
                return
            
            inventario = [
                # Cemento y agregados
                ('MAT001', 'Cemento Portland Tipo I', 'Cemento gris para uso general en construcción', 'Cemento', 'Tipo I', 'Bolsa 50kg', 32.50, 200, 30, 300, 'Cementos Nacionales S.A.', 'Almacén A-1'),
                ('MAT002', 'Cemento Portland Tipo II', 'Cemento con moderada resistencia a sulfatos', 'Cemento', 'Tipo II', 'Bolsa 50kg', 34.00, 150, 25, 200, 'Cementos Nacionales S.A.', 'Almacén A-1'),
                ('MAT003', 'Arena Fina Lavada', 'Arena fina para acabados y morteros', 'Agregados', 'Arena', 'Metro cúbico', 48.00, 50, 10, 80, 'Áridos del Sur Ltda.', 'Patio B-1'),
                ('MAT004', 'Arena Gruesa', 'Arena para concreto y mezclas estructurales', 'Agregados', 'Arena', 'Metro cúbico', 45.00, 60, 15, 100, 'Áridos del Sur Ltda.', 'Patio B-1'),
                ('MAT005', 'Grava 3/4"', 'Grava triturada para concreto', 'Agregados', 'Grava', 'Metro cúbico', 52.00, 40, 10, 70, 'Áridos del Sur Ltda.', 'Patio B-2'),
                ('MAT006', 'Piedra Chancada 1/2"', 'Piedra chancada para concreto fino', 'Agregados', 'Piedra', 'Metro cúbico', 55.00, 35, 8, 60, 'Áridos del Sur Ltda.', 'Patio B-2'),
                
                # Hierro y acero
                ('MAT007', 'Hierro Corrugado 8mm', 'Varilla de hierro corrugado Grado 60', 'Hierro', '8mm', 'Varilla 12m', 25.80, 500, 50, 600, 'Siderúrgica Nacional', 'Almacén C-1'),
                ('MAT008', 'Hierro Corrugado 10mm', 'Varilla de hierro corrugado Grado 60', 'Hierro', '10mm', 'Varilla 12m', 28.50, 400, 40, 500, 'Siderúrgica Nacional', 'Almacén C-1'),
                ('MAT009', 'Hierro Corrugado 12mm', 'Varilla de hierro corrugado Grado 60', 'Hierro', '12mm', 'Varilla 12m', 38.75, 350, 35, 450, 'Siderúrgica Nacional', 'Almacén C-1'),
                ('MAT010', 'Hierro Corrugado 16mm', 'Varilla de hierro corrugado Grado 60', 'Hierro', '16mm', 'Varilla 12m', 65.00, 200, 25, 300, 'Siderúrgica Nacional', 'Almacén C-1'),
                ('MAT011', 'Alambre Negro #16', 'Alambre negro para amarres', 'Hierro', 'Alambre', 'Rollo 100kg', 185.00, 50, 10, 80, 'Siderúrgica Nacional', 'Almacén C-2'),
                ('MAT012', 'Malla Electrosoldada 6x6', 'Malla electrosoldada para losas', 'Hierro', 'Malla', 'Rollo 2x50m', 450.00, 30, 5, 50, 'Siderúrgica Nacional', 'Almacén C-2'),
                
                # Mampostería
                ('MAT013', 'Bloque de Hormigón 15cm', 'Bloque hueco 15x20x40cm', 'Mampostería', 'Bloque', 'Unidad', 3.80, 2000, 200, 3000, 'Bloques Constructivos', 'Patio A-1'),
                ('MAT014', 'Bloque de Hormigón 20cm', 'Bloque hueco 20x20x40cm', 'Mampostería', 'Bloque', 'Unidad', 4.50, 1800, 180, 2500, 'Bloques Constructivos', 'Patio A-1'),
                ('MAT015', 'Ladrillo Común 6 huecos', 'Ladrillo cerámico común', 'Mampostería', 'Ladrillo', 'Unidad', 1.20, 5000, 500, 8000, 'Bloques Constructivos', 'Patio A-2'),
                ('MAT016', 'Ladrillo Visto', 'Ladrillo cerámico para vista', 'Mampostería', 'Ladrillo', 'Unidad', 2.50, 1000, 100, 1500, 'Bloques Constructivos', 'Patio A-2'),
                
                # Pinturas
                ('MAT017', 'Pintura Latex Interior Premium', 'Pintura latex lavable para interiores', 'Pintura', 'Latex', 'Galón', 52.00, 100, 15, 150, 'Pinturas Profesionales', 'Almacén D-1'),
                ('MAT018', 'Pintura Latex Exterior', 'Pintura latex resistente a intemperie', 'Pintura', 'Latex', 'Galón', 58.00, 80, 12, 120, 'Pinturas Profesionales', 'Almacén D-1'),
                ('MAT019', 'Esmalte Sintético', 'Esmalte sintético para metal y madera', 'Pintura', 'Esmalte', 'Galón', 65.00, 60, 10, 100, 'Pinturas Profesionales', 'Almacén D-1'),
                ('MAT020', 'Primer Sellador', 'Primer sellador para paredes nuevas', 'Pintura', 'Primer', 'Galón', 45.00, 70, 12, 120, 'Pinturas Profesionales', 'Almacén D-1'),
                
                # Fontanería
                ('MAT021', 'Tubería PVC 4" Desagüe', 'Tubería PVC para desagües', 'Fontanería', 'PVC', 'Metro', 15.50, 200, 30, 300, 'Tuberías Técnicas', 'Almacén E-1'),
                ('MAT022', 'Tubería PVC 2" Desagüe', 'Tubería PVC para desagües', 'Fontanería', 'PVC', 'Metro', 8.75, 300, 40, 400, 'Tuberías Técnicas', 'Almacén E-1'),
                ('MAT023', 'Tubería PVC 1/2" Agua', 'Tubería PVC para agua potable', 'Fontanería', 'PVC', 'Metro', 3.20, 500, 50, 600, 'Tuberías Técnicas', 'Almacén E-1'),
                ('MAT024', 'Tubería PVC 3/4" Agua', 'Tubería PVC para agua potable', 'Fontanería', 'PVC', 'Metro', 4.80, 400, 40, 500, 'Tuberías Técnicas', 'Almacén E-1'),
                
                # Eléctrico
                ('MAT025', 'Cable THW 12 AWG', 'Cable eléctrico para 20A', 'Eléctrico', 'Cable', 'Metro', 3.20, 1000, 100, 1500, 'Eléctricos Modernos', 'Almacén F-1'),
                ('MAT026', 'Cable THW 14 AWG', 'Cable eléctrico para 15A', 'Eléctrico', 'Cable', 'Metro', 2.50, 1200, 120, 1800, 'Eléctricos Modernos', 'Almacén F-1'),
                ('MAT027', 'Conduit PVC 3/4"', 'Conduit PVC para instalaciones eléctricas', 'Eléctrico', 'Conduit', 'Metro', 2.80, 300, 30, 400, 'Eléctricos Modernos', 'Almacén F-1'),
                ('MAT028', 'Caja Octogonal PVC', 'Caja octogonal para luminarias', 'Eléctrico', 'Caja', 'Unidad', 1.50, 500, 50, 800, 'Eléctricos Modernos', 'Almacén F-2'),
                
                # Madera
                ('MAT029', 'Madera Pino 2x4"', 'Madera de pino para estructura', 'Madera', 'Pino', 'Tabla 3m', 18.50, 200, 30, 300, 'Maderas del Bosque', 'Almacén G-1'),
                ('MAT030', 'Madera Pino 2x6"', 'Madera de pino para estructura', 'Madera', 'Pino', 'Tabla 3m', 26.00, 150, 25, 250, 'Maderas del Bosque', 'Almacén G-1'),
                ('MAT031', 'Madera Pino 2x8"', 'Madera de pino para vigas', 'Madera', 'Pino', 'Tabla 3m', 38.50, 100, 20, 150, 'Maderas del Bosque', 'Almacén G-1'),
                ('MAT032', 'Triplay 15mm', 'Triplay de pino para encofrado', 'Madera', 'Triplay', 'Plancha 1.22x2.44m', 85.00, 80, 15, 120, 'Maderas del Bosque', 'Almacén G-2'),
            ]
            
            for datos in inventario:
                self.db_inventario.execute_non_query("""
                    INSERT INTO inventario (codigo, nombre, descripcion, categoria, subcategoria, unidad, precio_unitario, stock_actual, stock_minimo, stock_maximo, proveedor, ubicacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos)
            
            print(f"OK - Creados {len(inventario)} items de inventario")
            
        except Exception as e:
            print(f"ERROR - Error poblando inventario: {e}")
    
    def populate_herrajes(self):
        """Pobla la tabla de herrajes con datos completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes")
            if result and result[0][0] > 0:
                print("INFO - Herrajes ya existen")
                return
            
            herrajes = [
                # Bisagras
                ('HER001', 'Bisagra Puerta 4" Acero', 'Bisagras', 'Estándar', 'Nacional', 'B-4A', 12.50, 150, 20, 12, 'Herrajes Premium', 'Almacén H-1', 'Acero inoxidable, carga 80kg'),
                ('HER002', 'Bisagra Puerta 5" Bronce', 'Bisagras', 'Premium', 'Importada', 'B-5B', 18.75, 100, 15, 24, 'Herrajes Premium', 'Almacén H-1', 'Bronce, carga 100kg'),
                ('HER003', 'Bisagra Vaivén 6"', 'Bisagras', 'Vaivén', 'Comercial', 'BV-6', 35.00, 50, 10, 12, 'Herrajes Premium', 'Almacén H-1', 'Para puertas comerciales'),
                
                # Cerraduras
                ('HER004', 'Cerradura Seguridad Exterior', 'Cerraduras', 'Seguridad', 'Yale', 'YS-300', 145.00, 80, 10, 36, 'Herrajes Premium', 'Almacén H-2', 'Con 3 llaves, cilindro europeo'),
                ('HER005', 'Cerradura Interior Paso', 'Cerraduras', 'Interior', 'Yale', 'YI-200', 95.00, 120, 15, 24, 'Herrajes Premium', 'Almacén H-2', 'Con 2 llaves, para interiores'),
                ('HER006', 'Cerradura Baño/Alcoba', 'Cerraduras', 'Privacidad', 'Yale', 'YP-150', 75.00, 100, 12, 12, 'Herrajes Premium', 'Almacén H-2', 'Con seguro interior'),
                ('HER007', 'Cerradura Multipunto', 'Cerraduras', 'Alta Seguridad', 'Importada', 'MS-500', 285.00, 30, 5, 12, 'Herrajes Premium', 'Almacén H-2', '5 puntos de anclaje'),
                
                # Manijas
                ('HER008', 'Manija Puerta Dorada', 'Manijas', 'Decorativa', 'Premium', 'MD-100', 42.00, 80, 10, 12, 'Herrajes Premium', 'Almacén H-3', 'Acabado dorado, ergonómica'),
                ('HER009', 'Manija Puerta Plateada', 'Manijas', 'Estándar', 'Nacional', 'MP-80', 35.00, 100, 12, 12, 'Herrajes Premium', 'Almacén H-3', 'Acabado cromado'),
                ('HER010', 'Manija Ventana Giratoria', 'Manijas', 'Ventana', 'Aluminio', 'MV-50', 25.00, 150, 20, 12, 'Herrajes Premium', 'Almacén H-3', 'Para ventanas batientes'),
                
                # Aldabas y seguros
                ('HER011', 'Aldaba Portón Grande', 'Aldabas', 'Portón', 'Industrial', 'AG-200', 65.00, 40, 8, 12, 'Herrajes Premium', 'Almacén H-4', 'Para portones pesados'),
                ('HER012', 'Aldaba Puerta Mediana', 'Aldabas', 'Puerta', 'Estándar', 'AM-100', 35.00, 60, 10, 12, 'Herrajes Premium', 'Almacén H-4', 'Uso general'),
                ('HER013', 'Pasador Puerta 8"', 'Pasadores', 'Puerta', 'Acero', 'PP-8', 22.00, 80, 12, 12, 'Herrajes Premium', 'Almacén H-4', 'Acero galvanizado'),
                
                # Candados
                ('HER014', 'Candado Seguridad 60mm', 'Candados', 'Seguridad', 'Master', 'CS-60', 35.00, 100, 15, 12, 'Herrajes Premium', 'Almacén H-5', 'Arco templado, 3 llaves'),
                ('HER015', 'Candado Marino 50mm', 'Candados', 'Marino', 'Importado', 'CM-50', 48.00, 50, 8, 12, 'Herrajes Premium', 'Almacén H-5', 'Resistente a corrosión'),
                ('HER016', 'Candado Combinación', 'Candados', 'Combinación', 'Master', 'CC-40', 28.00, 75, 10, 12, 'Herrajes Premium', 'Almacén H-5', '4 dígitos'),
                
                # Rieles y rodamientos
                ('HER017', 'Riel Corredizo 2m', 'Rieles', 'Corredizo', 'Nacional', 'RC-2000', 85.00, 30, 5, 12, 'Herrajes Premium', 'Almacén H-6', 'Incluye rodamientos'),
                ('HER018', 'Riel Corredizo 3m', 'Rieles', 'Corredizo', 'Nacional', 'RC-3000', 120.00, 25, 4, 12, 'Herrajes Premium', 'Almacén H-6', 'Para puertas pesadas'),
                ('HER019', 'Rodamiento Puerta', 'Rodamientos', 'Puerta', 'Industrial', 'RP-50', 15.00, 100, 15, 12, 'Herrajes Premium', 'Almacén H-6', 'Rodamiento de bolas'),
                
                # Tornillería
                ('HER020', 'Tornillo Madera 3" Caja', 'Tornillería', 'Madera', 'Galvanizado', 'TM-3', 12.50, 200, 25, 12, 'Herrajes Premium', 'Almacén H-7', 'Caja x100 unidades'),
                ('HER021', 'Tornillo Madera 2" Caja', 'Tornillería', 'Madera', 'Galvanizado', 'TM-2', 8.75, 250, 30, 12, 'Herrajes Premium', 'Almacén H-7', 'Caja x100 unidades'),
                ('HER022', 'Tornillo Autoperforante', 'Tornillería', 'Metal', 'Acero', 'TA-1', 15.00, 180, 20, 12, 'Herrajes Premium', 'Almacén H-7', 'Para metal, caja x100'),
                
                # Picaportes
                ('HER023', 'Picaporte Bronce Decorativo', 'Picaportes', 'Decorativo', 'Bronce', 'PB-100', 28.50, 60, 10, 12, 'Herrajes Premium', 'Almacén H-8', 'Acabado bronce antiguo'),
                ('HER024', 'Picaporte Cromo Simple', 'Picaportes', 'Estándar', 'Cromado', 'PC-50', 18.00, 80, 12, 12, 'Herrajes Premium', 'Almacén H-8', 'Acabado cromado'),
            ]
            
            for datos in herrajes:
                self.db_inventario.execute_non_query("""
                    INSERT INTO herrajes (codigo, nombre, tipo, subtipo, marca, modelo, precio, stock, stock_minimo, garantia_meses, proveedor, ubicacion, especificaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos)
            
            print(f"OK - Creados {len(herrajes)} herrajes")
            
        except Exception as e:
            print(f"ERROR - Error poblando herrajes: {e}")
    
    def populate_vidrios(self):
        """Pobla la tabla de vidrios con datos completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM vidrios")
            if result and result[0][0] > 0:
                print("INFO - Vidrios ya existen")
                return
            
            vidrios = [
                # Vidrios templados
                ('VID001', 'Vidrio Templado', 'Seguridad', 6.0, 2.20, 3.20, 'Transparente', 95.00, 150.0, 25.0, 'Vidrios del Centro', 'Almacén V-1', 'Vidrio de seguridad templado'),
                ('VID002', 'Vidrio Templado', 'Seguridad', 8.0, 2.20, 3.20, 'Transparente', 110.00, 120.0, 20.0, 'Vidrios del Centro', 'Almacén V-1', 'Extra resistente'),
                ('VID003', 'Vidrio Templado', 'Seguridad', 10.0, 2.20, 3.20, 'Transparente', 125.00, 100.0, 15.0, 'Vidrios del Centro', 'Almacén V-1', 'Para estructuras'),
                
                # Vidrios laminados
                ('VID004', 'Vidrio Laminado', 'Seguridad', 6.38, 2.20, 3.20, 'Transparente', 115.00, 80.0, 15.0, 'Vidrios del Centro', 'Almacén V-2', 'Laminado con PVB'),
                ('VID005', 'Vidrio Laminado', 'Seguridad', 8.76, 2.20, 3.20, 'Transparente', 135.00, 60.0, 12.0, 'Vidrios del Centro', 'Almacén V-2', 'Alta seguridad'),
                ('VID006', 'Vidrio Laminado', 'Acústico', 10.76, 2.20, 3.20, 'Transparente', 155.00, 40.0, 8.0, 'Vidrios del Centro', 'Almacén V-2', 'Aislamiento acústico'),
                
                # Vidrios comunes
                ('VID007', 'Vidrio Común', 'Estándar', 4.0, 2.20, 3.20, 'Transparente', 42.00, 200.0, 30.0, 'Vidrios del Centro', 'Almacén V-3', 'Uso general'),
                ('VID008', 'Vidrio Común', 'Estándar', 5.0, 2.20, 3.20, 'Transparente', 48.00, 180.0, 25.0, 'Vidrios del Centro', 'Almacén V-3', 'Uso general'),
                ('VID009', 'Vidrio Común', 'Estándar', 6.0, 2.20, 3.20, 'Transparente', 55.00, 160.0, 20.0, 'Vidrios del Centro', 'Almacén V-3', 'Uso general'),
                
                # Vidrios esmerilados
                ('VID010', 'Vidrio Esmerilado', 'Privacidad', 6.0, 2.20, 3.20, 'Esmerilado', 75.00, 80.0, 15.0, 'Vidrios del Centro', 'Almacén V-4', 'Para privacidad'),
                ('VID011', 'Vidrio Esmerilado', 'Privacidad', 8.0, 2.20, 3.20, 'Esmerilado', 85.00, 60.0, 12.0, 'Vidrios del Centro', 'Almacén V-4', 'Baños y oficinas'),
                
                # Vidrios tintados
                ('VID012', 'Vidrio Tintado', 'Control Solar', 6.0, 2.20, 3.20, 'Bronce', 88.00, 70.0, 12.0, 'Vidrios del Centro', 'Almacén V-5', 'Reduce calor solar'),
                ('VID013', 'Vidrio Tintado', 'Control Solar', 6.0, 2.20, 3.20, 'Gris', 88.00, 70.0, 12.0, 'Vidrios del Centro', 'Almacén V-5', 'Reduce calor solar'),
                ('VID014', 'Vidrio Tintado', 'Control Solar', 6.0, 2.20, 3.20, 'Azul', 92.00, 50.0, 10.0, 'Vidrios del Centro', 'Almacén V-5', 'Estético y funcional'),
                
                # Vidrios especiales
                ('VID015', 'Vidrio Espejo', 'Espejo', 4.0, 2.20, 3.20, 'Espejo', 65.00, 100.0, 15.0, 'Vidrios del Centro', 'Almacén V-6', 'Espejo de primera'),
                ('VID016', 'Vidrio Espejo', 'Espejo', 6.0, 2.20, 3.20, 'Espejo', 75.00, 80.0, 12.0, 'Vidrios del Centro', 'Almacén V-6', 'Espejo biselado'),
                
                # Vidrios dobles
                ('VID017', 'Vidrio Doble', 'Térmico', 20.0, 2.20, 3.20, 'Transparente', 165.00, 50.0, 8.0, 'Vidrios del Centro', 'Almacén V-7', 'DVH 4+12+4'),
                ('VID018', 'Vidrio Doble', 'Térmico', 24.0, 2.20, 3.20, 'Transparente', 185.00, 40.0, 6.0, 'Vidrios del Centro', 'Almacén V-7', 'DVH 6+12+6'),
                
                # Vidrios decorativos
                ('VID019', 'Vitral Decorativo', 'Decorativo', 6.0, 1.50, 2.00, 'Multicolor', 220.00, 25.0, 5.0, 'Vidrios del Centro', 'Almacén V-8', 'Hecho a mano'),
                ('VID020', 'Vidrio Catedral', 'Decorativo', 4.0, 2.20, 3.20, 'Varios', 95.00, 30.0, 6.0, 'Vidrios del Centro', 'Almacén V-8', 'Textura decorativa'),
            ]
            
            for datos in vidrios:
                self.db_inventario.execute_non_query("""
                    INSERT INTO vidrios (codigo, tipo, subtipo, espesor, ancho, alto, color, precio_m2, stock_m2, stock_minimo_m2, proveedor, ubicacion, caracteristicas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos)
            
            print(f"OK - Creados {len(vidrios)} vidrios")
            
        except Exception as e:
            print(f"ERROR - Error poblando vidrios: {e}")
    
    def populate_empleados(self):
        """Pobla la tabla de empleados con datos completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados")
            if result and result[0][0] > 0:
                print("INFO - Empleados ya existen")
                return
            
            empleados = [
                ('EMP001', 'Carlos Alberto', 'Rodríguez Silva', '12345678', '555-3001', 'carlos@rexus.com', 'Av. Central 123', 'Capital', 'Supervisor de Obra', 'Obras', 48000.00, 'Activo', 'supervisor'),
                ('EMP002', 'María Elena', 'González López', '87654321', '555-3002', 'maria@rexus.com', 'Calle Norte 456', 'Norte', 'Arquitecta Senior', 'Diseño', 62000.00, 'Activo', 'arquitecto'),
                ('EMP003', 'Juan Carlos', 'Pérez Martínez', '11223344', '555-3003', 'juan@rexus.com', 'Av. Sur 789', 'Sur', 'Maestro Albañil', 'Obras', 38000.00, 'Activo', 'supervisor'),
                ('EMP004', 'Ana Patricia', 'López García', '44332211', '555-3004', 'ana@rexus.com', 'Sector Este 321', 'Este', 'Ingeniera Civil', 'Ingeniería', 58000.00, 'Activo', 'ingeniero'),
                ('EMP005', 'Pedro Miguel', 'Martínez Torres', '55667788', '555-3005', 'pedro@rexus.com', 'Zona Oeste 654', 'Oeste', 'Operario Especializado', 'Obras', 32000.00, 'Activo', 'supervisor'),
                ('EMP006', 'Laura Cristina', 'Sánchez Ruiz', '99887766', '555-3006', 'laura@rexus.com', 'Av. Principal 987', 'Centro', 'Contadora', 'Administración', 45000.00, 'Activo', 'contador'),
                ('EMP007', 'Diego Fernando', 'Fernández Castro', '66778899', '555-3007', 'diego@rexus.com', 'Calle Industrial 147', 'Norte', 'Electricista', 'Instalaciones', 42000.00, 'Activo', 'supervisor'),
                ('EMP008', 'Carmen Rosa', 'Torres Vega', '33445566', '555-3008', 'carmen@rexus.com', 'Av. Comercial 258', 'Centro', 'Diseñadora', 'Diseño', 44000.00, 'Activo', 'arquitecto'),
                ('EMP009', 'Roberto Carlos', 'Silva Mendoza', '77889900', '555-3009', 'roberto@rexus.com', 'Sector Residencial 369', 'Sur', 'Soldador', 'Talleres', 36000.00, 'Activo', 'supervisor'),
                ('EMP010', 'Patricia Isabel', 'Morales Jiménez', '22334455', '555-3010', 'patricia@rexus.com', 'Calle Técnica 741', 'Este', 'Jefa de Compras', 'Compras', 52000.00, 'Activo', 'compras'),
                ('EMP011', 'Luis Eduardo', 'Ramírez Herrera', '88990011', '555-3011', 'luis@rexus.com', 'Av. Logística 852', 'Oeste', 'Almacenero', 'Almacén', 28000.00, 'Activo', 'almacen'),
                ('EMP012', 'Mónica Alejandra', 'Guerrero Peña', '44556677', '555-3012', 'monica@rexus.com', 'Sector Comercial 963', 'Norte', 'Vendedora', 'Ventas', 35000.00, 'Activo', 'vendedor'),
                ('EMP013', 'Jorge Antonio', 'Castillo Vargas', '66889911', '555-3013', 'jorge@rexus.com', 'Calle Operativa 159', 'Centro', 'Operador de Grúa', 'Equipos', 40000.00, 'Activo', 'supervisor'),
                ('EMP014', 'Silvia Beatriz', 'Ramos Delgado', '11335577', '555-3014', 'silvia@rexus.com', 'Av. Administrativa 357', 'Sur', 'Secretaria', 'Administración', 25000.00, 'Activo', 'admin'),
                ('EMP015', 'Fernando José', 'Ortiz Campos', '99112233', '555-3015', 'fernando@rexus.com', 'Sector Técnico 468', 'Este', 'Técnico en Refrigeración', 'Instalaciones', 38000.00, 'Activo', 'supervisor'),
            ]
            
            for datos in empleados:
                codigo, nombre, apellido, dni, telefono, email, direccion, ciudad, cargo, departamento, salario, estado, supervisor = datos
                fecha_ingreso = datetime.now() - timedelta(days=random.randint(30, 1095))
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO empleados (codigo, nombre, apellido, dni, telefono, email, direccion, ciudad, cargo, departamento, salario, fecha_ingreso, estado, supervisor)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, apellido, dni, telefono, email, direccion, ciudad, cargo, departamento, salario, fecha_ingreso, estado, supervisor))
            
            print(f"OK - Creados {len(empleados)} empleados")
            
        except Exception as e:
            print(f"ERROR - Error poblando empleados: {e}")
    
    def populate_equipos(self):
        """Pobla la tabla de equipos con datos completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM equipos")
            if result and result[0][0] > 0:
                print("INFO - Equipos ya existen")
                return
            
            equipos = [
                ('EQU001', 'Mezcladora de Concreto Móvil', 'Mezcladora', 'Construcción', 'Caterpillar', 'CM-500', 'CAT500M2024', 28000.00, 26000.00, 'Operativo', 'Obra Torres del Parque', 'Carlos Alberto Rodríguez Silva', 'Maquinarias SA'),
                ('EQU002', 'Grúa Torre 50 Toneladas', 'Grúa', 'Izaje', 'Liebherr', 'LTM-1050', 'LH1050T2023', 220000.00, 210000.00, 'Operativo', 'Obra Plaza Central', 'Jorge Antonio Castillo Vargas', 'Grúas Industriales'),
                ('EQU003', 'Excavadora Hidráulica', 'Excavadora', 'Movimiento Tierra', 'Caterpillar', '320D', 'CAT320D2022', 185000.00, 175000.00, 'Operativo', 'Obra Business Hub', 'Pedro Miguel Martínez Torres', 'Maquinarias SA'),
                ('EQU004', 'Soldadora Industrial TIG', 'Soldadora', 'Soldadura', 'Lincoln', 'Power Wave AC/DC', 'LN-PWAC2024', 12500.00, 12000.00, 'Operativo', 'Taller Principal', 'Roberto Carlos Silva Mendoza', 'Soldaduras Pro'),
                ('EQU005', 'Compresor de Aire Estacionario', 'Compresor', 'Aire Comprimido', 'Atlas Copco', 'GA-55', 'AC-GA55-2023', 18500.00, 17500.00, 'Operativo', 'Taller Principal', 'Diego Fernando Fernández Castro', 'Equipos Neumáticos'),
                ('EQU006', 'Camión Volquete 15 Toneladas', 'Transporte', 'Carga', 'Volvo', 'FH16-750', 'VLV-FH16-2023', 145000.00, 135000.00, 'Operativo', 'Base Logística', 'Juan Carlos Pérez Martínez', 'Volvo Trucks'),
                ('EQU007', 'Martillo Neumático Pesado', 'Herramienta', 'Demolición', 'Bosch', 'GSH-27VC', 'BSH-27VC-2024', 1450.00, 1350.00, 'Operativo', 'Almacén Herramientas', 'Luis Eduardo Ramírez Herrera', 'Herramientas Pro'),
                ('EQU008', 'Cortadora de Concreto', 'Cortadora', 'Corte', 'Husqvarna', 'K-970', 'HSQ-K970-2023', 4200.00, 3800.00, 'Mantenimiento', 'Taller Reparaciones', 'Fernando José Ortiz Campos', 'Máquinas Diamante'),
                ('EQU009', 'Andamio Móvil 8 Metros', 'Andamio', 'Acceso', 'Layher', 'Topic', 'LY-TOP8-2024', 8500.00, 8200.00, 'Operativo', 'Obra Villa Esperanza', 'Carlos Alberto Rodríguez Silva', 'Andamios Seguros'),
                ('EQU010', 'Vibrador de Concreto', 'Vibrador', 'Compactación', 'Wacker', 'M-3000', 'WK-M3000-2024', 2800.00, 2600.00, 'Operativo', 'Obra Torres del Parque', 'Pedro Miguel Martínez Torres', 'Vibradores SA'),
                ('EQU011', 'Generador Eléctrico 150KVA', 'Generador', 'Energía', 'Caterpillar', 'C6.6-150', 'CAT-C6-2023', 35000.00, 33000.00, 'Operativo', 'Obra Centro Médico', 'Diego Fernando Fernández Castro', 'Generadores Pro'),
                ('EQU012', 'Bomba de Agua Centrífuga', 'Bomba', 'Agua', 'Grundfos', 'CR-64', 'GRF-CR64-2024', 5500.00, 5200.00, 'Operativo', 'Obra Condominio Jardines', 'Fernando José Ortiz Campos', 'Bombas Industriales'),
                ('EQU013', 'Plataforma Elevadora 12m', 'Elevador', 'Acceso', 'JLG', 'E-400AJP', 'JLG-E400-2023', 65000.00, 62000.00, 'Operativo', 'Obra Business Hub', 'Jorge Antonio Castillo Vargas', 'Elevadores Aéreos'),
                ('EQU014', 'Taladro Industrial', 'Taladro', 'Perforación', 'Hilti', 'DD-350', 'HLT-DD350-2024', 3200.00, 3000.00, 'Operativo', 'Taller Principal', 'Roberto Carlos Silva Mendoza', 'Hilti Store'),
                ('EQU015', 'Minicargadora', 'Cargadora', 'Carga', 'Bobcat', 'S-650', 'BBC-S650-2022', 75000.00, 70000.00, 'Operativo', 'Obra Warehouse Logística', 'Pedro Miguel Martínez Torres', 'Maquinarias SA'),
            ]
            
            for datos in equipos:
                codigo, nombre, tipo, categoria, marca, modelo, numero_serie, valor_compra, valor_actual, estado, ubicacion, responsable, proveedor = datos
                fecha_compra = datetime.now() - timedelta(days=random.randint(30, 730))
                garantia_hasta = fecha_compra + timedelta(days=365)
                ultimo_mantenimiento = datetime.now() - timedelta(days=random.randint(1, 90))
                proximo_mantenimiento = ultimo_mantenimiento + timedelta(days=random.randint(90, 180))
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO equipos (codigo, nombre, tipo, categoria, marca, modelo, numero_serie, fecha_compra, valor_compra, valor_actual, estado, ubicacion, responsable, proveedor, garantia_hasta, fecha_ultimo_mantenimiento, proximo_mantenimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, tipo, categoria, marca, modelo, numero_serie, fecha_compra, valor_compra, valor_actual, estado, ubicacion, responsable, proveedor, garantia_hasta, ultimo_mantenimiento, proximo_mantenimiento))
            
            print(f"OK - Creados {len(equipos)} equipos")
            
        except Exception as e:
            print(f"ERROR - Error poblando equipos: {e}")
    
    def populate_pedidos(self):
        """Pobla la tabla de pedidos con datos completos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM pedidos")
            if result and result[0][0] > 0:
                print("INFO - Pedidos ya existen")
                return
            
            # Obtener IDs de obras
            obra_ids = self.db_inventario.execute_query("SELECT id FROM obras")
            if not obra_ids:
                print("WARNING - No hay obras para crear pedidos")
                return
            
            obra_ids = [row[0] for row in obra_ids]
            
            pedidos = [
                ('PED001', 'Cementos Nacionales S.A.', 'Jorge Ramírez', '555-1001', 'Aprobado', 45000.00, 5400.00, 50400.00, 0.00, 'Transferencia', 'Materiales para cimentación'),
                ('PED002', 'Siderúrgica Nacional', 'Carlos Pérez', '555-1003', 'Entregado', 32000.00, 3840.00, 35840.00, 1600.00, 'Cheque', 'Hierro estructural'),
                ('PED003', 'Vidrios del Centro', 'Ana Martínez', '555-1004', 'En Proceso', 18500.00, 2220.00, 20720.00, 925.00, 'Crédito 30 días', 'Ventanas segundo piso'),
                ('PED004', 'Herrajes Premium', 'Luis Rodríguez', '555-1005', 'Pendiente', 12800.00, 1536.00, 14336.00, 0.00, 'Contado', 'Cerraduras y bisagras'),
                ('PED005', 'Pinturas Profesionales', 'Carmen Silva', '555-1006', 'Aprobado', 8900.00, 1068.00, 9968.00, 445.00, 'Crédito 30 días', 'Pintura acabados'),
                ('PED006', 'Tuberías Técnicas', 'Roberto García', '555-1007', 'En Proceso', 15600.00, 1872.00, 17472.00, 780.00, 'Crédito 60 días', 'Instalaciones sanitarias'),
                ('PED007', 'Eléctricos Modernos', 'Patricia López', '555-1008', 'Pendiente', 22400.00, 2688.00, 25088.00, 1120.00, 'Crédito 45 días', 'Instalación eléctrica'),
                ('PED008', 'Maderas del Bosque', 'Diego Fernández', '555-1009', 'Entregado', 28000.00, 3360.00, 31360.00, 1400.00, 'Transferencia', 'Estructura de techo'),
                ('PED009', 'Áridos del Sur Ltda.', 'María González', '555-1002', 'Aprobado', 35000.00, 4200.00, 39200.00, 1750.00, 'Cheque', 'Arena y grava'),
                ('PED010', 'Bloques Constructivos', 'Elena Torres', '555-1010', 'En Proceso', 16800.00, 2016.00, 18816.00, 840.00, 'Crédito 15 días', 'Bloques mampostería'),
            ]
            
            for i, datos in enumerate(pedidos):
                numero, proveedor, contacto, telefono, estado, subtotal, impuestos, total, descuento, forma_pago, condiciones = datos
                
                obra_id = obra_ids[i % len(obra_ids)]
                fecha_pedido = datetime.now() - timedelta(days=random.randint(1, 60))
                fecha_entrega_est = fecha_pedido + timedelta(days=random.randint(7, 30))
                
                if estado == 'Entregado':
                    fecha_entrega_real = fecha_entrega_est - timedelta(days=random.randint(0, 5))
                else:
                    fecha_entrega_real = None
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO pedidos (numero_pedido, obra_id, proveedor, contacto_proveedor, telefono_proveedor, fecha_pedido, fecha_entrega_estimada, fecha_entrega_real, estado, subtotal, impuestos, total, descuento, forma_pago, condiciones, usuario_solicita)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (numero, obra_id, proveedor, contacto, telefono, fecha_pedido, fecha_entrega_est, fecha_entrega_real, estado, subtotal, impuestos, total, descuento, forma_pago, condiciones, 'compras'))
            
            print(f"OK - Creados {len(pedidos)} pedidos")
            
        except Exception as e:
            print(f"ERROR - Error poblando pedidos: {e}")
    
    def populate_materiales_obra(self):
        """Asigna materiales a las obras para crear flujo completo"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM materiales_obra")
            if result and result[0][0] > 0:
                print("INFO - Materiales de obra ya existen")
                return
            
            # Obtener IDs necesarios
            obras = self.db_inventario.execute_query("SELECT id FROM obras LIMIT 5")
            inventario = self.db_inventario.execute_query("SELECT id FROM inventario")
            herrajes = self.db_inventario.execute_query("SELECT id FROM herrajes")
            vidrios = self.db_inventario.execute_query("SELECT id FROM vidrios")
            
            if not obras:
                print("WARNING - No hay obras para asignar materiales")
                return
            
            obras = [row[0] for row in obras]
            inventario_ids = [row[0] for row in inventario] if inventario else []
            herraje_ids = [row[0] for row in herrajes] if herrajes else []
            vidrio_ids = [row[0] for row in vidrios] if vidrios else []
            
            # Asignar materiales a cada obra
            for obra_id in obras:
                # Asignar materiales de inventario
                for _ in range(random.randint(8, 15)):
                    if inventario_ids:
                        material_id = random.choice(inventario_ids)
                        cantidad_req = random.randint(50, 500)
                        cantidad_asig = int(cantidad_req * random.uniform(0.7, 1.0))
                        cantidad_cons = int(cantidad_asig * random.uniform(0.3, 0.8))
                        precio = random.uniform(15, 65)
                        
                        self.db_inventario.execute_non_query("""
                            INSERT INTO materiales_obra (obra_id, material_id, tipo_material, cantidad_requerida, cantidad_asignada, cantidad_consumida, precio_unitario, costo_total)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (obra_id, material_id, 'inventario', cantidad_req, cantidad_asig, cantidad_cons, precio, cantidad_req * precio))
                
                # Asignar herrajes
                for _ in range(random.randint(5, 10)):
                    if herraje_ids:
                        material_id = random.choice(herraje_ids)
                        cantidad_req = random.randint(10, 50)
                        cantidad_asig = int(cantidad_req * random.uniform(0.8, 1.0))
                        cantidad_cons = int(cantidad_asig * random.uniform(0.4, 0.9))
                        precio = random.uniform(25, 150)
                        
                        self.db_inventario.execute_non_query("""
                            INSERT INTO materiales_obra (obra_id, material_id, tipo_material, cantidad_requerida, cantidad_asignada, cantidad_consumida, precio_unitario, costo_total)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (obra_id, material_id, 'herrajes', cantidad_req, cantidad_asig, cantidad_cons, precio, cantidad_req * precio))
                
                # Asignar vidrios
                for _ in range(random.randint(3, 8)):
                    if vidrio_ids:
                        material_id = random.choice(vidrio_ids)
                        cantidad_req = random.uniform(15, 100)
                        cantidad_asig = cantidad_req * random.uniform(0.8, 1.0)
                        cantidad_cons = cantidad_asig * random.uniform(0.5, 0.9)
                        precio = random.uniform(85, 220)
                        
                        self.db_inventario.execute_non_query("""
                            INSERT INTO materiales_obra (obra_id, material_id, tipo_material, cantidad_requerida, cantidad_asignada, cantidad_consumida, precio_unitario, costo_total)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (obra_id, material_id, 'vidrios', cantidad_req, cantidad_asig, cantidad_cons, precio, cantidad_req * precio))
            
            print("OK - Materiales asignados a obras")
            
        except Exception as e:
            print(f"ERROR - Error asignando materiales a obras: {e}")
    
    def populate_audit_logs(self):
        """Pobla logs de auditoría con datos de ejemplo"""
        try:
            # Crear algunos registros de auditoría
            acciones = [
                ('admin', 'LOGIN', 'usuarios', 1, '', '', '127.0.0.1', 'Inicio de sesión exitoso'),
                ('supervisor', 'INSERT', 'obras', 1, '', 'Nueva obra creada', '192.168.1.100', 'Creación de obra Torres del Parque'),
                ('compras', 'INSERT', 'pedidos', 1, '', 'Nuevo pedido creado', '192.168.1.101', 'Pedido PED001 creado'),
                ('almacen', 'UPDATE', 'inventario', 1, 'stock: 200', 'stock: 180', '192.168.1.102', 'Actualización de stock'),
                ('arquitecto', 'UPDATE', 'obras', 2, 'estado: Planificada', 'estado: Activa', '192.168.1.103', 'Cambio de estado de obra'),
            ]
            
            for accion in acciones:
                fecha = datetime.now() - timedelta(days=random.randint(1, 30))
                self.db_auditoria.execute_non_query("""
                    INSERT INTO auditoria (usuario, accion, tabla_afectada, registro_id, valores_anteriores, valores_nuevos, fecha, ip_address, detalles)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, accion[:6] + (fecha,) + accion[6:])
            
            # Crear logs de acceso
            usuarios = ['admin', 'supervisor', 'compras', 'almacen', 'arquitecto']
            for _ in range(50):
                usuario = random.choice(usuarios)
                fecha = datetime.now() - timedelta(days=random.randint(1, 30))
                exitoso = random.choice([True, True, True, False])  # 75% exitoso
                
                self.db_auditoria.execute_non_query("""
                    INSERT INTO log_accesos (usuario, accion, exitoso, fecha, ip_address, mensaje)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario, 'LOGIN', exitoso, fecha, f'192.168.1.{random.randint(100, 200)}', 'Intento de login' if exitoso else 'Login fallido'))
            
            print("OK - Logs de auditoría creados")
            
        except Exception as e:
            print(f"ERROR - Error creando logs de auditoría: {e}")
    
    def populate_all_databases(self):
        """Pobla todas las bases de datos con datos completos"""
        print("INICIANDO POBLACION DE DATOS COMPLETOS")
        print("=" * 80)
        
        try:
            # Crear tablas
            print("\nCREANDO TABLAS...")
            if not self.create_tables_inventario():
                return False
            if not self.create_tables_users():
                return False
            if not self.create_tables_auditoria():
                return False
            
            # Poblar datos base
            print("\nPOBLANDO DATOS BASE...")
            self.populate_users()
            self.populate_proveedores()
            
            # Poblar datos de inventario
            print("\nPOBLANDO INVENTARIO...")
            self.populate_inventario()
            self.populate_herrajes()
            self.populate_vidrios()
            
            # Poblar datos operativos
            print("\nPOBLANDO DATOS OPERATIVOS...")
            self.populate_obras()
            self.populate_empleados()
            self.populate_equipos()
            self.populate_pedidos()
            self.populate_materiales_obra()
            
            # Poblar auditoría
            print("\nPOBLANDO AUDITORIA...")
            self.populate_audit_logs()
            
            print("\n" + "=" * 80)
            print("POBLACION DE DATOS COMPLETADA")
            print("=" * 80)
            
            # Mostrar resumen
            self.show_summary()
            
            return True
            
        except Exception as e:
            print(f"Error poblando datos: {e}")
            return False
    
    def show_summary(self):
        """Muestra resumen de datos creados"""
        print("\nRESUMEN DE DATOS CREADOS:")
        print("-" * 50)
        
        # Base de datos users
        print("Base de datos USERS:")
        try:
            result = self.db_users.execute_query("SELECT COUNT(*) FROM usuarios")
            print(f"   - Usuarios: {result[0][0] if result else 0}")
        except:
            print("   - Usuarios: Error al consultar")
        
        # Base de datos inventario
        print("\nBase de datos INVENTARIO:")
        tables = {
            'obras': 'Obras',
            'inventario': 'Inventario General',
            'herrajes': 'Herrajes',
            'vidrios': 'Vidrios',
            'empleados': 'Empleados',
            'equipos': 'Equipos',
            'pedidos': 'Pedidos',
            'materiales_obra': 'Materiales por Obra',
            'proveedores': 'Proveedores'
        }
        
        for table, name in tables.items():
            try:
                result = self.db_inventario.execute_query(f"SELECT COUNT(*) FROM {table}")
                print(f"   - {name}: {result[0][0] if result else 0}")
            except:
                print(f"   - {name}: Error al consultar")
        
        # Base de datos auditoría
        print("\nBase de datos AUDITORIA:")
        try:
            result = self.db_auditoria.execute_query("SELECT COUNT(*) FROM auditoria")
            print(f"   - Registros de auditoria: {result[0][0] if result else 0}")
            result = self.db_auditoria.execute_query("SELECT COUNT(*) FROM log_accesos")
            print(f"   - Logs de acceso: {result[0][0] if result else 0}")
        except:
            print("   - Auditoria: Error al consultar")
    
    def cleanup(self):
        """Limpia recursos"""
        if self.db_inventario:
            self.db_inventario.disconnect()
        if self.db_users:
            self.db_users.disconnect()
        if self.db_auditoria:
            self.db_auditoria.disconnect()


def main():
    """Función principal"""
    print("SISTEMA DE POBLACION DE DATOS REXUS.APP")
    print("=" * 80)
    
    populator = DataPopulator()
    
    try:
        if not populator.db_inventario or not populator.db_users or not populator.db_auditoria:
            print("ERROR - Error: No se pudieron conectar a las bases de datos")
            return 1
        
        success = populator.populate_all_databases()
        
        if success:
            print("\nDATOS POBLADOS EXITOSAMENTE!")
            print("La aplicacion Rexus.app ahora tiene datos completos para:")
            print("- Flujo completo de obras")
            print("- Gestion de inventario, herrajes y vidrios")
            print("- Empleados y equipos")
            print("- Pedidos y proveedores")
            print("- Usuarios y auditoria")
            print("\nCredenciales de acceso:")
            print("- admin / admin123")
            print("- supervisor / super123")
            print("- compras / comp123")
            print("- almacen / alm123")
            return 0
        else:
            print("\nERROR - Error poblando datos")
            return 1
            
    except Exception as e:
        print(f"\nFATAL - Error fatal: {e}")
        return 1
    finally:
        populator.cleanup()


if __name__ == "__main__":
    sys.exit(main())