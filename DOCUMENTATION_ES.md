# Sistema de Gestión AirSolutions - Documentación

# Descripción del Proyecto

AirSolutions es un sistema integral de gestión diseñado para empresas de climatización y aires acondicionados. Maneja todo, desde pequeñas cotizaciones de servicio hasta proyectos comerciales de gran escala como hoteles y edificios de oficinas.

Este sistema fue desarrollado durante aproximadamente un año como un proyecto personal para modernizar y optimizar las operaciones comerciales de una empresa familiar de climatización.

---

# Propósito y Motivación

## El Problema

La empresa familiar de climatización enfrentaba dificultades con:
- Procesos manuales de cotización usando hojas de cálculo de Excel
- Información de clientes dispersa sin historial centralizado
- Dificultad para gestionar proyectos grandes de múltiples niveles
- Sin integración entre cotizaciones, inventario y gestión de proyectos
- Generación manual de PDFs y comunicación por email que consume mucho tiempo
- Ausencia de un sistema de respaldo confiable y seguro

## La Solución

AirSolutions proporciona:
- Generación automatizada de cotizaciones con salida profesional en PDF
- Gestión centralizada de clientes con historial completo
- Gestión de proyectos grandes con estructura jerárquica (niveles e items)
- Catálogo de componentes preconfigurado con más de 51 items
- Integración con Excel para edición externa y actualizaciones masivas
- Integración con email para entrega directa de cotizaciones
- Seguridad robusta con credenciales encriptadas y control de acceso
- Base de datos SQLite local garantizando propiedad y privacidad de datos

---

# Arquitectura del Sistema

## Stack Tecnológico

- Lenguaje: Python 3.13
- Framework GUI: Tkinter (nativo, multiplataforma)
- Base de Datos: SQLite3 (local, basada en archivos)
- Seguridad: bcrypt (hash de contraseñas), Fernet/AES-128 (encriptación)
- Generación de Documentos: ReportLab (PDF), openpyxl (Excel)
- Bibliotecas Adicionales: Pillow, matplotlib, tkcalendar

## Patrón de Arquitectura

El sistema sigue un patrón Modelo-Vista-Controlador (MVC):

```
├── models/          # Capa de datos (base de datos, lógica de negocio)
├── views/           # Capa de presentación (ventanas de interfaz)
├── utils/           # Servicios (encriptación, PDF, email, Excel)
└── main.py          # Punto de entrada de la aplicación
```

## Esquema de Base de Datos

14 tablas organizadas en tres módulos:

1. Módulo Central (2 tablas)
   - `usuarios` - Autenticación de usuarios
   - `configuracion` - Configuración del sistema

2. Módulo de Cotizaciones (7 tablas)
   - `clientes` - Información de clientes
   - `productos_equipos` - Catálogo de equipos de climatización
   - `materiales_repuestos` - Materiales y repuestos
   - `cotizaciones` - Encabezados de cotizaciones
   - `detalle_cotizacion` - Líneas de cotización (equipos)
   - `cotizacion_materiales` - Materiales de cotización
   - `gastos_adicionales` - Gastos adicionales (viáticos, transporte)

3. Módulo de Proyectos Grandes (5 tablas)
   - `catalogo_hvac` - Componentes preconfigurados (51 items)
   - `proyectos` - Encabezados de proyectos
   - `proyecto_niveles` - Niveles de proyecto (pisos, áreas)
   - `proyecto_items` - Items por nivel con costeo en 3 columnas
   - `proyecto_archivos` - Archivos vinculados (planos de AutoCAD, PDFs)

---

# Características Principales

## 1. Sistema de Gestión Dual

**Proyectos Pequeños (Cotizaciones)**
- Creación rápida de cotizaciones
- Selección de equipos y materiales desde catálogo
- Precio automático con margen e impuestos
- Generación profesional de PDFs
- Entrega por email

**Proyectos Grandes**
- Estructura jerárquica: Proyecto → Niveles → Items
- Ejemplo: Hotel con S100 (Sótano), N1 (Piso 1), N2 (Piso 2)
- Costeo en 3 columnas: Equipo, Materiales, Mano de Obra
- Totales automáticos por nivel y proyecto completo
- Exportación/importación de Excel para colaboración externa

