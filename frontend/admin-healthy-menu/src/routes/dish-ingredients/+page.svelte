<script>
    import { onMount } from 'svelte';
    import DishIngredientForm from '../../components/DishIngredientForm.svelte';
    import DishIngredientTable from '../../components/DishIngredientTable.svelte';

    let items = [];

    onMount(async () => {
        const response = await fetch('http://localhost:8001/dish-ingredients/');
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
