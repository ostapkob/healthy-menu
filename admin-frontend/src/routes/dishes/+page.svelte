<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  const API_BASE_URL = window.location.origin; // или с добавлением пути /api
  let dishes = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/dishes/`);
      dishes = await res.json();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  const deleteDish = async (id) => {
    if (!confirm('Удалить блюдо? Это действие нельзя отменить.')) return;
    await fetch(`${API_BASE_URL}/api/v1/admin/dishes/${id}`, { method: 'DELETE' });
    dishes = dishes.filter(d => d.id !== id);
  };
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-2xl font-bold">🍽️ Блюда</h2>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if dishes.length === 0}
    <div class="text-center py-12 text-base-content/70">
      <p>Нет блюд. Добавьте первое в технологической карте</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each dishes as dish}
        <div class="card bg-base-100 shadow-md">
          <div class="bg-gray-200 aspect-video flex items-center justify-center">
            {#if dish.image_url}
              <img
                src={dish.image_url}
                alt={dish.name}
                class="w-full h-full object-cover"
                loading="lazy"
              />
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            {/if}
          </div>
          <div class="card-body p-4">
            <h3 class="font-bold">{dish.name}</h3>
            <p class="text-info">₽{dish.price.toLocaleString()}</p>
            <div class="card-actions justify-end mt-3 space-x-2">
              <a href={`${base}/dishes/${dish.id}`} class="btn btn-ghost btn-xs">✏️ Редактировать</a>
              <button
                class="btn btn-ghost btn-xs text-error"
                on:click={() => deleteDish(dish.id)}
              >
                🗑️ Удалить
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
