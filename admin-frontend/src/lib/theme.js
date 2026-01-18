// src/lib/theme.js

import { writable } from 'svelte/store';

// Поддерживаемые темы (совместимы с daisyUI)
const THEMES = ['light', 'dark', 'corporate', 'emerald', 'coffee', 'lemonade'];

// Получаем сохранённую или системную тему
export const theme = writable(getStoredTheme());

function getStoredTheme() {
  if (typeof window === 'undefined') return 'lemonade'; // default для админки

  const saved = localStorage.getItem('theme');
  if (saved && THEMES.includes(saved)) return saved;

  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }

  return 'corporate';
}

// Устанавливаем тему и сохраняем
export function setTheme(newTheme) {
  if (!THEMES.includes(newTheme)) return;
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  theme.set(newTheme);
}

// Применяем начальную тему без мигания
if (typeof window !== 'undefined') {
  setTheme(getStoredTheme());

  // Следим за системной темой (только если нет ручного выбора)
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const handleChange = (e) => {
    const saved = localStorage.getItem('theme');
    if (!saved || saved === 'light' || saved === 'dark') {
      setTheme(e.matches ? 'dark' : 'corporate');
    }
  };
  mediaQuery.addEventListener('change', handleChange);
}
