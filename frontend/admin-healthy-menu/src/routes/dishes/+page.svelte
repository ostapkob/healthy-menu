<script>
    import { onMount } from 'svelte';

    let dishes = [];

    onMount(async () => {
        const response = await fetch('http://localhost:8001/dishes/');
        dishes = await response.json();
    });
</script>

<h2 class="text-xl font-bold mb-4">Блюда</h2>

<table class="min-w-full border">
    <thead>
        <tr>
            <th class="border px-4 py-2">ID</th>
            <th class="border px-4 py-2">Название</th>
            <th class="border px-4 py-2">Цена</th>
        </tr>
    </thead>
    <tbody>
        {#each dishes as dish}
        <tr>
            <td class="border px-4 py-2">{dish.id}</td>
            <td class="border px-4 py-2">{dish.name}</td>
            <td class="border px-4 py-2">{dish.price}</td>
        </tr>
        {/each}
    </tbody>
</table>
