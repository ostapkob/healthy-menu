<!-- ./routes/tech/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths'; 
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  
  let dishes = [];
  let loading = true;
  let creating = false;
  let form = {
    name: '',
    ingredients: []
  };
  
  let allFood = [];
  let foodLoading = false;
  let foodSearch = '';
  let foodCategory = '';
  let foodCategories = [];
  let foodPage = 0;
  const FOODS_PER_PAGE = 20;
  let hasMoreFood = true;
  
  // Список созданных блюд с ингредиентами
  let techDishes = [];
  
  onMount(async () => {
    await Promise.all([
      fetchDishes(),
      fetchTechDishes(),
      fetchFoodList(true),
      fetchCategories()
    ]);
  });
  
  async function fetchCategories() {
    try {
      // Здесь нужно добавить endpoint для категорий продуктов
      // временно используем пустой массив
      foodCategories = [];
    } catch(e) {
      console.error('Не удалось загрузить категории');
    }
  }
  
  async function fetchFoodList(reset = false) {
    if (foodLoading) return;
    
    foodLoading = true;
    try {
      const params = new URLSearchParams({
        limit: FOODS_PER_PAGE.toString(),
        offset: (reset ? 0 : foodPage * FOODS_PER_PAGE).toString()
      });
      
      if (foodSearch) params.set('q', foodSearch);
      if (foodCategory) params.set('category_id', foodCategory);
      
      const res = await fetch(`${API_BASE_URL}/foods/?${params}`);
      if (res.ok) {
        const data = await res.json();
        
        if (reset) {
          allFood = data.items;
          foodPage = 1;
        } else {
          allFood = [...allFood, ...data.items];
          foodPage++;
        }
        
        hasMoreFood = data.items.length === FOODS_PER_PAGE;
      }
    } catch(e) {
      console.error('Не удалось загрузить продукты');
    } finally {
      foodLoading = false;
    }
  }
  
  async function fetchDishes() {
    try {
      const res = await fetch(`${API_BASE_URL}/dishes/`);
      dishes = await res.json();
    } catch(e) {
      console.error('Не удалось загрузить блюда');
    }
  }
  
  async function fetchTechDishes() {
    try {
      const res = await fetch(`${API_BASE_URL}/tech/dishes/`);
      if (res.ok) {
        techDishes = await res.json();
      }
    } catch(e) {
      console.error('Не удалось загрузить технологические карты');
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
        techDishes = [...techDishes, newDish];
        form = { name: '', ingredients: [] };
        alert('✅ Технологическая карта создана');
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
    
    const selectedFood = allFood.find(f => f.fdc_id === +selectedFoodId);
    if (!selectedFood) {
      alert('Продукт не найден');
      return;
    }
    
    form.ingredients = [...form.ingredients, {
      food_id: +selectedFoodId,
      amount_grams: +gramsInput,
      food_name: selectedFood.name // сохраняем название для отображения
    }];
    selectedFoodId = '';
    gramsInput = '';
  }
  
  function removeIngredient(index) {
    form.ingredients = form.ingredients.filter((_, i) => i !== index);
  }
  
  async function deleteTechDish(dishId) {
    if (!confirm('Удалить технологическую карту? Это действие нельзя отменить.')) return;
    
    try {
      const res = await fetch(`${API_BASE_URL}/tech/dishes/${dishId}`, {
        method: 'DELETE'
      });
      
      if (res.ok) {
        techDishes = techDishes.filter(d => d.id !== dishId);
        alert('✅ Карта удалена');
      }
    } catch(e) {
      alert('❌ Ошибка удаления');
    }
  }
  
  function updateIngredientGrams(index, value) {
    form.ingredients[index].amount_grams = +value;
    form.ingredients = [...form.ingredients]; // trigger reactivity
  }
</script>

<div class="space-y-8">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h2 class="text-2xl font-bold">🔬 Технологическая карта</h2>
      <p class="text-sm opacity-75 mt-1">Формирование блюд из базы продуктов FDC</p>
    </div>
    <a href="/dishes" class="btn btn-ghost">🍽️ К админ-панели</a>
  </div>
  
  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else}
    <!-- Создание блюда -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h3 class="card-title text-lg">➕ Новая технологическая карта</h3>
        
        <div class="space-y-6">
          <!-- Название блюда -->
          <div>
            <label class="label">
              <span class="label-text font-semibold">Название блюда *</span>
            </label>
            <input
              class="input input-bordered w-full max-w-2xl"
              placeholder="Омлет с овощами, Борщ классический, ..."
              bind:value={form.name}
            />
          </div>
          
          <!-- Выбор продуктов -->
          <div class="space-y-4">
            <h4 class="font-semibold text-lg">📦 Состав блюда</h4>
            
            <!-- Поиск и фильтры продуктов -->
            <div class="bg-base-200 p-4 rounded-lg space-y-4">
              <div class="flex flex-wrap gap-4 items-end">
                <!-- Поиск -->
                <div class="flex-1 min-w-[300px]">
                  <label class="label">
                    <span class="label-text">Поиск продукта</span>
                  </label>
                  <div class="join w-full">
                    <input
                      type="text"
                      class="input input-bordered join-item flex-1"
                      placeholder="Название продукта..."
                      bind:value={foodSearch}
                      on:input={() => fetchFoodList(true)}
                    />
                    <button 
                      class="btn join-item"
                      on:click={() => fetchFoodList(true)}
                      disabled={foodLoading}
                    >
                      {#if foodLoading}
                        <span class="loading loading-spinner loading-xs"></span>
                      {/if}
                      Найти
                    </button>
                  </div>
                </div>
                
                <!-- Количество -->
                <div>
                  <label class="label">
                    <span class="label-text">Количество (г)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    class="input input-bordered w-32"
                    placeholder="100"
                    bind:value={gramsInput}
                  />
                </div>
                
                <!-- Кнопка добавления -->
                <div>
                  <button 
                    class="btn btn-primary"
                    on:click={addIngredient}
                    disabled={!selectedFoodId || !gramsInput}
                  >
                    ➕ Добавить
                  </button>
                </div>
              </div>
              
              <!-- Список продуктов -->
              <div class="max-h-60 overflow-y-auto">
                <table class="table table-zebra table-sm">
                  <thead class="sticky top-0 bg-base-300">
                    <tr>
                      <th></th>
                      <th>Название</th>
                      <th>Категория</th>
                      <th>FDC ID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each allFood as food}
                      <tr 
                        class="cursor-pointer hover:bg-base-100 {selectedFoodId == food.fdc_id ? 'bg-primary/10' : ''}"
                        on:click={() => selectedFoodId = food.fdc_id}
                      >
                        <td>
                          <input 
                            type="radio" 
                            name="selectedFood" 
                            class="radio radio-sm"
                            checked={selectedFoodId == food.fdc_id}
                            on:click={() => selectedFoodId = food.fdc_id}
                          />
                        </td>
                        <td>
                          <div class="font-medium">{food.name}</div>
                          {#if food.description_en}
                            <div class="text-xs opacity-75">{food.description_en}</div>
                          {/if}
                        </td>
                        <td>{food.category_name || '—'}</td>
                        <td class="font-mono">{food.fdc_id}</td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
                
                {#if foodLoading}
                  <div class="flex justify-center py-4">
                    <span class="loading loading-spinner"></span>
                  </div>
                {:else if hasMoreFood && allFood.length > 0}
                  <button 
                    class="btn btn-sm btn-ghost w-full mt-2"
                    on:click={() => fetchFoodList()}
                  >
                    Загрузить еще...
                  </button>
                {/if}
              </div>
            </div>
            
            <!-- Список добавленных ингредиентов -->
            {#if form.ingredients.length === 0}
              <div class="alert alert-info">
                <span>Добавьте ингредиенты для блюда</span>
              </div>
            {:else}
              <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>Продукт</th>
                      <th>FDC ID</th>
                      <th>Количество (г)</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each form.ingredients as ing, i}
                      <tr>
                        <td class="font-medium">{ing.food_name}</td>
                        <td class="font-mono text-sm">FDC #{ing.food_id}</td>
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
                            🗑️ Удалить
                          </button>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}
          </div>
          
          <!-- Итог -->
          <div class="bg-base-200 p-4 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <div class="text-sm opacity-75">Ингредиентов:</div>
                <div class="text-xl font-bold">{form.ingredients.length}</div>
              </div>
              <div>
                <div class="text-sm opacity-75">Общий вес:</div>
                <div class="text-xl font-bold">
                  {form.ingredients.reduce((sum, ing) => sum + ing.amount_grams, 0).toFixed(1)} г
                </div>
              </div>
            </div>
          </div>
          
          <button 
            class="btn btn-primary btn-lg w-full" 
            on:click={createDish}
            disabled={!form.name.trim() || form.ingredients.length === 0 || creating}
          >
            {#if creating}
              <span class="loading loading-spinner"></span>
              Создание...
            {:else}
              ✅ Создать технологическую карту
            {/if}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Список созданных технологических карт -->
    {#if techDishes.length > 0}
      <div>
        <h3 class="text-xl font-bold mb-4">📋 Созданные технологические карты</h3>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {#each techDishes as dish}
            <div class="card bg-base-100 shadow-md">
              <div class="card-body">
                <div class="flex justify-between items-start">
                  <h4 class="font-bold text-lg">{dish.name}</h4>
                  <div class="dropdown dropdown-end">
                    <button class="btn btn-sm btn-ghost">⋮</button>
                    <ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-50">
                      <li>
                        <a href={`/dishes/${dish.id}`} class="text-primary">
                          ✏️ Передать админу
                        </a>
                      </li>
                      <li>
                        <button 
                          on:click={() => deleteTechDish(dish.id)}
                          class="text-error"
                        >
                          🗑️ Удалить карту
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
                
                <div class="space-y-3 mt-4">
                  <div class="badge badge-outline badge-sm">
                    {dish.ingredients.length} ингредиентов
                  </div>
                  
                  <div class="text-sm space-y-2 max-h-40 overflow-y-auto">
                    {#each dish.ingredients as ing}
                      <div class="flex justify-between items-center py-1 border-b border-base-200 last:border-b-0">
                        <div>
                          <span class="font-medium">FDC #{ing.food_id}</span>
                          <span class="text-xs opacity-75 ml-2">({ing.amount_grams} г)</span>
                        </div>
                        <div class="text-xs opacity-75">
                          {#if allFood.find(f => f.fdc_id === ing.food_id)?.name}
                            {allFood.find(f => f.fdc_id === ing.food_id).name}
                          {:else}
                            Продукт #{ing.food_id}
                          {/if}
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
                
                <div class="card-actions justify-end mt-4">
                  <a 
                    href={`/tech/dishes/${dish.id}/edit`}
                    class="btn btn-sm btn-outline"
                  >
                    Редактировать состав
                  </a>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {:else}
      <div class="text-center py-12 text-base-content/70">
        <p>Нет созданных технологических карт</p>
        <p class="text-sm mt-2">Создайте первую карту выше</p>
      </div>
    {/if}
  {/if}
</div>
