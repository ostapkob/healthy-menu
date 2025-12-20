<script>
  import { onMount } from 'svelte';
  const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

  let rows = [], loading = true, saving = false;
  let form = { id:null, name:'' };

  onMount(async () => fetchRows());

  async function fetchRows(){
     rows = await fetch(`${API}/ingredients/`).then(r=>r.json());
     loading = false;
  }
  async function save(){
     saving = true;
     const method = form.id ? 'PUT' : 'POST';
     const url   = form.id ? `${API}/ingredients/${form.id}` : `${API}/ingredients/`;
     await fetch(url,{method, headers:{'Content-Type':'application/json'},
                      body:JSON.stringify(form)});
     form = {id:null,name:''};
     saving = false;
     await fetchRows();
  }
  async function del(id){
     if(!confirm('Удалить?')) return;
     await fetch(`${API}/ingredients/${id}`,{method:'DELETE'});
     await fetchRows();
  }
  function edit(r){ form = {...r}; }
</script>

<h2 class="text-xl font-bold mb-4">🥬 Ингредиенты</h2>

{#if loading}
  <progress class="progress w-56"/>
{:else}
 <div class="max-w-xl space-y-4">
   <form class="flex gap-2" on:submit|preventDefault={save}>
      <input class="input input-bordered flex-1" placeholder="Название"
             bind:value={form.name} required />
      <button class="btn btn-primary" class:loading={saving} type="submit">
         {form.id ? 'Сохранить' : 'Добавить'}
      </button>
      {#if form.id}
        <button type=button class="btn btn-ghost" on:click={()=>form={id:null,name:''}}>Отмена</button>
      {/if}
   </form>

   <div class="overflow-x-auto">
     <table class="table table-zebra w-full">
       <thead><tr><th>ID</th><th>Название</th><th/></tr></thead>
       <tbody>
         {#each rows as r}
         <tr>
           <td>{r.id}</td>
           <td>{r.name}</td>
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
