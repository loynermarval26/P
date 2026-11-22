# AromaLuxe Perfumería - Catálogo & Notas Olfativas (Estilo Fragrantica)

Plataforma web para tienda de perfumería con diseño estético de lujo oscuro en tonos azules y verdes esmeralda, inspirada en el concepto olfativo de **Fragrantica**.

---

## 🌟 Características Principales

1. **Sin Carrito de Compras Complejo (Contacto Directo por WhatsApp):**
   - Cada perfume tiene un botón destacado de **"Consultar / Comprar por WhatsApp"**.
   - Genera automáticamente un mensaje personalizado con el nombre de la fragancia, la casa/marca, la concentración, el tamaño en ml y el precio, listo para enviar con un solo toque.
   - Botón flotante de WhatsApp en toda la web para asesoría directa.
   - El número de WhatsApp y los mensajes son configurables desde el panel administrativo.

2. **Concepto & Estética Fragrantica:**
   - **Barras de Acordes Principales:** Barras horizontales a color (Cítrico, Amaderado, Ámbar, Marino, etc.) con porcentajes de intensidad visual.
   - **Pirámide Olfativa Completa:**
     - *Notas de Salida* (Top Notes)
     - *Notas de Corazón* (Heart Notes)
     - *Notas de Fondo* (Base Notes)
   - **Ficha Técnica & Rendimiento:** Familia olfativa, año de lanzamiento, perfumista/nariz, temporadas recomendadas, momentos de uso, longevidad en piel y estela/proyección.
   - **Buscador Específico Avanzado:** Búsqueda en tiempo real por nombre, notas (ej. Vainilla, Bergamota), acordes, género (Hombre, Mujer, Unisex), casa de perfumería y disponibilidad en stock.

3. **Sistema de Gestión de Stock Móvil (Admin Panel `/admin`):**
   - **Diseñado para usarse desde el teléfono móvil** o PC sin tocar una sola línea de código.
   - Acceso protegido por **PIN de seguridad** (PIN inicial: `1234`).
   - **Control Rápido de Stock a 1 Clic (AJAX):** El dueño puede activar o desactivar la disponibilidad de cualquier perfume (*En Stock* / *Agotado*) instantáneamente con un solo toque desde su teléfono.
   - **Gestión de Perfumes:** Añadir, editar o eliminar fragancias con subida de fotos (desde el teléfono o URL), creación dinámica de acordes y notas.
   - **Gestión de Marcas y Colecciones:** Crear marcas con país y descripción, además de líneas exclusivas.
   - **Ajustes Generales:** Cambiar número de WhatsApp, nombre de la tienda, mensaje superior y PIN de acceso.

---

## 🚀 Cómo Iniciar el Proyecto

### Opción Rápida (Windows):
Haz doble clic en el archivo:
```
iniciar_servidor.bat
```

### O por Terminal:
```powershell
python app.py
```

---

## 📱 Acceso desde tu Teléfono Móvil

Con tu teléfono conectado a la misma red Wi-Fi:
- **Catálogo Web:** `http://192.168.15.3:5000`
- **Panel del Dueño / Admin:** `http://192.168.15.3:5000/admin`
- **PIN por defecto:** `1234`

*(Si cambia tu IP local, puedes verificarla ejecutando `ipconfig` en Windows).*

---

## 📂 Estructura del Proyecto

```
pagina2/
├── app.py                     # Servidor Flask, rutas de cliente y panel admin
├── database.py                # Base de datos SQLite y consultas de catálogo
├── seed.py                    # Carga inicial con 11 fragancias icónicas y marcas
├── perfumes.db                # Base de datos SQLite
├── requirements.txt           # Dependencias (Flask, Pillow, etc.)
├── iniciar_servidor.bat       # Acceso rápido en Windows
├── static/
│   ├── css/custom.css         # Estilos oscuros, acordes olfativos y botones
│   ├── js/main.js             # Lógica cliente y filtros
│   ├── js/admin.js            # Toggle AJAX de stock a 1 clic y constructor de acordes
│   └── uploads/               # Imágenes subidas por el dueño
└── templates/
    ├── base.html              # Plantilla base con navegación y WhatsApp flotante
    ├── index.html             # Portada con acordes populares y destacados
    ├── catalog.html           # Buscador específico y filtros avanzados
    ├── detail.html            # Ficha técnica y pirámide estilo Fragrantica
    ├── brands.html            # Directorio de marcas
    ├── brand_detail.html      # Perfumes filtrados por marca
    └── admin/
        ├── login.html         # Login con PIN
        ├── dashboard.html     # Estadísticas y control rápido de stock
        ├── perfumes_list.html # Listado con toggle rápido y acciones
        ├── perfume_form.html  # Formulario completo de perfume y acordes
        ├── brands_list.html   # Gestión de marcas y colecciones
        └── settings.html      # Configuración de WhatsApp y tienda
```
