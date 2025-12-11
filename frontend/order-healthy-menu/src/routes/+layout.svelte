<!-- src/routes/+layout.svelte -->
<script>
  import { base } from '$app/paths';
  import { theme, setTheme } from '$lib/theme.js';
  import { onMount } from 'svelte';

  let mounted = false;
  // Для плавного появления после гидратации
  onMount(() => {
    mounted = true;
  });

  const toggleTheme = () => {
    const current = $theme;
    const next = current === 'light' ? 'dark' : 'light';
    setTheme(next);
  };
</script>

<div class="min-h-screen flex flex-col bg-base-100">
  <!-- Navbar -->
  <div class="navbar bg-base-200 shadow-sm">
    <div class="navbar-start">
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </div>
        <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          <li><a href="{base}/" class="flex items-center gap-2"><span>🍽️</span> Меню</a></li>
          <li><a href="{base}/cart" class="flex items-center gap-2"><span>🛒</span> Корзина</a></li>
          <li><a href="{base}/orders" class="flex items-center gap-2"><span>📋</span> Заказы</a></li>
        </ul>
      </div>
      <a href="{base}/" class="btn btn-ghost text-xl font-bold">HealthyMenu</a>
    </div>
    <div class="navbar-end">
      <!-- Переключатель темы -->
      {#if mounted}
        <button
          class="btn btn-ghost btn-square"
          aria-label="Переключить тему"
          on:click={toggleTheme}
        >
          {#if $theme === 'dark'}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          {/if}
        </button>
        
      {/if}

      <!-- Основное меню (на десктопе) -->
      <ul class="menu menu-horizontal px-1 hidden lg:flex">
        <li><a href="{base}/"><span>🍽️</span> Меню</a></li>
        <li><a href="{base}/cart"><span>🛒</span> Корзина</a></li>
        <li><a href="{base}/orders"><span>📋</span> Заказы</a></li>
      </ul>
    </div>
  </div>

  <main class="flex-grow container mx-auto px-4 py-6 max-w-6xl">
    <slot />
  </main>

  <footer class="footer footer-center p-4 bg-base-200 text-base-content border-t">
    <aside>
      <p>© {new Date().getFullYear()} HealthyMenu. Питайтесь с умом 🌱</p>
    </aside>
  </footer>
</div>
