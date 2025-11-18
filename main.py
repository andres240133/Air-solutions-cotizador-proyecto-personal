"""
main.py - Archivo principal de AirSolutions

Este es el archivo que se ejecuta para iniciar la aplicación.
Primero verifica que la base de datos exista, luego abre el login.
"""

import sys
import os

# Asegurar que los imports funcionen correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import DatabaseManager, inicializar_base_datos
from views.login_window import LoginWindow


def main():
    """Función principal de la aplicación"""
    print("="*60)
    print("AIRSOLUTIONS - SISTEMA DE COTIZACIONES")
    print("="*60)
    print()

    # Verificar/crear base de datos
    print("[INFO] Verificando base de datos...")
    db = DatabaseManager()

    # Si no existe, se crea automáticamente
    if not os.path.exists('models/airsolutions.db'):
        print("[INFO] Primera vez ejecutando. Creando base de datos...")
        inicializar_base_datos()
    else:
        print("[OK] Base de datos encontrada")
        # Conectar para verificar que funcione
        if db.conectar():
            db.desconectar()

    print()
    print("[INFO] Iniciando interfaz gráfica...")
    print()

    # Iniciar aplicación con ventana de login
    app = LoginWindow()
    app.run()

    print()
    print("[INFO] Aplicación cerrada")
    print("="*60)


if __name__ == '__main__':
    main()
