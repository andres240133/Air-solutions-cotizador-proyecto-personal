"""
backup_manager.py - Sistema de Respaldo de Base de Datos

Permite:
- Crear respaldos automáticos o manuales de la base de datos
- Comprimir respaldos en ZIP
- Restaurar desde respaldo
- Listar y eliminar respaldos antiguos
"""

import os
import shutil
import zipfile
from datetime import datetime
import sqlite3


class BackupManager:
    """Gestor de respaldos de la base de datos"""

    def __init__(self, db_path, backup_dir=None):
        """
        Inicializa el gestor de respaldos

        Args:
            db_path: Ruta a la base de datos principal
            backup_dir: Directorio donde guardar respaldos (opcional)
        """
        self.db_path = db_path

        if backup_dir is None:
            # Crear carpeta backups en el mismo directorio que la DB
            db_dir = os.path.dirname(db_path)
            self.backup_dir = os.path.join(db_dir, 'backups')
        else:
            self.backup_dir = backup_dir

        # Crear directorio de backups si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def crear_backup(self, descripcion=""):
        """
        Crea un respaldo de la base de datos

        Args:
            descripcion: Descripción opcional del respaldo

        Returns:
            tuple: (éxito, ruta_backup o mensaje_error)
        """
        try:
            # Verificar que la base de datos existe
            if not os.path.exists(self.db_path):
                return False, "La base de datos no existe"

            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"airsolutions_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)

            # Copiar base de datos
            shutil.copy2(self.db_path, backup_path)

            # Comprimir en ZIP
            zip_name = f"airsolutions_backup_{timestamp}.zip"
            zip_path = os.path.join(self.backup_dir, zip_name)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_name)

                # Agregar archivo de metadata
                metadata = f"""Respaldo de AirSolutions
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Descripción: {descripcion if descripcion else 'Respaldo manual'}
Archivo DB: {backup_name}
"""
                zipf.writestr('INFO.txt', metadata)

            # Eliminar archivo .db temporal (ya está en el ZIP)
            os.remove(backup_path)

            return True, zip_path

        except Exception as e:
            return False, f"Error al crear respaldo: {str(e)}"

    def listar_backups(self):
        """
        Lista todos los respaldos disponibles

        Returns:
            list: Lista de tuplas (nombre_archivo, fecha_creacion, tamaño_mb)
        """
        try:
            backups = []

            for archivo in os.listdir(self.backup_dir):
                if archivo.endswith('.zip') and archivo.startswith('airsolutions_backup_'):
                    ruta = os.path.join(self.backup_dir, archivo)

                    # Obtener información del archivo
                    stats = os.stat(ruta)
                    tamaño_mb = stats.st_size / (1024 * 1024)  # Convertir a MB
                    fecha = datetime.fromtimestamp(stats.st_mtime)

                    backups.append((archivo, fecha, tamaño_mb, ruta))

            # Ordenar por fecha (más reciente primero)
            backups.sort(key=lambda x: x[1], reverse=True)

            return backups

        except Exception as e:
            print(f"Error listando backups: {e}")
            return []

    def restaurar_backup(self, backup_path):
        """
        Restaura la base de datos desde un respaldo

        Args:
            backup_path: Ruta al archivo ZIP de respaldo

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(backup_path):
                return False, "El archivo de respaldo no existe"

            # Crear respaldo de seguridad de la DB actual antes de restaurar
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_actual = os.path.join(
                self.backup_dir,
                f"pre_restore_backup_{timestamp}.db"
            )
            shutil.copy2(self.db_path, backup_actual)

            # Extraer el archivo de la base de datos del ZIP
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Buscar el archivo .db dentro del ZIP
                db_files = [f for f in zipf.namelist() if f.endswith('.db')]

                if not db_files:
                    return False, "No se encontró archivo de base de datos en el respaldo"

                # Extraer a ubicación temporal
                temp_db = os.path.join(self.backup_dir, 'temp_restore.db')
                zipf.extract(db_files[0], self.backup_dir)

                extracted_path = os.path.join(self.backup_dir, db_files[0])
                shutil.move(extracted_path, temp_db)

            # Verificar integridad del archivo extraído
            try:
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM clientes")
                conn.close()
            except Exception as e:
                os.remove(temp_db)
                return False, f"El archivo de respaldo está corrupto: {str(e)}"

            # Reemplazar base de datos actual
            if os.path.exists(self.db_path):
                os.remove(self.db_path)

            shutil.move(temp_db, self.db_path)

            return True, f"Base de datos restaurada correctamente. Respaldo previo guardado en: {backup_actual}"

        except Exception as e:
            return False, f"Error al restaurar: {str(e)}"

    def eliminar_backup(self, backup_path):
        """
        Elimina un archivo de respaldo

        Args:
            backup_path: Ruta al archivo de respaldo

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return True, "Respaldo eliminado correctamente"
            else:
                return False, "El archivo no existe"

        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"

    def limpiar_backups_antiguos(self, dias=30):
        """
        Elimina respaldos más antiguos que X días

        Args:
            dias: Días de antigüedad máxima

        Returns:
            tuple: (cantidad_eliminada, mensaje)
        """
        try:
            fecha_limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)
            eliminados = 0

            for archivo in os.listdir(self.backup_dir):
                if archivo.endswith('.zip') and archivo.startswith('airsolutions_backup_'):
                    ruta = os.path.join(self.backup_dir, archivo)

                    if os.path.getmtime(ruta) < fecha_limite:
                        os.remove(ruta)
                        eliminados += 1

            return eliminados, f"Se eliminaron {eliminados} respaldos antiguos"

        except Exception as e:
            return 0, f"Error al limpiar: {str(e)}"

    def obtener_info_backup(self, backup_path):
        """
        Obtiene información detallada de un respaldo

        Args:
            backup_path: Ruta al archivo de respaldo

        Returns:
            dict: Información del respaldo
        """
        try:
            info = {}

            # Información del archivo
            stats = os.stat(backup_path)
            info['tamaño_mb'] = stats.st_size / (1024 * 1024)
            info['fecha_creacion'] = datetime.fromtimestamp(stats.st_mtime)

            # Leer metadata del ZIP
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'INFO.txt' in zipf.namelist():
                    info['metadata'] = zipf.read('INFO.txt').decode('utf-8')

                info['archivos'] = zipf.namelist()

            return info

        except Exception as e:
            return {'error': str(e)}
