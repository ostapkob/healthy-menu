<script>
    import { onMount } from 'svelte';

    let dishId = '';
    let ingredientId = '';
    let amountGrams = '';
    let dishes = [];
    let ingredients = [];

    onMount(async () => {
        const [dishesRes, ingredientsRes] = await Promise.all([
            fetch('http://localhost:8001/dishes/'),
            fetch('http://localhost:8001/ingredients/')
        ]);
        dishes = await dishesRes.json();
        ingredients = await ingredientsRes.json();
    });

    const submitForm = async (e) => {
        e.preventDefault();
        const response = await fetch('http://localhost:8001/dish-ingredients/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dish_id: parseInt(dishId),
                ingredient_id: parseInt(ingredientId),
                amount_grams: parseFloat(amountGrams)
            })
        });

        if (response.ok) {
            alert('Состав добавлен');
            dishId = '';
            ingredientId = '';
            amountGrams = '';
            // обновить список
            window.location.reload();
        } else {
            alert('Ошибка');
        }
    };
</script>

<form on:submit={submitForm} class="mb-4">
    <div class="mb-2">
        <label>Блюдо:</label>
        <select bind:value={dishId} required class="border p-2">
            <option value="">Выберите блюдо</option>
            {#each dishes as dish}
                <option value={dish.id}>{dish.name}</option>
            {/each}
        </select>
    </div>
    <div class="mb-2">
        <label>Ингредиент:</label>
        <select bind:value={ingredientId} required class="border p-2">
            <option value="">Выберите ингредиент</option>
            {#each ingredients as ing}
                <option value={ing.id}>{ing.name}</option>
            {/each}
        </select>
    </div>
    <div class="mb-2">
        <label>Граммы:</label>
        <input type="number" bind:value={amountGrams} required class="border p-2" />
    </div>
    <button type="submit" class="bg-blue-500 text-white px-4 py-2">Добавить</button>
</form>
