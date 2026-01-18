<!-- src/pages/Orders.svelte -->
<script>
  import { onMount } from 'svelte';
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';
  let orders = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/orders/1`); // user_id = 1
      orders = await res.json();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  const statusBadge = (status) => {
    const map = {
      'pending': 'badge-warning',
      'confirmed': 'badge-info',
      'completed': 'badge-success',
      'cancelled': 'badge-error',
    };
    return map[status] || 'badge-neutral';
  };
</script>

<div class="py-2">
  <h1 class="text-3xl font-bold text-center mb-6">📋 Мои заказы</h1>

  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if orders.length === 0}
    <div class="text-center py-12">
      <p class="text-lg text-base-content/70 mb-4">Пока нет заказов</p>
      <a href="/" class="btn btn-outline btn-primary">Заказать еду</a>
    </div>
  {:else}
    <div class="space-y-4">
      {#each orders as order}
        <div class="card bg-base-100 shadow-sm">
          <div class="card-body">
            <div class="flex justify-between items-start">
              <h2 class="card-title">Заказ #{order.id}</h2>
              <span class={`badge ${statusBadge(order.status)}`}>{order.status}</span>
            </div>
            <p class="text-xl font-bold text-success">Итого: {order.total_price} ₽</p>
            <p class="text-sm text-base-content/70">
              📅 {new Date(order.created_at).toLocaleString('ru-RU')}
            </p>
            {#if order.items && order.items.length > 0}
              <div class="text-sm mt-2">
                <strong>Состав:</strong>
                <ul class="list-disc pl-5 mt-1">
                  {#each order.items as item}
                    <li>{item.dish_name} × {item.quantity}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
