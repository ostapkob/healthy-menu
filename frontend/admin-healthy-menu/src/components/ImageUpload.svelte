<script>
  export let dishId = 0;
  export let currentImageUrl = null;
  
  let fileInput;
  let uploadStatus = 'idle';
  let uploadError = '';
  let previewUrl = null;
  let tempImageUrl = '';

  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  $: previewUrl = tempImageUrl || currentImageUrl || null;

  const triggerFilePicker = () => {
    fileInput.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!['image/jpg', 'image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      uploadStatus = 'error';
      uploadError = 'Поддерживаются только JPG, PNG, WebP';
      return;
    }

    // Создаем временную ссылку для превью
    const tempUrl = URL.createObjectURL(file);
    tempImageUrl = tempUrl;
    uploadStatus = 'uploading';

    // Имитируем задержку загрузки
    setTimeout(() => {
      // Диспатчим событие с временным URL (пользователь сам сохранит через PUT)
      dispatch('image-uploaded', tempUrl);
      uploadStatus = 'success';
      setTimeout(() => {
        uploadStatus = 'idle';
        // Очищаем временную ссылку
        URL.revokeObjectURL(tempUrl);
      }, 2000);
    }, 1500);
  };

  const removeImage = () => {
    tempImageUrl = '';
    dispatch('image-uploaded', null);
  };
</script>

<div class="space-y-4">
  <div class="flex flex-col sm:flex-row gap-4">
    <div class="w-32 h-32 rounded-lg bg-base-200 flex items-center justify-center overflow-hidden">
      {#if previewUrl}
        <img src={previewUrl} alt="Превью" class="w-full h-full object-cover" />
      {:else}
        <span class="text-sm text-gray-500 text-center px-2">Нет фото</span>
      {/if}
    </div>

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
        accept="image/jpeg,image/png,image/webp"
        class="hidden"
        bind:this={fileInput}
        on:change={handleFileChange}
      />

      {#if uploadStatus === 'uploading'}
        <div class="mt-2">
          <progress class="progress progress-primary w-full" />
          <p class="text-sm mt-1">Обработка…</p>
        </div>
      {/if}

      {#if uploadStatus === 'error'}
        <div class="alert alert-error shadow-sm mt-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{uploadError}</span>
        </div>
      {/if}
    </div>
  </div>

  {#if previewUrl && !currentImageUrl}
    <div class="alert alert-info shadow-sm">
      <span>📝 Скопируйте URL изображения и сохраните блюдо</span>
    </div>
  {/if}

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

