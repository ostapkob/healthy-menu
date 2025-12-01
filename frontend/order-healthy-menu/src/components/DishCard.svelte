<script>
    import { addToCart } from '../stores/cart.js';

    export let dish;

    const handleAdd = () => {
        addToCart(dish);
    };
</script>

<div class="dish-card">
    <h3>{dish.name}</h3>
    <p>Цена: {dish.price} ₽</p>
    <button on:click={handleAdd}>Добавить в корзину</button>
</div>

<style>
    .dish-card {
        border: 1px solid #ccc;
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 4px;
    }
</style>
