<script>
  import { onMount } from 'svelte';
  import ImageUpload from '$lib/components/ImageUpload.svelte';
  import { base } from '$app/paths';

  export let params;
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

  let dish = {
    name: '',
    price: 0,
    description: '',
    image_url: null
  };
  let loading = true;
  let saving = false;

  onMount(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/dishes/${params.id}`);
      dish = await res.json();
    } catch (e) {
      alert('Ошибка загрузки блюда');
    } finally {
      loading = false;
    }
  });


  const saveDish = async () => {
    saving = true;
    try {
      const method = dish.id ? 'PUT' : 'POST';
      const url = dish.id ? `${API_BASE_URL}/dishes/${dish.id}` : `${API_BASE_URL}/dishes/`;
      const payload = {
        name: dish.name,
        price: Number(dish.price), 
        description: dish.description || null,
        image_url: dish.image_url?.trim() ? dish.image_url : null
      };
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        alert('✅ Блюдо сохранено');
        if (!dish.id) {
          // Редирект на /dishes после создания
          window.location.href = '/dishes';
        }
      } else {
        throw new Error('Ошибка API');
      }
    } catch (e) {
      alert('❌ Не удалось сохранить');
    } finally {
      saving = false;
    }
  };

  const handleImageUploaded = (url) => {
  console.log('🖼 handleImageUploaded called with:', url);
  console.log(type(url))  
  dish = { ...dish, image_url: url };
  console.log('Dish updated:', dish.id, dish.image_url);
};
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-2xl font-bold">
      {dish.id ? '✏️ Редактировать' : '🆕 Создать'} блюдо
    </h2>
    <a href="{base}/dishes" class="btn btn-ghost">← Назад к списку</a>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else}
    <form class="space-y-6 max-w-2xl" on:submit|preventDefault={saveDish}>
      <!-- Image upload -->
      <div>
        <h3 class="font-semibold mb-2">Фотография</h3>
        <ImageUpload
          dishId={dish.id}
          currentImageUrl={dish.image_url}
          on:image-uploaded={handleImageUploaded}
        />
      </div>

      <!-- Name -->
      <div>
        <label class="label">
          <span class="label-text">Название *</span>
        </label>
        <input
          type="text"
          class="input input-bordered w-full"
          bind:value={dish.name}
          required
        />
      </div>

      <!-- Price -->
      <div>
        <label class="label">
          <span class="label-text">Цена (₽) *</span>
        </label>
        <input
          type="number"
          step="1"
          min="0"
          class="input input-bordered w-full"
          bind:value={dish.price}
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label class="label">
          <span class="label-text">Описание</span>
        </label>
        <textarea
          class="textarea textarea-bordered w-full"
          rows="3"
          placeholder="Например: Омлет из 2 яиц с помидорами и перцем"
          bind:value={dish.description}
        />
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button
          type="submit"
          class="btn btn-primary"
          class:btn-disabled={saving}
        >
          {#if saving}
            <span class="loading loading-spinner loading-xs"></span>
          {/if}
          {dish.id ? 'Сохранить' : 'Создать'}
        </button>
        {#if dish.id}
          <button
            type="button"
            class="btn btn-ghost"
            on:click={() => window.location.reload()}
          >
            Отменить
          </button>
        {/if}
      </div>
    </form>
  {/if}
</div>
