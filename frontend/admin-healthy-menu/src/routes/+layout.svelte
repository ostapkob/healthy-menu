<script>
  import { base } from '$app/paths';
  import { theme, setTheme } from '$lib/theme.js';
  import { onMount } from 'svelte';
	import '../app.css'; 

  let mounted = false;
  onMount(() => {
    mounted = true;
  });

  const toggleTheme = () => {
    const current = $theme;
    const next = current === 'lemonade' ? 'dark' : 'lemonade';
    setTheme(next);
  };
</script>

<div class="flex min-h-screen bg-base-100">
  <!-- Sidebar -->
  <div class="w-64 bg-base-200 flex flex-col">
    <div class="p-4 border-b">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
        </svg>
        HealthyMenu Admin
      </h1>
    </div>
    <nav class="flex-1 p-2">
      <ul class="menu bg-base-200">
        <li><a href="{base}/" class="flex items-center gap-2"><span>🏠</span> Главная</a></li>
        <li><a href="{base}/dishes" class="flex items-center gap-2"><span>🍽️</span> Блюда</a></li>
        <li><a href="{base}/dish-ingredients" class="flex items-center gap-2"><span>🥬</span> Состав блюд</a></li>
        <li><a href="{base}/coverage" class="flex items-center gap-2"><span>📊</span> Покрытие витаминов</a></li>
      </ul>
    </nav>
  </div>

  <!-- Main content -->
  <div class="flex-1 flex flex-col">
    <!-- Topbar -->
    <div class="navbar bg-base-200 border-b px-4">
      <div class="flex-1">
        <h2 class="text-lg font-semibold">Админ-панель</h2>
      </div>
      <div class="flex-none">
        {#if mounted}
          <button
            class="btn btn-ghost btn-square"
            on:click={toggleTheme}
            aria-label="Тема"
          >
            {#if $theme === 'dark'}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" /></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414z" clip-rule="evenodd" /></svg>
            {/if}
          </button>
        {/if}
      </div>
    </div>

    <!-- Page content -->
    <main class="flex-1 p-6 overflow-auto">
      <slot />
    </main>
  </div>
</div>
