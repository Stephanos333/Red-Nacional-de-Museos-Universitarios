# Arquitectura Técnica y Despliegue - Costo $0

## 1. Stack Tecnológico (versiones reales del lockfile)
- **Generador de Sitios Estáticos (SSG):** Astro 4.16.x (`output: "static"`). Cero JavaScript por defecto; solo las islas React se hidratan.
- **Estilos:** Tailwind CSS 3.4.x vía `@astrojs/tailwind` 5.1.x (`applyBaseStyles: false`; las directivas viven en `src/styles/global.css`). Paleta institucional `brand-*` (burgundy, navy, gold, parchment) en `tailwind.config.mjs`.
- **Islas de Interactividad:** React 18.3 + TypeScript 5 (modo `strict`) mediante `@astrojs/react` 3.6.x. Iconos con `lucide-react`.
  - `DirectorioMuseos.tsx`: búsqueda y filtros del directorio.
  - `FaqAccordion.tsx`: acordeón de preguntas frecuentes con selector por categoría.
- **Tipografía:** exclusivamente pilas de fuentes nativas del sistema (`ui-sans-serif`/`system-ui` y `ui-serif`/`Georgia`). No se cargan fuentes externas (ni Google Fonts ni CDNs), para no enviar IPs de visitantes a terceros.
- **Accesibilidad:** objetivo WCAG AA (enlace "saltar al contenido", foco visible, `aria-*` en controles interactivos).

### Deuda técnica conocida
`npm audit` reporta vulnerabilidades en Astro 4 y sus dependencias (vite, esbuild, sharp, zod). La mayoría afectan a SSR, middleware o al servidor de desarrollo; el sitio publicado es estático. La corrección requiere migrar a Astro 5+ y a Tailwind 4 (`@tailwindcss/vite`, porque `@astrojs/tailwind` queda obsoleto). Es un cambio incompatible que se hará en una tarea aparte.

## 2. Pipeline de Datos (ETL)
- **Entrada:** `data-raw/Base_consolidada_museos_universitarios_octubre_2026.csv` (local y estrictamente ignorado por git).
- **Reglas compartidas:** `scripts/rnmu_rules.py` (lista blanca, catálogos, política de correos, entidades no IES, ciudad → departamento, categorías FAQ).
- **ETL:** `scripts/limpiar_base.py` (Python 3, solo biblioteca estándar). Normaliza textos, unifica universidades, resuelve ciudades contra el departamento, aplica la política de correos y calcula `stats.json`. Valida en memoria antes de escribir: si algo falla, no escribe archivos y sale con código 1.
- **Validador:** `scripts/validar_json.py`. Falla con código 1 ante claves fuera de la lista blanca, correos no permitidos, valores fuera de catálogo, URLs sin `http(s)://`, `stats.json` descuadrado o `faq.json` incompleto o mal categorizado.
- **Salida pública:** `src/data/museos.json`, `src/data/stats.json` y `src/data/faq.json` (este último se edita a mano y lo valida el mismo script).

Comandos:
```bash
npm run clean-data     # python scripts/limpiar_base.py (requiere data-raw/ local)
npm run validate-data  # python scripts/validar_json.py
npm run check          # astro check (tipos de .astro, .ts y .tsx)
npm run build          # astro build
```

## 3. Infraestructura y Hosting
- **Costo:** $0 COP / USD.
- **Alojamiento:** Repositorio público `Stephanos333/Red-Nacional-de-Museos-Universitarios` + GitHub Pages (fuente: GitHub Actions).
- **Rutas:** `site` y `base` en `astro.config.mjs` (sobrescribibles con `ASTRO_SITE` y `ASTRO_BASE`). Todos los enlaces internos usan `import.meta.env.BASE_URL`.
- **CI/CD (`.github/workflows/deploy.yml`), en cada push a `main`:**
  1. Falla si hay archivos `data-raw/`, `.csv`, `.xlsx` o `.xls` versionados.
  2. `python scripts/validar_json.py` (sin base cruda: reglas heurísticas de correo).
  3. `npm ci`.
  4. `npm run check` (astro check).
  5. `npm run build` y despliegue del artefacto `dist/` en GitHub Pages.
