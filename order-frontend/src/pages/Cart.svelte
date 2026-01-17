<!-- src/pages/Cart.svelte -->
<script>
  import { cart, clearCart } from '../stores/cart.js';
  import CartItem from '../components/CartItem.svelte';
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';
  import { base } from '$app/paths';
  let submitting = false;

  $: total = $cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  const placeOrder = async () => {
    if ($cart.length === 0) return;
    submitting = true;
    try {
      const order = {
        user_id: 1,
        items: $cart.map(item => ({
          dish_id: item.id,
          quantity: item.quantity
        }))
      };
      const res = await fetch(`${API_BASE_URL}/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(order)
      });
      if (res.ok) {
        alert('✅ Заказ успешно оформлен!');
        clearCart();
      } else {
        alert('❌ Ошибка: не удалось отправить заказ');
      }
    } catch (e) {
      alert('⚠️ Произошла ошибка при подключении к серверу');
    } finally {
      submitting = false;
    }
  };
</script>

<div class="py-2">
  <h1 class="text-3xl font-bold text-center mb-6">🛒 Корзина</h1>

  {#if $cart.length === 0}
    <div class="text-center py-12">
      <p class="text-xl text-base-content/70 mb-4">Ваша корзина пуста</p>
      <a href="{base}/" class="btn btn-outline btn-primary">Выбрать блюда</a>
    </div>
  {:else}
    <div class="space-y-4 mb-6">
      {#each $cart as item}
        <CartItem {item} />
      {/each}
    </div>

    <div class="card bg-base-200 rounded-box p-4 mb-6">
      <div class="flex justify-between text-lg font-semibold">
        <span>Итого:</span>
        <span>{total.toFixed(2)} ₽</span>
      </div>
    </div>

    <div class="flex flex-col sm:flex-row gap-3 justify-center">
      <button
        class="btn btn-outline btn-error"
        on:click={clearCart}
        disabled={$cart.length === 0}
      >
        Очистить корзину
      </button>
      <button
        class="btn btn-primary flex items-center gap-2"
        class:btn-disabled={submitting}
        on:click={placeOrder}
      >
        {#if submitting}
          <span class="loading loading-spinner loading-xs"></span>
        {/if}
        Оформить заказ ({total.toFixed(2)} ₽)
      </button>
    </div>
  {/if}
</div>
