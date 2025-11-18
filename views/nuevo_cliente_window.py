"""
nuevo_cliente_window.py - Ventana para agregar nuevo cliente

Permite agregar clientes al sistema:
- Nombre de empresa
- Persona de contacto
- Teléfono, email, dirección
- Notas adicionales
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class NuevoClienteWindow:
    """Ventana modal para agregar nuevo cliente"""

    def __init__(self, parent):
        """
        Inicializa la ventana de nuevo cliente

        Args:
            parent: Ventana principal que llama a esta ventana
        """
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Nuevo Cliente")
        self.window.geometry("600x600")
        self.window.resizable(False, False)

        # Hacer ventana modal
        self.window.transient(parent.root if hasattr(parent, 'root') else parent)
        self.window.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Variables del formulario
        self.nombre_empresa_var = tk.StringVar()
        self.cedula_juridica_var = tk.StringVar()
        self.contacto_nombre_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.notas_var = tk.StringVar()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 600
        height = 600
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#10b981', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Nuevo Cliente",
            font=("Arial", 16, "bold"),
            bg='#10b981',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Contenedor principal
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Formulario
        self.crear_formulario(main_container)

        # Botones
        self.crear_botones(main_container)

    def crear_formulario(self, parent):
        """Crea el formulario de datos del cliente"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Nombre de empresa (obligatorio)
        tk.Label(
            form_frame,
            text="Nombre de Empresa *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Ejemplo: Hotel Aurola, Multiplaza, etc.",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        nombre_entry = tk.Entry(
            form_frame,
            textvariable=self.nombre_empresa_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        )
        nombre_entry.grid(row=2, column=0, sticky=tk.W, pady=(0, 15), ipady=5)
        nombre_entry.focus()

        # Cédula Jurídica
        tk.Label(
            form_frame,
            text="Cédula Jurídica",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Ejemplo: 3-101-123456",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))

        tk.Entry(
            form_frame,
            textvariable=self.cedula_juridica_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=5, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Persona de contacto
        tk.Label(
            form_frame,
            text="Persona de Contacto",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=6, column=0, sticky=tk.W, pady=(10, 5))

        tk.Entry(
            form_frame,
            textvariable=self.contacto_nombre_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=7, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Teléfono
        tk.Label(
            form_frame,
            text="Teléfono",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=8, column=0, sticky=tk.W, pady=(10, 5))

        tk.Entry(
            form_frame,
            textvariable=self.telefono_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=9, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Email
        tk.Label(
            form_frame,
            text="Email",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=10, column=0, sticky=tk.W, pady=(10, 5))

        tk.Entry(
            form_frame,
            textvariable=self.email_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=11, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Dirección
        tk.Label(
            form_frame,
            text="Dirección",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=12, column=0, sticky=tk.W, pady=(10, 5))

        tk.Entry(
            form_frame,
            textvariable=self.direccion_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=13, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Notas
        tk.Label(
            form_frame,
            text="Notas",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=14, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Información adicional relevante",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=15, column=0, sticky=tk.W, pady=(0, 5))

        tk.Entry(
            form_frame,
            textvariable=self.notas_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=16, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Nota sobre campos obligatorios
        tk.Label(
            form_frame,
            text="* Campos obligatorios",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=17, column=0, sticky=tk.W, pady=(15, 0))

    def crear_botones(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        # Botón Cancelar
        tk.Button(
            btn_frame,
            text="Cancelar",
            font=("Arial", 11),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.cancelar
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Botón Guardar
        tk.Button(
            btn_frame,
            text="Guardar Cliente",
            font=("Arial", 11, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_cliente
        ).pack(side=tk.RIGHT)

    def guardar_cliente(self):
        """Guarda el cliente en la base de datos"""
        # Validar campos obligatorios
        nombre_empresa = self.nombre_empresa_var.get().strip()

        if not nombre_empresa:
            messagebox.showwarning(
                "Campos Incompletos",
                "El nombre de empresa es obligatorio"
            )
            return

        cedula_juridica = self.cedula_juridica_var.get().strip()
        contacto_nombre = self.contacto_nombre_var.get().strip()
        telefono = self.telefono_var.get().strip()
        email = self.email_var.get().strip()
        direccion = self.direccion_var.get().strip()
        notas = self.notas_var.get().strip()

        try:
            # Verificar si ya existe un cliente con ese nombre
            cursor = self.db.cursor.execute(
                "SELECT COUNT(*) FROM clientes WHERE nombre_empresa = ?",
                (nombre_empresa,)
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Cliente Existente",
                    f"Ya existe un cliente con el nombre '{nombre_empresa}'"
                )
                return

            # Insertar cliente
            self.db.cursor.execute('''
                INSERT INTO clientes (
                    nombre_empresa, cedula_juridica, contacto_nombre, telefono,
                    email, direccion, notas, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (nombre_empresa, cedula_juridica, contacto_nombre, telefono, email, direccion, notas))

            self.db.conn.commit()

            messagebox.showinfo(
                "Éxito",
                f"Cliente '{nombre_empresa}' guardado correctamente"
            )

            print(f"Cliente guardado: {nombre_empresa}")

            # Actualizar lista en ventana principal si existe el método
            if hasattr(self.parent, 'cargar_clientes'):
                self.parent.cargar_clientes()

            # Cerrar ventana
            self.cerrar()

        except Exception as e:
            print(f"Error al guardar cliente: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el cliente:\n{e}"
            )

    def cancelar(self):
        """Cancela y cierra la ventana"""
        # Verificar si hay datos ingresados
        if self.nombre_empresa_var.get().strip():
            if messagebox.askyesno(
                "Confirmar",
                "Hay datos sin guardar. ¿Deseas salir de todos modos?"
            ):
                self.cerrar()
        else:
            self.cerrar()

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
