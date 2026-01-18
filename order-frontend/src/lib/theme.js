// src/lib/theme.js

import { writable } from 'svelte/store';

// Возможные темы (должны совпадать с темами в daisyUI)
const THEMES = ['light', 'dark', 'emerald', 'corporate', 'coffee'];

// Сохраняем текущую тему
export const theme = writable(getStoredTheme());

function getStoredTheme() {
  if (typeof window === 'undefined') return 'light';

  // 1. Проверяем localStorage
  const saved = localStorage.getItem('theme');
  if (saved && THEMES.includes(saved)) return saved;

  // 2. Проверяем системную тему
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }

  // 3. Дефолт
  return 'light';
}

// Устанавливает тему и сохраняет в localStorage
export function setTheme(newTheme) {
  if (!THEMES.includes(newTheme)) return;
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  theme.set(newTheme);
}

// Следим за изменением системной темы
if (typeof window !== 'undefined') {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const handleChange = (e) => {
    const saved = localStorage.getItem('theme');
    // Меняем тему автоматически, **только если пользователь не выбирал вручную**
    if (!saved || saved === 'light' || saved === 'dark') {
      setTheme(e.matches ? 'dark' : 'light');
    }
  };
  mediaQuery.addEventListener('change', handleChange);

  // Применяем начальную тему сразу (без мигания)
  setTheme(getStoredTheme());
}
