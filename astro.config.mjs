// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// The site is deployed as plain files over FTPS to shared Apache hosting.
// There is no Node runtime on the server, so the output must be fully static.
export default defineConfig({
  site: 'https://paniagua.dev',
  output: 'static',
  trailingSlash: 'ignore',

  // English sits at the root, French under /fr/. Both are emitted as static
  // files and cross-linked with hreflang, so search engines serve the right
  // one to a Geneva prospect and to an international reader alike.
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr'],
    routing: { prefixDefaultLocale: false },
  },

  integrations: [
    sitemap({
      i18n: { defaultLocale: 'en', locales: { en: 'en', fr: 'fr-CH' } },
    }),
  ],

  build: {
    // Apache serves /styles/*.css straight from disk. Keeping assets in a
    // predictable folder makes the .htaccess cache rules readable.
    assets: 'assets',
    inlineStylesheets: 'auto',
  },

  image: {
    // Responsive derivatives are generated at build time by sharp.
    responsiveStyles: true,
  },

  vite: {
    plugins: [tailwindcss()],
    build: {
      // Lightning CSS folds `animation-timeline` into the `animation`
      // shorthand, producing `animation: linear both rise view()`. Chrome
      // rejects that outright, which silently kills every scroll-driven
      // animation on the page. esbuild's CSS minifier leaves them alone.
      cssMinify: 'esbuild',
    },
  },
});
