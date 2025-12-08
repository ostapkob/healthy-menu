import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    paths: {
      base: '/admin', // <-- Указываем базовый путь
    },
    adapter: adapter({
      pages: 'build', // Папка для статических файлов
      assets: 'build',
      fallback: 'index.html' // Для обработки SPA
    })
  }
};

