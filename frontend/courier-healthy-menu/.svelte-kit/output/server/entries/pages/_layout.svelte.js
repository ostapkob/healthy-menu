import { w as slot } from "../../chunks/index.js";
function _layout($$renderer, $$props) {
  $$renderer.push(`<nav class="bg-gray-800 text-white p-4"><a href="/" class="mr-4">Главная</a> <a href="/couriers" class="mr-4">Курьеры</a> <a href="/orders" class="mr-4">Доступные заказы</a> <a href="/my-deliveries" class="mr-4">Мои доставки</a></nav> <div class="p-4"><!--[-->`);
  slot($$renderer, $$props, "default", {});
  $$renderer.push(`<!--]--></div>`);
}
export {
  _layout as default
};
