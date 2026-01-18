import adapter from '@sveltejs/adapter-static';

const basePath = process.env.SVELTEKIT_BASEPATH || '';

export default {
  kit: {
    paths: {
      base: basePath,
    },
    adapter: adapter({
      pages: 'build', // Папка для статических файлов
      assets: 'build',
      fallback: 'index.html' // Для обработки SPA
    })
  }
};

