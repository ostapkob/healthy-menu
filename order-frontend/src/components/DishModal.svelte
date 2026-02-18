<script>
  import { createEventDispatcher } from 'svelte';

  export let dish;
  export let open = false;

  const dispatch = createEventDispatcher();

  const close = () => {
    dispatch('close');
  };

  // Группируем микроэлементы для удобства отображения
  $: micronutrientsList = dish.micronutrients
    ? Object.values(dish.micronutrients)
    : [];

  // Макросы для отображения
  const macros = [
    { name: 'Ккал', value: dish.macros?.calories?.toFixed(0) || '—', color: 'bg-error/10 text-error' },
    { name: 'Белки', value: `${dish.macros?.protein?.toFixed(1) || '—'} г`, color: 'bg-success/10 text-success' },
    { name: 'Жиры', value: `${dish.macros?.fat?.toFixed(1) || '—'} г`, color: 'bg-warning/10 text-warning' },
    { name: 'Углеводы', value: `${dish.macros?.carbs?.toFixed(1) || '—'} г`, color: 'bg-accent/10 text-accent' },
  ];

  // Для score: 1 = ⭐, 2 = ⭐⭐, ..., 5 = ⭐⭐⭐⭐⭐
  $: stars = Array.from({ length: 5 }, (_, i) => i < (dish.score || 0));
</script>

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
    on:click|self={close}
    role="dialog"
    aria-modal="true"
    aria-labelledby="dish-modal-title"
  >
    <div
      class="w-full max-w-lg bg-base-100 rounded-2xl shadow-xl overflow-hidden transform transition-all duration-300 scale-100 opacity-100"
      on:click|stopPropagation
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-primary to-secondary p-5 text-white">
        <div class="flex justify-between items-start">
          <div>
            <h2 id="dish-modal-title" class="text-2xl font-bold">{dish.name}</h2>
            <p class="opacity-90 mt-1">₽{dish.price.toLocaleString()}</p>
          </div>
          <button
            class="btn btn-ghost btn-sm text-white hover:bg-white/20"
            on:click={close}
            aria-label="Закрыть"
          >
            ✕
          </button>
        </div>
        {#if dish.description}
          <p class="mt-3 opacity-95">{dish.description}</p>
        {/if}
      </div>

      <!-- Scrollable content -->
      <div class="max-h-[60vh] overflow-y-auto p-5">
        <!-- Score -->
        {#if typeof dish.score === 'number' && dish.score > 0}
          <div class="mb-5">
            <div class="flex items-center gap-2">
              <span class="font-medium">Оценка здоровья:</span>
              <div class="flex">
                {#each stars as _, i}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.784-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                {/each}
                {#if dish.score < 5}
                  {#each Array(5 - stars.length) as _}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-300" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.784-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  {/each}
                {/if}
              </div>
              <span class="text-sm opacity-75 ml-1">({dish.score}/5)</span>
            </div>
            {#if dish.score >= 4}
              <div class="badge badge-success mt-1">Высокая пищевая ценность</div>
            {:else if dish.score >= 3}
              <div class="badge badge-warning mt-1">Сбалансировано</div>
            {:else}
              <div class="badge badge-error mt-1">Низкая пищевая ценность</div>
            {/if}
          </div>
        {/if}

        <!-- Macros -->
        {#if dish.macros}
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8M4 8h16m-8 8v4" />
              </svg>
              Макронутриенты (на порцию)
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {#each macros as macro}
                <div class={`p-3 rounded-lg text-center font-medium ${macro.color}`}>
                  <div class="text-lg">{macro.value}</div>
                  <div class="text-xs opacity-80">{macro.name}</div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Micronutrients -->
        {#if micronutrientsList.length > 0}
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Витамины и минералы
            </h3>
            <div class="space-y-3">
              {#each micronutrientsList as nutr}
                <div class="flex items-center">
                  <div class="w-24 text-sm font-medium">{nutr.name}</div>
                  <div class="flex-1 ml-2">
                    <div class="flex justify-between text-sm mb-1">
                      <span>{nutr.value} {nutr.unit}</span>
                      <span class="font-medium">{nutr.coverage_percent}%</span>
                    </div>
                    <progress
                      class="progress progress-primary w-full"
                      value={Math.min(nutr.coverage_percent, 100)}
                      max="100"
                    />
                    {#if nutr.coverage_percent > 100}
                      <div class="text-xs text-warning mt-1">⚠️ Превышение нормы</div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Recommendations -->
        {#if dish.recommendations && dish.recommendations.length > 0}
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-2">Рекомендации</h3>
            <div class="space-y-2">
              {#each dish.recommendations as rec}
                <div class="badge badge-outline badge-info py-2 px-3 text-left">{rec}</div>
              {/each}
            </div>
          </div>
        {:else if typeof dish.score === 'number' && dish.score < 3}
          <div class="alert alert-warning shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span>Это блюдо имеет низкую пищевую ценность. Рассмотрите альтернативы.</span>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-4 border-t bg-base-200">
        <button
          class="btn btn-primary w-full"
          on:click={() => {
            dispatch('add-to-cart', dish);
            close();
          }}
        >
          + Добавить в корзину
        </button>
      </div>
    </div>
  </div>
{/if}
