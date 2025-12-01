<script>
    import { cart, clearCart } from '../stores/cart.js';
    import CartItem from '../components/CartItem.svelte';

    let total = 0;

    $: total = $cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    const placeOrder = async () => {
        const order = {
            user_id: 1, // можно заменить на логин
            items: $cart.map(item => ({
                dish_id: item.id,
                quantity: item.quantity
            }))
        };

        const response = await fetch('http://localhost:8002/orders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(order)
        });

        if (response.ok) {
            alert('Заказ оформлен!');
            clearCart();
        } else {
            alert('Ошибка при оформлении заказа');
        }
    };
</script>

<h1>Корзина</h1>
{#if $cart.length === 0}
    <p>Корзина пуста</p>
{:else}
    {#each $cart as item}
        <CartItem {item} />
    {/each}
    <h3>Итого: {total.toFixed(2)} ₽</h3>
    <button on:click={placeOrder}>Оформить заказ</button>
{/if}
