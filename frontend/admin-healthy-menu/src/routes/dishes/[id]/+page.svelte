<script>
  import { onMount } from 'svelte';
  import ImageUpload from '$lib/components/ImageUpload.svelte';
  import { base } from '$app/paths';
  
  export let params;
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  
  let dish = {
    id: null,
    name: '',
    price: 0,
    description: '',
    image_url: null
  };
  
  let loading = true;
  let saving = false;
  
  onMount(async () => {
    if (params.id !== 'new') {
      try {
        const res = await fetch(`${API_BASE_URL}/dishes/${params.id}`);
        if (res.ok) {
          dish = await res.json();
        }
      } catch (e) {
        alert('Ошибка загрузки блюда');
      }
    }
    loading = false;
  });
  
  const saveDish = async () => {
    if (!dish.name || dish.price <= 0) {
      alert('Заполните название и цену');
      return;
    }
    
    saving = true;
    try {
      const method = dish.id ? 'PUT' : 'POST';
      const url = dish.id ? `${API_BASE_URL}/dishes/${dish.id}` : `${API_BASE_URL}/admin/dishes/`;
      
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price: Number(dish.price),
          description: dish.description || null,
          image_url: dish.image_url || null
        })
      });
      
      if (res.ok) {
        alert('✅ Блюдо обновлено');
      } else {
        throw new Error('Ошибка API');
      }
    } catch (e) {
      alert('❌ Не удалось сохранить');
    } finally {
      saving = false;
    }
  };
  
  const handleImageUploaded = (event) => {
    dish.image_url = event.detail;
  };
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-2xl font-bold">🍽️ {dish.id ? 'Редактировать' : 'Новое'} блюдо</h2>
    <a href="/dishes" class="btn btn-ghost">← К списку</a>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else}
    <form class="space-y-6 max-w-2xl" on:submit|preventDefault={saveDish}>
      <!-- Только название для просмотра -->
      <div class="alert alert-info">
        <span>📝 Название: <strong>{dish.name}</strong> (задано технологом)</span>
      </div>
      
      <!-- Фото -->
      <div>
        <h3 class="font-semibold mb-2">📸 Фото</h3>
        <ImageUpload
          dishId={dish.id}
          currentImageUrl={dish.image_url}
          on:image-uploaded={handleImageUploaded}
        />
      </div>
      
      <!-- Цена -->
      <div>
        <label class="label">
          <span class="label-text">💰 Цена (₽) *</span>
        </label>
        <input
          type="number"
          step="0.01"
          min="0"
          class="input input-bordered w-full"
          bind:value={dish.price}
          required
        />
      </div>
      
      <!-- Описание -->
      <div>
        <label class="label">
          <span class="label-text">📝 Описание</span>
        </label>
        <textarea
          class="textarea textarea-bordered w-full"
          rows="4"
          placeholder="Краткое описание для меню..."
          bind:value={dish.description}
        />
      </div>
      
      <!-- Кнопки -->
      <div class="flex gap-3">
        <button
          type="submit"
          class="btn btn-primary flex-1"
          disabled={saving || dish.price <= 0}
        >
          {#if saving}
            <span class="loading loading-spinner loading-xs"></span>
          {/if}
          Сохранить
        </button>
        <a href="/dishes" class="btn btn-ghost">Отмена</a>
      </div>
    </form>
  {/if}
</div>

