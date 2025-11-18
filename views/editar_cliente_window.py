"""
editar_cliente_window.py - Ventana para editar cliente existente

Permite editar información del cliente:
- Nombre de empresa
- Persona de contacto
- Teléfono, email, dirección
- Notas adicionales
- Activar/desactivar
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class EditarClienteWindow:
    """Ventana modal para editar cliente"""

    def __init__(self, parent, id_cliente):
        """
        Inicializa la ventana de edición

        Args:
            parent: Ventana principal
            id_cliente: ID del cliente a editar
        """
        self.parent = parent
        self.id_cliente = id_cliente
        self.window = tk.Toplevel()
        self.window.title("Editar Cliente")
        self.window.geometry("600x650")
        self.window.resizable(False, False)

        # Hacer ventana modal
        self.window.transient(parent.root if hasattr(parent, 'root') else parent)
        self.window.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Cargar datos del cliente
        self.cargar_cliente()

        # Variables del formulario
        self.nombre_empresa_var = tk.StringVar(value=self.cliente[1])
        self.cedula_juridica_var = tk.StringVar(value=self.cliente[9] or '')
        self.contacto_nombre_var = tk.StringVar(value=self.cliente[2] or '')
        self.telefono_var = tk.StringVar(value=self.cliente[3] or '')
        self.email_var = tk.StringVar(value=self.cliente[4] or '')
        self.direccion_var = tk.StringVar(value=self.cliente[5] or '')
        self.notas_var = tk.StringVar(value=self.cliente[6] or '')
        self.activo_var = tk.BooleanVar(value=bool(self.cliente[7]))

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 600
        height = 650
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_cliente(self):
        """Carga los datos del cliente desde la base de datos"""
        try:
            query = "SELECT * FROM clientes WHERE id_cliente = ?"
            result = self.db.ejecutar_query(query, (self.id_cliente,))
            self.cliente = result.fetchone()

            if not self.cliente:
                messagebox.showerror("Error", "No se encontró el cliente")
                self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cliente:\n{e}")
            self.window.destroy()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#f59e0b', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Editar Cliente",
            font=("Arial", 16, "bold"),
            bg='#f59e0b',
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

        # ID (solo lectura)
        tk.Label(
            form_frame,
            text=f"ID: {self.id_cliente}",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Nombre de empresa (obligatorio)
        tk.Label(
            form_frame,
            text="Nombre de Empresa *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

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

        tk.Entry(
            form_frame,
            textvariable=self.notas_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        ).grid(row=15, column=0, sticky=tk.W, pady=(0, 15), ipady=5)

        # Estado (activo/inactivo)
        tk.Label(
            form_frame,
            text="Estado",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=16, column=0, sticky=tk.W, pady=(10, 5))

        tk.Checkbutton(
            form_frame,
            text="Cliente activo (disponible para cotizaciones)",
            variable=self.activo_var,
            font=("Arial", 10),
            bg='white'
        ).grid(row=17, column=0, sticky=tk.W, pady=(0, 15))

        # Nota
        tk.Label(
            form_frame,
            text="* Campos obligatorios",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=18, column=0, sticky=tk.W, pady=(15, 0))

    def crear_botones(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        # Botón Desactivar
        tk.Button(
            btn_frame,
            text="Desactivar",
            font=("Arial", 11),
            bg='#ef4444',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.desactivar_cliente
        ).pack(side=tk.LEFT)

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
            command=self.cerrar
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Botón Guardar
        tk.Button(
            btn_frame,
            text="Guardar Cambios",
            font=("Arial", 11, "bold"),
            bg='#f59e0b',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_cambios
        ).pack(side=tk.RIGHT)

    def guardar_cambios(self):
        """Guarda los cambios del cliente"""
        nombre_empresa = self.nombre_empresa_var.get().strip()

        if not nombre_empresa:
            messagebox.showwarning("Campo Requerido", "El nombre de empresa es obligatorio")
            return

        cedula_juridica = self.cedula_juridica_var.get().strip()
        contacto_nombre = self.contacto_nombre_var.get().strip()
        telefono = self.telefono_var.get().strip()
        email = self.email_var.get().strip()
        direccion = self.direccion_var.get().strip()
        notas = self.notas_var.get().strip()
        activo = 1 if self.activo_var.get() else 0

        try:
            # Actualizar cliente
            self.db.cursor.execute('''
                UPDATE clientes
                SET nombre_empresa = ?, cedula_juridica = ?, contacto_nombre = ?, telefono = ?,
                    email = ?, direccion = ?, notas = ?, activo = ?
                WHERE id_cliente = ?
            ''', (nombre_empresa, cedula_juridica, contacto_nombre, telefono, email,
                  direccion, notas, activo, self.id_cliente))

            self.db.conn.commit()

            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")

            # Actualizar tabla en ventana principal
            if hasattr(self.parent, 'cargar_clientes'):
                self.parent.cargar_clientes()

            self.cerrar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente:\n{e}")

    def desactivar_cliente(self):
        """Desactiva el cliente"""
        if messagebox.askyesno(
            "Confirmar",
            "¿Desactivar este cliente? No aparecerá en las cotizaciones"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE clientes SET activo = 0 WHERE id_cliente = ?",
                    (self.id_cliente,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Cliente desactivado")

                if hasattr(self.parent, 'cargar_clientes'):
                    self.parent.cargar_clientes()

                self.cerrar()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo desactivar:\n{e}")

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
