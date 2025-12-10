<script>
    import { onMount } from 'svelte';
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'; // Значение по умолчанию для dev
    let orders = [];

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/orders/1`); // FIX user_id = 1
        orders = await response.json();
    });
</script>

<h1>Мои заказы</h1>
{#if orders.length === 0}
    <p>У вас нет заказов</p>
{:else}
    {#each orders as order}
        <div class="order">
            <p>Заказ #{order.id}, статус: {order.status}</p>
            <p>Цена: {order.total_price} ₽</p>
            <p>Создан: {order.created_at}</p>
        </div>
    {/each}
{/if}

<style>
    .order {
        border: 1px solid #ccc;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
