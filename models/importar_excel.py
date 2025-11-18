"""
importar_excel.py - Importador de datos desde Excel

Este script lee el archivo Excel con los precios y equipos,
y los importa a la base de datos.
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DatabaseManager


def importar_equipos_desde_excel(ruta_excel):
    """
    Importa equipos desde el Excel a la base de datos

    Args:
        ruta_excel (str): Ruta al archivo Excel
    """
    print(f"\n[INFO] Leyendo archivo: {ruta_excel}")

    try:
        # Leer la hoja de "MANTENIMIENTO PREVENTIVO"
        df = pd.read_excel(
            ruta_excel,
            sheet_name='MANTENIMIENTO PREVENTIVO',
            header=None
        )

        print(f"[OK] Archivo leído: {df.shape[0]} filas, {df.shape[1]} columnas")

        # Conectar a base de datos
        db = DatabaseManager()
        db.conectar()

        # EXTRAER EQUIPOS (aproximadamente desde fila 24 en adelante)
        equipos_insertados = 0
        print("\n[INFO] Extrayendo equipos...")

        # Tipos de equipos conocidos del Excel
        tipos_equipos = []

        for i in range(24, min(60, len(df))):
            equipo_nombre = df.iloc[i, 2]  # Columna C (índice 2)

            if pd.notna(equipo_nombre) and isinstance(equipo_nombre, str):
                equipo_nombre = str(equipo_nombre).strip()

                # Identificar si es un equipo válido
                categorias_validas = [
                    'CONDENSADOR', 'EVAPORADOR', 'SISTEMA', 'PAQUETE',
                    'CHILLER', 'SPLIT', 'MANEJADORA', 'FANCOIL', 'CASSETTE'
                ]

                es_equipo = any(cat in equipo_nombre.upper() for cat in categorias_validas)

                if es_equipo and len(equipo_nombre) > 10:
                    # Determinar categoría
                    categoria = 'Otro'
                    if 'CONDENSADOR' in equipo_nombre:
                        categoria = 'Condensador'
                    elif 'EVAPORADOR' in equipo_nombre:
                        categoria = 'Evaporador'
                    elif 'CHILLER' in equipo_nombre:
                        categoria = 'Chiller'
                    elif 'PAQUETE' in equipo_nombre:
                        categoria = 'Paquete'
                    elif 'SPLIT' in equipo_nombre:
                        categoria = 'Split'
                    elif 'SISTEMA' in equipo_nombre:
                        categoria = 'Sistema Precision'

                    # Horas de mantenimiento estimadas (puedes ajustar)
                    horas = 2.5  # Por defecto

                    if 'GRANDE' in equipo_nombre or 'SUPERIOR' in equipo_nombre:
                        horas = 4.0
                    elif 'PEQUEÑO' in equipo_nombre or 'PEQUE' in equipo_nombre:
                        horas = 2.0

                    # Insertar en base de datos
                    try:
                        db.cursor.execute('''
                            INSERT INTO productos_equipos
                            (tipo_equipo, categoria, precio_base, horas_mantenimiento, activo)
                            VALUES (?, ?, ?, ?, 1)
                        ''', (equipo_nombre, categoria, 0, horas))

                        equipos_insertados += 1
                        print(f"  [+] {equipo_nombre} ({categoria}) - {horas}h")

                    except Exception as e:
                        if 'UNIQUE' not in str(e):
                            print(f"  [ERROR] {equipo_nombre}: {e}")

        db.conn.commit()
        print(f"\n[OK] {equipos_insertados} equipos importados")

        # EXTRAER MATERIALES (filas 11-19 aproximadamente)
        materiales_insertados = 0
        print("\n[INFO] Extrayendo materiales...")

        for i in range(11, 20):
            if i < len(df):
                material_nombre = df.iloc[i, 2]  # Columna C
                cantidad = df.iloc[i, 5]  # Columna F
                precio = df.iloc[i, 6]   # Columna G

                if pd.notna(material_nombre) and isinstance(material_nombre, str):
                    material_nombre = str(material_nombre).strip()

                    if len(material_nombre) > 3 and 'SUB TOTAL' not in material_nombre:
                        # Precio unitario
                        precio_unitario = 0
                        if pd.notna(precio) and precio != '':
                            try:
                                precio_unitario = float(precio)
                            except:
                                precio_unitario = 0

                        # Unidad de medida
                        unidad = 'unidad'
                        if pd.notna(cantidad):
                            try:
                                cant_float = float(cantidad)
                                if cant_float < 1:
                                    unidad = 'fracción'
                            except:
                                pass

                        # Insertar material
                        try:
                            db.cursor.execute('''
                                INSERT INTO materiales_repuestos
                                (nombre_material, precio_unitario, unidad_medida, activo)
                                VALUES (?, ?, ?, 1)
                            ''', (material_nombre, precio_unitario, unidad))

                            materiales_insertados += 1
                            print(f"  [+] {material_nombre} - ${precio_unitario}")

                        except Exception as e:
                            if 'UNIQUE' not in str(e):
                                print(f"  [ERROR] {material_nombre}: {e}")

        db.conn.commit()
        print(f"\n[OK] {materiales_insertados} materiales importados")

        db.desconectar()

        print("\n" + "="*60)
        print("IMPORTACIÓN COMPLETADA")
        print("="*60)
        print(f"Equipos: {equipos_insertados}")
        print(f"Materiales: {materiales_insertados}")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[ERROR] Error durante la importación: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Ruta al Excel (ajusta según sea necesario)
    ruta = "C:/Users/Andres/Downloads/COT-MT-25-03-XX MACHOTE MANTENIMIENTO PREVENTIVO (1).xlsx"

    if not os.path.exists(ruta):
        print(f"[ERROR] No se encuentra el archivo: {ruta}")
        print("\nPor favor, ajusta la ruta del archivo Excel en el código.")
    else:
        importar_equipos_desde_excel(ruta)
