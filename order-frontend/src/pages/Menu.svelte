<script>
  import { onMount } from 'svelte';
  import DishCard from '../components/DishCard.svelte';
  // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';
  const API_BASE_URL = window.location.origin;
  let dishes = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/order/dishes/menu/`);
      dishes = await res.json();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="py-2">
  <h1 class="text-3xl font-bold text-center mb-6">🍽️ Меню</h1>

  {#if loading}
    <div class="flex justify-center items-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if dishes.length === 0}
    <div class="text-center py-12">
      <p class="text-lg text-base-content/70">Меню пока пусто</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each dishes as dish}
        <DishCard {dish} />
      {/each}
    </div>
  {/if}
</div>
