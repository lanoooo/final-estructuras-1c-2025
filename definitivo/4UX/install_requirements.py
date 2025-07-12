#!/usr/bin/env python3
"""
Script para instalar las dependencias requeridas
"""

import subprocess
import sys

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=== Instalador de Dependencias - Padel Club ===")
    
    packages = [
        "pymysql",
        "Pillow"
    ]
    
    for package in packages:
        print(f"\nInstalando {package}...")
        if install_package(package):
            print(f"✓ {package} instalado correctamente")
        else:
            print(f"✗ Error al instalar {package}")
    
    print("\n=== Instalación completada ===")
    print("Ahora puede ejecutar la aplicación con: python 4UX/run_app.py")

if __name__ == '__main__':
    main()
