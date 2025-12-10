<script>
    import { onMount } from 'svelte';
    import DishCard from '../components/DishCard.svelte';
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'; // Значение по умолчанию для dev

    let dishes = [];

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/menu/`);
        dishes = await response.json();
    });
</script>

<h1>Меню</h1>
{#each dishes as dish}
    <DishCard {dish} />
{/each}
