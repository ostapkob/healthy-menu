<script>
  // Просто инициализируем пустое блюдо
  let dish = {
    name: '',
    price: 0,
    description: '',
    image_url: null
  };
</script>

<svelte:component this={import('../[id]/+page.svelte')} params={{ id: 'new' }} {dish} />
