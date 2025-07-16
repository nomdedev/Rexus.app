#!/usr/bin/env python3
"""
Script para crear las tablas críticas faltantes del sistema
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def crear_tabla_usuarios(db):
    """Crea la tabla usuarios mejorada"""
    sql = """
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        nombre VARCHAR(100),
        apellido VARCHAR(100),
        rol VARCHAR(50) DEFAULT 'usuario',
        activo BIT DEFAULT 1,
        ultimo_login DATETIME,
        intentos_fallidos INT DEFAULT 0,
        bloqueado BIT DEFAULT 0,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_roles(db):
    """Crea la tabla roles"""
    sql = """
    CREATE TABLE roles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(50) UNIQUE NOT NULL,
        descripcion TEXT,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_permisos_usuario(db):
    """Crea la tabla permisos_usuario"""
    sql = """
    CREATE TABLE permisos_usuario (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        modulo VARCHAR(50) NOT NULL,
        permiso VARCHAR(50) NOT NULL,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_modulos(db):
    """Crea la tabla modulos"""
    sql = """
    CREATE TABLE modulos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(50) UNIQUE NOT NULL,
        descripcion TEXT,
        icono VARCHAR(100),
        activo BIT DEFAULT 1,
        orden INT DEFAULT 0,
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_pedidos_detalle(db):
    """Crea la tabla pedidos_detalle"""
    sql = """
    CREATE TABLE pedidos_detalle (
        id INT IDENTITY(1,1) PRIMARY KEY,
        pedido_id INT NOT NULL,
        producto_codigo VARCHAR(50),
        descripcion VARCHAR(255) NOT NULL,
        cantidad DECIMAL(10,2) NOT NULL,
        precio_unitario DECIMAL(10,2) NOT NULL,
        subtotal DECIMAL(10,2) NOT NULL,
        descuento DECIMAL(10,2) DEFAULT 0,
        impuesto DECIMAL(10,2) DEFAULT 0,
        total DECIMAL(10,2) NOT NULL,
        estado VARCHAR(50) DEFAULT 'PENDIENTE',
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_pedidos_historial(db):
    """Crea la tabla pedidos_historial"""
    sql = """
    CREATE TABLE pedidos_historial (
        id INT IDENTITY(1,1) PRIMARY KEY,
        pedido_id INT NOT NULL,
        estado_anterior VARCHAR(50),
        estado_nuevo VARCHAR(50),
        fecha_cambio DATETIME DEFAULT GETDATE(),
        usuario_id INT,
        observaciones TEXT,
        ip_address VARCHAR(45)
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_herrajes(db):
    """Crea la tabla herrajes"""
    sql = """
    CREATE TABLE herrajes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT,
        categoria VARCHAR(50),
        proveedor VARCHAR(100),
        precio_unitario DECIMAL(10,2),
        stock_actual INT DEFAULT 0,
        stock_minimo INT DEFAULT 0,
        unidad_medida VARCHAR(20) DEFAULT 'UND',
        especificaciones TEXT,
        imagen_url VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_vidrios(db):
    """Crea la tabla vidrios"""
    sql = """
    CREATE TABLE vidrios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        tipo VARCHAR(50) NOT NULL,
        espesor DECIMAL(4,2) NOT NULL,
        color VARCHAR(50),
        precio_m2 DECIMAL(10,2),
        proveedor VARCHAR(100),
        especificaciones TEXT,
        propiedades TEXT,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_vidrios_medidas(db):
    """Crea la tabla vidrios_medidas"""
    sql = """
    CREATE TABLE vidrios_medidas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        obra_id INT NOT NULL,
        vidrio_id INT NOT NULL,
        ancho DECIMAL(8,2) NOT NULL,
        alto DECIMAL(8,2) NOT NULL,
        cantidad INT NOT NULL,
        metros_cuadrados DECIMAL(10,2),
        precio_total DECIMAL(10,2),
        estado VARCHAR(50) DEFAULT 'PENDIENTE',
        fecha_pedido DATE,
        fecha_entrega DATE,
        observaciones TEXT,
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_clientes(db):
    """Crea la tabla clientes"""
    sql = """
    CREATE TABLE clientes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        nit VARCHAR(20),
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion TEXT,
        ciudad VARCHAR(50),
        tipo_cliente VARCHAR(50) DEFAULT 'INDIVIDUAL',
        estado VARCHAR(50) DEFAULT 'ACTIVO',
        descuento_default DECIMAL(5,2) DEFAULT 0,
        limite_credito DECIMAL(12,2) DEFAULT 0,
        dias_credito INT DEFAULT 0,
        contacto_principal VARCHAR(100),
        observaciones TEXT,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_notificaciones(db):
    """Crea la tabla notificaciones"""
    sql = """
    CREATE TABLE notificaciones (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        titulo VARCHAR(255) NOT NULL,
        mensaje TEXT NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        modulo VARCHAR(50),
        referencia_id INT,
        leida BIT DEFAULT 0,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_leida DATETIME,
        prioridad VARCHAR(20) DEFAULT 'NORMAL',
        url_accion VARCHAR(255)
    )
    """
    return db.execute_non_query(sql)

def insertar_datos_iniciales(db):
    """Inserta datos iniciales en las nuevas tablas"""
    print("\n[DATOS INICIALES] Insertando datos básicos...")
    
    try:
        # Insertar roles básicos
        roles = [
            ('admin', 'Administrador con acceso completo'),
            ('supervisor', 'Supervisor con permisos de lectura/escritura'),
            ('usuario', 'Usuario con permisos básicos de lectura')
        ]
        
        for nombre, descripcion in roles:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM roles WHERE nombre = ?", (nombre,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO roles (nombre, descripcion) VALUES (?, ?)", 
                                 (nombre, descripcion))
                    db.commit()
                    print(f"[OK] Rol {nombre} insertado")
                else:
                    print(f"[EXISTE] Rol {nombre}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Rol {nombre}: {str(e)[:50]}...")
        
        # Insertar módulos del sistema
        modulos = [
            ('inventario', 'Gestión de inventario y stock', 'inventory.svg', 1),
            ('obras', 'Gestión de obras y proyectos', 'obras.svg', 2),
            ('compras', 'Gestión de compras y proveedores', 'compras.svg', 3),
            ('contabilidad', 'Gestión contable y financiera', 'contabilidad.svg', 4),
            ('usuarios', 'Gestión de usuarios y permisos', 'users.svg', 5),
            ('herrajes', 'Catálogo de herrajes', 'herrajes.svg', 6),
            ('vidrios', 'Gestión de vidrios y medidas', 'vidrios.svg', 7),
            ('logistica', 'Gestión logística y entregas', 'logistica.svg', 8),
            ('mantenimiento', 'Mantenimiento de equipos', 'mantenimiento.svg', 9),
            ('auditoria', 'Auditoría y logs del sistema', 'auditoria.svg', 10)
        ]
        
        for nombre, descripcion, icono, orden in modulos:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM modulos WHERE nombre = ?", (nombre,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO modulos (nombre, descripcion, icono, orden) 
                        VALUES (?, ?, ?, ?)
                    """, (nombre, descripcion, icono, orden))
                    db.commit()
                    print(f"[OK] Módulo {nombre} insertado")
                else:
                    print(f"[EXISTE] Módulo {nombre}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Módulo {nombre}: {str(e)[:50]}...")
        
        # Insertar algunos herrajes básicos
        herrajes_basicos = [
            ('HER001', 'Bisagra Piano 1m', 'Bisagra piano de 1 metro', 'BISAGRAS', 'Proveedor A', 25.00, 50, 10),
            ('HER002', 'Cerradura Multipunto', 'Cerradura multipunto seguridad', 'CERRADURAS', 'Proveedor B', 150.00, 20, 5),
            ('HER003', 'Manija Aluminio', 'Manija de aluminio anodizado', 'MANIJAS', 'Proveedor A', 35.00, 100, 20),
            ('HER004', 'Riel Corredizo 2m', 'Riel para ventana corrediza', 'RIELES', 'Proveedor C', 45.00, 30, 10)
        ]
        
        for codigo, nombre, desc, categoria, proveedor, precio, stock, minimo in herrajes_basicos:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM herrajes WHERE codigo = ?", (codigo,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO herrajes (codigo, nombre, descripcion, categoria, proveedor, 
                                            precio_unitario, stock_actual, stock_minimo) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, desc, categoria, proveedor, precio, stock, minimo))
                    db.commit()
                    print(f"[OK] Herraje {codigo} insertado")
                else:
                    print(f"[EXISTE] Herraje {codigo}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Herraje {codigo}: {str(e)[:50]}...")
        
        # Insertar tipos de vidrios básicos
        vidrios_basicos = [
            ('Transparente', 4.0, 'Incoloro', 25.00, 'Vidriería Central'),
            ('Transparente', 6.0, 'Incoloro', 35.00, 'Vidriería Central'),
            ('Laminado', 6.0, 'Incoloro', 45.00, 'Vidriería Premium'),
            ('Templado', 8.0, 'Incoloro', 55.00, 'Vidriería Premium'),
            ('Reflectivo', 6.0, 'Bronce', 65.00, 'Vidriería Especializada')
        ]
        
        for tipo, espesor, color, precio, proveedor in vidrios_basicos:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM vidrios WHERE tipo = ? AND espesor = ? AND color = ?", 
                             (tipo, espesor, color))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO vidrios (tipo, espesor, color, precio_m2, proveedor) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (tipo, espesor, color, precio, proveedor))
                    db.commit()
                    print(f"[OK] Vidrio {tipo} {espesor}mm insertado")
                else:
                    print(f"[EXISTE] Vidrio {tipo} {espesor}mm")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Vidrio {tipo}: {str(e)[:50]}...")
        
        # Insertar algunos clientes básicos
        clientes_basicos = [
            ('Constructora ABC S.A.S.', '900123456-1', '301-234-5678', 'info@constructoraabc.com', 
             'Carrera 15 #85-32', 'Bogotá', 'CORPORATIVO', 5.0, 50000000, 30),
            ('Arquitectos & Diseño Ltda.', '800234567-2', '301-345-6789', 'contacto@arqydiseno.com', 
             'Calle 72 #10-45', 'Bogotá', 'CORPORATIVO', 3.0, 20000000, 15),
            ('Juan Pérez', '12345678-9', '310-456-7890', 'juan.perez@email.com', 
             'Calle 123 #45-67', 'Bogotá', 'INDIVIDUAL', 0.0, 5000000, 0)
        ]
        
        for nombre, nit, telefono, email, direccion, ciudad, tipo, descuento, limite, dias in clientes_basicos:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO clientes (nombre, nit, telefono, email, direccion, ciudad, 
                                            tipo_cliente, descuento_default, limite_credito, dias_credito) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nombre, nit, telefono, email, direccion, ciudad, tipo, descuento, limite, dias))
                    db.commit()
                    print(f"[OK] Cliente {nombre} insertado")
                else:
                    print(f"[EXISTE] Cliente {nombre}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Cliente {nombre}: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error insertando datos iniciales: {e}")
        return False

