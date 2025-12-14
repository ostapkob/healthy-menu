<!-- src/routes/orders/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import OrderCard from '../../components/OrderCard.svelte';

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';
  const WEB_SOCKET_URL = import.meta.env.VITE_WEB_SOCKET_URL || 'ws://localhost:8003';
  const courierId = 1;

  let orders = [];
  let ws = null;

  onMount(async () => {
    // Получаем начальные заказы
    const response = await fetch(`${API_BASE_URL}/available-orders/`);
    orders = await response.json();

    // Подключаемся к WebSocket
    ws = new WebSocket(`${WEB_SOCKET_URL}/ws/${courierId}`);

    ws.onopen = () => console.log('WebSocket connected');
    ws.onclose = () => console.log('WebSocket disconnected');

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'new_order') {
        // 🔁 Запрашиваем **полные данные** нового заказа
        try {
          const orderRes = await fetch(`${API_BASE_URL}/available-orders/`);
          const allOrders = await orderRes.json();

          // Находим только что появившийся заказ
          const newOrder = allOrders.find(o => o.id === data.order_id);

          if (newOrder) {
            orders = [newOrder, ...orders.filter(o => o.id !== newOrder.id)];
          }
        } catch (e) {
          console.error('Ошибка получения данных заказа:', e);
        }
      } else if (data.type === 'order_assigned') {
        // Удаляем заказ, если его взяли
        orders = orders.filter(o => o.id !== data.order_id);
      }
    };
  });

  onDestroy(() => {
    if (ws) ws.close();
  });
</script>

<div>
  <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
    Доступные заказы
  </h2>

  <div class="mb-4">
    <span class="badge badge-info">Количество заказов: {orders.length}</span>
  </div>

  {#if orders.length > 0}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each orders as order}
        <OrderCard {order} />
      {/each}
    </div>
  {:else}
    <div class="text-center py-12">
      <p class="text-lg text-base-content/70">Нет доступных заказов</p>
    </div>
  {/if}
</div>
