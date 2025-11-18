"""
login_window.py - Ventana de Login

Esta es la primera pantalla que ve el usuario.
Pide usuario y contraseña para entrar al sistema.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import time
from PIL import Image, ImageTk

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class LoginWindow:
    """Ventana de inicio de sesión"""

    def __init__(self):
        """Inicializa la ventana de login"""
        self.root = tk.Tk()
        self.root.title("AirSolutions - Login")
        self.root.geometry("400x550")
        self.root.resizable(False, False)

        # Centrar ventana en la pantalla
        self.centrar_ventana()

        # Variables para credenciales
        self.usuario_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Usuario autenticado (se llena si login exitoso)
        self.usuario_autenticado = None

        # Sistema de limitación de intentos (seguridad)
        self.intentos_fallidos = {}
        self.tiempo_bloqueo = {}

        # Crear interfaz
        self.crear_interfaz()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def crear_interfaz(self):
        """Crea todos los elementos visuales de la ventana"""

        # Frame principal con padding
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # LOGO / TÍTULO
        title_frame = tk.Frame(main_frame, bg='#2563eb', height=150)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        # Intentar cargar el logo
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'resources', 'images', 'logo.jpg'
        )

        if os.path.exists(logo_path):
            try:
                # Cargar y redimensionar logo
                img = Image.open(logo_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)

                # Mostrar logo
                logo_label = tk.Label(
                    title_frame,
                    image=self.logo_img,
                    bg='#2563eb'
                )
                logo_label.pack(pady=(15, 10))
            except Exception as e:
                print(f"Error cargando logo: {e}")

        titulo = tk.Label(
            title_frame,
            text="AirSolutions",
            font=("Arial", 28, "bold"),
            bg='#2563eb',
            fg='white'
        )
        titulo.pack(pady=5)

        subtitulo = tk.Label(
            title_frame,
            text="Sistema de Cotizaciones HVAC",
            font=("Arial", 12),
            bg='#2563eb',
            fg='white'
        )
        subtitulo.pack(pady=(0, 15))

        # FORMULARIO DE LOGIN
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Usuario
        tk.Label(
            form_frame,
            text="Usuario:",
            font=("Arial", 11),
            bg='#f0f0f0'
        ).pack(anchor=tk.W, pady=(0, 5))

        entry_usuario = tk.Entry(
            form_frame,
            textvariable=self.usuario_var,
            font=("Arial", 12),
            relief=tk.SOLID,
            bd=1
        )
        entry_usuario.pack(fill=tk.X, ipady=8, pady=(0, 20))

        # Contraseña
        tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Arial", 11),
            bg='#f0f0f0'
        ).pack(anchor=tk.W, pady=(0, 5))

        entry_password = tk.Entry(
            form_frame,
            textvariable=self.password_var,
            font=("Arial", 12),
            show="*",
            relief=tk.SOLID,
            bd=1
        )
        entry_password.pack(fill=tk.X, ipady=8, pady=(0, 30))

        # Botón de Login
        btn_login = tk.Button(
            form_frame,
            text="Iniciar Sesión",
            font=("Arial", 13, "bold"),
            bg='#2563eb',
            fg='white',
            activebackground='#1e40af',
            activeforeground='white',
            cursor='hand2',
            relief=tk.FLAT,
            command=self.intentar_login
        )
        btn_login.pack(fill=tk.X, ipady=12)

        # Información de ayuda - SIN MOSTRAR CREDENCIALES (seguridad)
        ayuda_frame = tk.Frame(main_frame, bg='#f0f0f0')
        ayuda_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        tk.Label(
            ayuda_frame,
            text="Sistema de Cotizaciones AirSolutions",
            font=("Arial", 9),
            bg='#f0f0f0',
            fg='#666'
        ).pack()

        tk.Label(
            ayuda_frame,
            text="Ingrese sus credenciales para acceder",
            font=("Arial", 9, "italic"),
            bg='#f0f0f0',
            fg='#999'
        ).pack()

        # Permitir login con Enter
        entry_password.bind('<Return>', lambda e: self.intentar_login())
        entry_usuario.bind('<Return>', lambda e: entry_password.focus())

        # Focus en campo usuario
        entry_usuario.focus()

    def intentar_login(self):
        """
        Verifica las credenciales del usuario con limitación de intentos
        Si son correctas, cierra esta ventana y abre la principal
        """
        usuario = self.usuario_var.get().strip()
        password = self.password_var.get().strip()

        # Validar que no estén vacíos
        if not usuario or not password:
            messagebox.showwarning(
                "Campos vacíos",
                "Por favor ingresa usuario y contraseña"
            )
            return

        # SEGURIDAD: Verificar si la cuenta está bloqueada temporalmente
        if usuario in self.tiempo_bloqueo:
            tiempo_restante = self.tiempo_bloqueo[usuario] - time.time()
            if tiempo_restante > 0:
                minutos = int(tiempo_restante // 60)
                segundos = int(tiempo_restante % 60)
                messagebox.showerror(
                    "Cuenta Bloqueada",
                    f"Demasiados intentos fallidos.\n\nCuenta bloqueada temporalmente.\nIntenta nuevamente en {minutos}m {segundos}s"
                )
                return
            else:
                # El bloqueo expiró, limpiar
                del self.tiempo_bloqueo[usuario]
                self.intentos_fallidos[usuario] = 0

        # Verificar en la base de datos
        resultado = self.db.verificar_login(usuario, password)

        if resultado:
            # Login exitoso - resetear contador de intentos
            if usuario in self.intentos_fallidos:
                del self.intentos_fallidos[usuario]
            if usuario in self.tiempo_bloqueo:
                del self.tiempo_bloqueo[usuario]

            self.usuario_autenticado = {
                'id': resultado[0],
                'usuario': resultado[1],
                'nombre': resultado[2]
            }

            print(f"[OK] Login exitoso: {resultado[1]}")
            self.cerrar_y_abrir_principal()

        else:
            # Login fallido - incrementar contador
            self.intentos_fallidos[usuario] = self.intentos_fallidos.get(usuario, 0) + 1

            intentos_restantes = 3 - self.intentos_fallidos[usuario]

            if self.intentos_fallidos[usuario] >= 3:
                # Bloquear cuenta por 5 minutos (300 segundos)
                self.tiempo_bloqueo[usuario] = time.time() + 300
                messagebox.showerror(
                    "Cuenta Bloqueada",
                    "Demasiados intentos fallidos.\n\nLa cuenta ha sido bloqueada temporalmente por 5 minutos por seguridad."
                )
            else:
                # Mostrar intentos restantes
                messagebox.showerror(
                    "Error de autenticación",
                    f"Usuario o contraseña incorrectos.\n\nIntentos restantes: {intentos_restantes}"
                )

            self.password_var.set("")  # Limpiar contraseña

    def cerrar_y_abrir_principal(self):
        """Cierra ventana de login y abre la principal"""
        print("[INFO] Cerrando ventana de login...")
        self.db.desconectar()
        self.root.destroy()

        # Importar y abrir ventana principal
        try:
            print("[INFO] Abriendo ventana principal...")
            # Importar ventana principal desde views
            from views.main_window import MainWindow
            app_principal = MainWindow(self.usuario_autenticado)
            app_principal.run()
        except Exception as e:
            print(f"[ERROR] No se pudo abrir ventana principal: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """Inicia el loop principal de la aplicación"""
        self.root.mainloop()


if __name__ == '__main__':
    # Si se ejecuta este archivo directamente
    app = LoginWindow()
    app.run()
