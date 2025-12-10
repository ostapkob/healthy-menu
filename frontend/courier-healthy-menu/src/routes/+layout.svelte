<script>
  import { base } from '$app/paths';
</script>

<nav class="bg-gray-800 text-white p-4">
    <a href="{base}/" class="mr-4">Главная</a>
    <a href="{base}/couriers" class="mr-4">Курьеры</a>
    <a href="{base}/orders" class="mr-4">Доступные заказы</a>
    <a href="{base}/my-deliveries" class="mr-4">Мои доставки</a>
</nav>

<div class="p-4">
    <slot />
</div>
