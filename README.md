# The Fragance´s | Alta Perfumería & Catálogo Fragrantica

Plataforma web de perfumería exclusiva inspirada en la arquitectura de **Fragrantica**, con pirámides olfativas completas (Notas de Salida, Corazón y Fondo), gráficos de acordes, reseñas verificadas y **pedidos directos vía WhatsApp (+58 424-2567728)** sin pasarelas de pago engorrosas.

---

## 🚀 Características Principales

- **Catálogo Oficial en Stock:** 20 fragancias exclusivas con frascos reales, presentaciones oficiales y rangos de precios (9 Caballero, 9 Dama, 2 Nicho & Unisex).
- **Atención Directa por WhatsApp:** Cada producto tiene un botón con mensaje pre-configurado para contactar al asesor al instante.
- **Doble Modo Claro / Oscuro:** Selector persistente de tema día/noche con acentos inspirados en gemas y perfumes.
- **Panel de Administrador Móvil:**
  - Control de stock con **1 solo clic** (En Stock / Agotado vía AJAX sin recargar la página).
  - Moderación y eliminación inmediata de reseñas inapropiadas (directamente en la ficha del perfume o desde el panel central).
  - Edición de precios, presentaciones, notas y número de WhatsApp.
- **Reseñas 100% Reales:** Registro de usuarios reales y cálculo automático de calificaciones.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.11+ / Flask 3.1
- **Base de Datos:** SQLite (`perfumes.db`) con auto-inicialización y seed automático.
- **Frontend:** HTML5, Tailwind CSS, FontAwesome 6, JavaScript nativo.
- **Servidor de Producción:** Gunicorn.
- **Despliegue:** Render / GitHub.

---

## 📦 Instrucciones para Subir el Proyecto a tu GitHub

Sigue estos 3 pasos para subir el código a tu propia cuenta de GitHub:

### Paso 1: Crea un repositorio nuevo en GitHub
1. Entra a tu cuenta en [github.com](https://github.com).
2. Haz clic en el botón verde **"New"** (Nuevo Repositorio).
3. Nómbralo por ejemplo: `the-fragances-web`.
4. Elige si deseas que sea **Público** o **Privado** (no marques inicializar con README).
5. Copia la URL del repositorio (ejemplo: `https://github.com/TU_USUARIO/the-fragances-web.git`).

### Paso 2: Conecta y sube el proyecto desde la terminal
Abre la consola en la carpeta del proyecto (`e:\1-perfumes\pagina2`) y ejecuta:

```powershell
# 1. Configura tu repositorio remoto (reemplaza con tu URL de GitHub)
git remote add origin https://github.com/TU_USUARIO/the-fragances-web.git

# 2. Si ya existía un remote previo, cámbialo con:
# git remote set-url origin https://github.com/TU_USUARIO/the-fragances-web.git

# 3. Sube el código a la rama principal (main)
git push -u origin main
```

---

## 🌐 Instrucciones para Desplegar en Render (Cuenta Paga)

Render desplegará la página automáticamente con cada cambio que subas a GitHub:

1. Entra a tu [Dashboard de Render](https://dashboard.render.com/).
2. Haz clic en **"New +"** y selecciona **"Web Service"**.
3. Selecciona la opción **"Build and deploy from a Git repository"** y elige tu repositorio `the-fragances-web`.
4. Configura los siguientes campos:
   - **Name:** `thefragances` (o el nombre que prefieras).
   - **Region:** Selecciona la más cercana (ej. *Oregon* o *Ohio*).
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python seed.py
     ```
   - **Start Command:**
     ```bash
     python -m gunicorn app:app
     ```
   - **Instance Type:** Elige el plan que desees de tu cuenta paga (Starter, Standard, etc.).
5. En la sección **Environment Variables** (Variables de Entorno), añade:
   - `FLASK_SECRET_KEY`: Una cadena segura aleatoria (ej. `thefragances_super_secret_key_2026`).
   - `PYTHON_VERSION`: `3.11.0`
6. Haz clic en **"Create Web Service"**.

¡Listo! En 2 minutos Render compilará el proyecto y te entregará tu enlace público seguro con SSL (`https://tu-proyecto.onrender.com`).

---

## 🔑 Credenciales de Acceso Administrador

- **URL de Inicio de Sesión:** `/login`
- **Correo Electrónico:** `admin@thefragances.com`
- **Contraseña:** `admin` *(Recomendado cambiar desde el perfil o BD)*
- **PIN Alternativo de Acceso Rápido:** `1234`
- **Acceso Directo al Panel:** `/admin` (Habilitado automáticamente tras iniciar sesión con el rol de admin).

---

## 📞 Soporte & Contacto
- **WhatsApp de Atención al Cliente:** `+58 424-2567728`
- **Modificación de Número:** Desde el Panel de Administrador en `/admin/ajustes`.
