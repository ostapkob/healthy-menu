<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  export let params;
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  
  let dish = null;
  let allFood = [];
  let loading = true;
  let saving = false;
  let foodSearch = '';
  
  onMount(async () => {
    await Promise.all([
      fetchDish(),
      fetchFoodList()
    ]);
  });
  
  async function fetchDish() {
    try {
      const res = await fetch(`${API_BASE_URL}/tech/dishes/${params.id}`);
      if (res.ok) {
        dish = await res.json();
      }
    } catch(e) {
      alert('Ошибка загрузки карты');
    }
  }
  
  async function fetchFoodList() {
    try {
      const res = await fetch(`${API_BASE_URL}/foods/?limit=100`);
      if (res.ok) {
        const data = await res.json();
        allFood = data.items;
      }
    } catch(e) {
      console.error('Ошибка загрузки продуктов');
    } finally {
      loading = false;
    }
  }
  
  async function updateIngredients() {
    saving = true;
    try {
      const res = await fetch(`${API_BASE_URL}/tech/dishes/${params.id}/ingredients`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ingredients: dish.ingredients.map(ing => ({
            food_id: ing.food_id,
            amount_grams: ing.amount_grams
          }))
        })
      });
      
      if (res.ok) {
        alert('✅ Состав обновлен');
        goto('/tech');
      }
    } catch(e) {
      alert('❌ Ошибка обновления');
    } finally {
      saving = false;
    }
  }
  
  function addIngredient() {
    // Здесь можно добавить интерфейс для добавления новых ингредиентов
  }
  
  function updateIngredientGrams(index, value) {
    dish.ingredients[index].amount_grams = +value;
    dish.ingredients = [...dish.ingredients];
  }
  
  function removeIngredient(index) {
    dish.ingredients = dish.ingredients.filter((_, i) => i !== index);
  }
</script>

<div class="max-w-4xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <div>
      <a href="/tech" class="btn btn-ghost btn-sm mb-2">← Назад</a>
      <h2 class="text-2xl font-bold">✏️ Редактирование состава: {dish?.name}</h2>
    </div>
  </div>
  
  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if dish}
    <div class="space-y-6">
      <div class="card bg-base-100 shadow-md">
        <div class="card-body">
          <h3 class="card-title">📦 Состав блюда</h3>
          
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Продукт</th>
                  <th>FDC ID</th>
                  <th>Категория</th>
                  <th>Количество (г)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {#each dish.ingredients as ing, i}
                  <!-- Создаем локальную переменную через обычный JS -->
                  {@const food = allFood.find(f => f.fdc_id === ing.food_id)}
                  <tr>
                    <td>
                      <div class="font-medium">{food?.name || 'Продукт не найден'}</div>
                      {#if food?.description_en}
                        <div class="text-xs opacity-75">{food.description_en}</div>
                      {/if}
                    </td>
                    <td class="font-mono">#{ing.food_id}</td>
                    <td>{food?.category_name || '—'}</td>
                    <td>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        class="input input-bordered input-sm w-24"
                        value={ing.amount_grams}
                        on:input={(e) => updateIngredientGrams(i, e.target.value)}
                      />
                    </td>
                    <td>
                      <button 
                        class="btn btn-xs btn-ghost text-error"
                        on:click={() => removeIngredient(i)}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          
          <div class="bg-base-200 p-4 rounded-lg mt-4">
            <div class="flex justify-between items-center">
              <div class="text-lg">
                Общий вес: <strong>{dish.ingredients.reduce((sum, ing) => sum + ing.amount_grams, 0).toFixed(1)} г</strong>
              </div>
              <div class="text-sm opacity-75">
                {dish.ingredients.length} ингредиентов
              </div>
            </div>
          </div>
          
          <div class="card-actions justify-end mt-6">
            <button 
              class="btn btn-primary"
              on:click={updateIngredients}
              disabled={saving}
            >
              {#if saving}
                <span class="loading loading-spinner"></span>
              {/if}
              Сохранить изменения
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
