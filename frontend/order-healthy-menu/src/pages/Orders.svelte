<script>
    import { onMount } from 'svelte';

    let orders = [];

    onMount(async () => {
        const response = await fetch('http://localhost:8002/orders/1'); // user_id = 1
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
