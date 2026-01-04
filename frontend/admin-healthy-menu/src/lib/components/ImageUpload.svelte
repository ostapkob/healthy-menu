<script>

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  export let dishId = 0;            // id блюда (для маршрута /dishes/{id}/image)
  export let currentImageUrl = null; // уже сохранённый URL из базы

  let fileInput;
  let uploadStatus = 'idle';        // 'idle' | 'uploading' | 'success' | 'error'
  let uploadError = '';
  let previewUrl = null;            // для локального превью

  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  $: previewUrl = currentImageUrl;

  /* клик по кнопке «Загрузить / Заменить» */
  const triggerFilePicker = () => fileInput.click();

  /* выбор файла */
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      uploadStatus = 'error';
      uploadError = 'Поддерживаются JPG, PNG, WebP';
      return;
    }

    /* временное превью (только для показа) */
    const tempUrl = URL.createObjectURL(file);
    previewUrl = tempUrl;

    uploadStatus = 'uploading';

    /* грузим на сервер */
    const form = new FormData();
    form.append('file', file);

    try {
    const res = await fetch(`${API_BASE_URL}/dishes/${dishId}/image`, {
        method: 'POST',
        body: form
      });

      if (!res.ok) throw new Error('upload failed');

      const updatedDish = await res.json();   // { id, name, image_url, ... }
      dispatch('image-uploaded', updatedDish.image_url); // передаём новый URL родителю
      uploadStatus = 'success';
    } catch (err) {
      console.log(err)
      uploadStatus = 'error';
      uploadError = 'Не удалось загрузить изображение';
    } finally {
      /* освобождаем временную blob-ссылку */
      URL.revokeObjectURL(tempUrl);
      setTimeout(() => (uploadStatus = 'idle'), 2000);
    }
  };

  /* кнопка «Удалить фото» – просто стираем URL */
  const removeImage = () => {
    dispatch('image-uploaded', null);
    previewUrl = null;
  };
</script>

<div class="space-y-4">
  <div class="flex flex-col sm:flex-row gap-4">
    <!-- превью -->
    <div class="w-32 h-32 rounded-lg bg-base-200 flex items-center justify-center overflow-hidden">
      {#if previewUrl}
        <img src={previewUrl} alt="Превью" class="w-full h-full object-cover" />
      {:else}
        <span class="text-sm text-gray-500 text-center px-2">Нет фото</span>
      {/if}
    </div>

    <!-- кнопки -->
    <div class="flex-1">
      <button
        type="button"
        class="btn btn-outline w-full"
        on:click={triggerFilePicker}
        disabled={uploadStatus === 'uploading'}
      >
        📤 {currentImageUrl ? 'Заменить фото' : 'Загрузить фото'}
      </button>

      <input
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        class="hidden"
        bind:this={fileInput}
        on:change={handleFileChange}
      />

      <!-- прогресс -->
      {#if uploadStatus === 'uploading'}
        <div class="mt-2">
          <progress class="progress progress-primary w-full" />
          <p class="text-sm mt-1">Отправляем на сервер…</p>
        </div>
      {/if}

      <!-- ошибка -->
      {#if uploadStatus === 'error'}
        <div class="alert alert-error shadow-sm mt-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{uploadError}</span>
        </div>
      {/if}

      <!-- успех -->
      {#if uploadStatus === 'success'}
        <div class="alert alert-success shadow-sm mt-2">
          <span>✅ Изображение сохранено в MinIO</span>
        </div>
      {/if}
    </div>
  </div>

  <!-- кнопка удалить -->
  {#if currentImageUrl}
    <button
      type="button"
      class="btn btn-sm btn-ghost text-error w-full"
      on:click={removeImage}
    >
      🗑️ Удалить фото
    </button>
  {/if}
</div>
