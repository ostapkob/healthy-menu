<script>
  import { onMount } from 'svelte';

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';
  const courierId = 1;

  let courier = null;
  let deliveries = [];
  let status = 'offline';
  let loading = true;

  onMount(async () => {
    try {
      const [courierRes, deliveriesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/couriers/${courierId}`),  // Добавь в бэкенд: GET /couriers/{id}
        fetch(`${API_BASE_URL}/my-deliveries/${courierId}?history=true`)  // Добавь фильтр на завершённые
      ]);

      if (courierRes.ok) {
        courier = await courierRes.json();
        status = courier.status;
      }

      if (deliveriesRes.ok) {
        deliveries = await deliveriesRes.json();
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  const updateStatus = async (newStatus) => {
    const res = await fetch(`${API_BASE_URL}/couriers/${courierId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });

    if (res.ok) {
      status = newStatus;
      courier.status = newStatus;
    } else {
      alert('Ошибка обновления статуса');
    }
  };
</script>

<div>
  <div class="flex flex-col md:flex-row gap-6">
    <!-- Avatar -->
    <div class="avatar">
      <div class="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
        {#if courier?.photo_url}
          <img src={courier.photo_url} alt="Фото курьера" class="w-full h-full object-cover rounded-full" />
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        {/if}
      </div>
    </div>

    <!-- Info -->
    <div class="flex-1">
      <h2 class="text-2xl font-bold">{courier?.name || 'Курьер'}</h2>
      <div class="mt-4">
        <div class="flex items-center gap-3">
          <span class="font-medium">Статус:</span>
          <span class={`badge ${status === 'available' ? 'badge-success' : 'badge-error'}`}>
            {status === 'available' ? '🟢 Онлайн' : '🔴 Офлайн'}
          </span>
          <div class="flex gap-2">
            <button
              class="btn btn-sm btn-success"
              on:click={() => updateStatus('available')}
              disabled={status === 'available'}
            >
              Онлайн
            </button>
            <button
              class="btn btn-sm btn-error"
              on:click={() => updateStatus('offline')}
              disabled={status === 'offline'}
            >
              Офлайн
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="mt-8">
    <h3 class="text-xl font-semibold mb-4">История доставок</h3>
    {#if deliveries.length > 0}
      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr>
              <th>Заказ</th>
              <th>Статус</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            {#each deliveries as d}
              <tr>
                <td>#{d.order_id}</td>
                <td><span class="badge badge-success">{d.status}</span></td>
                <td>{d.delivered_at || d.assigned_at}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-base-content/70">Нет завершённых доставок</p>
    {/if}
  </div>
</div>
