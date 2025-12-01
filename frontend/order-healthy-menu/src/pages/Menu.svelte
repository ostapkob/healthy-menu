<script>
    import { onMount } from 'svelte';
    import DishCard from '../components/DishCard.svelte';

    let dishes = [];

    onMount(async () => {
        const response = await fetch('http://localhost:8002/menu/');
        dishes = await response.json();
    });
</script>

<h1>Меню</h1>
{#each dishes as dish}
    <DishCard {dish} />
{/each}
