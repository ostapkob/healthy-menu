<script>
    import { courierId } from '../stores/courier.js';

    export let order;
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003'; // Значение по умолчанию для dev

    const acceptOrder = async () => {
        const response = await fetch(`${API_BASE_URL}/assign-delivery/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                courier_id: $courierId,
                order_id: order.id
            })
        });

        if (response.ok) {
            alert('Заказ принят');
            // обновить список
            window.location.reload();
        } else {
            alert('Ошибка при принятии заказа');
        }
    };
</script>

<div class="border p-4 mb-2 rounded">
    <p>Заказ #{order.id}</p>
    <p>Цена: {order.total_price} ₽</p>
    <p>Статус: {order.status}</p>
    <button on:click={acceptOrder} class="bg-green-500 text-white px-2 py-1">Принять</button>
</div>

