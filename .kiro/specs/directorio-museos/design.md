# Design Document: Directorio Interactivo de Museos

## Overview

El directorio es una página estática de Astro (`src/pages/directorio.astro`) que importa `src/data/museos.json` en tiempo de build y lo pasa a una isla React (`DirectorioMuseos`, `client:load`) que resuelve búsqueda, filtros y paginación en el navegador. No hay backend ni llamadas de red.

## Architecture

```
data-raw/*.csv (local, ignorado)
   └─ scripts/limpiar_base.py ── usa ── scripts/rnmu_rules.py
         └─ valida en memoria con scripts/validar_json.py
               └─ src/data/museos.json + stats.json
                     └─ src/pages/directorio.astro
                           └─ <DirectorioMuseos client:load initialMuseos={...} />
```

## Components and Interfaces

### `DirectorioMuseos.tsx`

```ts
export type EstadoAtencion =
  'Abierto' | 'Cita previa' | 'Cerrado temporalmente' | 'Cerrado' | 'Sin información';

export interface Museo {
  id: number;
  nombre: string;
  universidad: string;
  naturaleza: 'Pública' | 'Privada' | 'No especificada';
  departamento: string;
  ciudad: string;
  direccion: string | null;
  tipologia: string | null;
  estadoAtencion: EstadoAtencion;
  registroSimco: 'Sí' | 'No' | 'En proceso / Por confirmar' | 'Sin información';
  paginaWeb: string | null;
  correoInstitucional: string | null;
}
```

- Estado local: `searchTerm`, `selectedDept`, `selectedNaturaleza`, `selectedEstado`, `selectedSimco`, `viewMode` (`grid` | `table`), `currentPage`.
- `filteredMuseos` y `paginatedMuseos` se calculan con `useMemo`.
- `EstadoBadge` centraliza la insignia de estado (clase CSS, etiqueta y punto verde solo para "Abierto").

### Estilos

Insignias en `src/styles/global.css`: `badge-pub`, `badge-priv`, `badge-open`, `badge-appointment`, `badge-closed`, `badge-unknown`, `badge-simco`.

## Data Models

Los catálogos de `naturaleza`, `estadoAtencion` y `registroSimco` se definen en `scripts/rnmu_rules.py` y deben coincidir con los tipos TypeScript. `validar_json.py` garantiza que el JSON no contenga valores fuera de catálogo.

## Error Handling

- Campos `null` (`direccion`, `tipologia`, `paginaWeb`, `correoInstitucional`) se muestran como ausentes o "Sin información"; nunca rompen el render.
- Si el JSON no cumple el esquema, el CI falla en `validar_json.py` o en `astro check`, antes del despliegue.

## Testing Strategy

- `python scripts/validar_json.py`: esquema, catálogos, correos y cuadre de estadísticas.
- `npm run check`: tipos de `.astro`, `.ts` y `.tsx`.
- `npm run build`: genera `dist/directorio/index.html` sin errores.
