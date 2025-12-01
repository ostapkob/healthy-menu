<script>
    export let items = [];
    let selectedId = null;

    const deleteItem = async (id) => {
        if (confirm('Удалить запись?')) {
            await fetch(`http://localhost:8001/dish-ingredients/${id}`, {
                method: 'DELETE'
            });
            // обновить список
            window.location.reload();
        }
    };
</script>

<table class="min-w-full border">
    <thead>
        <tr>
            <th class="border px-4 py-2">ID</th>
            <th class="border px-4 py-2">Блюдо</th>
            <th class="border px-4 py-2">Ингредиент</th>
            <th class="border px-4 py-2">Граммы</th>
            <th class="border px-4 py-2">Действия</th>
        </tr>
    </thead>
    <tbody>
        {#each items as item}
        <tr>
            <td class="border px-4 py-2">{item.id}</td>
            <td class="border px-4 py-2">{item.dish_id}</td>
            <td class="border px-4 py-2">{item.ingredient_id}</td>
            <td class="border px-4 py-2">{item.amount_grams}</td>
            <td class="border px-4 py-2">
                <button on:click={() => deleteItem(item.id)} class="text-red-500">Удалить</button>
            </td>
        </tr>
        {/each}
    </tbody>
</table>
