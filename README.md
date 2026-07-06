<div align="center">

# 🤖 AutoAgent

**Agente de IA fullstack con ejecución de herramientas en tiempo real**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular 17](https://img.shields.io/badge/Angular-17-DD0031?logo=angular&logoColor=white)](https://angular.dev)
[![Groq AI](https://img.shields.io/badge/Groq-LLM-F55036?logo=groq&logoColor=white)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Descripción

**AutoAgent** es un asistente de inteligencia artificial que recibe instrucciones en lenguaje natural y ejecuta acciones reales sobre tu computador y el mundo exterior. Puede buscar información en la web, leer y escribir archivos, enviar correos electrónicos, consultar APIs externas y ejecutar comandos shell — todo desde una interfaz web moderna con streaming en tiempo real.

Construido con **FastAPI + Groq (Qwen 3 32B)** en el backend y **Angular 17** en el frontend, con comunicación vía **Server-Sent Events (SSE)** para respuestas instantáneas.

<!--
TODO: Agregar grabación de pantalla
![Demo](docs/demo.gif)
-->

---

## ✨ Características

- 🔍 **Búsqueda web** — Consulta DuckDuckGo y obtén resultados reales con títulos, descripciones y enlaces
- 📄 **Lectura de archivos** — Lee archivos del sistema con protección contra path traversal
- ✏️ **Escritura de archivos** — Crea y sobrescribe archivos de texto
- 📧 **Envío de emails** — Envía correos vía SMTP con STARTTLS
- 🌐 **Llamadas a APIs** — Consulta APIs REST externas (GET/POST)
- 🖥️ **Ejecución de comandos** — Ejecuta comandos shell restringidos a una lista blanca
- ⚡ **Streaming en tiempo real** — Las respuestas del agente llegan carácter por carácter vía SSE
- 💬 **Memoria de sesión** — El agente recuerda el historial completo de la conversación
- 📊 **Panel de herramientas en vivo** — Visualiza cada tool que el agente ejecuta, con sus argumentos
- 🌙 **Dark theme** — Interfaz oscura moderna con acentos morados

---

## 🛠️ Stack Tecnológico

| Backend | Frontend |
|---------|----------|
| Python 3.12 | Angular 17.3 |
| FastAPI | TypeScript 5.4 |
| Groq SDK (Qwen 3 32B) | RxJS 7.8 |
| DuckDuckGo Search (ddgs) | SCSS |
| SMTP (smtplib) | HTML5 |
| Pydantic | Fetch API (SSE) |
| Uvicorn | Karma + Jasmine |

---

## 🏗️ Arquitectura

```
┌─────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ Usuario │────▶│ Angular   │────▶│ FastAPI  │────▶│ Groq LLM │
│ (Chrome)│     │ :4200     │     │ :8000    │     │ (Qwen 3) │
└─────────┘     └───────────┘     └──────────┘     └──────────┘
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
            │ web_search │    │ read_file  │    │ write_file │
            │ email_tool │    │ call_api   │    │ run_command│
            └────────────┘    └────────────┘    └────────────┘
                    │                  │                  │
                    ▼                  ▼                  ▼
               Resultados ────────▶ SSE stream ────────▶ UI
```

---

## 📦 Instalación y Uso

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
# Editar .env con tu GROQ_API_KEY (obtenida en console.groq.com)

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
| `GROQ_API_KEY` | ✅ Sí | Tu API key de Groq (gratis en console.groq.com) |
| `SMTP_HOST` | ❌ No | Servidor SMTP (ej. `smtp.gmail.com`) |
| `SMTP_PORT` | ❌ No | Puerto SMTP (ej. `587`) |
| `SMTP_USER` | ❌ No | Tu correo electrónico |
| `SMTP_PASS` | ❌ No | App Password de Gmail o contraseña SMTP |
| `ALLOWED_COMMANDS` | ❌ No | Comandos shell permitidos separados por coma |

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

| Herramienta | Descripción | Ejemplo de uso |
|-------------|-------------|----------------|
| `web_search` | Busca en la web usando DuckDuckGo | "Busca información sobre inteligencia artificial" |
| `read_file` | Lee el contenido de un archivo | "Lee el archivo config.json" |
| `write_file` | Escribe contenido en un archivo | "Guarda un resumen en resumen.txt" |
| `send_email` | Envía un correo electrónico vía SMTP | "Envíale un email a miguel@example.com" |
| `call_api` | Hace una petición HTTP a una API externa | "Consulta el clima en la API de OpenWeather" |
| `run_command` | Ejecuta un comando shell (lista blanca) | "Ejecuta ls -la para listar los archivos" |

---

## 💬 Ejemplos de Uso

Puedes escribir estos prompts directamente en el chat:

```
1. "Busca en la web las mejores prácticas de Python y guarda un resumen
    en python_tips.txt"

2. "Lee el archivo output.txt y dime de qué trata"

3. "Encuentra noticias recientes sobre inteligencia artificial y envíame
    un email con el resumen a miguel@example.com"

4. "Consulta el estado del tipo de cambio hoy usando una API pública"

5. "Lista los archivos del directorio actual y guarda el resultado en
    lista_archivos.txt"
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
