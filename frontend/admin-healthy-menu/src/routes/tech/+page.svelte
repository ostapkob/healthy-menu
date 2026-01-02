<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths'; 
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'; // tech API на 8002
  
  let dishes = [];
  let loading = true;
  let creating = false;
  let form = {
    name: '',
    ingredients: []
  };
  
  let allFood = []; // список всех food из FDC (пока загружаем dishes, потом сделаем отдельный endpoint)
  
  onMount(async () => {
    await Promise.all([
      fetchFoodList(),
      fetchDishes()
    ]);
  });
  
  async function fetchFoodList() {
    try {
      // ВРЕМЕННО: используем список блюд для демонстрации (fdc_id → название)
      // Позже сделаем отдельный endpoint /admin/food/
      const res = await fetch(`${API_BASE_URL}/admin/dishes/`);
      allFood = await res.json();
    } catch(e) {
      console.error('Не удалось загрузить продукты');
    }
  }
  
  async function fetchDishes() {
    try {
      // Пока нет GET /tech/dishes/, используем админский список
      const res = await fetch(`${API_BASE_URL}/admin/dishes/`);
      dishes = await res.json();
    } catch(e) {
      console.error('Не удалось загрузить блюда');
    } finally {
      loading = false;
    }
  }
  
  async function createDish() {
    if (!form.name || form.ingredients.length === 0) {
      alert('Заполните название и добавьте ингредиенты');
      return;
    }
    
    creating = true;
    try {
      const res = await fetch(`${API_BASE_URL}/tech/dishes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      
      if (res.ok) {
        const newDish = await res.json();
        dishes = [...dishes, newDish];
        form = { name: '', ingredients: [] };
        alert('✅ Блюдо создано');
      } else {
        const err = await res.json();
        alert(`❌ ${err.detail || 'Ошибка создания'}`);
      }
    } catch(e) {
      alert('❌ Ошибка сети');
    } finally {
      creating = false;
    }
  }
  
  let selectedFoodId = '';
  let gramsInput = '';
  
  function addIngredient() {
    if (!selectedFoodId || !gramsInput) {
      alert('Выберите продукт и укажите граммы');
      return;
    }
    
    if (form.ingredients.some(i => i.food_id === +selectedFoodId)) {
      alert('Ингредиент уже добавлен');
      return;
    }
    
    form.ingredients = [...form.ingredients, {
      food_id: +selectedFoodId,
      amount_grams: +gramsInput
    }];
    selectedFoodId = '';
    gramsInput = '';
  }
  
  function removeIngredient(index) {
    form.ingredients = form.ingredients.filter((_, i) => i !== index);
  }
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-2xl font-bold">🔬 Технологическая карта</h2>
    <a href="/dishes" class="btn btn-ghost">🍽️ Админ-панель</a>
  </div>
  
  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else}
    <!-- Создание блюда -->
    <div class="card bg-base-100 shadow-xl mb-8 max-w-4xl">
      <div class="card-body">
        <h3 class="card-title">➕ Новая технологическая карта</h3>
        <div class="space-y-4">
          <div>
            <label class="label">
              <span class="label-text">Название блюда *</span>
            </label>
            <input
              class="input input-bordered w-full max-w-2xl"
              placeholder="Омлет с овощами, Борщ классический, ..."
              bind:value={form.name}
            />
          </div>
          
          <!-- Добавление ингредиентов -->
          <div>
            <h4 class="font-semibold mb-3">Состав блюда</h4>
            <div class="flex flex-wrap gap-2 items-end mb-4 p-4 bg-base-200 rounded-lg">
              <select class="select select-bordered flex-1 max-w-xs" bind:value={selectedFoodId}>
                <option value="">Выберите продукт из базы FDC</option>
                {#each allFood as food}
                  <option value={food.id}>{food.name || food.fdc_id}</option>
                {/each}
              </select>
              <input
                type="number" 
                step="0.1" 
                min="0.1"
                class="input input-bordered w-28"
                placeholder="г"
                bind:value={gramsInput}
              />
              <button 
                class="btn btn-sm btn-primary" 
                on:click={addIngredient}
                disabled={!selectedFoodId || !gramsInput}
              >
                ➕ Добавить
              </button>
            </div>
            
            {#if form.ingredients.length === 0}
              <div class="alert alert-info">
                <span>Добавьте ингредиенты для блюда</span>
              </div>
            {:else}
              <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>ID продукта</th>
                      <th>Количество</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each form.ingredients as ing, i}
                      <tr>
                        <td class="font-mono text-sm">FDC #{ing.food_id}</td>
                        <td><strong>{ing.amount_grams} г</strong></td>
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
            {/if}
          </div>
          
          <button 
            class="btn btn-primary btn-lg w-full" 
            on:click={createDish}
            disabled={!form.name.trim() || form.ingredients.length === 0 || creating}
          >
            {#if creating}
              <span class="loading loading-spinner"></span>
              Создаётся...
            {:else}
              ✅ Создать технологическую карту
            {/if}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Список созданных блюд -->
    {#if dishes.length > 0}
      <div>
        <h3 class="text-xl font-bold mb-4">📋 Созданные блюда (для админа)</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each dishes as dish}
            <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
              <div class="card-body">
                <h4 class="font-bold text-lg">{dish.name}</h4>
                <div class="text-sm opacity-75 mb-3">
                  💰 {dish.price > 0 ? `₽${dish.price}` : 'Цена не задана'}
                  {dish.image_url ? '🖼️' : ''}
                </div>
                <div class="badge badge-outline badge-sm mb-2">{dish.ingredients.length} ингредиентов</div>
                <div class="card-actions justify-end">
                  <a href={`/dishes/${dish.id}`} class="btn btn-sm btn-primary">
                    ✏️ Передать админу
                  </a>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

