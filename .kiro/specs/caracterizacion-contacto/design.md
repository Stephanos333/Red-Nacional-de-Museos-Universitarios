# Design Document: Caracterización y Contacto Institucional

## Overview

Dos páginas estáticas de Astro:
- `caracterizacion.astro`: explicación del proceso, garantías (sin costos ni obligaciones) y canales de contacto.
- `faq.astro`: importa `src/data/faq.json` y lo pasa a la isla React `FaqAccordion` (`client:load`).

## Components and Interfaces

### `FaqAccordion.tsx`

```ts
export const FAQ_CATEGORIAS = [
  'Marco Legal, Naturaleza y Vinculación',
  'Autonomía, Compromisos y Gratuidad',
  'Dinámica de Trabajo, Beneficios y Caracterización',
] as const;

export interface FaqItem {
  id: number;
  categoria: (typeof FAQ_CATEGORIAS)[number];
  pregunta: string;
  respuesta: string;
}
```

- Estado: `categoria` (`'Todas'` o una categoría), `searchTerm`, `openIds`.
- Render: un `<section>` por categoría con encabezado `<h2>` y sus preguntas; las categorías sin resultados se ocultan.
- Formato de respuesta: párrafos separados por `\n\n`; los párrafos que empiezan por `- ` se muestran como lista.

## Data Models

`faq.json` es contenido editorial mantenido a mano. La correspondencia id → categoría se define en `FAQ_CATEGORIES` (`scripts/rnmu_rules.py`) y la verifica `validar_json.py`.

## Error Handling

- Búsqueda sin coincidencias: mensaje explícito.
- `faq.json` inválido: falla la validación en el ETL y en el CI.

## Testing Strategy

- `python scripts/validar_json.py` (12 preguntas, claves y categorías).
- `npm run check` y `npm run build`.
- Revisión manual del texto contra el documento fuente oficial (no automatizable mientras el documento no esté en el repositorio).
