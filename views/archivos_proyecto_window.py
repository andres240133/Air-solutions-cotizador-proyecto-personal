"""
archivos_proyecto_window.py - Ventana de Gestión de Archivos

Permite vincular archivos al proyecto (planos AutoCAD, PDFs, etc.)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess


class ArchivosProyectoWindow:
    """Ventana para gestionar archivos del proyecto"""

    def __init__(self, parent, db, id_proyecto):
        """
        Inicializa la ventana de archivos

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_proyecto: ID del proyecto
        """
        self.db = db
        self.id_proyecto = id_proyecto

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestión de Archivos del Proyecto")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Obtener información del proyecto
        self.cargar_proyecto()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 900
        height = 600
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_proyecto(self):
        """Carga información del proyecto"""
        cursor = self.db.ejecutar_query('''
            SELECT numero_proyecto, nombre_proyecto
            FROM proyectos
            WHERE id_proyecto = ?
        ''', (self.id_proyecto,))

        self.proyecto = cursor.fetchone()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.dialog, bg='#1e293b')
        header.pack(fill=tk.X)

        info_frame = tk.Frame(header, bg='#1e293b')
        info_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            info_frame,
            text=f"Archivos del Proyecto: {self.proyecto[0]} - {self.proyecto[1]}",
            font=("Arial", 14, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w')

        # Botones de acción
        btn_frame = tk.Frame(header, bg='#1e293b')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        tk.Button(
            btn_frame,
            text="📎 Vincular Archivo",
            font=("Arial", 10),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.vincular_archivo
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="🔄 Actualizar",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.cargar_archivos
        ).pack(side=tk.LEFT)

        # Contenedor principal
        main_container = tk.Frame(self.dialog, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Info
        info_label = tk.Label(
            main_container,
            text="Los archivos no se copian, solo se vinculan. Puedes vincular planos AutoCAD (.dwg), PDFs, imágenes, etc.",
            font=("Arial", 9),
            bg='#f3f4f6',
            fg='#6b7280',
            padx=10,
            pady=10,
            wraplength=800,
            justify=tk.LEFT
        )
        info_label.pack(fill=tk.X, pady=(0, 15))

        # Tabla de archivos
        table_frame = tk.Frame(main_container, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_archivos = ttk.Treeview(
            table_frame,
            columns=('Nombre', 'Tipo', 'Nivel', 'Descripción', 'Ruta'),
            show='headings',
            yscrollcommand=scrollbar.set
        )

        self.tree_archivos.heading('Nombre', text='Nombre Archivo')
        self.tree_archivos.heading('Tipo', text='Tipo')
        self.tree_archivos.heading('Nivel', text='Nivel')
        self.tree_archivos.heading('Descripción', text='Descripción')
        self.tree_archivos.heading('Ruta', text='Ruta Completa')

        self.tree_archivos.column('Nombre', width=200)
        self.tree_archivos.column('Tipo', width=80)
        self.tree_archivos.column('Nivel', width=100)
        self.tree_archivos.column('Descripción', width=250)
        self.tree_archivos.column('Ruta', width=300)

        self.tree_archivos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_archivos.yview)

        # Eventos
        self.tree_archivos.bind('<Double-1>', self.abrir_archivo)
        self.tree_archivos.bind('<Button-3>', self.menu_archivo)

        # Botones inferiores
        bottom_frame = tk.Frame(main_container, bg='white')
        bottom_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Button(
            bottom_frame,
            text="📂 Abrir Archivo",
            font=("Arial", 10),
            bg='#3b82f6',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=lambda: self.abrir_archivo(None)
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            bottom_frame,
            text="📁 Abrir Carpeta",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.abrir_carpeta
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            bottom_frame,
            text="🗑️ Desvincular",
            font=("Arial", 10),
            bg='#ef4444',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.desvincular_archivo
        ).pack(side=tk.LEFT)

        # Cargar archivos
        self.cargar_archivos()

    def cargar_archivos(self):
        """Carga los archivos vinculados"""
        # Limpiar tabla
        for item in self.tree_archivos.get_children():
            self.tree_archivos.delete(item)

        # Cargar archivos
        cursor = self.db.ejecutar_query('''
            SELECT
                pa.id_archivo, pa.nombre_archivo, pa.tipo_archivo,
                pn.codigo_nivel, pa.descripcion, pa.ruta_archivo
            FROM proyecto_archivos pa
            LEFT JOIN proyecto_niveles pn ON pa.id_nivel = pn.id_nivel
            WHERE pa.id_proyecto = ?
            ORDER BY pa.fecha_agregado DESC
        ''', (self.id_proyecto,))

        archivos = cursor.fetchall()

        for archivo in archivos:
            id_archivo, nombre, tipo, nivel, descripcion, ruta = archivo

            nivel_str = nivel or 'General'
            tipo_str = tipo or self.obtener_extension(nombre)
            desc_str = descripcion or '-'

            self.tree_archivos.insert('', 'end', values=(
                nombre, tipo_str, nivel_str, desc_str, ruta
            ), tags=(id_archivo,))

    def obtener_extension(self, nombre_archivo):
        """Obtiene la extensión del archivo"""
        if not nombre_archivo:
            return 'Desconocido'

        ext = os.path.splitext(nombre_archivo)[1].upper()
        if ext:
            return ext[1:]  # Remover el punto
        return 'Sin extensión'

    def vincular_archivo(self):
        """Vincula un nuevo archivo"""
        # Selector de archivo
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos AutoCAD", "*.dwg"),
                ("Archivos PDF", "*.pdf"),
                ("Imágenes", "*.png *.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        # Verificar que el archivo existe
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "El archivo no existe")
            return

        # Crear diálogo para información adicional
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Información del Archivo")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.dialog)
        dialog.grab_set()

        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f'500x300+{x}+{y}')

        main_frame = tk.Frame(dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Nombre del archivo (readonly)
        row = 0
        tk.Label(
            main_frame,
            text="Archivo:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        nombre_archivo = os.path.basename(ruta)
        tk.Label(
            main_frame,
            text=nombre_archivo,
            font=("Arial", 10, "bold"),
            bg='white'
        ).grid(row=row, column=1, sticky='w', pady=10, padx=(10, 0))

        # Nivel (opcional)
        row += 1
        tk.Label(
            main_frame,
            text="Nivel (opcional):",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        nivel_var = tk.StringVar()
        nivel_combo = ttk.Combobox(
            main_frame,
            textvariable=nivel_var,
            font=("Arial", 10),
            width=30,
            state='readonly'
        )
        nivel_combo.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        # Cargar niveles
        cursor = self.db.ejecutar_query('''
            SELECT id_nivel, codigo_nivel, nombre_nivel
            FROM proyecto_niveles
            WHERE id_proyecto = ?
            ORDER BY orden, codigo_nivel
        ''', (self.id_proyecto,))

        niveles = cursor.fetchall()
        niveles_dict = {}
        niveles_list = ['(Sin nivel específico)']

        for id_nivel, codigo, nombre in niveles:
            display = f"{codigo} - {nombre}"
            niveles_list.append(display)
            niveles_dict[display] = id_nivel

        nivel_combo['values'] = niveles_list
        nivel_combo.current(0)

        # Descripción
        row += 1
        tk.Label(
            main_frame,
            text="Descripción:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='nw', pady=10)

        descripcion_text = tk.Text(
            main_frame,
            font=("Arial", 10),
            width=30,
            height=4,
            wrap=tk.WORD
        )
        descripcion_text.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        main_frame.columnconfigure(1, weight=1)

        def guardar_vinculo():
            nivel_seleccionado = nivel_var.get()
            id_nivel = niveles_dict.get(nivel_seleccionado)
            descripcion = descripcion_text.get('1.0', tk.END).strip()

            tipo_archivo = self.obtener_extension(nombre_archivo)

            try:
                self.db.ejecutar_query('''
                    INSERT INTO proyecto_archivos (
                        id_proyecto, id_nivel, nombre_archivo,
                        ruta_archivo, tipo_archivo, descripcion
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.id_proyecto,
                    id_nivel,
                    nombre_archivo,
                    ruta,
                    tipo_archivo,
                    descripcion if descripcion else None
                ))

                messagebox.showinfo("Éxito", f"Archivo '{nombre_archivo}' vinculado correctamente")
                dialog.destroy()
                self.cargar_archivos()

            except Exception as e:
                messagebox.showerror("Error", f"Error al vincular archivo:\n{e}")

        # Botones
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="✅ Vincular",
            font=("Arial", 10, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=guardar_vinculo
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT)

    def abrir_archivo(self, event):
        """Abre el archivo seleccionado"""
        selection = self.tree_archivos.selection()
        if not selection:
            if event is None:
                messagebox.showwarning("Selección Requerida", "Selecciona un archivo para abrir")
            return

        item = self.tree_archivos.item(selection[0])
        ruta = item['values'][4]

        if not os.path.exists(ruta):
            messagebox.showerror(
                "Archivo No Encontrado",
                f"El archivo no existe en la ruta:\n{ruta}\n\n"
                "Puede haber sido movido o eliminado."
            )
            return

        try:
            # Abrir con la aplicación asociada
            os.startfile(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir archivo:\n{e}")

    def abrir_carpeta(self):
        """Abre la carpeta que contiene el archivo"""
        selection = self.tree_archivos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un archivo")
            return

        item = self.tree_archivos.item(selection[0])
        ruta = item['values'][4]

        if not os.path.exists(ruta):
            messagebox.showerror("Archivo No Encontrado", "El archivo no existe")
            return

        try:
            carpeta = os.path.dirname(ruta)
            os.startfile(carpeta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir carpeta:\n{e}")

    def desvincular_archivo(self):
        """Desvincula un archivo"""
        selection = self.tree_archivos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un archivo para desvincular")
            return

        item = self.tree_archivos.item(selection[0])
        nombre = item['values'][0]
        id_archivo = item['tags'][0]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Desvincular el archivo '{nombre}'?\n\n"
            "El archivo no se eliminará, solo se quitará el vínculo."
        ):
            try:
                self.db.ejecutar_query(
                    'DELETE FROM proyecto_archivos WHERE id_archivo = ?',
                    (id_archivo,)
                )
                self.cargar_archivos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al desvincular archivo:\n{e}")

    def menu_archivo(self, event):
        """Menú contextual para archivos"""
        selection = self.tree_archivos.selection()
        if not selection:
            return

        menu = tk.Menu(self.dialog, tearoff=0)
        menu.add_command(label="📂 Abrir Archivo", command=lambda: self.abrir_archivo(None))
        menu.add_command(label="📁 Abrir Carpeta", command=self.abrir_carpeta)
        menu.add_separator()
        menu.add_command(label="🗑️ Desvincular", command=self.desvincular_archivo)

        menu.post(event.x_root, event.y_root)
