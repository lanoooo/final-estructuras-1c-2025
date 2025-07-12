#!/usr/bin/env python3
"""
Script principal para ejecutar la aplicación del Padel Club
"""

import sys
import os

def check_dependencies():
    """Verificar que todas las dependencias estén disponibles"""
    try:
        import tkinter
        print("✓ tkinter disponible")
    except ImportError:
        print("✗ tkinter no está disponible")
        return False
    
    try:
        import pymysql
        print("✓ pymysql disponible")
    except ImportError:
        print("✗ pymysql no está disponible. Instale con: pip install pymysql")
        return False
    
    # Verificar que el archivo backend existe
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    backend_path = os.path.join(parent_dir, 'Backend', 'padel_backend.py')
    
    if not os.path.exists(backend_path):
        print("✗ padel_backend.py no encontrado")
        print(f"Buscando en: {backend_path}")
        return False
    else:
        print("✓ padel_backend.py encontrado")
    
    return True

def main():
    print("=== Padel Club - Sistema de Reservas ===")
    print("Verificando dependencias...")
    
    if not check_dependencies():
        print("\nError: Faltan dependencias requeridas")
        input("Presione Enter para salir...")
        return
    
    print("\nIniciando aplicación...")
    
    try:
        # Agregar Frontend al path (desde 4UX hacia Frontend)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        frontend_dir = os.path.join(parent_dir, 'Frontend')
        
        # Cambiar al directorio Frontend para que las importaciones funcionen correctamente
        os.chdir(frontend_dir)
        sys.path.insert(0, frontend_dir)
        
        print(f"Directorio de trabajo cambiado a: {frontend_dir}")
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_app", os.path.join(frontend_dir, "main_app.py"))
        if spec is None or spec.loader is None:
            raise ImportError("No se pudo cargar el módulo main_app")
        main_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_app)
        App = main_app.App
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")

if __name__ == '__main__':
    main()
