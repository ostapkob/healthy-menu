
<script>
  import { addToCart } from '../stores/cart.js';
  export let dish;
  
  let loading = false;

  const handleAdd = async () => {
    loading = true;
    addToCart(dish);
    setTimeout(() => loading = false, 300); // имитация "отклика"
  };
</script>

<div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow duration-300">
  <div class="card-body p-4">
    <h3 class="card-title text-lg font-semibold">{dish.name}</h3>
    <p class="text-info font-medium">{dish.price.toLocaleString()} ₽</p>
    {#if dish.description}
      <p class="text-sm text-base-content/70 mt-1">{dish.description}</p>
    {/if}
    <div class="card-actions justify-end mt-3">
      <button
        class="btn btn-primary btn-sm"
        class:btn-disabled={loading}
        on:click={handleAdd}
      >
        {#if loading}
          <span class="loading loading-spinner loading-xs"></span>
        {/if}
        <span>В корзину</span>
      </button>
    </div>
  </div>
</div>
