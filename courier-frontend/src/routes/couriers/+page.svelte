<script>
    import { onMount } from 'svelte';
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003'; // Значение по умолчанию для dev

    let couriers = [];

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/couriers/`);
        couriers = await response.json();
    });
</script>

<h2 class="text-xl font-bold mb-4">Курьеры</h2>

<table class="min-w-full border">
    <thead>
        <tr>
            <th class="border px-4 py-2">ID</th>
            <th class="border px-4 py-2">Имя</th>
            <th class="border px-4 py-2">Статус</th>
            <th class="border px-4 py-2">Текущий заказ</th>
        </tr>
    </thead>
    <tbody>
        {#each couriers as courier}
        <tr>
            <td class="border px-4 py-2">{courier.id}</td>
            <td class="border px-4 py-2">{courier.name}</td>
            <td class="border px-4 py-2">{courier.status}</td>
            <td class="border px-4 py-2">{courier.current_order_id || 'Нет'}</td>
        </tr>
        {/each}
    </tbody>
</table>
