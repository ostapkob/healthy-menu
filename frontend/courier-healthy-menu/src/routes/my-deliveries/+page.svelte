<script>
    import { onMount } from 'svelte';

    let deliveries = [];
    const courierId = 1; // FIX можно заменить на логин
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003'; // Значение по умолчанию для dev

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/my-deliveries/${courierId}`);
        deliveries = await response.json();
    });

    const updateStatus = async (deliveryId, newStatus) => {
        const response = await fetch(`${API_BASE_URL}/update-delivery-status/${deliveryId}?status=${newStatus}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            // обновляем статус в списке
            deliveries = deliveries.map(d =>
                d.id === deliveryId ? { ...d, status: newStatus } : d
            );
        } else {
            alert('Ошибка обновления статуса');
        }
    };
</script>

<h2 class="text-xl font-bold mb-4">Мои доставки</h2>

{#if deliveries.length > 0}
    <table class="min-w-full border">
        <thead>
            <tr>
                <th class="border px-4 py-2">ID доставки</th>
                <th class="border px-4 py-2">ID заказа</th>
                <th class="border px-4 py-2">Статус</th>
                <th class="border px-4 py-2">Действия</th>
            </tr>
        </thead>
        <tbody>
            {#each deliveries as delivery}
            <tr>
                <td class="border px-4 py-2">{delivery.id}</td>
                <td class="border px-4 py-2">{delivery.order_id}</td>
                <td class="border px-4 py-2">{delivery.status}</td>
                <td class="border px-4 py-2">
                    {#if delivery.status === 'assigned'}
                        <button on:click={() => updateStatus(delivery.id, 'picked_up')} class="bg-blue-500 text-white px-2 py-1">Забрал</button>
                    {:else if delivery.status === 'picked_up'}
                        <button on:click={() => updateStatus(delivery.id, 'delivered')} class="bg-green-500 text-white px-2 py-1">Доставлен</button>
                    {/if}
                </td>
            </tr>
            {/each}
        </tbody>
    </table>
{:else}
    <p>У вас нет активных доставок</p>
{/if}
