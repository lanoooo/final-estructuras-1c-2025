#!/usr/bin/env python3
"""
Script para configurar y verificar la base de datos
"""

import pymysql
import sys
import os

# Agregar el directorio Backend al path (desde 4UX hacia Backend)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(parent_dir, 'Backend')
sys.path.insert(0, backend_dir)

# Configuración de conexión
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'padelclub'
}

def test_connection():
    """Probar conexión a la base de datos"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✓ Conexión a la base de datos exitosa")
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ Versión de MySQL: {version[0]}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False

def check_tables():
    """Verificar que las tablas necesarias existan"""
    required_tables = ['usuarios', 'reservas', 'canchas_dia_1', 'canchas_dia_2', 
                      'canchas_dia_3', 'canchas_dia_4', 'torneos', 'equipos', 'partidos']
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✓ Tabla '{table}' existe")
            else:
                print(f"✗ Tabla '{table}' no existe")
                missing_tables.append(table)
        
        connection.close()
        
        if missing_tables:
            print(f"\nTablas faltantes: {', '.join(missing_tables)}")
            print("Ejecute los scripts SQL proporcionados para crear las tablas.")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error al verificar tablas: {e}")
        return False

def create_test_user():
    """Crear usuario de prueba"""
    try:
        from padel_backend import UsuarioManager
        
        um = UsuarioManager()
        
        # Crear usuario admin de prueba
        if um.crear_usuario("admin", "admin123", "admin"):
            print("✓ Usuario admin de prueba creado (usuario: admin, contraseña: admin123)")
        
        # Crear usuario jugador de prueba
        if um.crear_usuario("jugador1", "123456", "jugador"):
            print("✓ Usuario jugador de prueba creado (usuario: jugador1, contraseña: 123456)")
        
        um.desconectar()
        
    except Exception as e:
        print(f"Error al crear usuarios de prueba: {e}")

def main():
    print("=== Configuración de Base de Datos - Padel Club ===")
    
    print("\n1. Probando conexión a la base de datos...")
    if not test_connection():
        print("Configure la conexión en DB_CONFIG antes de continuar.")
        return
    
    print("\n2. Verificando tablas...")
    if not check_tables():
        print("Ejecute los scripts SQL antes de continuar.")
        return
    
    print("\n3. Creando usuarios de prueba...")
    create_test_user()
    
    print("\n4. Ejecutando script SQL para crear tablas de torneos...")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Leer y ejecutar el script SQL
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(current_dir, 'create_tournament_tables.sql')
        
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Ejecutar cada statement por separado
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            connection.commit()
            print("✓ Tablas de torneos creadas exitosamente")
        else:
            print("✗ Archivo create_tournament_tables.sql no encontrado")
        
        connection.close()
        
    except Exception as e:
        print(f"Error al crear tablas de torneos: {e}")
    
    print("\n✓ Configuración completada exitosamente!")
    print("\nCredenciales de prueba:")
    print("- Admin: usuario='admin', contraseña='admin123'")
    print("- Jugador: usuario='jugador1', contraseña='123456'")

if __name__ == '__main__':
    main()
