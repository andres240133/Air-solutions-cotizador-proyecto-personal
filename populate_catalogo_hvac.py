"""
populate_catalogo_hvac.py - Poblar catálogo de componentes HVAC

Popula el catálogo con componentes HVAC estándar basados en la terminología
común de la industria.
"""

import sqlite3
import os


def poblar_catalogo():
    """Popula el catálogo de componentes HVAC"""

    db_path = 'models/airsolutions.db'

    if not os.path.exists(db_path):
        print("[ERROR] Base de datos no encontrada")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("="*70)
        print("POBLANDO CATALOGO DE COMPONENTES HVAC")
        print("="*70)

        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM catalogo_hvac")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"[INFO] Ya existen {count} componentes en el catálogo")
            respuesta = input("¿Desea reemplazar el catálogo? (s/n): ")
            if respuesta.lower() != 's':
                print("[INFO] Operación cancelada")
                return False

            cursor.execute("DELETE FROM catalogo_hvac")
            print("[OK] Catálogo limpiado")

        # Componentes HVAC estándar
        componentes = [
            # Dampers / Compuertas
            ('DM', 'Damper Manual', 'Dampers', 'unidad', 150.00, 50.00, 75.00),
            ('DA', 'Damper Automático', 'Dampers', 'unidad', 450.00, 150.00, 100.00),
            ('ABD', 'Automatic Balancing Damper', 'Dampers', 'unidad', 500.00, 180.00, 120.00),
            ('FD', 'Fire Damper (Cortafuego)', 'Dampers', 'unidad', 600.00, 200.00, 150.00),
            ('SD', 'Smoke Damper', 'Dampers', 'unidad', 650.00, 220.00, 160.00),
            ('VCD', 'Volume Control Damper', 'Dampers', 'unidad', 300.00, 100.00, 80.00),

            # Extractores y Ventiladores
            ('ST-EX', 'Extractor de Aire', 'Extractores', 'unidad', 800.00, 250.00, 200.00),
            ('ST-IN', 'Inyector de Aire', 'Inyectores', 'unidad', 850.00, 280.00, 220.00),
            ('VE-AX', 'Ventilador Axial', 'Ventiladores', 'unidad', 700.00, 200.00, 180.00),
            ('VE-CE', 'Ventilador Centrífugo', 'Ventiladores', 'unidad', 1200.00, 400.00, 300.00),
            ('EX-BA', 'Extractor de Baño', 'Extractores', 'unidad', 350.00, 100.00, 80.00),
            ('EX-CO', 'Extractor de Cocina', 'Extractores', 'unidad', 900.00, 300.00, 200.00),

            # Rejillas y Difusores
            ('RE', 'Rejilla', 'Rejillas', 'unidad', 45.00, 15.00, 25.00),
            ('RE-EX', 'Rejilla Extracción', 'Rejillas', 'unidad', 50.00, 18.00, 28.00),
            ('RE-IN', 'Rejilla Inyección', 'Rejillas', 'unidad', 50.00, 18.00, 28.00),
            ('RE-RE', 'Rejilla Retorno', 'Rejillas', 'unidad', 55.00, 20.00, 30.00),
            ('DI', 'Difusor', 'Difusores', 'unidad', 80.00, 30.00, 35.00),
            ('DI-CI', 'Difusor Circular', 'Difusores', 'unidad', 85.00, 32.00, 38.00),
            ('DI-LI', 'Difusor Lineal', 'Difusores', 'unidad', 120.00, 45.00, 50.00),
            ('DI-RE', 'Difusor Rectangular', 'Difusores', 'unidad', 90.00, 35.00, 40.00),

            # Ductos
            ('DU-RE', 'Ducto Rectangular', 'Ductos', 'm²', 35.00, 25.00, 15.00),
            ('DU-CI', 'Ducto Circular', 'Ductos', 'ml', 28.00, 20.00, 12.00),
            ('DU-FL', 'Ducto Flexible', 'Ductos', 'ml', 18.00, 12.00, 8.00),
            ('DU-FI', 'Ducto Fibra de Vidrio', 'Ductos', 'm²', 42.00, 30.00, 18.00),
            ('CO-DU', 'Codo de Ducto', 'Accesorios Ductos', 'unidad', 25.00, 15.00, 12.00),
            ('TE-DU', 'Tee de Ducto', 'Accesorios Ductos', 'unidad', 35.00, 22.00, 15.00),
            ('RE-DU', 'Reducción de Ducto', 'Accesorios Ductos', 'unidad', 28.00, 18.00, 12.00),

            # Aislamiento
            ('AI-TH', 'Aislamiento Térmico', 'Aislamiento', 'm²', 0.00, 15.00, 8.00),
            ('AI-AC', 'Aislamiento Acústico', 'Aislamiento', 'm²', 0.00, 22.00, 10.00),
            ('VA-AI', 'Vapor Barrier (Aislamiento)', 'Aislamiento', 'm²', 0.00, 8.00, 5.00),

            # Soportería y Estructura
            ('SO-DU', 'Soporte para Ducto', 'Soportería', 'unidad', 0.00, 25.00, 15.00),
            ('SO-EQ', 'Soporte para Equipo', 'Soportería', 'unidad', 0.00, 45.00, 30.00),
            ('VI-AN', 'Vibración Aislador', 'Soportería', 'unidad', 35.00, 15.00, 12.00),
            ('BA-ES', 'Base Estructural', 'Soportería', 'unidad', 0.00, 80.00, 60.00),

            # Equipos Principales
            ('MA-AI', 'Manejadora de Aire', 'Equipos', 'unidad', 5000.00, 1500.00, 1000.00),
            ('FA-CO', 'Fan Coil', 'Equipos', 'unidad', 1200.00, 350.00, 250.00),
            ('UM-AC', 'Unidad Condensadora', 'Equipos', 'unidad', 2500.00, 800.00, 500.00),
            ('UM-EV', 'Unidad Evaporadora', 'Equipos', 'unidad', 1800.00, 600.00, 400.00),
            ('CH-AG', 'Chiller Agua', 'Equipos', 'unidad', 15000.00, 4000.00, 2500.00),

            # Controles y Automatización
            ('TE-AM', 'Termostato Ambiente', 'Controles', 'unidad', 120.00, 35.00, 40.00),
            ('SE-TE', 'Sensor de Temperatura', 'Controles', 'unidad', 80.00, 25.00, 30.00),
            ('SE-HU', 'Sensor de Humedad', 'Controles', 'unidad', 95.00, 30.00, 35.00),
            ('AC-DA', 'Actuador para Damper', 'Controles', 'unidad', 250.00, 80.00, 60.00),
            ('CO-BM', 'Control BMS', 'Controles', 'unidad', 800.00, 250.00, 200.00),

            # Filtros
            ('FI-AI', 'Filtro de Aire', 'Filtros', 'unidad', 45.00, 25.00, 15.00),
            ('FI-HE', 'Filtro HEPA', 'Filtros', 'unidad', 180.00, 80.00, 30.00),
            ('FI-CA', 'Filtro de Carbón', 'Filtros', 'unidad', 120.00, 60.00, 25.00),

            # Otros Componentes
            ('SI-RU', 'Silenciador de Ruido', 'Accesorios', 'unidad', 350.00, 120.00, 80.00),
            ('LO-AI', 'Louver de Aire', 'Accesorios', 'unidad', 200.00, 80.00, 60.00),
            ('PU-AC', 'Puerta de Acceso', 'Accesorios', 'unidad', 85.00, 35.00, 25.00),
            ('VI-IN', 'Visor/Inspección', 'Accesorios', 'unidad', 45.00, 20.00, 15.00),
        ]

        cursor.executemany('''
            INSERT INTO catalogo_hvac
            (codigo, descripcion, categoria, unidad_medida,
             costo_equipo_base, costo_material_base, costo_mano_obra_base)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', componentes)

        conn.commit()

        print(f"[OK] {len(componentes)} componentes agregados al catálogo")
        print()
        print("CATEGORÍAS INCLUIDAS:")
        print("  - Dampers (Compuertas)")
        print("  - Extractores y Ventiladores")
        print("  - Rejillas y Difusores")
        print("  - Ductos y Accesorios")
        print("  - Aislamiento")
        print("  - Soportería")
        print("  - Equipos Principales")
        print("  - Controles y Automatización")
        print("  - Filtros")
        print("  - Accesorios Varios")
        print()
        print("="*70)
        print("[OK] Catálogo HVAC poblado exitosamente")
        print("="*70)

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] Error al poblar catálogo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    poblar_catalogo()
