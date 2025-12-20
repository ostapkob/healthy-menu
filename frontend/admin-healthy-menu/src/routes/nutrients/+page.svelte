<script>
  import { onMount } from 'svelte';
  const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

  let list=[],ing=[],nut=[],loading=true;
  let form={id:null,ingredient_id:'',nutrient_id:'',content_per_100g:0};

  onMount(async ()=>{               // 3 параллельных запроса
     [list,ing,nut] = await Promise.all([
        fetch(`${API}/nutrient-contents/`).then(r=>r.json()),
        fetch(`${API}/ingredients/`).then(r=>r.json()),
        fetch(`${API}/nutrients/`).then(r=>r.json())
     ]);
     loading=false;
  });

  async function save(){
     const m = form.id ? 'PUT':'POST';
     const u = form.id ? `${API}/nutrient-contents/${form.id}` : `${API}/nutrient-contents/`;
     await fetch(u,{method:m,headers:{'Content-Type':'application/json'},
                    body:JSON.stringify(form)});
     form={id:null,ingredient_id:'',nutrient_id:'',content_per_100g:0};
     location.reload();        // быстрое обновление
  }
  async function del(id){
     if(!confirm('Удалить?')) return;
     await fetch(`${API}/nutrient-contents/${id}`,{method:'DELETE'});
     location.reload();
  }
  function edit(r){ form={...r}; }
</script>

<h2 class="text-xl font-bold mb-4">💊 Витамины / Минералы</h2>

{#if loading}
 <progress class="progress w-56"/>
{:else}
 <div class="max-w-4xl space-y-4">
   <form class="grid grid-cols-1 md:grid-cols-4 gap-2" on:submit|preventDefault={save}>
      <select class="select select-bordered" bind:value={form.ingredient_id} required>
         <option value="">Ингредиент</option>
         {#each ing as i}<option value={i.id}>{i.name}</option>{/each}
      </select>
      <select class="select select-bordered" bind:value={form.nutrient_id} required>
         <option value="">Витамин</option>
         {#each nut as n}<option value={n.id}>{n.name} ({n.short_name})</option>{/each}
      </select>
      <input type=number step=0.01 min=0 class="input input-bordered" placeholder="мг/100г"
             bind:value={form.content_per_100g} required>
      <button class="btn btn-primary" type="submit">{form.id?'Сохранить':'Добавить'}</button>
   </form>

   <div class="overflow-x-auto">
     <table class="table table-zebra w-full">
       <thead><tr><th>Ингредиент</th><th>Нутриент</th><th>мг/100г</th><th/></tr></thead>
       <tbody>
         {#each list as r}
         <tr>
           <td>{r.ingredient_name}</td>
           <td>{r.nutrient_name}</td>
           <td>{r.content_per_100g}</td>
           <td class="flex gap-2">
              <button class="btn btn-xs btn-ghost" on:click={()=>edit(r)}>✏️</button>
              <button class="btn btn-xs btn-ghost text-error" on:click={()=>del(r.id)}>🗑️</button>
           </td>
         </tr>
         {/each}
       </tbody>
     </table>
   </div>
 </div>
{/if}
