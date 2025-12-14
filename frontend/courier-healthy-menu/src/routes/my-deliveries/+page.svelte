<!-- src/routes/my-deliveries/+page.svelte -->
<script>
  import { onMount } from 'svelte';

  let deliveries = [];
  const courierId = 1;
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';

  onMount(async () => {
    const response = await fetch(`${API_BASE_URL}/my-deliveries/${courierId}`);
    deliveries = await response.json();
  });

  const updateStatus = async (deliveryId, newStatus) => {
    const response = await fetch(`${API_BASE_URL}/update-delivery-status/${deliveryId}?status=${newStatus}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });

    if (response.ok) {
      deliveries = deliveries.map(d =>
        d.id === deliveryId ? { ...d, status: newStatus } : d
      );
    } else {
      alert('Ошибка обновления статуса');
    }
  };
</script>

<div>
  <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
    Мои доставки
  </h2>

  {#if deliveries.length > 0}
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th>Заказ</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {#each deliveries as delivery}
            <tr>
              <td>#{delivery.order_id}</td>
              <td>
                <span class={`badge ${
                  delivery.status === 'assigned' ? 'badge-warning' :
                  delivery.status === 'picked_up' ? 'badge-info' :
                  'badge-success'
                }`}>
                  {delivery.status}
                </span>
              </td>
              <td>
                {#if delivery.status === 'assigned'}
                  <button
                    class="btn btn-sm btn-primary"
                    on:click={() => updateStatus(delivery.id, 'picked_up')}
                  >
                    Забрал
                  </button>
                {:else if delivery.status === 'picked_up'}
                  <button
                    class="btn btn-sm btn-success"
                    on:click={() => updateStatus(delivery.id, 'delivered')}
                  >
                    Доставлен
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {:else}
    <div class="text-center py-12">
      <p class="text-lg text-base-content/70">Нет активных доставок</p>
    </div>
  {/if}
</div>
