<script>
    import { removeFromCart } from '../stores/cart.js';

    export let item;

    const handleRemove = () => {
        removeFromCart(item.id);
    };
</script>

<div class="cart-item">
    <span>{item.name} x {item.quantity} = {(item.price * item.quantity).toFixed(2)} ₽</span>
    <button on:click={handleRemove}>Удалить</button>
</div>

<style>
    .cart-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        border-bottom: 1px solid #eee;
    }
</style>
