# Requirements Document: Caracterización y Contacto Institucional

## Introduction

Este módulo guía a las Instituciones de Educación Superior (IES) interesadas en registrar, actualizar y caracterizar sus museos y colecciones, y resuelve dudas sobre compromisos y beneficios mediante las 12 preguntas frecuentes oficiales. Comprende `src/pages/caracterizacion.astro`, `src/pages/faq.astro`, `src/components/FaqAccordion.tsx` y `src/data/faq.json`.

## Requirements

### Requirement 1: Llamado a la acción de caracterización

**User Story:** Como representante de una IES, quiero saber cómo caracterizar mi museo, para iniciar el proceso sin dudas.

#### Acceptance Criteria

1. THE sistema SHALL ofrecer contacto directo por correo a `reddemuseosuniversitarios@gmail.com` (enlace `mailto:` con asunto prellenado).
2. THE sistema SHALL ofrecer el canal de WhatsApp de apoyo `+57 316 496 3906` mediante `wa.me` con `rel="noopener noreferrer"`.
3. THE sistema SHALL explicar que la caracterización NO genera costos, obligaciones jurídicas ni adhesión formal.
4. THE sistema SHALL informar que la coordinación vigente corresponde al Museo de Trajes de la Universidad de América.

### Requirement 2: Preguntas frecuentes categorizadas

**User Story:** Como directivo universitario, quiero consultar las preguntas frecuentes por tema, para encontrar rápido la respuesta que necesito.

#### Acceptance Criteria

1. THE `faq.json` SHALL contener exactamente 12 preguntas con las claves `id`, `categoria`, `pregunta` y `respuesta`.
2. THE preguntas SHALL agruparse en tres categorías:
   - "Marco Legal, Naturaleza y Vinculación": 1, 3, 5, 6.
   - "Autonomía, Compromisos y Gratuidad": 2, 4, 9, 11.
   - "Dinámica de Trabajo, Beneficios y Caracterización": 7, 8, 10, 12.
3. THE textos de `pregunta` y `respuesta` SHALL ser íntegros respecto al documento fuente oficial de la Red.
4. THE sistema SHALL ofrecer un selector de categoría (incluida la opción "Todas") y mostrar las preguntas agrupadas bajo el encabezado de su categoría.
5. THE sistema SHALL permitir buscar texto en preguntas y respuestas, y desplegar o colapsar todas.
6. WHEN `faq.json` no cumple 2.1 o 2.2 THEN `validar_json.py` SHALL fallar con código 1.

### Requirement 3: Accesibilidad

**User Story:** Como usuario de teclado o lector de pantalla, quiero operar el acordeón, para acceder a las respuestas.

#### Acceptance Criteria

1. THE botones del acordeón SHALL exponer `aria-expanded` y `aria-controls`.
2. THE botones del selector de categoría SHALL exponer `aria-pressed`.
3. THE foco SHALL ser visible en todos los controles.
