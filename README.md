<div align="center">

# 🤖 AutoAgent

**Agente de IA fullstack con ejecución de herramientas en tiempo real**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular 17](https://img.shields.io/badge/Angular-17-DD0031?logo=angular&logoColor=white)](https://angular.dev)
[![Groq AI](https://img.shields.io/badge/Groq-LLM-F55036?logo=groq&logoColor=white)](https://groq.com)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render&logoColor=white)](https://render.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Descripción

**AutoAgent** es un asistente de inteligencia artificial que recibe instrucciones en lenguaje natural y ejecuta acciones reales sobre tu computador y el mundo exterior. Puede buscar información en la web, leer y escribir archivos, enviar correos electrónicos, consultar APIs externas y ejecutar comandos shell — todo desde una interfaz web moderna con streaming en tiempo real.

Construido con **FastAPI + Groq (Qwen 3 32B)** en el backend y **Angular 17** en el frontend, con comunicación vía **Server-Sent Events (SSE)** para respuestas instantáneas.

---

## ✨ Características

- 🔍 **Búsqueda web** — Consulta DuckDuckGo y obtén resultados reales con títulos, descripciones y enlaces
- 📄 **Lectura de archivos** — Lee archivos del sistema con protección contra path traversal *(solo local)*
- ✏️ **Escritura de archivos** — Crea y sobrescribe archivos de texto *(solo local)*
- 📧 **Envío de emails** — Envía correos vía SMTP (local) o SendGrid API (producción)
- 🌐 **Llamadas a APIs** — Consulta APIs REST externas (GET/POST)
- 🖥️ **Ejecución de comandos** — Ejecuta comandos shell restringidos a una lista blanca *(solo local)*
- ⚡ **Streaming en tiempo real** — Las respuestas del agente llegan carácter por carácter vía SSE
- 💬 **Memoria de sesión** — El agente recuerda el historial completo de la conversación
- 📊 **Panel de herramientas en vivo** — Visualiza cada tool que el agente ejecuta, con sus argumentos
- 🌙 **Dark theme** — Interfaz oscura moderna con acentos morados
- 🚀 **Despliegue cloud** — Backend en Render, frontend en Vercel

---

## 🛠️ Stack Tecnológico

| Backend | Frontend | Cloud |
|---------|----------|-------|
| Python 3.12 | Angular 17.3 | Render (backend) |
| FastAPI | TypeScript 5.4 | Vercel (frontend) |
| Groq SDK (Qwen 3 32B) | RxJS 7.8 | SendGrid (email) |
| DuckDuckGo Search (ddgs) | SCSS | Groq (LLM) |
| SMTP / SendGrid API | Fetch API (SSE) | |
| Pydantic | Karma + Jasmine | |
| Uvicorn | | |

---

## 🏗️ Arquitectura

```
┌─────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ Usuario │────▶│ Angular   │────▶│ FastAPI  │────▶│ Groq LLM │
│ (Chrome)│     │ :4200 /   │     │ :8000 /  │     │ (Qwen 3) │
│         │     │ Vercel    │     │ Render   │     └──────────┘
└─────────┘     └───────────┘     └────┬─────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │   Agent       │
                                │  (Orquestador)│
                                └──────┬───────┘
                                        │
                     ┌──────────────────┼──────────────────┐
                     ▼                  ▼                  ▼
             ┌────────────┐    ┌────────────┐    ┌────────────┐
             │ web_search │    │ send_email  │    │ call_api   │
             │ (siempre)  │    │(SMTP/SendGrid)│   │ (siempre)  │
             └────────────┘    └────────────┘    └────────────┘
             ┌────────────┐    ┌────────────┐    ┌────────────┐
             │ read_file  │    │ write_file │    │ run_command│
             │ (solo local│    │ (solo local│    │ (solo local│
             │  activado) │    │  activado) │    │  activado) │
             └────────────┘    └────────────┘    └────────────┘
                     │                  │                  │
                     ▼                  ▼                  ▼
                Resultados ────────▶ SSE stream ────────▶ UI
```

---

## 📦 Instalación y Uso Local

### Requisitos previos

- Python 3.12 o superior
- Node.js 18+ y npm
- Cuenta gratuita en [console.groq.com](https://console.groq.com) para obtener una API Key

### Paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/miguelrt29/AutoAgent.git
cd AutoAgent

# 2. Backend — instalar dependencias
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY y las credenciales que necesites

# 4. Iniciar el backend
uvicorn main:app --reload
# El servidor arranca en http://localhost:8000

# 5. Frontend — en otra terminal
cd ../frontend
npm install
ng serve --open
# La aplicación se abre en http://localhost:4200
```

---

## ⚙️ Configuración (`.env`)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GROQ_API_KEY` | ✅ Sí | API key de Groq (gratis en console.groq.com) |
| `SMTP_HOST` | ❌ No | Servidor SMTP (ej. `smtp.gmail.com`) |
| `SMTP_PORT` | ❌ No | Puerto SMTP (ej. `587`) |
| `SMTP_USER` | ❌ No | Tu correo electrónico |
| `SMTP_PASS` | ❌ No | App Password de Gmail o contraseña SMTP |
| `ALLOWED_COMMANDS` | ❌ No | Comandos shell permitidos separados por coma (ej. `ls,pwd,echo`) |
| `SENDGRID_API_KEY` | ❌ No | API key de SendGrid para envío de emails en producción |
| `ENABLE_LOCAL_TOOLS` | ❌ No | `true` para activar tools locales (read_file, write_file, run_command). Default: `false` |

---

## 🚀 Despliegue en Producción

### Backend — Render

1. Sube el repositorio a GitHub
2. Ve a [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**
3. Conecta tu repo — Render detecta automáticamente `render.yaml`
4. En el dashboard del servicio, configura las variables de entorno marcadas con `sync: false`:
   - `GROQ_API_KEY`
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
   - `SENDGRID_API_KEY` (necesaria para enviar emails desde producción)
5. Render se redeploya automáticamente con cada push a `main`

> **Nota:** Render bloquea tráfico SMTP saliente (puertos 25, 465, 587, 2525). Para enviar emails en producción necesitas una API key de [SendGrid](https://sendgrid.com) (gratis: 100 emails/día).

### Frontend — Vercel

1. Ve a [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Importa tu repo de GitHub
3. Configura:
   - **Root Directory:** `frontend/`
   - **Build Command:** `npm run build:vercel`
   - **Output Directory:** `dist/autoagent-ui/browser` (configurado en `vercel.json`)
4. Vercel despliega automáticamente con cada push a `main`

### Orden de despliegue

1. **Primero** el backend en Render
2. **Después** el frontend en Vercel
3. Actualiza `frontend/src/environments/environment.prod.ts` con la URL real de Render
4. Actualiza `backend/main.py` con la URL real de Vercel en CORS (si usas lista fija)

---

## 🌐 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del servidor |
| `GET` | `/tools` | Lista de herramientas disponibles |
| `POST` | `/chat` | Envía un mensaje al agente (respuesta SSE en streaming) |
| `GET` | `/sessions/{id}/history` | Historial de una sesión |

---

## 🔧 Herramientas Disponibles

| Herramienta | Local | Producción | Descripción |
|-------------|-------|------------|-------------|
| `web_search` | ✅ | ✅ | Busca en la web usando DuckDuckGo |
| `send_email` | ✅ (SMTP) | ✅ (SendGrid) | Envía correos electrónicos — usa SMTP en local, SendGrid API en producción |
| `call_api` | ✅ | ✅ | Hace peticiones HTTP a APIs externas |
| `read_file` | ✅ | ❌ | Lee archivos del sistema (deshabilitado en producción) |
| `write_file` | ✅ | ❌ | Escribe archivos en el sistema (deshabilitado en producción) |
| `run_command` | ✅ | ❌ | Ejecuta comandos shell restringidos (deshabilitado en producción) |

> Las tools locales se activan con `ENABLE_LOCAL_TOOLS=true` en `.env`. En producción por defecto están deshabilitadas.

---

## 💬 Ejemplos de Uso

Puedes escribir estos prompts directamente en el chat:

```
1. "Busca en la web las mejores prácticas de Python"

2. "Encuentra noticias recientes sobre inteligencia artificial y envíame
    un email con el resumen a miguel@example.com"

3. "Consulta el estado del tipo de cambio hoy usando una API pública"

4. "Lee el archivo output.txt y dime de qué trata"
    (solo funciona localmente con ENABLE_LOCAL_TOOLS=true)

5. "Lista los archivos del directorio actual"
    (solo funciona localmente con ENABLE_LOCAL_TOOLS=true)
```

---

## 👨‍💻 Autor

**Miguel Angel Reyes Torres**

Desarrollador Fullstack  
SENA — Análisis y Desarrollo de Software

[![GitHub](https://img.shields.io/badge/GitHub-miguelrt29-181717?logo=github&logoColor=white)](https://github.com/miguelrt29)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Miguel_Reyes-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/miguel-reyes-torres-5b621a373)

---

## 📄 Licencia

```
MIT License

Copyright (c) 2025 Miguel Angel Reyes Torres

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