## 2. Implementación de Seguridad

- Hash de contraseñas con bcrypt con salt automático
- Limitador de intentos de login (3 intentos, bloqueo de 5 minutos)
- Encriptación Fernet (AES-128) para credenciales de email
- Prevención de inyección SQL mediante queries parametrizadas
- Restricciones de clave foránea para integridad de datos
- Respaldos automáticos antes de migraciones de base de datos

## 3. Integración con Excel

**Exportación**: Genera archivos Excel profesionales con:
- Encabezados y totales formateados
- Secciones codificadas por color según nivel
- Precios y cantidades editables
- Fórmulas automáticas

**Importación**: Actualiza la base de datos desde archivos Excel editados:
- Lee cantidades y costos modificados
- Crea nuevos items automáticamente
- Mantiene la integridad de la estructura del proyecto

## 4. Gestión de Archivos

Vincula archivos externos a proyectos:
- Planos de AutoCAD (.dwg)
- PDFs, imágenes, especificaciones
- Asocia archivos con niveles específicos
- Abre archivos con doble clic (usa la aplicación predeterminada del sistema)

## 5. Generación de Documentos

**PDFs de Cotizaciones**:
- Logo y marca de la empresa
- Equipos y materiales detallados
- Cálculos automáticos de impuestos y margen
- Formato profesional
- Conversión de moneda (USD/CRC)

**Reportes en Excel**:
- Desglose de proyectos por nivel
- Análisis de costos (equipo/materiales/mano de obra)
- Plantillas editables

---

# Lógica de Negocio

## Modelo de Precios

```
Costo Equipo + Costo Materiales = Subtotal
Subtotal × Factor de Margen = Subtotal con Margen
Subtotal con Margen × (1 + IVA%) = Total
```

Parámetros configurables:
- Factor de margen (predeterminado: 1.5 = 50% de margen)
- Tasa de impuesto (predeterminado: 13% IVA)
- Tipo de cambio (USD a CRC)
- Tarifa por hora del técnico

## Flujo de Trabajo del Proyecto

1. Crear Proyecto → Ingresar información básica
2. Definir Niveles → Agregar S100, N1, N2, etc.
3. Agregar Items → Seleccionar del catálogo o ingreso manual
4. Exportar a Excel → Compartir con el equipo para revisión
5. Editar en Excel → Ajustar cantidades/costos
6. Importar de Vuelta → Actualizar base de datos automáticamente
7. Vincular Archivos → Adjuntar planos y especificaciones
8. Generar Cotizaciones → Crear cotizaciones individuales por área
9. Entregar → PDF + Email al cliente

---

# Proceso de Desarrollo

## Línea de Tiempo

Año 1 (2024-2025): Desarrollo completo del sistema

- Meses 1-3: Arquitectura central, diseño de base de datos, autenticación
- Meses 4-6: Módulo de cotizaciones, generación de PDFs
- Meses 7-9: Módulo de proyectos grandes, integración con Excel
- Meses 10-12: Refuerzo de seguridad, pruebas, implementación

## Desafíos Superados

1. Diseño de Base de Datos: Balancear flexibilidad vs. rendimiento para proyectos pequeños y grandes
2. Integración con Excel: Sincronización bidireccional sin pérdida de datos
3. Seguridad: Implementar seguridad de nivel empresarial en una aplicación de escritorio
4. Experiencia de Usuario: Crear una interfaz intuitiva para usuarios no técnicos
5. Gestión de Archivos: Vincular archivos externos sin copiar (mantener flujo de trabajo de AutoCAD)

## Aprendizajes Clave

- SQLite es lo suficientemente potente para aplicaciones de PYMES
- Tkinter puede crear interfaces profesionales con diseño adecuado
- Seguridad debe estar incorporada desde el día uno, no agregada después
- Retroalimentación del usuario es crucial—múltiples iteraciones basadas en uso real
- Documentación ahorra tiempo a largo plazo

---

# Aspectos Técnicos Destacados

## Estadísticas del Código

