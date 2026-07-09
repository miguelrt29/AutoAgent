<div align="center">

# AutoAgent

**Agente de IA fullstack con ejecución de herramientas en tiempo real**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular 17](https://img.shields.io/badge/Angular-17-DD0031?logo=angular&logoColor=white)](https://angular.dev)
[![Groq AI](https://img.shields.io/badge/Groq-LLM-F55036?logo=groq&logoColor=white)](https://groq.com)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render&logoColor=white)](https://render.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?logo=vercel&logoColor=white)](https://vercel.com)


</div>

---

## Descripcion

**AutoAgent** es un asistente de inteligencia artificial que recibe instrucciones en lenguaje natural y ejecuta acciones reales sobre tu computador y el mundo exterior. Puede buscar informacion en la web, leer y escribir archivos, enviar correos electronicos, consultar APIs externas y ejecutar comandos shell — todo desde una interfaz web moderna con streaming en tiempo real.

Construido con **FastAPI + Groq (Qwen 3 32B)** en el backend y **Angular 17** en el frontend, con comunicacion via **Server-Sent Events (SSE)** para respuestas instantaneas.

---

## Caracteristicas

- **Busqueda web** — Consulta DuckDuckGo y obtén resultados reales con titulos, descripciones y enlaces
- **Lectura de archivos** — Lee archivos del sistema con proteccion contra path traversal *(solo local)*
- **Escritura de archivos** — Crea y sobrescribe archivos de texto *(solo local)*
- **Envio de emails** — Envia correos via SMTP (local) o SendGrid API (produccion)
- **Llamadas a APIs** — Consulta APIs REST externas (GET/POST)
- **Ejecucion de comandos** — Ejecuta comandos shell restringidos a una lista blanca *(solo local)*
- **Streaming en tiempo real** — Las respuestas del agente llegan caracter por caracter via SSE
- **Memoria de sesion** — El agente recuerda el historial completo de la conversacion
- **Sidebar de conversaciones** — Lista persistente con seleccion, titulos generados automaticamente y orden por ultima actividad
- **Anclar chats** — Fija conversaciones importantes al inicio del sidebar (en memoria, sin migraciones)
- **Modal de confirmacion** — Dialogo centrado antes de eliminar una conversacion
- **Panel de herramientas en vivo** — Visualiza cada tool que el agente ejecuta, con sus argumentos
- **Dark theme** — Interfaz oscura moderna con acentos morados
- **Despliegue cloud** — Backend en Render, frontend en Vercel

---

## Stack Tecnologico

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

## Arquitectura

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

## Instalacion y Uso Local

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

## Configuracion (`.env`)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GROQ_API_KEY` | Si | API key de Groq (gratis en console.groq.com) |
| `SMTP_HOST` | No | Servidor SMTP (ej. `smtp.gmail.com`) |
| `SMTP_PORT` | No | Puerto SMTP (ej. `587`) |
| `SMTP_USER` | No | Tu correo electrónico |
| `SMTP_PASS` | No | App Password de Gmail o contraseña SMTP |
| `ALLOWED_COMMANDS` | No | Comandos shell permitidos separados por coma (ej. `ls,pwd,echo`) |
| `SENDGRID_API_KEY` | No | API key de SendGrid para envío de emails en producción |
| `ENABLE_LOCAL_TOOLS` | No | `true` para activar tools locales (read_file, write_file, run_command). Default: `false` |

---

## Despliegue en Produccion

### Backend — Render

1. Sube el repositorio a GitHub
2. Ve a [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**
3. Conecta tu repo — Render detecta automáticamente `render.yaml`
4. En el dashboard del servicio, configura las variables de entorno marcadas con `sync: false`:
   - `GROQ_API_KEY`
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
   - `SENDGRID_API_KEY` (necesaria para enviar emails desde producción)
5. Render se redeploya automáticamente con cada push a `main`

> **Nota:** Render bloquea trafico SMTP saliente (puertos 25, 465, 587, 2525). Para enviar emails en produccion necesitas una API key de [SendGrid](https://sendgrid.com) (gratis: 100 emails/dia).

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

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del servidor |
| `GET` | `/tools` | Lista de herramientas disponibles |
| `POST` | `/chat` | Envía un mensaje al agente (respuesta SSE en streaming) |
| `GET` | `/sessions` | Lista todas las conversaciones (ordenadas, ancladas primero) |
| `GET` | `/sessions/{id}` | Detalle de una conversación con sus mensajes |
| `PUT` | `/sessions/{id}/title` | Actualiza el título de una conversación |
| `PUT` | `/sessions/{id}/pin` | Ancla / desancla una conversación |
| `DELETE` | `/sessions/{id}` | Elimina una conversación y sus mensajes |

---

## Herramientas Disponibles

| Herramienta | Local | Produccion | Descripcion |
|-------------|-------|------------|-------------|
| `web_search` | Si | Si | Busca en la web usando DuckDuckGo |
| `send_email` | Si (SMTP) | Si (SendGrid) | Envia correos electronicos |
| `call_api` | Si | Si | Hace peticiones HTTP a APIs externas |
| `read_file` | Si | No | Lee archivos del sistema (deshabilitado en produccion) |
| `write_file` | Si | No | Escribe archivos en el sistema (deshabilitado en produccion) |
| `run_command` | Si | No | Ejecuta comandos shell restringidos (deshabilitado en produccion) |

Las tools locales se activan con `ENABLE_LOCAL_TOOLS=true` en `.env`. En produccion por defecto estan deshabilitadas.

---

## Ejemplos de Uso

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

## Seguridad

AutoAgent incorpora las siguientes medidas de seguridad:

| Medida | Descripción |
|--------|-------------|
| **Shell seguro** | `shell=False` + `shlex.split()` — metacaracteres (`;`, `\|`, `$()`) se tratan como texto literal, no como comandos |
| **XSS prevenido** | `DOMPurify` sanitiza todo HTML generado por el LLM antes de inyectarlo en el DOM |
| **SSRF protegido** | Bloqueo de IPs privadas (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16) y metadatos cloud |
| **Path traversal** | Validación que impide leer/escribir archivos fuera del directorio de trabajo |
| **Security headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options configurados en el backend |
| **CORS** | Configuración abierta para previews de Vercel (API stateless sin autenticación) |
| **Secrets** | Todas las credenciales vía variables de entorno; `.env` en `.gitignore` |

---

## Autor

**Miguel Angel Reyes Torres**

Desarrollador Fullstack  
SENA — Análisis y Desarrollo de Software

[![GitHub](https://img.shields.io/badge/GitHub-miguelrt29-181717?logo=github&logoColor=white)](https://github.com/miguelrt29)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Miguel_Reyes-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/miguel-reyes-torres-5b621a373)

---


