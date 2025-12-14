<!-- src/components/OrderCard.svelte -->
<script>
    import { courierId } from '../stores/courier.js';

    export let order;
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';

    let isAccepting = false; // для отображения состояния

    const acceptOrder = async () => {
        isAccepting = true;

        // Ждём полсекунды (500мс) с активным спиннером
        await new Promise(resolve => setTimeout(resolve, 500));

        try {
            const response = await fetch(`${API_BASE_URL}/assign-delivery/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    courier_id: $courierId,
                    order_id: order.id
                })
            });

            if (response.ok) {
                // alert('Заказ принят');
                // window.location.reload(); // обновить список
            } else {
                alert('Ошибка при принятии заказа');
            }
        } catch (e) {
            alert('Ошибка сети');
        } finally {
            isAccepting = false;
        }
    };
</script>

<div class="border p-4 mb-2 rounded bg-base-100 shadow-sm">
    <p>Заказ #{order.id}</p>
    <p>Цена: {order.total_price} ₽</p>
    <p>Статус: {order.status}</p>
    <button
        on:click={acceptOrder}
        class="btn btn-success btn-sm transition-all duration-150 active:scale-95 disabled:opacity-50"
        disabled={isAccepting}
        aria-label="Принять заказ"
    >
        {#if isAccepting}
            <span class="loading loading-spinner loading-xs"></span>
            Принимаю...
        {:else}
            Принять
        {/if}
    </button>
</div>
