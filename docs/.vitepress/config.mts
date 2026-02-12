import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "WhatsApp Integration for Frappe Helpdesk Documentation",
  description: "WhatsApp Integration for Frappe Helpdesk Documentation",
  outDir: '../helpdesk_whatsapp/www',
  assetsDir: 'assets/helpdesk_whatsapp',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Desk', link: '/' },
      { text: 'Documentation Home', link: '/helpdesk_whatsapp_introduction' },
      { text: 'Starktail', link: 'https://starktail.com' }
    ],

    sidebar: [
      { text: 'Introduction', link: '/helpdesk_whatsapp_introduction.md' }
    ],

    socialLinks: [
      { icon: 'whatsapp', link: 'https://wa.me/27686318877?text=Hi%2C%20I%20have%20a%20question%20on%20WhatsApp%20Integration%20for%20Frappe%20Helpdesk'},
      { icon: 'mailgun', link: 'mailto:support@starktail.com'},
      { icon: 'github', link: 'https://github.com/Starktail/helpdesk_whatsapp' }
    ],

    editLink: {
      pattern: 'https://github.com/Starktail/helpdesk_whatsapp/edit/version-15/docs/:path'
    }
  },
  // Set metaChunk to avoid having window.__VP_HASH_MAP__ in the generated HTML, 
  // as this blocks jinja template rendering for frappe portal pages
  metaChunk: true,
  ignoreDeadLinks: [
    // ignore all links starting with /app/ (these point to doctypes or other resources
    //  hosted on the frappe site, and won't be alive at build time)
    /^\/app\//
  ],
  // Links that point to pages outside our vitepress docs, like Doctype links should not
  // be appended with .html
  transformHtml: (code) => {
    return code.replace(/href="(\/app\/[^"]*)\.html"/g, 'href="$1"');
  },
  // Inline ALL images to avoid having images in the public directory
  vite: {
    build: {
      assetsInlineLimit: 52428800, // 50 MB,
      chunkSizeWarningLimit: 2000 // 2000 KB
    },
  },
})