"""
encryption.py - Módulo de encriptación para datos sensibles

Proporciona funciones para encriptar y desencriptar datos sensibles
como contraseñas de email usando Fernet (AES-128)
"""

import os
from cryptography.fernet import Fernet


class EncryptionManager:
    """Gestor de encriptación para datos sensibles"""

    def __init__(self):
        """Inicializa el gestor con la clave de encriptación"""
        self.key_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            '.encryption_key'
        )
        self.key = self._cargar_o_generar_clave()
        self.cipher = Fernet(self.key)

    def _cargar_o_generar_clave(self):
        """Carga la clave existente o genera una nueva"""
        # Crear directorio config si no existe
        config_dir = os.path.dirname(self.key_file)
        os.makedirs(config_dir, exist_ok=True)

        if os.path.exists(self.key_file):
            # Cargar clave existente
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generar nueva clave
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)

            # Cambiar permisos del archivo (solo lectura/escritura para propietario)
            try:
                import stat
                os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)  # 600
            except:
                pass  # En Windows puede fallar, pero no es crítico

            print(f"[OK] Clave de encriptación generada: {self.key_file}")
            return key

    def encriptar(self, texto):
        """
        Encripta un texto

        Args:
            texto (str): Texto a encriptar

        Returns:
            str: Texto encriptado en base64
        """
        if not texto:
            return ""

        try:
            encrypted = self.cipher.encrypt(texto.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            print(f"Error al encriptar: {e}")
            return ""

    def desencriptar(self, texto_encriptado):
        """
        Desencripta un texto

        Args:
            texto_encriptado (str): Texto encriptado en base64

        Returns:
            str: Texto desencriptado
        """
        if not texto_encriptado:
            return ""

        try:
            decrypted = self.cipher.decrypt(texto_encriptado.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Error al desencriptar: {e}")
            # Puede ser que el texto no esté encriptado (datos viejos)
            return texto_encriptado


# Instancia global para usar en toda la aplicación
_encryption_manager = None


def get_encryption_manager():
    """Obtiene la instancia global del gestor de encriptación"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


# Funciones de conveniencia
def encriptar_password(password):
    """Encripta una contraseña"""
    return get_encryption_manager().encriptar(password)


def desencriptar_password(password_encriptada):
    """Desencripta una contraseña"""
    return get_encryption_manager().desencriptar(password_encriptada)
