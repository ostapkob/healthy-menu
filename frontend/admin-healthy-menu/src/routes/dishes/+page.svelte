<script>
    import { onMount } from 'svelte';

    let dishes = [];
    // const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для разработки
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для dev

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/dishes/`);
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
