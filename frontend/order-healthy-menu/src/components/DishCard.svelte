<!-- src/components/DishCard.svelte -->
<script>
  import { addToCart } from '../stores/cart.js';
  import DishModal from './DishModal.svelte';

  export let dish;

  let showModal = false;

  const handleAdd = () => {
    addToCart(dish);
  };

  const handleOpenModal = () => {
    showModal = true;
  };

  const handleClose = () => {
    showModal = false;
  };

  const handleAddFromModal = () => {
    addToCart(dish);
  };
</script>

<div
  class="card bg-base-100 shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden"
  on:click={handleOpenModal}
>
  <!-- Изображение (пока заглушка) -->
  <div class="bg-gray-200 border-b aspect-video flex items-center justify-center">
    {#if dish.image_url}
      <img
        src={dish.image_url}
        alt={dish.name}
        class="w-full h-full object-cover"
        loading="lazy"
        on:error={(e) => e.target.src = '/placeholder-dish.jpg'}
      />
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    {/if}
  </div>

  <div class="card-body p-4">
    <h3 class="card-title text-lg font-semibold line-clamp-1">{dish.name}</h3>
    <p class="text-info font-medium">₽{dish.price.toLocaleString()}</p>
    {#if dish.description}
      <p class="text-sm text-base-content/70 line-clamp-2 mt-1">{dish.description}</p>
    {/if}

    <!-- Кнопка "Быстрое добавление" -->
    <div class="card-actions justify-end mt-3">
      <button
        class="btn btn-circle btn-sm btn-ghost text-primary hover:bg-primary/10 tooltip"
        data-tip="В корзину"
        on:click|stopPropagation={handleAdd}
        aria-label="В корзину"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </button>
    </div>
  </div>
</div>

<DishModal
  {dish}
  open={showModal}
  on:close={handleClose}
  on:add-to-cart={handleAddFromModal}
/>
