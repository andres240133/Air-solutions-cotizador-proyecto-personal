# AirSolutions Management System - Documentation

# Project Overview

AirSolutions is a comprehensive management system designed for HVAC and air conditioning companies. It handles everything from small service quotations to large-scale commercial projects like hotels and office buildings.

This system was developed over the course of approximately one year as a personal project to modernize and streamline business operations for a family HVAC company.

---

# Purpose and Motivation

## The Problem

The family HVAC business faced difficulties with:
- Manual quotation processes using Excel spreadsheets
- Scattered client information without centralized history
- Difficulty managing large multi-level projects
- No integration between quotations, inventory, and project management
- Time-consuming manual PDF generation and email communication
- Absence of a reliable and secure backup system

## The Solution

AirSolutions provides:
- Automated quotation generation with professional PDF output
- Centralized client management with complete history
- Large project management with hierarchical structure (levels and items)
- Pre-configured component catalog with 51+ items
- Excel integration for external editing and bulk updates
- Email integration for direct quotation delivery
- Robust security with encrypted credentials and access control
- Local SQLite database ensuring data ownership and privacy

---

# System Architecture

## Technology Stack

- Language: Python 3.13
- GUI Framework: Tkinter (native, cross-platform)
- Database: SQLite3 (local, file-based)
- Security: bcrypt (password hashing), Fernet/AES-128 (encryption)
- Document Generation: ReportLab (PDF), openpyxl (Excel)
- Additional Libraries: Pillow, matplotlib, tkcalendar

## Architecture Pattern

The system follows a Model-View-Controller (MVC) pattern:

```
├── models/          # Data layer (database, business logic)
├── views/           # Presentation layer (UI windows)
├── utils/           # Services (encryption, PDF, email, Excel)
└── main.py          # Application entry point
```

## Database Schema

14 tables organized in three modules:

1. Core Module (2 tables)
   - `usuarios` - User authentication
   - `configuracion` - System configuration

2. Quotations Module (7 tables)
   - `clientes` - Client information
   - `productos_equipos` - HVAC equipment catalog
   - `materiales_repuestos` - Materials and parts
   - `cotizaciones` - Quotation headers
   - `detalle_cotizacion` - Quotation line items (equipment)
   - `cotizacion_materiales` - Quotation materials
   - `gastos_adicionales` - Additional expenses (travel, transport)

3. Large Projects Module (5 tables)
   - `catalogo_hvac` - Pre-configured components (51 items)
   - `proyectos` - Project headers
   - `proyecto_niveles` - Project levels (floors, areas)
   - `proyecto_items` - Items per level with 3-column costing
   - `proyecto_archivos` - Linked files (AutoCAD drawings, PDFs)

---

# Key Features

## 1. Dual Management System

**Small Projects (Quotations)**
- Quick quotation creation
- Equipment and materials selection from catalog
- Automatic pricing with markup and tax
- Professional PDF generation
- Email delivery

**Large Projects**
- Hierarchical structure: Project → Levels → Items
- Example: Hotel with S100 (Basement), N1 (Floor 1), N2 (Floor 2)
- 3-column costing: Equipment, Materials, Labor
- Automatic totals per level and project-wide
- Excel export/import for external collaboration

## 2. Security Implementation

- bcrypt password hashing with automatic salt
- Login attempt limiter (3 attempts, 5-minute lockout)
- Fernet (AES-128) encryption for email credentials
- SQL injection prevention through parameterized queries
- Foreign key constraints for data integrity
- Automatic backups before database migrations

## 3. Excel Integration

**Export**: Generate professional Excel files with:
- Formatted headers and totals
- Color-coded sections by level
- Editable pricing and quantities
- Automatic formulas

**Import**: Update database from edited Excel files:
- Read modified quantities and costs
- Create new items automatically
- Maintain project structure integrity

## 4. File Management

Link external files to projects:
- AutoCAD drawings (.dwg)
- PDFs, images, specifications
- Associate files with specific levels
- Open files with double-click (uses system default application)

## 5. Document Generation

**PDF Quotations**:
- Company logo and branding
- Itemized equipment and materials
- Automatic tax and markup calculations
- Professional formatting
- Currency conversion (USD/CRC)

**Excel Reports**:
- Project breakdowns by level
- Cost analysis (equipment/materials/labor)
- Editable templates

---

# Business Logic

## Pricing Model

```
Equipment Cost + Materials Cost = Subtotal
Subtotal × Markup Factor = Subtotal with Markup
Subtotal with Markup × (1 + IVA%) = Total
```

