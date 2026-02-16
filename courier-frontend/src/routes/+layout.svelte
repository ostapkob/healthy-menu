<script>
  import { base } from '$app/paths';
  import { theme, setTheme } from '$lib/theme.js';
  import { onMount } from 'svelte';
  import '../app.css';

  // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';
  const API_BASE_URL = window.location.origin;



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

  // FIX Статус курьера
  let courierStatus = 'offline';
  let courierName = 'Курьер #1';
  let courierPhoto = null;

  onMount(async () => {
    const res = await fetch(`${API_BASE_URL}/api/v1/courier/couriers/1`);
    const data = await res.json();
    courierName = data.name;
    courierStatus = data.status;
    courierPhoto = data.photo_url;
  });
</script>

<div class="flex min-h-screen bg-base-100">
  <!-- Mobile Menu Overlay -->
  {#if sidebarOpen}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      on:click={toggleSidebar}
      aria-hidden="true"
    ></div>
  {/if}

  <!-- Sidebar -->
  <aside
    class="fixed lg:static inset-y-0 left-0 z-50 w-64 bg-base-200 flex flex-col border-r border-base-300 transform transition-transform duration-300 ease-in-out lg:transform-none lg:transition-none {sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0"
    role="navigation"
    aria-label="Основная навигация"
  >
    <!-- Mobile Close Button -->
    <button
      class="lg:hidden absolute top-4 right-4 btn btn-ghost btn-circle btn-sm"
      on:click={toggleSidebar}
      aria-label="Закрыть меню"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Шапка с профилем -->
    <div class="p-4 border-b border-base-300 flex items-center gap-3">
      <div class="avatar">
        <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
          {#if courierPhoto}
            <img src={courierPhoto} alt="Фото курьера" class="w-full h-full object-cover rounded-full" />
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          {/if}
        </div>
      </div>

      <div class="flex-1 min-w-0">
        <div class="font-semibold text-sm truncate">{courierName}</div>
        <div class="text-xs mt-1">
          <span class={`badge badge-xs ${
            courierStatus === 'available' ? 'badge-success' :
            courierStatus === 'offline' ? 'badge-error' :
            'badge-warning'
          }`}>
            {courierStatus === 'available' ? '🟢 Онлайн' :
             courierStatus === 'offline' ? '🔴 Офлайн' :
             '🟡 В пути'}
          </span>
        </div>
      </div>
    </div>

    <!-- Меню -->
    <nav class="flex-1 p-4">
      <ul class="menu bg-base-200 space-y-2">
        <li>
          <a href="{base}/profile" class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors">
            <span class="text-lg">👤</span>
            <span class="text-sm font-medium">Профиль</span>
          </a>
        </li>
        <li>
          <a href="{base}/orders" class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors">
            <span class="text-lg">📦</span>
            <span class="text-sm font-medium">Доступные заказы</span>
          </a>
        </li>
        <li>
          <a href="{base}/my-deliveries" class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-300 transition-colors">
            <span class="text-lg">🚚</span>
            <span class="text-sm font-medium">Мои доставки</span>
          </a>
        </li>
      </ul>
    </nav>
  </aside>

  <!-- Main content -->
  <div class="flex-1 flex flex-col min-w-0">
    <!-- Topbar -->
    <header class="navbar bg-base-200 border-b border-base-300 px-4 py-3">
      <div class="flex-1 flex items-center">
        <!-- Mobile Menu Button -->
        <button
          class="lg:hidden btn btn-ghost btn-circle mr-2"
          on:click={toggleSidebar}
          aria-label="Открыть меню"
          aria-expanded={sidebarOpen}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div class="flex items-center gap-3">
          <div class="lg:hidden">
            <div class="avatar">
              <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                {#if courierPhoto}
                  <img src={courierPhoto} alt="Фото курьера" class="w-full h-full object-cover rounded-full" />
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                {/if}
              </div>
            </div>
          </div>

          <h1 class="text-lg md:text-xl font-semibold truncate">Courier Dashboard</h1>
        </div>
      </div>

      <div class="flex-none flex items-center gap-2">
        <!-- Mobile Status Badge -->
        <div class="lg:hidden">
          <span class={`badge badge-sm ${
            courierStatus === 'available' ? 'badge-success' :
            courierStatus === 'offline' ? 'badge-error' :
            'badge-warning'
          }`}>
            {courierStatus === 'available' ? '🟢' :
             courierStatus === 'offline' ? '🔴' :
             '🟡'}
          </span>
        </div>

        {#if mounted}
          <button
            class="btn btn-ghost btn-square btn-sm md:btn-md"
            on:click={toggleTheme}
            aria-label="Переключить тему"
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
      </div>
    </header>

    <main class="flex-1 p-4 md:p-6 overflow-auto">
      <slot />
    </main>
  </div>
</div>

<style>
  /* Анимация для мобильного меню */
  aside {
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }

  /* Улучшаем скролл на мобильных */
  @media (max-width: 1023px) {
    aside {
      max-width: 85%;
    }

    main {
      -webkit-overflow-scrolling: touch;
    }
  }

  @media (max-width: 768px) {
    aside {
      max-width: 280px;
    }
  }
</style>
