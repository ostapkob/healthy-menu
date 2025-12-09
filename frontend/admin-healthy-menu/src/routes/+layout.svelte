<script>
  import { base } from '$app/paths';
</script>

<nav class="bg-gray-800 text-white p-4">
  <a href="{base}/" class="mr-4">Главная-</a>
  <a href="{base}/dish-ingredients" class="mr-4">Состав блюд</a>
  <a href="{base}/coverage" class="mr-4">Покрытие витаминов</a>
  <a href="{base}/dishes" class="mr-4">Блюда</a>
</nav>
<div class="p-4">
  <slot />
</div>