Configurable parameters:
- Markup factor (default: 1.5 = 50% margin)
- Tax rate (default: 13% VAT)
- Exchange rate (USD to CRC)
- Technician hourly rate

## Project Workflow

1. Create Project → Enter basic information
2. Define Levels → Add S100, N1, N2, etc.
3. Add Items → Select from catalog or manual entry
4. Export to Excel → Share with team for review
5. Edit in Excel → Adjust quantities/costs
6. Import Back → Update database automatically
7. Link Files → Attach drawings and specifications
8. Generate Quotations → Create individual quotes per area
9. Deliver → PDF + Email to client

---

# Development Journey

## Timeline

Year 1 (2024-2025): Complete system development

- Months 1-3: Core architecture, database design, authentication
- Months 4-6: Quotations module, PDF generation
- Months 7-9: Large projects module, Excel integration
- Months 10-12: Security hardening, testing, deployment

## Challenges Overcome

1. Database Design: Balancing flexibility vs. performance for both small and large projects
2. Excel Integration: Bidirectional sync without data loss
3. Security: Implementing enterprise-grade security in a desktop application
4. User Experience: Creating an intuitive interface for non-technical users
5. File Management: Linking external files without copying (maintaining AutoCAD workflow)

## Key Learnings

- SQLite is powerful enough for SME applications
- Tkinter can create professional UIs with proper design
- Security must be built-in from day one, not added later
- User feedback is crucial—multiple iterations based on real usage
- Documentation saves time in the long run

---

# Technical Highlights

## Code Statistics

- Approximately 8,000 lines of Python code
- Over 40 modules (.py files)
- 15 GUI windows for different operations
- 14 database tables with foreign key relationships
- 51 pre-configured components

## Performance

- Instant database queries (SQLite on SSD)
- PDF generation: less than 2 seconds
- Excel export: less than 5 seconds for 500-item projects
- Startup time: less than 3 seconds

## Testing

- Manual testing throughout development
- Database integrity verification scripts
- Security audit tools included
- Real-world deployment with actual business data

---

# Deployment

## Installation Methods

**Method 1: Source Code**
```bash
git clone [repository]
cd airsolutions-facturador
pip install -r requirements.txt
python main.py
```

**Method 2: Standalone Executable**
```bash
pyinstaller --onefile --windowed main.py
# Distribute .exe file (no Python required)
```

**Method 3: Direct Copy**
- Copy entire folder to target machine
- Install Python 3.13
- Double-click `Iniciar_AirSolutions.bat`

## System Requirements

- OS: Windows 7+, macOS 10.12+, Linux (any modern distro)
- Python: 3.13 or higher
- RAM: 512 MB minimum (2 GB recommended)
- Disk: 100 MB for application + database storage
- Screen: 1280x720 minimum resolution

---

# Security Considerations

## Data Protection

- Local-first: All data stored locally, no cloud dependency
- Encrypted credentials: Email passwords encrypted with AES-128
- Password hashing: bcrypt with automatic salt (12 rounds)
- .gitignore: Prevents accidental upload of sensitive data

## Access Control

- User authentication required for all operations
- Session management with automatic lockout
- No default admin backdoors
- Password complexity requirements (can be customized)

## Compliance

- GDPR-friendly: Local data storage, easy export/delete
- Data portability: SQLite database can be backed up easily
- Audit trail: Timestamps on all records
- No telemetry: Zero external data transmission

---

# Future Enhancements

## Short Term
- Project templates (Hotel, Office Building, Hospital)
- Copy existing project as template
- Advanced search and filtering
- Batch operations

## Medium Term
- User roles and permissions (Admin, Salesperson, Technician)
- Two-factor authentication (2FA)
- Automated email reminders
- Dashboard analytics with charts

## Long Term
- REST API for integrations
- Mobile app (React Native)
- Cloud sync option (optional, encrypted)
- BIM (Building Information Modeling) integration

---

# About the Developer

This system was developed independently over one year as a personal project to solve real business problems in the HVAC industry. It demonstrates:

- Full-stack development skills (database, business logic, UI)
- Software architecture design and implementation
- Security best practices in desktop applications
- User-centered design based on actual business needs
- Project management from conception to deployment

The goal was to create a production-ready system that could replace manual processes and improve operational efficiency for a family business.

---

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# Acknowledgments

- Family business for providing real-world requirements and feedback
- Python community for excellent libraries and documentation
- Open-source projects that inspired architectural decisions

---

Developed with dedication over one year (2024-2025)

A comprehensive HVAC management solution built from the ground up.
