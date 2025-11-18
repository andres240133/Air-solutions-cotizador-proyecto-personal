"""
main_window.py - Ventana Principal de la Aplicación

Esta es la ventana principal donde tu papá trabajará.
Tiene pestañas para:
- Cotizaciones
- Clientes
- Productos/Equipos
- Materiales
- Configuración
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import shutil
import zipfile

# Agregar path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager
from utils.encryption import encriptar_password, desencriptar_password


class MainWindow:
    """Ventana principal de la aplicación"""

    def __init__(self, usuario):
        """
        Inicializa la ventana principal

        Args:
            usuario (dict): Datos del usuario autenticado
        """
        self.usuario = usuario
        self.root = tk.Tk()
        self.root.title("AirSolutions - Sistema de Cotizaciones")
        self.root.geometry("1200x700")

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Crear interfaz
        self.crear_menu_superior()
        self.crear_notebook()

        # Evento al cerrar ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def crear_menu_superior(self):
        """Crea la barra superior con logo y usuario"""
        header = tk.Frame(self.root, bg='#1e293b', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Frame para logo + título
        logo_frame = tk.Frame(header, bg='#1e293b')
        logo_frame.pack(side=tk.LEFT, padx=20, pady=5)

        # Intentar cargar logo
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'resources', 'images', 'logo.jpg'
        )

        if os.path.exists(logo_path):
            try:
                # Cargar y redimensionar logo
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)

                # Mostrar logo
                logo_label = tk.Label(
                    logo_frame,
                    image=self.logo_img,
                    bg='#1e293b'
                )
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            except Exception as e:
                print(f"Error cargando logo: {e}")

        # Título
        tk.Label(
            logo_frame,
            text="AirSolutions",
            font=("Arial", 18, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)

        # Usuario y botón cerrar sesión
        user_frame = tk.Frame(header, bg='#1e293b')
        user_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            user_frame,
            text=f"Usuario: {self.usuario['nombre']}",
            font=("Arial", 11),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            user_frame,
            text="Cerrar Sesión",
            font=("Arial", 10),
            bg='#ef4444',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            command=self.cerrar_sesion
        ).pack(side=tk.LEFT)

    def crear_notebook(self):
        """Crea las pestañas (tabs) de la aplicación"""
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear cada pestaña
        self.crear_tab_dashboard()
        self.crear_tab_cotizaciones()
        self.crear_tab_proyectos()
        self.crear_tab_clientes()
        self.crear_tab_productos()
        self.crear_tab_materiales()
        self.crear_tab_configuracion()
        self.crear_tab_respaldos()

    def crear_tab_dashboard(self):
        """Pestaña de Dashboard con estadísticas"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  📊 Dashboard  ')

        # Header
        header = tk.Frame(tab, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header,
            text="Dashboard - Estadísticas",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        # Botón refrescar
        tk.Button(
            header,
            text="🔄 Actualizar",
            font=("Arial", 11),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.actualizar_dashboard
        ).pack(side=tk.RIGHT)

        # Contenedor principal con scroll
        main_container = tk.Frame(tab, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.dashboard_frame = tk.Frame(canvas, bg='white')

        self.dashboard_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.dashboard_frame, anchor="nw", width=1000)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar datos del dashboard
        self.cargar_dashboard()

    def cargar_dashboard(self):
        """Carga los datos y gráficos del dashboard"""
        # Limpiar frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        # KPIs en la parte superior
        kpi_frame = tk.Frame(self.dashboard_frame, bg='white')
        kpi_frame.pack(fill=tk.X, pady=(0, 20))

        # Obtener estadísticas
        try:
            # Total de cotizaciones
            result = self.db.ejecutar_query("SELECT COUNT(*) FROM cotizaciones")
            total_cotizaciones = result.fetchone()[0]

            # Cotizaciones por estado
            result = self.db.ejecutar_query("""
                SELECT estado, COUNT(*)
                FROM cotizaciones
                GROUP BY estado
            """)
            estados_data = result.fetchall()
            estados_dict = {estado: count for estado, count in estados_data}

            aprobadas = estados_dict.get('Aprobada', 0)
            enviadas = estados_dict.get('Enviada', 0)
            borradores = estados_dict.get('Borrador', 0)
            rechazadas = estados_dict.get('Rechazada', 0)

            # Tasa de conversión
            conversion_rate = (aprobadas / total_cotizaciones * 100) if total_cotizaciones > 0 else 0

            # Ingresos totales de cotizaciones aprobadas
            result = self.db.ejecutar_query("""
                SELECT SUM(total)
                FROM cotizaciones
                WHERE estado = 'aprobada'
            """)
            ingresos_totales = result.fetchone()[0] or 0

            # Total clientes
            result = self.db.ejecutar_query("SELECT COUNT(*) FROM clientes WHERE activo = 1")
            total_clientes = result.fetchone()[0]

            # Crear KPIs
            kpis = [
                ("Total Cotizaciones", str(total_cotizaciones), "#2563eb"),
                ("Aprobadas", str(aprobadas), "#10b981"),
                ("Enviadas", str(enviadas), "#f59e0b"),
                ("Borradores", str(borradores), "#6b7280"),
                ("% Conversión", f"{conversion_rate:.1f}%", "#8b5cf6"),
                ("Ingresos Totales", f"${ingresos_totales:,.0f}", "#10b981"),
                ("Clientes Activos", str(total_clientes), "#2563eb")
            ]

            for i, (titulo, valor, color) in enumerate(kpis):
                kpi_card = tk.Frame(kpi_frame, bg=color, relief=tk.RAISED, bd=2)
                kpi_card.grid(row=0, column=i, padx=10, sticky='ew')
                kpi_frame.grid_columnconfigure(i, weight=1)

                tk.Label(
                    kpi_card,
                    text=titulo,
                    font=("Arial", 10),
                    bg=color,
                    fg='white'
                ).pack(pady=(10, 5))

                tk.Label(
                    kpi_card,
                    text=valor,
                    font=("Arial", 18, "bold"),
                    bg=color,
                    fg='white'
                ).pack(pady=(0, 10))

            # Frame para gráficos
            charts_frame = tk.Frame(self.dashboard_frame, bg='white')
            charts_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            # Gráfico 1: Estados de cotizaciones (Pie Chart)
            self.crear_grafico_estados(charts_frame, estados_data)

            # Gráfico 2: Cotizaciones por mes (Bar Chart)
            self.crear_grafico_mensual(charts_frame)

            # Tabla de top clientes
            self.crear_tabla_top_clientes(charts_frame)

        except Exception as e:
            print(f"Error cargando dashboard: {e}")
            import traceback
            traceback.print_exc()
            tk.Label(
                self.dashboard_frame,
                text=f"Error cargando estadísticas: {e}",
                font=("Arial", 12),
                bg='white',
                fg='red'
            ).pack(pady=20)

    def crear_grafico_estados(self, parent, estados_data):
        """Crea gráfico de pie con estados de cotizaciones"""
        if not estados_data:
            return

        frame = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(0, weight=1)

        tk.Label(
            frame,
            text="Cotizaciones por Estado",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)

        # Crear figura de matplotlib
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        labels = [estado for estado, _ in estados_data]
        sizes = [count for _, count in estados_data]
        colors = {
            'Borrador': '#6b7280',
            'Enviada': '#f59e0b',
            'Aprobada': '#10b981',
            'Rechazada': '#ef4444'
        }
        colores = [colors.get(label, '#2563eb') for label in labels]

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colores, startangle=90)
        ax.axis('equal')

        # Incrustar en tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def crear_grafico_mensual(self, parent):
        """Crea gráfico de barras con cotizaciones por mes"""
        frame = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(1, weight=1)

        tk.Label(
            frame,
            text="Cotizaciones por Mes (últimos 6 meses)",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)

        try:
            # Obtener cotizaciones de últimos 6 meses
            fecha_inicio = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            result = self.db.ejecutar_query("""
                SELECT strftime('%Y-%m', fecha_emision) as mes, COUNT(*) as total
                FROM cotizaciones
                WHERE fecha_emision >= ?
                GROUP BY mes
                ORDER BY mes
            """, (fecha_inicio,))

            datos = result.fetchall()

            if datos:
                meses = [mes for mes, _ in datos]
                totales = [total for _, total in datos]

                # Crear figura
                fig = Figure(figsize=(5, 4), dpi=100)
                ax = fig.add_subplot(111)

                ax.bar(meses, totales, color='#2563eb')
                ax.set_xlabel('Mes')
                ax.set_ylabel('Cantidad')
                ax.tick_params(axis='x', rotation=45)

                fig.tight_layout()

                # Incrustar en tkinter
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                tk.Label(
                    frame,
                    text="No hay datos suficientes",
                    font=("Arial", 11),
                    bg='white',
                    fg='#666'
                ).pack(pady=40)

        except Exception as e:
            print(f"Error en gráfico mensual: {e}")
            tk.Label(
                frame,
                text="Error cargando datos",
                font=("Arial", 11),
                bg='white',
                fg='red'
            ).pack(pady=40)

    def crear_tabla_top_clientes(self, parent):
        """Crea tabla con top 5 clientes"""
        frame = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        tk.Label(
            frame,
            text="Top 5 Clientes (por cotizaciones aprobadas)",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)

        try:
            result = self.db.ejecutar_query("""
                SELECT cl.nombre_empresa,
                       COUNT(c.id_cotizacion) as total_cotizaciones,
                       SUM(c.total) as total_ingresos
                FROM clientes cl
                LEFT JOIN cotizaciones c ON cl.id_cliente = c.id_cliente
                    AND c.estado = 'aprobada'
                GROUP BY cl.id_cliente
                HAVING total_cotizaciones > 0
                ORDER BY total_ingresos DESC
                LIMIT 5
            """)

            datos = result.fetchall()

            if datos:
                # Crear tabla
                table_frame = tk.Frame(frame, bg='white')
                table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

                headers = ["Cliente", "Cotizaciones", "Ingresos Totales"]
                for i, header in enumerate(headers):
                    tk.Label(
                        table_frame,
                        text=header,
                        font=("Arial", 11, "bold"),
                        bg='#f3f4f6',
                        relief=tk.SOLID,
                        bd=1,
                        padx=10,
                        pady=8
                    ).grid(row=0, column=i, sticky='ew')

                for row_idx, (cliente, total_cot, total_ing) in enumerate(datos, start=1):
                    tk.Label(
                        table_frame,
                        text=cliente,
                        font=("Arial", 10),
                        bg='white',
                        anchor='w',
                        padx=10,
                        pady=5
                    ).grid(row=row_idx, column=0, sticky='ew')

                    tk.Label(
                        table_frame,
                        text=str(total_cot),
                        font=("Arial", 10),
                        bg='white',
                        anchor='center',
                        padx=10,
                        pady=5
                    ).grid(row=row_idx, column=1, sticky='ew')

                    tk.Label(
                        table_frame,
                        text=f"${total_ing:,.2f}",
                        font=("Arial", 10, "bold"),
                        bg='white',
                        fg='#10b981',
                        anchor='e',
                        padx=10,
                        pady=5
                    ).grid(row=row_idx, column=2, sticky='ew')

                table_frame.grid_columnconfigure(0, weight=2)
                table_frame.grid_columnconfigure(1, weight=1)
                table_frame.grid_columnconfigure(2, weight=1)
            else:
                tk.Label(
                    frame,
                    text="No hay datos de clientes con cotizaciones aprobadas",
                    font=("Arial", 11),
                    bg='white',
                    fg='#666'
                ).pack(pady=20)

        except Exception as e:
            print(f"Error en tabla top clientes: {e}")

    def actualizar_dashboard(self):
        """Actualiza los datos del dashboard"""
        self.cargar_dashboard()

    def crear_tab_cotizaciones(self):
        """Pestaña de Cotizaciones"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  Cotizaciones  ')

        # Frame superior con botón
        top_frame = tk.Frame(tab, bg='white')
        top_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_frame,
            text="Cotizaciones",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            top_frame,
            text="+ Nueva Cotización",
            font=("Arial", 11, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.nueva_cotizacion
        ).pack(side=tk.RIGHT)

        # Barra de búsqueda y filtros
        search_frame = tk.Frame(tab, bg='white')
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Búsqueda por texto
        tk.Label(
            search_frame,
            text="Buscar:",
            font=("Arial", 10, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filtrar_cotizaciones())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 11),
            width=30,
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Filtro por estado
        tk.Label(
            search_frame,
            text="Estado:",
            font=("Arial", 10, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.filtro_estado_var = tk.StringVar(value="Todos")
        estados = ["Todos", "Borrador", "Enviada", "Aprobada", "Rechazada"]

        estado_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filtro_estado_var,
            values=estados,
            font=("Arial", 10),
            width=12,
            state='readonly'
        )
        estado_combo.pack(side=tk.LEFT, padx=(0, 20))
        estado_combo.bind('<<ComboboxSelected>>', lambda e: self.filtrar_cotizaciones())

        # Filtro por mes
        tk.Label(
            search_frame,
            text="Mes:",
            font=("Arial", 10, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.filtro_mes_var = tk.StringVar(value="Todos")
        meses = ["Todos", "Este mes", "Último mes", "Últimos 3 meses", "Últimos 6 meses", "Este año"]

        mes_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filtro_mes_var,
            values=meses,
            font=("Arial", 10),
            width=15,
            state='readonly'
        )
        mes_combo.pack(side=tk.LEFT, padx=(0, 10))
        mes_combo.bind('<<ComboboxSelected>>', lambda e: self.filtrar_cotizaciones())

        # Botón limpiar filtros
        tk.Button(
            search_frame,
            text="Limpiar",
            font=("Arial", 9),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.limpiar_filtros
        ).pack(side=tk.LEFT)

        # Tabla de cotizaciones
        self.crear_tabla_cotizaciones(tab)

    def crear_tabla_cotizaciones(self, parent):
        """Crea la tabla para mostrar cotizaciones"""
        # Frame con scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview (tabla)
        columns = ('Número', 'Cliente', 'Fecha', 'Total', 'Estado')
        self.tree_cotizaciones = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set
        )

        # Configurar columnas
        self.tree_cotizaciones.heading('Número', text='Número')
        self.tree_cotizaciones.heading('Cliente', text='Cliente')
        self.tree_cotizaciones.heading('Fecha', text='Fecha')
        self.tree_cotizaciones.heading('Total', text='Total')
        self.tree_cotizaciones.heading('Estado', text='Estado')

        self.tree_cotizaciones.column('Número', width=150)
        self.tree_cotizaciones.column('Cliente', width=300)
        self.tree_cotizaciones.column('Fecha', width=120)
        self.tree_cotizaciones.column('Total', width=120)
        self.tree_cotizaciones.column('Estado', width=120)

        self.tree_cotizaciones.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_cotizaciones.yview)

        # Doble click para ver detalle
        self.tree_cotizaciones.bind('<Double-1>', self.ver_detalle_cotizacion)

        # Clic derecho para menú contextual
        self.tree_cotizaciones.bind('<Button-3>', self.mostrar_menu_cotizacion)

        # Cargar datos
        self.cargar_cotizaciones()

    def crear_tab_proyectos(self):
        """Pestaña de Proyectos Grandes"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  🏗️ Proyectos  ')

        # Frame superior con título y botones
        top_frame = tk.Frame(tab, bg='white')
        top_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_frame,
            text="Gestión de Proyectos Grandes",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        # Botones
        buttons_frame = tk.Frame(top_frame, bg='white')
        buttons_frame.pack(side=tk.RIGHT)

        tk.Button(
            buttons_frame,
            text="➕ Nuevo Proyecto",
            font=("Arial", 11),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.nuevo_proyecto
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="🔄 Actualizar",
            font=("Arial", 11),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.cargar_proyectos
        ).pack(side=tk.LEFT, padx=5)

        # Frame de búsqueda
        search_frame = tk.Frame(tab, bg='white')
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            search_frame,
            text="Buscar:",
            font=("Arial", 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.buscar_proyecto_var = tk.StringVar()
        self.buscar_proyecto_var.trace('w', lambda *args: self.cargar_proyectos())

        tk.Entry(
            search_frame,
            textvariable=self.buscar_proyecto_var,
            font=("Arial", 11),
            width=40
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            search_frame,
            text="Estado:",
            font=("Arial", 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 10))

        self.filtro_estado_proyecto_var = tk.StringVar(value='todos')
        estados_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filtro_estado_proyecto_var,
            values=['todos', 'en_planificacion', 'en_curso', 'pausado', 'completado', 'cancelado'],
            state='readonly',
            width=20
        )
        estados_combo.pack(side=tk.LEFT)
        estados_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_proyectos())

        # Tabla de proyectos
        tree_frame = tk.Frame(tab, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_proyectos = ttk.Treeview(
            tree_frame,
            columns=('Número', 'Nombre', 'Cliente', 'Ubicación', 'Responsable', 'Estado', 'Total', 'Fecha'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )

        # Configurar columnas
        self.tree_proyectos.heading('Número', text='Número')
        self.tree_proyectos.heading('Nombre', text='Nombre Proyecto')
        self.tree_proyectos.heading('Cliente', text='Cliente')
        self.tree_proyectos.heading('Ubicación', text='Ubicación')
        self.tree_proyectos.heading('Responsable', text='Responsable')
        self.tree_proyectos.heading('Estado', text='Estado')
        self.tree_proyectos.heading('Total', text='Total Proyecto')
        self.tree_proyectos.heading('Fecha', text='Fecha Inicio')

        self.tree_proyectos.column('Número', width=100)
        self.tree_proyectos.column('Nombre', width=200)
        self.tree_proyectos.column('Cliente', width=150)
        self.tree_proyectos.column('Ubicación', width=150)
        self.tree_proyectos.column('Responsable', width=120)
        self.tree_proyectos.column('Estado', width=120)
        self.tree_proyectos.column('Total', width=120)
        self.tree_proyectos.column('Fecha', width=100)

        self.tree_proyectos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_proyectos.yview)

        # Doble click para ver detalle
        self.tree_proyectos.bind('<Double-1>', self.ver_detalle_proyecto)

        # Clic derecho para menú contextual
        self.tree_proyectos.bind('<Button-3>', self.mostrar_menu_proyecto)

        # Cargar datos
        self.cargar_proyectos()

    def crear_tab_clientes(self):
        """Pestaña de Clientes"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  Clientes  ')

        # Frame superior con título y botón
        top_frame = tk.Frame(tab, bg='white')
        top_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_frame,
            text="Gestión de Clientes",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            top_frame,
            text="+ Nuevo Cliente",
            font=("Arial", 11, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.nuevo_cliente
        ).pack(side=tk.RIGHT)

        # Tabla de clientes
        self.crear_tabla_clientes(tab)

    def crear_tabla_clientes(self, parent):
        """Crea la tabla para mostrar clientes"""
        # Frame con scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview (tabla)
        columns = ('ID', 'Empresa', 'Contacto', 'Telefono', 'Email', 'Direccion')
        self.tree_clientes = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set
        )

        # Configurar columnas
        self.tree_clientes.heading('ID', text='ID')
        self.tree_clientes.heading('Empresa', text='Empresa')
        self.tree_clientes.heading('Contacto', text='Contacto')
        self.tree_clientes.heading('Telefono', text='Telefono')
        self.tree_clientes.heading('Email', text='Email')
        self.tree_clientes.heading('Direccion', text='Direccion')

        self.tree_clientes.column('ID', width=50)
        self.tree_clientes.column('Empresa', width=250)
        self.tree_clientes.column('Contacto', width=200)
        self.tree_clientes.column('Telefono', width=120)
        self.tree_clientes.column('Email', width=200)
        self.tree_clientes.column('Direccion', width=250)

        self.tree_clientes.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_clientes.yview)

        # Doble click para editar
        self.tree_clientes.bind('<Double-1>', self.editar_cliente)

        # Cargar datos desde BD
        self.cargar_clientes()

    def cargar_clientes(self):
        """Carga los clientes desde la base de datos"""
        # Limpiar tabla
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        try:
            query = """
                SELECT id_cliente, nombre_empresa, contacto_nombre,
                       telefono, email, direccion
                FROM clientes
                WHERE activo = 1
                ORDER BY nombre_empresa
            """
            result = self.db.ejecutar_query(query)

            # Insertar en la tabla
            for row in result.fetchall():
                self.tree_clientes.insert('', 'end', values=row)

        except Exception as e:
            print(f"Error al cargar clientes: {e}")

    def crear_tab_productos(self):
        """Pestaña de Productos/Equipos"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  Productos/Equipos  ')

        # Frame superior con título y botones
        top_frame = tk.Frame(tab, bg='white')
        top_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_frame,
            text="Catálogo de Equipos HVAC",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        # Botones
        btn_frame = tk.Frame(top_frame, bg='white')
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(
            btn_frame,
            text="+ Nuevo Equipo",
            font=("Arial", 10, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.nuevo_equipo
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Importar Excel",
            font=("Arial", 10, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.importar_excel
        ).pack(side=tk.LEFT, padx=5)

        # Tabla de equipos
        self.crear_tabla_productos(tab)

    def crear_tabla_productos(self, parent):
        """Crea la tabla para mostrar productos/equipos"""
        # Frame con scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview (tabla)
        columns = ('ID', 'Nombre', 'Categoría', 'Horas Mant.', 'Precio/Hora')
        self.tree_productos = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set
        )

        # Configurar columnas
        self.tree_productos.heading('ID', text='ID')
        self.tree_productos.heading('Nombre', text='Nombre del Equipo')
        self.tree_productos.heading('Categoría', text='Categoría')
        self.tree_productos.heading('Horas Mant.', text='Horas Mant.')
        self.tree_productos.heading('Precio/Hora', text='Precio/Hora')

        self.tree_productos.column('ID', width=50)
        self.tree_productos.column('Nombre', width=400)
        self.tree_productos.column('Categoría', width=200)
        self.tree_productos.column('Horas Mant.', width=100)
        self.tree_productos.column('Precio/Hora', width=100)

        self.tree_productos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_productos.yview)

        # Doble click para editar
        self.tree_productos.bind('<Double-1>', self.editar_equipo)

        # Cargar datos desde BD
        self.cargar_productos()

    def cargar_equipos(self):
        """Alias para cargar_productos - mantiene compatibilidad"""
        self.cargar_productos()

    def cargar_productos(self):
        """Carga los productos desde la base de datos"""
        # Limpiar tabla
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        try:
            # Obtener configuración para precio por hora
            costo_hora = float(self.db.obtener_configuracion('costo_hora_tecnico') or 15)

            query = """
                SELECT id_equipo, tipo_equipo, categoria, horas_mantenimiento
                FROM productos_equipos
                WHERE activo = 1
                ORDER BY categoria, tipo_equipo
            """
            result = self.db.ejecutar_query(query)

            # Insertar en la tabla
            for row in result.fetchall():
                id_equipo, nombre, categoria, horas = row
                precio_hora = horas * costo_hora
                self.tree_productos.insert('', 'end', values=(
                    id_equipo,
                    nombre,
                    categoria,
                    f"{horas:.1f}h",
                    f"${precio_hora:.2f}"
                ))

        except Exception as e:
            print(f"Error al cargar productos: {e}")

    def crear_tab_materiales(self):
        """Pestaña de Materiales"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  Materiales  ')

        # Frame superior con título y botón
        top_frame = tk.Frame(tab, bg='white')
        top_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_frame,
            text="Materiales y Repuestos",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            top_frame,
            text="+ Nuevo Material",
            font=("Arial", 10, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.nuevo_material
        ).pack(side=tk.RIGHT)

        # Tabla de materiales
        self.crear_tabla_materiales(tab)

    def crear_tabla_materiales(self, parent):
        """Crea la tabla para mostrar materiales"""
        # Frame con scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview (tabla)
        columns = ('ID', 'Nombre', 'Precio')
        self.tree_materiales = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set
        )

        # Configurar columnas
        self.tree_materiales.heading('ID', text='ID')
        self.tree_materiales.heading('Nombre', text='Nombre del Material')
        self.tree_materiales.heading('Precio', text='Precio')

        self.tree_materiales.column('ID', width=80)
        self.tree_materiales.column('Nombre', width=600)
        self.tree_materiales.column('Precio', width=150)

        self.tree_materiales.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_materiales.yview)

        # Doble click para editar
        self.tree_materiales.bind('<Double-1>', self.editar_material)

        # Cargar datos desde BD
        self.cargar_materiales()

    def cargar_materiales(self):
        """Carga los materiales desde la base de datos"""
        # Limpiar tabla
        for item in self.tree_materiales.get_children():
            self.tree_materiales.delete(item)

        try:
            query = """
                SELECT id_material, nombre_material, precio_unitario
                FROM materiales_repuestos
                WHERE activo = 1
                ORDER BY nombre_material
            """
            result = self.db.ejecutar_query(query)

            # Insertar en la tabla
            for row in result.fetchall():
                id_material, nombre, precio = row
                self.tree_materiales.insert('', 'end', values=(
                    id_material,
                    nombre,
                    f"${precio:.2f}" if precio else "N/A"
                ))

        except Exception as e:
            print(f"Error al cargar materiales: {e}")

    def crear_tab_configuracion(self):
        """Pestaña de Configuración"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  Configuración  ')

        # Frame principal con padding y scrollbar
        main_container = tk.Frame(tab, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=40, pady=30)
        scrollbar.pack(side="right", fill="y")

        # Frame de configuración
        config_frame = scrollable_frame

        tk.Label(
            config_frame,
            text="Configuración General del Sistema",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(anchor=tk.W, pady=(0, 10))

        tk.Label(
            config_frame,
            text="Personaliza los parámetros de cálculo y facturación",
            font=("Arial", 10),
            bg='white',
            fg='#666'
        ).pack(anchor=tk.W, pady=(0, 30))

        # --- SECCIÓN: COSTOS Y PRECIOS ---
        tk.Label(
            config_frame,
            text="Costos y Precios",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2563eb'
        ).pack(anchor=tk.W, pady=(10, 15))

        form1 = tk.Frame(config_frame, bg='white')
        form1.pack(fill=tk.X, pady=(0, 20))

        # Factor de venta
        self.crear_campo_config(form1, "Factor de Venta:", "factor_venta", 0,
            "Multiplicador de precio sobre el costo base")

        # IVA
        self.crear_campo_config(form1, "IVA (%):", "iva", 1,
            "Impuesto sobre el valor agregado")

        # Tipo de cambio
        self.crear_campo_config(form1, "Tipo de Cambio (₡/$):", "tipo_cambio", 2,
            "Conversión de dólares a colones")

        # Costo hora técnico
        self.crear_campo_config(form1, "Costo Hora Técnico ($):", "costo_hora_tecnico", 3,
            "Precio por hora de mano de obra")

        # --- SECCIÓN: INS Y CCSS ---
        tk.Label(
            config_frame,
            text="Cargas Sociales (INS/CCSS)",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2563eb'
        ).pack(anchor=tk.W, pady=(20, 15))

        form2 = tk.Frame(config_frame, bg='white')
        form2.pack(fill=tk.X, pady=(0, 20))

        # Porcentaje INS/CCSS
        self.crear_campo_config(form2, "Porcentaje INS/CCSS (%):", "porcentaje_ins_ccss", 0,
            "Usualmente 35% sobre mano de obra")

        # Checkbox para incluir por defecto
        checkbox_frame = tk.Frame(form2, bg='white')
        checkbox_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=15)

        self.incluir_ins_ccss_var = tk.BooleanVar()
        tk.Checkbutton(
            checkbox_frame,
            text="Incluir INS/CCSS por defecto en nuevas cotizaciones",
            variable=self.incluir_ins_ccss_var,
            font=("Arial", 10),
            bg='white'
        ).pack(side=tk.LEFT)

        # Cargar valor de checkbox
        valor_checkbox = self.db.obtener_configuracion('incluir_ins_ccss_defecto')
        if valor_checkbox and valor_checkbox == '1':
            self.incluir_ins_ccss_var.set(True)

        # --- SECCIÓN: INFORMACIÓN DE EMPRESA ---
        tk.Label(
            config_frame,
            text="Información de la Empresa",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2563eb'
        ).pack(anchor=tk.W, pady=(20, 15))

        form3 = tk.Frame(config_frame, bg='white')
        form3.pack(fill=tk.X, pady=(0, 20))

        # Nombre empresa
        self.crear_campo_config(form3, "Nombre Empresa:", "nombre_empresa", 0,
            "Aparece en PDFs y documentos")

        # Teléfono
        self.crear_campo_config(form3, "Teléfono:", "telefono_empresa", 1,
            "Teléfono de contacto")

        # Email
        self.crear_campo_config(form3, "Email:", "email_empresa", 2,
            "Correo electrónico de contacto")

        # Dirección
        self.crear_campo_config(form3, "Dirección:", "direccion_empresa", 3,
            "Dirección física de la empresa")

        # --- SECCIÓN: CONFIGURACIÓN DE EMAIL ---
        tk.Label(
            config_frame,
            text="Configuración de Email (para envío de cotizaciones)",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2563eb'
        ).pack(anchor=tk.W, pady=(20, 15))

        form4 = tk.Frame(config_frame, bg='white')
        form4.pack(fill=tk.X, pady=(0, 20))

        # Servidor SMTP
        self.crear_campo_config(form4, "Servidor SMTP:", "smtp_server", 0,
            "Ej: smtp.gmail.com")

        # Puerto SMTP
        self.crear_campo_config(form4, "Puerto SMTP:", "smtp_port", 1,
            "Puerto del servidor (ej: 587 para TLS)")

        # Email remitente
        self.crear_campo_config(form4, "Email Remitente:", "email_remitente", 2,
            "Email desde el cual se enviarán las cotizaciones")

        # Contraseña de email
        label_pass = tk.Label(
            form4,
            text="Contraseña de Email:",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#666'
        )
        label_pass.grid(row=3, column=0, sticky=tk.W, pady=15)

        # Entry de contraseña (oculta) - DESENCRIPTADA para mostrar
        self.email_password_var = tk.StringVar()
        valor_pass_encriptado = self.db.obtener_configuracion('email_password')
        if valor_pass_encriptado:
            # Desencriptar contraseña para mostrar en el campo
            valor_pass = desencriptar_password(valor_pass_encriptado)
            self.email_password_var.set(valor_pass)

        entry_pass = tk.Entry(
            form4,
            textvariable=self.email_password_var,
            font=("Arial", 11),
            width=40,
            show="*"  # Ocultar contraseña
        )
        entry_pass.grid(row=3, column=1, sticky=tk.W, pady=15, padx=(0, 10))

        tk.Label(
            form4,
            text="Para Gmail, usa 'App Password' en vez de tu contraseña normal",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Nombre del remitente
        self.crear_campo_config(form4, "Nombre Remitente:", "email_nombre", 5,
            "Nombre que aparecerá como remitente")

        # Botón probar conexión
        test_btn_frame = tk.Frame(form4, bg='white')
        test_btn_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=15)

        tk.Button(
            test_btn_frame,
            text="🔌 Probar Conexión Email",
            font=("Arial", 10),
            bg='#8b5cf6',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.probar_conexion_email
        ).pack(side=tk.LEFT)

        # Botón guardar
        btn_frame = tk.Frame(config_frame, bg='white')
        btn_frame.pack(fill=tk.X, pady=(30, 20))

        tk.Button(
            btn_frame,
            text="Guardar Configuración",
            font=("Arial", 12, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=40,
            pady=12,
            command=self.guardar_configuracion
        ).pack(side=tk.LEFT)

        tk.Label(
            btn_frame,
            text="Los cambios se aplicarán a las nuevas cotizaciones",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).pack(side=tk.LEFT, padx=20)

    def crear_campo_config(self, parent, label, clave, row, descripcion=""):
        """Crea un campo de configuración"""
        # Label principal
        tk.Label(
            parent,
            text=label,
            font=("Arial", 11, "bold"),
            bg='white'
        ).grid(row=row, column=0, sticky=tk.W, pady=(15, 5), padx=(0, 20))

        # Entry
        entry = tk.Entry(
            parent,
            font=("Arial", 11),
            width=40,
            relief=tk.SOLID,
            bd=1
        )
        entry.grid(row=row, column=1, sticky=tk.W, pady=(15, 5), ipady=3)

        # Descripción si existe
        if descripcion:
            tk.Label(
                parent,
                text=descripcion,
                font=("Arial", 9),
                bg='white',
                fg='#666'
            ).grid(row=row, column=2, sticky=tk.W, pady=(15, 5), padx=(10, 0))

        # Cargar valor desde BD
        valor = self.db.obtener_configuracion(clave)
        if valor:
            entry.insert(0, valor)

        # Guardar referencia
        setattr(self, f'entry_{clave}', entry)

    # --- MÉTODOS DE ACCIONES ---

    def cargar_cotizaciones(self):
        """Carga las cotizaciones desde la base de datos"""
        # Limpiar tabla
        for item in self.tree_cotizaciones.get_children():
            self.tree_cotizaciones.delete(item)

        # Consultar base de datos
        try:
            query = """
                SELECT c.numero_cotizacion, cl.nombre_empresa, c.fecha_emision, c.total, c.estado
                FROM cotizaciones c
                LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
                ORDER BY c.fecha_creacion DESC
            """
            result = self.db.ejecutar_query(query)

            # Insertar en la tabla
            for row in result.fetchall():
                self.tree_cotizaciones.insert('', 'end', values=row)

        except Exception as e:
            print(f"Error al cargar cotizaciones: {e}")

    def filtrar_cotizaciones(self):
        """Filtra cotizaciones según criterios de búsqueda"""
        # Limpiar tabla
        for item in self.tree_cotizaciones.get_children():
            self.tree_cotizaciones.delete(item)

        try:
            # Construir query con filtros
            query = """
                SELECT c.numero_cotizacion, cl.nombre_empresa, c.fecha_emision,
                       c.total, c.estado
                FROM cotizaciones c
                LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
                WHERE 1=1
            """
            params = []

            # Filtro por texto de búsqueda (número o cliente)
            texto_busqueda = self.search_var.get().strip()
            if texto_busqueda:
                query += " AND (c.numero_cotizacion LIKE ? OR cl.nombre_empresa LIKE ?)"
                params.extend([f'%{texto_busqueda}%', f'%{texto_busqueda}%'])

            # Filtro por estado
            estado_filtro = self.filtro_estado_var.get()
            if estado_filtro != "Todos":
                query += " AND c.estado = ?"
                params.append(estado_filtro)

            # Filtro por fecha
            mes_filtro = self.filtro_mes_var.get()
            if mes_filtro != "Todos":
                from datetime import datetime, timedelta
                hoy = datetime.now()

                if mes_filtro == "Este mes":
                    inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
                    query += " AND c.fecha >= ?"
                    params.append(inicio)

                elif mes_filtro == "Último mes":
                    fin_mes_pasado = hoy.replace(day=1) - timedelta(days=1)
                    inicio_mes_pasado = fin_mes_pasado.replace(day=1)
                    query += " AND c.fecha >= ? AND c.fecha <= ?"
                    params.extend([inicio_mes_pasado.strftime('%Y-%m-%d'),
                                 fin_mes_pasado.strftime('%Y-%m-%d')])

                elif mes_filtro == "Últimos 3 meses":
                    inicio = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
                    query += " AND c.fecha >= ?"
                    params.append(inicio)

                elif mes_filtro == "Últimos 6 meses":
                    inicio = (hoy - timedelta(days=180)).strftime('%Y-%m-%d')
                    query += " AND c.fecha >= ?"
                    params.append(inicio)

                elif mes_filtro == "Este año":
                    inicio = hoy.replace(month=1, day=1).strftime('%Y-%m-%d')
                    query += " AND c.fecha >= ?"
                    params.append(inicio)

            query += " ORDER BY c.fecha DESC, c.numero_cotizacion DESC"

            # Ejecutar query
            result = self.db.ejecutar_query(query, tuple(params))

            # Insertar resultados en la tabla
            for row in result.fetchall():
                # Formatear total como moneda
                numero, cliente, fecha, total, estado = row
                total_fmt = f"${total:,.2f}" if total else "$0.00"
                self.tree_cotizaciones.insert('', 'end',
                    values=(numero, cliente, fecha, total_fmt, estado))

        except Exception as e:
            print(f"Error al filtrar cotizaciones: {e}")
            import traceback
            traceback.print_exc()

    def limpiar_filtros(self):
        """Limpia todos los filtros y recarga cotizaciones"""
        self.search_var.set("")
        self.filtro_estado_var.set("Todos")
        self.filtro_mes_var.set("Todos")
        self.cargar_cotizaciones()

    def nueva_cotizacion(self):
        """Abre ventana para crear nueva cotización"""
        from views.nueva_cotizacion_window import NuevaCotizacionWindow
        NuevaCotizacionWindow(self)

    def ver_detalle_cotizacion(self, event):
        """Ver detalle de cotización al hacer doble click"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        # Obtener número de cotización de la fila seleccionada
        item = self.tree_cotizaciones.item(selection[0])
        numero_cotizacion = item['values'][0]

        # Abrir ventana de detalle
        from views.detalle_cotizacion_window import DetalleCotizacionWindow
        DetalleCotizacionWindow(self, numero_cotizacion)

    def mostrar_menu_cotizacion(self, event):
        """Muestra menú contextual al hacer clic derecho en una cotización"""
        # Seleccionar el item donde se hizo clic
        item = self.tree_cotizaciones.identify_row(event.y)
        if item:
            self.tree_cotizaciones.selection_set(item)

            # Obtener datos de la cotización seleccionada
            item_data = self.tree_cotizaciones.item(item)
            estado = item_data['values'][4]  # Estado está en columna 4

            # Crear menú contextual
            menu = tk.Menu(self.tree_cotizaciones, tearoff=0)

            menu.add_command(
                label="Ver Detalle",
                command=lambda: self.ver_detalle_cotizacion(None)
            )

            menu.add_separator()

            # Opciones según el estado
            if estado == 'pendiente':
                menu.add_command(
                    label="Aprobar Cotización",
                    command=self.aprobar_cotizacion
                )
                menu.add_command(
                    label="Rechazar Cotización",
                    command=self.rechazar_cotizacion
                )
                menu.add_command(
                    label="Marcar como Vencida",
                    command=self.marcar_vencida_cotizacion
                )

            menu.add_separator()
            menu.add_command(
                label="Eliminar Cotización",
                command=self.eliminar_cotizacion
            )

            # Mostrar menú en la posición del cursor
            menu.post(event.x_root, event.y_root)

    def aprobar_cotizacion(self):
        """Marca una cotización como aprobada"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        item = self.tree_cotizaciones.item(selection[0])
        numero_cotizacion = item['values'][0]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Aprobar la cotización {numero_cotizacion}?"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE cotizaciones SET estado = 'aprobada' WHERE numero_cotizacion = ?",
                    (numero_cotizacion,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Cotización aprobada correctamente")
                self.cargar_cotizaciones()
                self.actualizar_dashboard()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aprobar la cotización:\n{e}")

    def rechazar_cotizacion(self):
        """Marca una cotización como rechazada"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        item = self.tree_cotizaciones.item(selection[0])
        numero_cotizacion = item['values'][0]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Rechazar la cotización {numero_cotizacion}?"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE cotizaciones SET estado = 'rechazada' WHERE numero_cotizacion = ?",
                    (numero_cotizacion,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Cotización rechazada")
                self.cargar_cotizaciones()
                self.actualizar_dashboard()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo rechazar la cotización:\n{e}")

    def marcar_vencida_cotizacion(self):
        """Marca una cotización como vencida"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        item = self.tree_cotizaciones.item(selection[0])
        numero_cotizacion = item['values'][0]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Marcar como vencida la cotización {numero_cotizacion}?"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE cotizaciones SET estado = 'vencida' WHERE numero_cotizacion = ?",
                    (numero_cotizacion,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Cotización marcada como vencida")
                self.cargar_cotizaciones()
                self.actualizar_dashboard()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo marcar como vencida:\n{e}")

    def eliminar_cotizacion(self):
        """Elimina una cotización y sus detalles"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        item = self.tree_cotizaciones.item(selection[0])
        numero_cotizacion = item['values'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la cotización {numero_cotizacion}?\n\nEsta acción no se puede deshacer."
        ):
            try:
                # Primero eliminar los detalles
                self.db.cursor.execute(
                    "DELETE FROM detalle_cotizacion WHERE id_cotizacion = (SELECT id_cotizacion FROM cotizaciones WHERE numero_cotizacion = ?)",
                    (numero_cotizacion,)
                )

                # Luego eliminar la cotización
                self.db.cursor.execute(
                    "DELETE FROM cotizaciones WHERE numero_cotizacion = ?",
                    (numero_cotizacion,)
                )

                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Cotización eliminada correctamente")
                self.cargar_cotizaciones()
                self.actualizar_dashboard()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la cotización:\n{e}")

    def nuevo_cliente(self):
        """Abre ventana para crear nuevo cliente"""
        from views.nuevo_cliente_window import NuevoClienteWindow
        NuevoClienteWindow(self)

    def editar_cliente(self, event):
        """Edita un cliente al hacer doble click"""
        selection = self.tree_clientes.selection()
        if not selection:
            return

        item = self.tree_clientes.item(selection[0])
        id_cliente = item['values'][0]

        from views.editar_cliente_window import EditarClienteWindow
        EditarClienteWindow(self, id_cliente)

    def nuevo_equipo(self):
        """Abre ventana para agregar nuevo equipo"""
        from views.nuevo_equipo_window import NuevoEquipoWindow
        NuevoEquipoWindow(self)

    def nuevo_material(self):
        """Abre ventana para agregar nuevo material"""
        from views.nuevo_material_window import NuevoMaterialWindow
        NuevoMaterialWindow(self)

    def editar_equipo(self, event):
        """Edita un equipo al hacer doble click"""
        selection = self.tree_productos.selection()
        if not selection:
            return

        # Obtener ID del equipo
        item = self.tree_productos.item(selection[0])
        id_equipo = item['values'][0]

        # Abrir ventana de edición
        from views.editar_equipo_window import EditarEquipoWindow
        EditarEquipoWindow(self, id_equipo)

    def editar_material(self, event):
        """Edita un material al hacer doble click"""
        selection = self.tree_materiales.selection()
        if not selection:
            return

        # Obtener ID del material
        item = self.tree_materiales.item(selection[0])
        id_material = item['values'][0]

        # Abrir ventana de edición
        from views.editar_material_window import EditarMaterialWindow
        EditarMaterialWindow(self, id_material)

    def importar_excel(self):
        """Importa datos desde el Excel"""
        messagebox.showinfo("Próximamente", "Importador de Excel en desarrollo")

    def guardar_configuracion(self):
        """Guarda la configuración en la base de datos"""
        try:
            # Guardar cada campo
            configs = [
                'factor_venta', 'iva', 'tipo_cambio', 'costo_hora_tecnico',
                'porcentaje_ins_ccss', 'nombre_empresa', 'telefono_empresa',
                'email_empresa', 'direccion_empresa',
                'smtp_server', 'smtp_port', 'email_remitente', 'email_nombre'
            ]

            for config in configs:
                entry = getattr(self, f'entry_{config}', None)
                if entry:
                    valor = entry.get().strip()
                    self.db.actualizar_configuracion(config, valor)

            # Guardar contraseña de email ENCRIPTADA
            if hasattr(self, 'email_password_var'):
                valor_pass = self.email_password_var.get().strip()
                if valor_pass:
                    # Encriptar antes de guardar
                    valor_pass_encriptado = encriptar_password(valor_pass)
                    self.db.actualizar_configuracion('email_password', valor_pass_encriptado)

            # Guardar checkbox de INS/CCSS
            incluir_ins = '1' if self.incluir_ins_ccss_var.get() else '0'
            self.db.actualizar_configuracion('incluir_ins_ccss_defecto', incluir_ins)

            messagebox.showinfo("Éxito", "Configuración guardada correctamente")

        except Exception as e:
            print(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"Error al guardar configuración:\n{e}")

    def probar_conexion_email(self):
        """Prueba la conexión con el servidor SMTP"""
        try:
            from utils.email_manager import EmailManager

            # Crear EmailManager con configuración actual
            email_manager = EmailManager(self.db)

            # Actualizar con valores actuales del formulario
            smtp_server = getattr(self, 'entry_smtp_server', None)
            smtp_port = getattr(self, 'entry_smtp_port', None)
            email_remitente = getattr(self, 'entry_email_remitente', None)
            email_nombre = getattr(self, 'entry_email_nombre', None)

            if smtp_server and smtp_port and email_remitente:
                email_manager.configurar_smtp(
                    smtp_server.get().strip(),
                    int(smtp_port.get().strip()) if smtp_port.get().strip() else 587,
                    email_remitente.get().strip(),
                    self.email_password_var.get().strip(),
                    email_nombre.get().strip() if email_nombre else "AirSolutions"
                )

                # Probar conexión
                exito, mensaje = email_manager.probar_conexion()

                if exito:
                    messagebox.showinfo("Conexión Exitosa", mensaje)
                else:
                    messagebox.showerror("Error de Conexión", mensaje)
            else:
                messagebox.showwarning(
                    "Campos Incompletos",
                    "Completa los campos de servidor SMTP, puerto y email remitente"
                )

        except Exception as e:
            print(f"Error probando conexión: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al probar conexión:\n{e}")

    def crear_tab_respaldos(self):
        """Pestaña de Respaldos"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='  💾 Respaldos  ')

        # Header
        header = tk.Frame(tab, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header,
            text="Sistema de Respaldos",
            font=("Arial", 20, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        # Botones de acción
        btn_frame = tk.Frame(header, bg='white')
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(
            btn_frame,
            text="✨ Crear Respaldo",
            font=("Arial", 11, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.crear_backup_manual
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="🔄 Actualizar",
            font=("Arial", 11),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.cargar_lista_backups
        ).pack(side=tk.LEFT)

        # Contenedor principal
        main_container = tk.Frame(tab, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Info del sistema
        info_frame = tk.Frame(main_container, bg='#f3f4f6', relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            info_frame,
            text="ℹ️ Los respaldos se guardan en formato ZIP comprimido. "
                 "Puedes restaurar cualquier respaldo anterior haciendo doble clic sobre él.",
            font=("Arial", 10),
            bg='#f3f4f6',
            fg='#666',
            wraplength=800,
            justify=tk.LEFT
        ).pack(padx=15, pady=15)

        # Tabla de respaldos
        table_frame = tk.Frame(main_container, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # TreeView
        columns = ('Archivo', 'Fecha Creación', 'Tamaño (MB)', 'Ruta')
        self.tree_backups = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )

        # Configurar columnas
        self.tree_backups.heading('Archivo', text='Archivo')
        self.tree_backups.heading('Fecha Creación', text='Fecha Creación')
        self.tree_backups.heading('Tamaño (MB)', text='Tamaño (MB)')
        self.tree_backups.heading('Ruta', text='Ruta')

        self.tree_backups.column('Archivo', width=300)
        self.tree_backups.column('Fecha Creación', width=180)
        self.tree_backups.column('Tamaño (MB)', width=120)
        self.tree_backups.column('Ruta', width=400)

        self.tree_backups.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_backups.yview)

        # Eventos
        self.tree_backups.bind('<Double-1>', self.restaurar_backup_seleccionado)

        # Botones inferiores
        bottom_frame = tk.Frame(main_container, bg='white')
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(
            bottom_frame,
            text="🔄 Restaurar Seleccionado",
            font=("Arial", 11),
            bg='#f59e0b',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.restaurar_backup_seleccionado
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            bottom_frame,
            text="🗑️ Eliminar Seleccionado",
            font=("Arial", 11),
            bg='#ef4444',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.eliminar_backup_seleccionado
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            bottom_frame,
            text="🧹 Limpiar Antiguos (30+ días)",
            font=("Arial", 11),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.limpiar_backups_antiguos
        ).pack(side=tk.LEFT)

        # Inicializar backup manager
        from utils.backup_manager import BackupManager
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'models', 'airsolutions.db'
        )
        self.backup_manager = BackupManager(db_path)

        # Cargar lista de backups
        self.cargar_lista_backups()

    def cargar_lista_backups(self):
        """Carga la lista de respaldos disponibles"""
        # Limpiar tabla
        for item in self.tree_backups.get_children():
            self.tree_backups.delete(item)

        # Cargar backups
        backups = self.backup_manager.listar_backups()

        for nombre, fecha, tamaño_mb, ruta in backups:
            fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
            self.tree_backups.insert('', 'end', values=(
                nombre,
                fecha_str,
                f"{tamaño_mb:.2f}",
                ruta
            ))

    def crear_backup_manual(self):
        """Crea un respaldo manual"""
        # Pedir descripción opcional
        dialog = tk.Toplevel(self.root)
        dialog.title("Crear Respaldo")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f'400x200+{x}+{y}')

        tk.Label(
            dialog,
            text="Crear Nuevo Respaldo",
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        tk.Label(
            dialog,
            text="Descripción (opcional):",
            font=("Arial", 10)
        ).pack(pady=(0, 5))

        desc_var = tk.StringVar()
        tk.Entry(
            dialog,
            textvariable=desc_var,
            font=("Arial", 11),
            width=35
        ).pack(pady=(0, 20))

        def ejecutar_backup():
            descripcion = desc_var.get().strip()
            dialog.destroy()

            # Mostrar mensaje de espera
            exito, resultado = self.backup_manager.crear_backup(descripcion)

            if exito:
                messagebox.showinfo(
                    "Éxito",
                    f"Respaldo creado correctamente:\n{os.path.basename(resultado)}"
                )
                self.cargar_lista_backups()
            else:
                messagebox.showerror("Error", resultado)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="Crear Respaldo",
            font=("Arial", 11, "bold"),
            bg='#10b981',
            fg='white',
            padx=20,
            pady=8,
            command=ejecutar_backup
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancelar",
            font=("Arial", 11),
            bg='#6b7280',
            fg='white',
            padx=20,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def restaurar_backup_seleccionado(self, event=None):
        """Restaura el respaldo seleccionado"""
        selection = self.tree_backups.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un respaldo para restaurar")
            return

        item = self.tree_backups.item(selection[0])
        ruta_backup = item['values'][3]
        nombre_backup = item['values'][0]

        if messagebox.askyesno(
            "Confirmar Restauración",
            f"¿Estás seguro de restaurar este respaldo?\n\n{nombre_backup}\n\n"
            "Se creará un respaldo de seguridad de la base de datos actual antes de restaurar.\n\n"
            "⚠️ La aplicación se cerrará después de la restauración."
        ):
            # Desconectar base de datos actual
            self.db.desconectar()

            # Restaurar
            exito, mensaje = self.backup_manager.restaurar_backup(ruta_backup)

            if exito:
                messagebox.showinfo(
                    "Éxito",
                    f"Respaldo restaurado correctamente.\n\n{mensaje}\n\n"
                    "La aplicación se cerrará. Por favor, vuelve a abrirla."
                )
                self.root.destroy()
            else:
                messagebox.showerror("Error", mensaje)
                # Reconectar base de datos
                self.db.conectar()

    def eliminar_backup_seleccionado(self):
        """Elimina el respaldo seleccionado"""
        selection = self.tree_backups.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un respaldo para eliminar")
            return

        item = self.tree_backups.item(selection[0])
        ruta_backup = item['values'][3]
        nombre_backup = item['values'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este respaldo?\n\n{nombre_backup}\n\n"
            "Esta acción no se puede deshacer."
        ):
            exito, mensaje = self.backup_manager.eliminar_backup(ruta_backup)

            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_lista_backups()
            else:
                messagebox.showerror("Error", mensaje)

    def limpiar_backups_antiguos(self):
        """Limpia respaldos antiguos (30+ días)"""
        if messagebox.askyesno(
            "Confirmar Limpieza",
            "¿Deseas eliminar todos los respaldos con más de 30 días de antigüedad?\n\n"
            "Esta acción no se puede deshacer."
        ):
            cantidad, mensaje = self.backup_manager.limpiar_backups_antiguos(30)

            messagebox.showinfo("Limpieza Completada", mensaje)
            self.cargar_lista_backups()

    # ===== MÉTODOS PARA PROYECTOS =====

    def cargar_proyectos(self):
        """Carga los proyectos en la tabla"""
        # Limpiar tabla
        for item in self.tree_proyectos.get_children():
            self.tree_proyectos.delete(item)

        # Construir query
        query = '''
            SELECT
                p.id_proyecto, p.numero_proyecto, p.nombre_proyecto,
                c.nombre_empresa, p.ubicacion, p.responsable,
                p.estado, p.total_proyecto, p.fecha_inicio
            FROM proyectos p
            LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE 1=1
        '''

        params = []

        # Filtro de búsqueda
        buscar = self.buscar_proyecto_var.get().strip()
        if buscar:
            query += ''' AND (
                p.numero_proyecto LIKE ? OR
                p.nombre_proyecto LIKE ? OR
                c.nombre_empresa LIKE ? OR
                p.ubicacion LIKE ?
            )'''
            buscar_param = f'%{buscar}%'
            params.extend([buscar_param, buscar_param, buscar_param, buscar_param])

        # Filtro de estado
        estado = self.filtro_estado_proyecto_var.get()
        if estado != 'todos':
            query += ' AND p.estado = ?'
            params.append(estado)

        query += ' ORDER BY p.fecha_creacion DESC'

        # Ejecutar query
        cursor = self.db.ejecutar_query(query, params if params else None)
        proyectos = cursor.fetchall()

        # Insertar en tabla
        for proyecto in proyectos:
            id_proyecto, numero, nombre, cliente, ubicacion, responsable, estado, total, fecha = proyecto

            # Formatear valores
            cliente_str = cliente or '-'
            ubicacion_str = ubicacion or '-'
            responsable_str = responsable or '-'

            # Traducir estado
            estados_traduccion = {
                'en_planificacion': 'En Planificación',
                'en_curso': 'En Curso',
                'pausado': 'Pausado',
                'completado': 'Completado',
                'cancelado': 'Cancelado'
            }
            estado_str = estados_traduccion.get(estado, estado)

            total_str = f'${total:,.2f}' if total else '$0.00'
            fecha_str = fecha or '-'

            self.tree_proyectos.insert('', 'end', values=(
                numero, nombre, cliente_str, ubicacion_str,
                responsable_str, estado_str, total_str, fecha_str
            ), tags=(id_proyecto,))

    def nuevo_proyecto(self):
        """Abre ventana para crear nuevo proyecto"""
        from views.nuevo_proyecto_window import NuevoProyectoWindow
        ventana = NuevoProyectoWindow(self.root, self.db)
        self.root.wait_window(ventana.dialog)
        self.cargar_proyectos()

    def ver_detalle_proyecto(self, event=None):
        """Muestra ventana de detalle del proyecto"""
        selection = self.tree_proyectos.selection()
        if not selection:
            return

        # Obtener id del proyecto
        item = self.tree_proyectos.item(selection[0])
        id_proyecto = item['tags'][0]

        # Abrir ventana de detalle
        from views.detalle_proyecto_window import DetalleProyectoWindow
        ventana = DetalleProyectoWindow(self.root, self.db, id_proyecto)
        self.root.wait_window(ventana.dialog)
        self.cargar_proyectos()

    def mostrar_menu_proyecto(self, event):
        """Muestra menú contextual para proyectos"""
        selection = self.tree_proyectos.selection()
        if not selection:
            return

        # Crear menú
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📄 Ver Detalle", command=self.ver_detalle_proyecto)
        menu.add_separator()
        menu.add_command(label="📊 Exportar a Excel", command=self.exportar_proyecto_excel)
        menu.add_command(label="📥 Importar desde Excel", command=self.importar_proyecto_excel)
        menu.add_separator()
        menu.add_command(label="📎 Gestionar Archivos", command=self.gestionar_archivos_proyecto)
        menu.add_separator()
        menu.add_command(label="🗑️ Eliminar Proyecto", command=self.eliminar_proyecto)

        # Mostrar menú
        menu.post(event.x_root, event.y_root)

    def exportar_proyecto_excel(self):
        """Exporta proyecto a Excel"""
        selection = self.tree_proyectos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un proyecto para exportar")
            return

        item = self.tree_proyectos.item(selection[0])
        id_proyecto = item['tags'][0]

        try:
            from utils.excel_manager import ExcelManager
            excel_manager = ExcelManager(self.db)

            ruta = excel_manager.exportar_proyecto(id_proyecto)

            if ruta:
                messagebox.showinfo(
                    "Exportación Exitosa",
                    f"Proyecto exportado a:\n{ruta}\n\n¿Deseas abrir el archivo?"
                )
                if messagebox.askyesno("Abrir Archivo", "¿Abrir el archivo Excel?"):
                    os.startfile(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar proyecto:\n{e}")

    def importar_proyecto_excel(self):
        """Importa proyecto desde Excel"""
        selection = self.tree_proyectos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un proyecto para importar")
            return

        item = self.tree_proyectos.item(selection[0])
        id_proyecto = item['tags'][0]

        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not ruta:
            return

        try:
            from utils.excel_manager import ExcelManager
            excel_manager = ExcelManager(self.db)

            exito, mensaje = excel_manager.importar_proyecto(id_proyecto, ruta)

            if exito:
                messagebox.showinfo("Importación Exitosa", mensaje)
                self.cargar_proyectos()
            else:
                messagebox.showerror("Error", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar proyecto:\n{e}")

    def gestionar_archivos_proyecto(self):
        """Abre ventana para gestionar archivos del proyecto"""
        selection = self.tree_proyectos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un proyecto")
            return

        item = self.tree_proyectos.item(selection[0])
        id_proyecto = item['tags'][0]

        from views.archivos_proyecto_window import ArchivosProyectoWindow
        ventana = ArchivosProyectoWindow(self.root, self.db, id_proyecto)
        self.root.wait_window(ventana.dialog)

    def eliminar_proyecto(self):
        """Elimina un proyecto"""
        selection = self.tree_proyectos.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona un proyecto para eliminar")
            return

        item = self.tree_proyectos.item(selection[0])
        numero_proyecto = item['values'][0]
        id_proyecto = item['tags'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar el proyecto {numero_proyecto}?\n\n"
            "Esta acción eliminará también:\n"
            "- Todos los niveles\n"
            "- Todos los items\n"
            "- Todas las referencias a archivos\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                self.db.ejecutar_query(
                    'DELETE FROM proyectos WHERE id_proyecto = ?',
                    (id_proyecto,)
                )
                messagebox.showinfo("Éxito", "Proyecto eliminado correctamente")
                self.cargar_proyectos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar proyecto:\n{e}")

    def cerrar_sesion(self):
        """Cierra sesión y vuelve al login"""
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de cerrar sesión?"):
            self.cerrar_aplicacion()
            # Volver a login
            from views.login_window import LoginWindow
            app = LoginWindow()
            app.run()

    def cerrar_aplicacion(self):
        """Cierra la aplicación correctamente"""
        self.db.desconectar()
        self.root.destroy()

    def run(self):
        """Inicia el loop principal"""
        self.root.mainloop()


if __name__ == '__main__':
    # Simular usuario para testing
    usuario_test = {
        'id': 1,
        'usuario': 'admin',
        'nombre': 'Administrador'
    }
    app = MainWindow(usuario_test)
    app.run()
