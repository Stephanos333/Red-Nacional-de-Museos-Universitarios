import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: process.env.ASTRO_SITE || 'https://stephanos333.github.io',
  base: process.env.ASTRO_BASE || '/Red-Nacional-de-Museos-Universitarios/',
  integrations: [
    react(),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
});
