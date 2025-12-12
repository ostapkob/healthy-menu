<script>
  export let items = [];
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

  const deleteItem = async (id) => {
    if (!confirm('Удалить запись?')) return;
    await fetch(`${API_BASE_URL}/dish-ingredients/${id}`, { method: 'DELETE' });
    window.location.reload(); // или обнови через store
  };
</script>

<div class="overflow-x-auto">
  <table class="table table-zebra w-full">
    <thead>
      <tr>
        <th>Блюдо</th>
        <th>Ингредиент</th>
        <th>Граммы</th>
        <th class="w-24">Действия</th>
      </tr>
    </thead>
    <tbody>
      {#each items as item}
        <tr>
          <td>{item.dish?.name || item.dish_id}</td>
          <td>{item.ingredient?.name || item.ingredient_id}</td>
          <td>{item.amount_grams} г</td>
          <td>
            <button
              class="btn btn-ghost btn-xs text-error"
              on:click={() => deleteItem(item.id)}
            >
              🗑️
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