def main():
    """Función principal"""
    print("CREANDO TABLAS CRÍTICAS FALTANTES")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexión a base de datos exitosa")
        
        # Lista de tablas críticas a crear
        tablas_criticas = [
            ("usuarios", crear_tabla_usuarios),
            ("roles", crear_tabla_roles),
            ("permisos_usuario", crear_tabla_permisos_usuario),
            ("modulos", crear_tabla_modulos),
            ("pedidos_detalle", crear_tabla_pedidos_detalle),
            ("pedidos_historial", crear_tabla_pedidos_historial),
            ("herrajes", crear_tabla_herrajes),
            ("vidrios", crear_tabla_vidrios),
            ("vidrios_medidas", crear_tabla_vidrios_medidas),
            ("clientes", crear_tabla_clientes),
            ("notificaciones", crear_tabla_notificaciones)
        ]
        
        creadas = 0
        errores = 0
        
        for nombre_tabla, funcion in tablas_criticas:
            try:
                # Verificar si la tabla ya existe
                cursor = db.cursor()
                cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (nombre_tabla,))
                if cursor.fetchone():
                    print(f"[EXISTE] {nombre_tabla}")
                    creadas += 1
                else:
                    if funcion(db):
                        print(f"[OK] {nombre_tabla} creada")
                        creadas += 1
                    else:
                        print(f"[ERROR] {nombre_tabla} falló")
                        errores += 1
                cursor.close()
                
            except Exception as e:
                print(f"[ERROR] {nombre_tabla}: {str(e)[:100]}...")
                errores += 1
        
        # Insertar datos iniciales
        if insertar_datos_iniciales(db):
            print("\n[OK] Datos iniciales insertados")
        else:
            print("\n[ERROR] Error insertando datos iniciales")
        
        print(f"\n{'='*60}")
        print("RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Tablas creadas/existentes: {creadas}")
        print(f"Errores: {errores}")
        print(f"Total: {len(tablas_criticas)}")
        
        return errores == 0
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

if __name__ == "__main__":
    main()