<script>
  import { base } from '$app/paths';
  import { theme, setTheme } from '$lib/theme.js';
  import { onMount } from 'svelte';

  let mounted = false;
  onMount(() => mounted = true);
	import '../app.css'; 

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
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        Courier Service
      </h1>
    </div>
    <nav class="flex-1 p-2">
      <ul class="menu bg-base-200">
        <li><a href="{base}/profile" class="flex items-center gap-2"><span>👤</span> Профиль</a></li>
        <li><a href="{base}/orders" class="flex items-center gap-2"><span>📦</span> Доступные заказы</a></li>
        <li><a href="{base}/my-deliveries" class="flex items-center gap-2"><span>🚚</span> Мои доставки</a></li>
      </ul>
    </nav>
  </div>

  <!-- Main content -->
  <div class="flex-1 flex flex-col">
    <!-- Topbar -->
    <div class="navbar bg-base-200 border-b px-4">
      <div class="flex-1">
        <h2 class="text-lg font-semibold">Courier Dashboard</h2>
      </div>
      <div class="flex-none">
        {#if mounted}
          <button class="btn btn-ghost btn-square" on:click={toggleTheme} aria-label="Тема">
            {#if $theme === 'dark'}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" /></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414z" clip-rule="evenodd" /></svg>
            {/if}
          </button>
        {/if}
      </div>
    </div>

    <main class="flex-1 p-6 overflow-auto">
      <slot />
    </main>
  </div>
</div>
