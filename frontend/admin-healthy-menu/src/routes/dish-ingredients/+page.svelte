<script>
    import { onMount } from 'svelte';
    import DishIngredientForm from '../../components/DishIngredientForm.svelte';
    import DishIngredientTable from '../../components/DishIngredientTable.svelte';
    // const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для разработки
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для dev

    let items = [];

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/dish-ingredients/`);
        items = await response.json();
    });
</script>

<h2 class="text-xl font-bold mb-4">Состав блюд</h2>

<DishIngredientForm />

{#if items.length > 0}
    <DishIngredientTable {items} />
{:else}
    <p>Нет данных</p>
{/if}