- Aproximadamente 8,000 líneas de código Python
- Más de 40 módulos (archivos .py)
- 15 ventanas GUI para diferentes operaciones
- 14 tablas de base de datos con relaciones de clave foránea
- 51 componentes preconfigurados

## Rendimiento

- Consultas de base de datos instantáneas (SQLite en SSD)
- Generación de PDF: menos de 2 segundos
- Exportación a Excel: menos de 5 segundos para proyectos de 500 items
- Tiempo de inicio: menos de 3 segundos

## Pruebas

- Pruebas manuales durante todo el desarrollo
- Scripts de verificación de integridad de base de datos
- Herramientas de auditoría de seguridad incluidas
- Implementación en el mundo real con datos comerciales reales

---

# Implementación

## Métodos de Instalación

**Método 1: Código Fuente**
```bash
git clone [repositorio]
cd airsolutions-facturador
pip install -r requirements.txt
python main.py
```

**Método 2: Ejecutable Independiente**
```bash
pyinstaller --onefile --windowed main.py
# Distribuir archivo .exe (no requiere Python)
```

**Método 3: Copia Directa**
- Copiar carpeta completa a la máquina destino
- Instalar Python 3.13
- Doble clic en `Iniciar_AirSolutions.bat`

## Requisitos del Sistema

- SO: Windows 7+, macOS 10.12+, Linux (cualquier distribución moderna)
- Python: 3.13 o superior
- RAM: 512 MB mínimo (2 GB recomendado)
- Disco: 100 MB para aplicación + almacenamiento de base de datos
- Pantalla: Resolución mínima 1280x720

---

# Consideraciones de Seguridad

## Protección de Datos

- Local primero: Todos los datos almacenados localmente, sin dependencia de la nube
- Credenciales encriptadas: Contraseñas de email encriptadas con AES-128
- Hash de contraseñas: bcrypt con salt automático (12 rondas)
- .gitignore: Previene carga accidental de datos sensibles

## Control de Acceso

- Autenticación de usuario requerida para todas las operaciones
- Gestión de sesión con bloqueo automático
- Sin puertas traseras de administrador predeterminadas
- Requisitos de complejidad de contraseña (personalizables)

## Cumplimiento

- Compatible con GDPR: Almacenamiento local de datos, fácil exportación/eliminación
- Portabilidad de datos: Base de datos SQLite se puede respaldar fácilmente
- Pista de auditoría: Marcas de tiempo en todos los registros
- Sin telemetría: Cero transmisión de datos externos

---

# Mejoras Futuras

## Corto Plazo
- Plantillas de proyecto (Hotel, Edificio de Oficinas, Hospital)
- Copiar proyecto existente como plantilla
- Búsqueda y filtrado avanzado
- Operaciones por lotes

## Mediano Plazo
- Roles y permisos de usuario (Admin, Vendedor, Técnico)
- Autenticación de dos factores (2FA)
- Recordatorios automáticos por email
- Análisis de dashboard con gráficos

## Largo Plazo
- API REST para integraciones
- Aplicación móvil (React Native)
- Opción de sincronización en la nube (opcional, encriptada)
- Integración con BIM (Building Information Modeling)

---

# Sobre el Desarrollador

Este sistema fue desarrollado de manera independiente durante un año como un proyecto personal para resolver problemas comerciales reales en la industria de climatización. Demuestra:

- Habilidades de desarrollo full-stack (base de datos, lógica de negocio, interfaz)
- Diseño de arquitectura de software e implementación
- Mejores prácticas de seguridad en aplicaciones de escritorio
- Diseño centrado en el usuario basado en necesidades comerciales reales
- Gestión de proyectos desde la concepción hasta la implementación

El objetivo era crear un sistema listo para producción que pudiera reemplazar procesos manuales y mejorar la eficiencia operativa para una empresa familiar.

---

# Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

# Agradecimientos

- Empresa familiar por proporcionar requisitos del mundo real y retroalimentación
- Comunidad de Python por excelentes bibliotecas y documentación
- Proyectos de código abierto que inspiraron decisiones arquitectónicas

---

Desarrollado con dedicación durante un año (2024-2025)

Una solución integral de gestión de climatización construida desde cero.
