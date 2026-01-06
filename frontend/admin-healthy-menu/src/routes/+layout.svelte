<script>
  import { base } from '$app/paths';
  import { theme, setTheme } from '$lib/theme.js';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import '../app.css';

  let mounted = false;
  let sidebarOpen = false;
  
  onMount(() => mounted = true);

  const toggleTheme = () => {
    const current = $theme;
    const next = current === 'lemonade' ? 'dark' : 'lemonade';
    setTheme(next);
  };

  const toggleSidebar = () => {
    sidebarOpen = !sidebarOpen;
  };

  const isActive = (path) => {
    return $page.url.pathname === path || $page.url.pathname.startsWith(path + '/');
  };
</script>

<div class="flex min-h-screen bg-base-100">
  <!-- Mobile Menu Overlay -->
  {#if sidebarOpen}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      role="button"
      tabindex="0"
      aria-label="Закрыть боковое меню"
      on:click={toggleSidebar}
      on:keydown={(e) => (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') && toggleSidebar()}
    ></div>
  {/if}

  <!-- Sidebar -->
  <aside 
    class="fixed lg:static inset-y-0 left-0 z-50 w-64 bg-base-200 flex flex-col border-r border-base-300 transform transition-transform duration-300 ease-in-out lg:transform-none {sidebarOpen ? 'translate-x-0' : '-translate-x-full'}"
  >
    <!-- Mobile Close Button -->
    <button 
      class="lg:hidden absolute top-4 right-4 btn btn-ghost btn-circle btn-sm"
      on:click={toggleSidebar}
      title="Close"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Шапка -->
    <div class="p-4 border-b border-base-300">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-primary/10 rounded-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-bold truncate">HealthyMenu Admin</h1>
          <div class="text-xs text-base-content/70 mt-1">Панель управления</div>
        </div>
      </div>
    </div>

    <!-- Меню -->
    <nav class="flex-1 p-4">
      <ul class="menu bg-base-200 space-y-2">
        <li>
          <a 
            href="{base}/" 
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors {isActive(base + '/') ? 'bg-base-300 font-semibold' : ''}"
          >
            <span class="text-lg">🏠</span>
            <span class="text-sm font-medium">Главная</span>
          </a>
        </li>
        <li>
          <a 
            href="{base}/dishes" 
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors {isActive(base + '/dishes') ? 'bg-base-300 font-semibold' : ''}"
          >
            <span class="text-lg">🍽️</span>
            <span class="text-sm font-medium">Блюда (админ)</span>
          </a>
        </li>
        <li>
          <a 
            href="{base}/tech" 
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors {isActive(base + '/tech') ? 'bg-base-300 font-semibold' : ''}"
          >
            <span class="text-lg">🔬</span>
            <span class="text-sm font-medium">Технолог</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Футер -->
    <div class="p-4 border-t border-base-300">
      <div class="text-xs text-base-content/70">
        <div>Версия 2.0.0</div>
        <div class="mt-1">© 2025 HealthyMenu</div>
      </div>
    </div>
  </aside>

  <!-- Main content -->
  <div class="flex-1 flex flex-col min-w-0">
    <!-- Topbar -->
    <header class="navbar bg-base-200 border-b border-base-300 px-4 py-3">
      <div class="flex-1 flex items-center">
        <button 
          class="lg:hidden btn btn-ghost btn-circle mr-2"
          on:click={toggleSidebar}
          title="Toggle"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="lg:hidden">
            <div class="p-2 bg-primary/10 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
            </div>
          </div>
          <h1 class="text-lg md:text-xl font-semibold truncate">Админ-панель</h1>
        </div>
      </div>
      
      <div class="flex-none flex items-center gap-2">
        {#if mounted}
          <button 
            class="btn btn-ghost btn-square btn-sm md:btn-md" 
            on:click={toggleTheme} 
            title="Сменить тему"
          >
            {#if $theme === 'dark'}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414z" clip-rule="evenodd" />
              </svg>
            {/if}
          </button>
        {/if}
        <div class="dropdown dropdown-end">
          <button class="btn btn-ghost btn-circle" title="Circle">
            <div class="avatar">
              <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A7 7 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </button>
          <ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 mt-2 z-50">
            <li><a href="localhost">Профиль</a></li>
            <li><a href="localhost">Настройки</a></li>
            <li><hr class="my-1"></li>
            <li><a  href="localhost" class="text-error">Выйти</a></li>
          </ul>
        </div>
      </div>
    </header>

    <main class="flex-1 p-4 md:p-6 overflow-auto bg-base-100/50">
      <div class="max-w-7xl mx-auto">
        <slot />
      </div>
    </main>
  </div>
</div>

