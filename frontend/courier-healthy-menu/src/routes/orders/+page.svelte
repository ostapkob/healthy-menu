<script>
    import { onMount, onDestroy } from 'svelte';
    import OrderCard from '../../components/OrderCard.svelte';
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003'; // Значение по умолчанию для dev

    let orders = [];
    let ws = null;

    onMount(async () => {
        // Получаем начальные заказы
        const response = await fetch(`${API_BASE_URL}/available-orders/`);
        orders = await response.json();

        // Подключаемся к WebSocket
        ws = new WebSocket(__WEB_SOCKET_URL__ + '/ws/1'); // FIX courier_id = 1

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'new_order') {
                // Добавляем новый заказ в список
                const newOrder = {
                    id: data.order_id,
                    total_price: 'N/A',
                    status: 'pending'
                };
                orders = [newOrder, ...orders];
            }
        };
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<h2 class="text-xl font-bold mb-4">Доступные заказы</h2>

{#if orders.length > 0}
    {#each orders as order}
        <OrderCard {order} />
    {/each}
{:else}
    <p>Нет доступных заказов</p>
{/if}
