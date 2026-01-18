<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { getFoods } from '$lib/api.js';

  export let selected = [];        // [{fdc_id, amount_grams}]
  const dispatch = createEventDispatcher();

  let q        = '';
  let category = '';
  let items    = [];
  let loading  = true;
  let grams    = '';



  $: updateList(q, category);          // 1. реактивно вызываем ОБЫЧНУЮ функцию
  async function updateList(q, category_id) { // 2. сама асинхронная функция
    loading = true;
    try {
      const res = await getFoods({ q, category_id, limit: 100 });
      items = res.items;
    } finally { loading = false; }
  }

  function add(f) {
    if (!grams || +grams<=0) return;
    if (selected.some(i => i.food_id === f.fdc_id)) return;
    selected = [...selected, {food_id:f.fdc_id, amount_grams:+grams}];
    grams = '';
    dispatch('change', selected);
  }
  function remove(idx) {
    selected = selected.filter((_,i)=>i!==idx);
    dispatch('change', selected);
  }
</script>

<div class="form-control">
  <label class="label"><span class="label-text">Поиск продуктов (FDC)</span></label>
  <input bind:value={q} placeholder="Начните вводить..." class="input input-bordered" />
</div>

{#if loading}
  <span class="loading loading-spinner loading-sm"/>
{:else}
  <table class="table table-compact w-full mt-2">
    <thead>
      <tr>
        <th>Продукт</th><th>Категория</th><th>Кол-во, г</th><th></th>
      </tr>
    </thead>
    <tbody>
      {#each items as f}
      <tr>
        <td>{f.name}</td>
        <td><span class="badge badge-outline">{f.category_name||'–'}</span></td>
        <td>
          <input type="number" step="0.1" min="0.1" bind:value={grams}
                 class="input input-sm input-bordered w-20" />
        </td>
        <td>
          <button class="btn btn-sm btn-primary" on:click={()=>add(f)}>+</button>
        </td>
      </tr>
      {/each}
    </tbody>
  </table>
{/if}

{#if selected.length}
  <div class="mt-4">
    <h4 class="font-semibold mb-2">Состав блюда</h4>
    <table class="table table-compact w-full">
      <thead><tr><th>ID</th><th>Грамм</th><th></th></tr></thead>
      <tbody>
      {#each selected as ing, idx}
        <tr>
          <td class="font-mono text-sm">FDC {ing.food_id}</td>
          <td>{ing.amount_grams} г</td>
          <td><button class="btn btn-xs btn-ghost text-error" on:click={()=>remove(idx)}>🗑</button></td>
        </tr>
      {/each}
      </tbody>
    </table>
  </div>
{/if}
