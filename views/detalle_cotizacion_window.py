"""
detalle_cotizacion_window.py - Ventana para ver detalle de cotización

Muestra toda la información de una cotización guardada:
- Información general
- Todos los items agregados por categoría
- Totales calculados
- Permite cambiar el estado de la cotización
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class DetalleCotizacionWindow:
    """Ventana modal para ver detalle de cotización"""

    def __init__(self, parent, numero_cotizacion):
        """
        Inicializa la ventana de detalle

        Args:
            parent: Ventana principal que llama a esta ventana
            numero_cotizacion: Número de la cotización a mostrar
        """
        self.parent = parent
        self.numero_cotizacion = numero_cotizacion
        self.window = tk.Toplevel()
        self.window.title(f"Detalle Cotización - {numero_cotizacion}")
        self.window.geometry("1000x700")

        # Hacer ventana modal
        self.window.transient(parent.root if hasattr(parent, 'root') else parent)
        self.window.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Cargar datos de la cotización
        self.cargar_cotizacion()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 1000
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_cotizacion(self):
        """Carga todos los datos de la cotización desde la base de datos"""
        try:
            # Datos principales de la cotización
            query = """
                SELECT c.*, cl.nombre_empresa, cl.contacto_nombre
                FROM cotizaciones c
                LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
                WHERE c.numero_cotizacion = ?
            """
            result = self.db.ejecutar_query(query, (self.numero_cotizacion,))
            self.cotizacion = result.fetchone()

            if not self.cotizacion:
                messagebox.showerror("Error", "No se encontró la cotización")
                self.window.destroy()
                return

            # Obtener ID de la cotización
            self.id_cotizacion = self.cotizacion[0]

            # Cargar equipos
            self.equipos = self.cargar_detalle_equipos()

            # Cargar ductos
            self.ductos = self.cargar_detalle_ductos()

            # Cargar difusores
            self.difusores = self.cargar_detalle_difusores()

            # Cargar rejillas
            self.rejillas = self.cargar_detalle_rejillas()

            # Cargar tuberías
            self.tuberias = self.cargar_detalle_tuberias()

            # Cargar mano de obra
            self.mano_obra = self.cargar_detalle_mano_obra()

            # Cargar materiales
            self.materiales = self.cargar_detalle_materiales()

            # Cargar gastos
            self.gastos = self.cargar_detalle_gastos()

        except Exception as e:
            print(f"Error al cargar cotización: {e}")
            messagebox.showerror("Error", f"Error al cargar la cotización:\n{e}")
            self.window.destroy()

    def cargar_detalle_equipos(self):
        """Carga equipos de la cotización"""
        query = """
            SELECT pe.tipo_equipo, dc.cantidad, dc.horas_por_equipo, dc.subtotal
            FROM detalle_cotizacion dc
            LEFT JOIN productos_equipos pe ON dc.id_equipo = pe.id_equipo
            WHERE dc.id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_ductos(self):
        """Carga ductos de la cotización"""
        query = """
            SELECT tipo_ducto, largo_suministro, largo_retorno, precio_unitario, subtotal
            FROM cotizacion_ductos
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_difusores(self):
        """Carga difusores de la cotización"""
        query = """
            SELECT tipo_difusor, cantidad, precio_unitario, subtotal
            FROM cotizacion_difusores
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_rejillas(self):
        """Carga rejillas de la cotización"""
        query = """
            SELECT tipo_rejilla, cantidad, precio_unitario, subtotal
            FROM cotizacion_rejillas
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_tuberias(self):
        """Carga tuberías de la cotización"""
        query = """
            SELECT tipo_tuberia, largo, precio_unitario, subtotal
            FROM cotizacion_tuberias
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_mano_obra(self):
        """Carga mano de obra de la cotización"""
        query = """
            SELECT descripcion, cantidad, precio_unitario, subtotal
            FROM cotizacion_mano_obra
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_materiales(self):
        """Carga materiales de la cotización"""
        query = """
            SELECT mr.nombre_material, cm.cantidad, cm.precio_unitario, cm.subtotal
            FROM cotizacion_materiales cm
            LEFT JOIN materiales_repuestos mr ON cm.id_material = mr.id_material
            WHERE cm.id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def cargar_detalle_gastos(self):
        """Carga gastos adicionales de la cotización"""
        query = """
            SELECT concepto, monto
            FROM gastos_adicionales
            WHERE id_cotizacion = ?
        """
        result = self.db.ejecutar_query(query, (self.id_cotizacion,))
        return result.fetchall()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#2563eb', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"Cotización {self.numero_cotizacion}",
            font=("Arial", 16, "bold"),
            bg='#2563eb',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Estado con color
        estado = self.cotizacion[16]  # estado está en la columna 16
        color_estado = {
            'pendiente': '#f59e0b',
            'aprobada': '#10b981',
            'rechazada': '#ef4444',
            'facturada': '#6366f1'
        }.get(estado if estado else 'pendiente', '#6b7280')

        tk.Label(
            header,
            text=str(estado).upper() if estado else 'PENDIENTE',
            font=("Arial", 12, "bold"),
            bg=color_estado,
            fg='white',
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=20, pady=15)

        # Contenido con scroll
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Contenido
        content = tk.Frame(scrollable_frame, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Información general
        self.crear_seccion_info_general(content)

        # Secciones de items (solo mostrar las que tienen datos)
        if self.equipos:
            self.crear_seccion_equipos(content)

        if self.ductos:
            self.crear_seccion_ductos(content)

        if self.difusores:
            self.crear_seccion_difusores(content)

        if self.rejillas:
            self.crear_seccion_rejillas(content)

        if self.tuberias:
            self.crear_seccion_tuberias(content)

        if self.mano_obra:
            self.crear_seccion_mano_obra(content)

        if self.materiales:
            self.crear_seccion_materiales(content)

        if self.gastos:
            self.crear_seccion_gastos(content)

        # Totales
        self.crear_seccion_totales(content)

        # Botones de acción
        self.crear_botones_accion(content)

    def crear_seccion_info_general(self, parent):
        """Muestra información general de la cotización"""
        frame = tk.LabelFrame(
            parent,
            text="Información General",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        info = [
            ("Cliente:", self.cotizacion[26]),  # nombre_empresa
            ("Contacto:", self.cotizacion[27] or "N/A"),  # contacto_nombre
            ("Fecha:", self.cotizacion[3]),  # fecha_emision
            ("Tipo de Servicio:", self.cotizacion[5]),  # tipo_servicio
            ("Visitas Anuales:", str(self.cotizacion[6])),  # visitas_anuales
            ("Factor de Venta:", f"{self.cotizacion[7]:.2f}"),  # factor_venta
        ]

        for i, (label, valor) in enumerate(info):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(
                frame,
                text=label,
                font=("Arial", 10, "bold"),
                bg='white',
                fg='#666'
            ).grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=5)

            tk.Label(
                frame,
                text=valor,
                font=("Arial", 10),
                bg='white'
            ).grid(row=row, column=col+1, sticky=tk.W, padx=(0, 40), pady=5)

    def crear_seccion_equipos(self, parent):
        """Muestra equipos de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Equipos HVAC",
            ('Equipo', 'Cantidad', 'Horas', 'Subtotal'),
            self.equipos
        )

    def crear_seccion_ductos(self, parent):
        """Muestra ductos de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Ductos",
            ('Tipo', 'Largo Sum (m)', 'Largo Ret (m)', 'Precio/m', 'Subtotal'),
            self.ductos
        )

    def crear_seccion_difusores(self, parent):
        """Muestra difusores de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Difusores",
            ('Tipo', 'Cantidad', 'Precio Unit', 'Subtotal'),
            self.difusores
        )

    def crear_seccion_rejillas(self, parent):
        """Muestra rejillas de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Rejillas",
            ('Tipo', 'Cantidad', 'Precio Unit', 'Subtotal'),
            self.rejillas
        )

    def crear_seccion_tuberias(self, parent):
        """Muestra tuberías de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Tuberias",
            ('Tipo', 'Largo (m)', 'Precio/m', 'Subtotal'),
            self.tuberias
        )

    def crear_seccion_mano_obra(self, parent):
        """Muestra mano de obra de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Mano de Obra",
            ('Descripcion', 'Cantidad', 'Precio Unit', 'Subtotal'),
            self.mano_obra
        )

    def crear_seccion_materiales(self, parent):
        """Muestra materiales de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Materiales y Repuestos",
            ('Material', 'Cantidad', 'Precio Unit', 'Subtotal'),
            self.materiales
        )

    def crear_seccion_gastos(self, parent):
        """Muestra gastos adicionales de la cotización"""
        self.crear_tabla_seccion(
            parent,
            "Gastos Adicionales",
            ('Concepto', 'Monto'),
            self.gastos
        )

    def crear_tabla_seccion(self, parent, titulo, columnas, datos):
        """Crea una sección con tabla de datos"""
        frame = tk.LabelFrame(
            parent,
            text=titulo,
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Tabla
        tree = ttk.Treeview(
            frame,
            columns=columnas,
            show='headings',
            height=min(len(datos), 5)
        )

        for col in columnas:
            tree.heading(col, text=col)

        # Insertar datos
        for row in datos:
            # Formatear valores monetarios
            formatted_row = []
            for val in row:
                if isinstance(val, (int, float)) and val > 0:
                    formatted_row.append(f"${val:.2f}" if val >= 0.01 else str(val))
                else:
                    formatted_row.append(val)
            tree.insert('', 'end', values=formatted_row)

        tree.pack(fill=tk.X)

    def crear_seccion_totales(self, parent):
        """Muestra los totales de la cotización"""
        frame = tk.LabelFrame(
            parent,
            text="Totales",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Índices de las columnas en la consulta
        subtotal = self.cotizacion[10]  # subtotal
        ins_ccss = self.cotizacion[19]  # ins_ccss
        total_iva = self.cotizacion[14]  # total_iva
        total = self.cotizacion[15]  # total

        totales = [
            ("Subtotal:", subtotal),
        ]

        if ins_ccss and ins_ccss > 0:
            totales.append(("INS y CCSS:", ins_ccss))

        totales.extend([
            ("IVA (13%):", total_iva),
            ("TOTAL FINAL:", total)
        ])

        for label, valor in totales:
            row_frame = tk.Frame(frame, bg='white')
            row_frame.pack(fill=tk.X, pady=3)

            tk.Label(
                row_frame,
                text=label,
                font=("Arial", 11, "bold") if "TOTAL" in label else ("Arial", 11),
                bg='white'
            ).pack(side=tk.LEFT)

            tk.Label(
                row_frame,
                text=f"${valor:.2f}",
                font=("Arial", 14, "bold") if "TOTAL FINAL" in label else ("Arial", 11),
                bg='white',
                fg='#2563eb' if "TOTAL FINAL" in label else 'black'
            ).pack(side=tk.RIGHT)

    def crear_botones_accion(self, parent):
        """Crea botones de acción"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.X, pady=20)

        # Botón Cambiar Estado
        tk.Button(
            frame,
            text="Cambiar Estado",
            bg='#f59e0b',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 11, "bold"),
            padx=30,
            pady=10,
            command=self.cambiar_estado
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botón Generar PDF
        tk.Button(
            frame,
            text="📄 Generar PDF",
            bg='#10b981',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 11, "bold"),
            padx=30,
            pady=10,
            command=self.generar_pdf
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botón Enviar por Email
        tk.Button(
            frame,
            text="📧 Enviar Email",
            bg='#8b5cf6',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 11, "bold"),
            padx=30,
            pady=10,
            command=self.enviar_por_email
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botón Cerrar
        tk.Button(
            frame,
            text="Cerrar",
            bg='#6b7280',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 11),
            padx=30,
            pady=10,
            command=self.cerrar
        ).pack(side=tk.RIGHT)

    def cambiar_estado(self):
        """Permite cambiar el estado de la cotización"""
        # Crear ventana de diálogo para seleccionar estado
        dialog = tk.Toplevel(self.window)
        dialog.title("Cambiar Estado")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        # Centrar
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - 175
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - 125
        dialog.geometry(f"350x250+{x}+{y}")

        tk.Label(
            dialog,
            text="Selecciona el nuevo estado:",
            font=("Arial", 12, "bold")
        ).pack(pady=20)

        # Variable para el estado
        nuevo_estado = tk.StringVar(value=self.cotizacion[16])  # estado

        # Opciones de estado
        estados = [
            ('pendiente', 'Pendiente'),
            ('aprobada', 'Aprobada'),
            ('rechazada', 'Rechazada'),
            ('facturada', 'Facturada')
        ]

        for valor, texto in estados:
            tk.Radiobutton(
                dialog,
                text=texto,
                variable=nuevo_estado,
                value=valor,
                font=("Arial", 11)
            ).pack(anchor=tk.W, padx=40, pady=5)

        # Botones
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        def guardar_estado():
            try:
                estado_seleccionado = nuevo_estado.get()

                # Actualizar en base de datos
                self.db.cursor.execute(
                    "UPDATE cotizaciones SET estado = ? WHERE numero_cotizacion = ?",
                    (estado_seleccionado, self.numero_cotizacion)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", f"Estado actualizado a: {estado_seleccionado}")

                # Actualizar tabla en ventana principal
                if hasattr(self.parent, 'cargar_cotizaciones'):
                    self.parent.cargar_cotizaciones()

                dialog.destroy()
                self.cerrar()

            except Exception as e:
                print(f"Error al cambiar estado: {e}")
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

        tk.Button(
            btn_frame,
            text="Guardar",
            bg='#2563eb',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=20,
            command=guardar_estado
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancelar",
            bg='#6b7280',
            fg='white',
            font=("Arial", 10),
            padx=20,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def generar_pdf(self):
        """Genera el PDF de la cotización"""
        try:
            from utils.pdf_generator import generar_pdf_cotizacion
            import os
            import subprocess

            # Generar PDF
            pdf_path = generar_pdf_cotizacion(self.numero_cotizacion, self.db)

            if pdf_path:
                messagebox.showinfo(
                    "Éxito",
                    f"PDF generado correctamente:\n{pdf_path}\n\n¿Deseas abrir el archivo?"
                )

                # Abrir el PDF
                if messagebox.askyesno("Abrir PDF", "¿Abrir el archivo PDF ahora?"):
                    # Abrir con el visualizador predeterminado
                    os.startfile(pdf_path)

            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo generar el PDF. Revisa la consola para más detalles."
                )

        except Exception as e:
            print(f"Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Error",
                f"Error al generar PDF:\n{e}"
            )

    def enviar_por_email(self):
        """Abre diálogo para enviar cotización por email"""
        try:
            from utils.email_manager import EmailManager
            from utils.pdf_generator import generar_pdf_cotizacion

            # Crear diálogo
            dialog = tk.Toplevel(self.window)
            dialog.title("Enviar Cotización por Email")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.window)
            dialog.grab_set()

            # Centrar
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 250
            y = (dialog.winfo_screenheight() // 2) - 200
            dialog.geometry(f'500x400+{x}+{y}')

            # Header
            header = tk.Frame(dialog, bg='#8b5cf6', height=60)
            header.pack(fill=tk.X)
            header.pack_propagate(False)

            tk.Label(
                header,
                text="📧 Enviar Cotización por Email",
                font=("Arial", 14, "bold"),
                bg='#8b5cf6',
                fg='white'
            ).pack(pady=20)

            # Contenido
            content = tk.Frame(dialog, bg='white')
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Email destino
            tk.Label(
                content,
                text="Email del Cliente:",
                font=("Arial", 10, "bold"),
                bg='white'
            ).pack(anchor=tk.W, pady=(10, 5))

            email_var = tk.StringVar()
            # Pre-cargar email si existe
            if hasattr(self, 'datos_cotizacion') and self.datos_cotizacion[5]:
                email_var.set(self.datos_cotizacion[5])

            tk.Entry(
                content,
                textvariable=email_var,
                font=("Arial", 11),
                width=40
            ).pack(anchor=tk.W, pady=(0, 15))

            # Mensaje personalizado
            tk.Label(
                content,
                text="Mensaje Personalizado (opcional):",
                font=("Arial", 10, "bold"),
                bg='white'
            ).pack(anchor=tk.W, pady=(10, 5))

            mensaje_text = tk.Text(
                content,
                font=("Arial", 10),
                height=8,
                width=50,
                relief=tk.SOLID,
                bd=1
            )
            mensaje_text.pack(anchor=tk.W, pady=(0, 15))

            # Información
            tk.Label(
                content,
                text="ℹ️ El email incluirá el PDF de la cotización adjunto",
                font=("Arial", 9),
                bg='white',
                fg='#666'
            ).pack(pady=10)

            # Botones
            btn_frame = tk.Frame(dialog, bg='white')
            btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

            def enviar():
                email_destino = email_var.get().strip()

                if not email_destino:
                    messagebox.showwarning("Campo Requerido", "Ingresa el email del destinatario")
                    return

                # Validar email básicamente
                if '@' not in email_destino or '.' not in email_destino:
                    messagebox.showwarning("Email Inválido", "Ingresa un email válido")
                    return

                mensaje_personalizado = mensaje_text.get("1.0", tk.END).strip()

                # Generar PDF primero
                dialog.destroy()
                pdf_path = generar_pdf_cotizacion(self.numero_cotizacion, self.db)

                if not pdf_path:
                    messagebox.showerror("Error", "No se pudo generar el PDF")
                    return

                # Enviar email
                email_manager = EmailManager(self.db)
                nombre_cliente = self.datos_cotizacion[1] if hasattr(self, 'datos_cotizacion') else "Cliente"

                exito, mensaje = email_manager.enviar_cotizacion(
                    email_destino,
                    nombre_cliente,
                    self.numero_cotizacion,
                    pdf_path,
                    mensaje_personalizado
                )

                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                else:
                    messagebox.showerror("Error", mensaje)

            tk.Button(
                btn_frame,
                text="📧 Enviar Email",
                font=("Arial", 11, "bold"),
                bg='#8b5cf6',
                fg='white',
                padx=20,
                pady=8,
                command=enviar
            ).pack(side=tk.LEFT, padx=(0, 10))

            tk.Button(
                btn_frame,
                text="Cancelar",
                font=("Arial", 11),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                command=dialog.destroy
            ).pack(side=tk.LEFT)

        except Exception as e:
            print(f"Error abriendo diálogo de email: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al abrir diálogo de email:\n{e}")

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
