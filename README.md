# Red Nacional de Museos Universitarios de Colombia (RNMU)

Portal web oficial y directorio público de la **Red Nacional de Museos Universitarios (RNMU)** de Colombia. Este proyecto opera con **costo $0 de infraestructura**, alojado en un repositorio público de GitHub y desplegado automáticamente en **GitHub Pages**.

---

## 🏛️ Sobre la RNMU
- **Naturaleza:** Red temática avalada por el **Programa Fortalecimiento de Museos (PFM)** del Ministerio de las Culturas, las Artes y los Saberes.
- **Marco Normativo:** Resolución 1975 de 2013 de MinCultura.
- **Acreditación Institucional:** Actor clave en el Factor 7 (Características 23 y 24) del CNA.
- **Coordinación (2026):** Museo de Trajes de la Universidad de América (aprobada en acta del Encuentro Nacional del 28 de mayo de 2026).
- **Contacto Institucional:** `reddemuseosuniversitarios@gmail.com` | WhatsApp: `+57 316 496 3906`

---

## 🔒 Regla Crítica de Privacidad y Habeas Data
El repositorio es **PÚBLICO**. En cumplimiento de la **Ley Estatutaria 1581 de 2012** de Colombia:
1. **NUNCA** se versionan archivos `.xlsx`, `.xls`, `.csv` crudos ni la carpeta `data-raw/` (protegidos en `.gitignore`).
2. Se excluyen del frontend teléfonos personales, nombres de personas, presupuestos, KPIs internos, membresía al grupo de WhatsApp y comentarios de diagnóstico.
3. Solo se publican **buzones institucionales genéricos** (`museo@`, `info@`, `cultura@`…). Los correos con nombres de personas o dominios comerciales (Gmail, Hotmail…) quedan en `null`.
4. El archivo público `src/data/museos.json` contiene únicamente la **lista blanca estricta**:
   - `id`
   - `nombre`
   - `universidad` (nombre canónico de la IES)
   - `naturaleza` ("Pública" | "Privada" | "No especificada")
   - `departamento`
   - `ciudad`
   - `direccion` (o `null`)
   - `tipologia` (o `null`)
   - `estadoAtencion` ("Abierto" | "Cita previa" | "Cerrado temporalmente" | "Cerrado" | "Sin información")
   - `registroSimco` ("Sí" | "No" | "En proceso / Por confirmar" | "Sin información")
   - `paginaWeb` (o `null`)
   - `correoInstitucional` (buzón genérico o `null`)

La política completa está en `.kiro/steering/data-privacy.md`.

---

## 🛠️ Stack Tecnológico
- **Framework:** [Astro](https://astro.build/) (SSG de alto rendimiento).
- **Estilos:** [Tailwind CSS](https://tailwindcss.com/) (Paleta institucional sobria y accesible WCAG AA).
- **Islas de Interactividad:** [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Lucide Icons](https://lucide.dev/).
- **Tipografía:** fuentes nativas del sistema (sin Google Fonts ni otros terceros).
- **ETL y validación:** Python 3 (solo biblioteca estándar): `scripts/limpiar_base.py`, `scripts/validar_json.py` y reglas compartidas en `scripts/rnmu_rules.py`.
- **CI/CD:** GitHub Actions (`.github/workflows/deploy.yml`) hacia GitHub Pages.

---

## 📂 Estructura del Proyecto
```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml        # Pipeline CI/CD hacia GitHub Pages
├── .kiro/
│   ├── steering/             # Lineamientos de producto, tecnología y privacidad
│   └── specs/                # Specs de Kiro (requirements, design, tasks)
├── data-raw/                 # EXCLUIDA EN GIT (almacenamiento de bases crudas)
├── docs/
│   └── analisis_duplicados_y_urls.md  # Pendientes de depuración para el comité
├── scripts/
│   ├── rnmu_rules.py         # Reglas compartidas (lista blanca, catálogos, correos)
│   ├── limpiar_base.py       # Pipeline ETL
│   └── validar_json.py       # Validador de los JSON públicos (también en CI)
├── src/
│   ├── components/           # Header, Footer, DirectorioMuseos, FaqAccordion, StatsDashboard
│   ├── data/                 # museos.json, stats.json, faq.json
│   ├── layouts/              # Layout.astro con SEO, OpenGraph y accesibilidad
│   ├── pages/                # index, quienes-somos, directorio, caracterizacion, faq
│   └── styles/               # global.css con directivas Tailwind y badges
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
└── package.json
```

---

## 🚀 Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Ejecutar pipeline ETL de datos (requiere data-raw/ local; valida antes de escribir)
npm run clean-data

# Validar los JSON públicos (lista blanca, correos, catálogos, stats, FAQ)
npm run validate-data

# Verificación de tipos
npm run check

# Iniciar servidor local de desarrollo
npm run dev

# Compilar para producción
npm run build
```

---

## 🌐 Despliegue en GitHub Pages ($0 Costo)
El flujo en `.github/workflows/deploy.yml` compila y publica automáticamente el sitio en GitHub Pages tras cada `push` a la rama `main`:
1. Falla si hay archivos de datos crudos (`data-raw/`, `.csv`, `.xlsx`, `.xls`) versionados.
2. Ejecuta `scripts/validar_json.py`.
3. Instala dependencias, ejecuta `astro check` y compila con Astro.
4. Despliega los artefactos estáticos sin costo de servidor.
