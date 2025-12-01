import { x as ensure_array_like } from "../../../chunks/index.js";
import { e as escape_html } from "../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let couriers = [];
    $$renderer2.push(`<h2 class="text-xl font-bold mb-4">Курьеры</h2> <table class="min-w-full border"><thead><tr><th class="border px-4 py-2">ID</th><th class="border px-4 py-2">Имя</th><th class="border px-4 py-2">Статус</th><th class="border px-4 py-2">Текущий заказ</th></tr></thead><tbody><!--[-->`);
    const each_array = ensure_array_like(couriers);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let courier = each_array[$$index];
      $$renderer2.push(`<tr><td class="border px-4 py-2">${escape_html(courier.id)}</td><td class="border px-4 py-2">${escape_html(courier.name)}</td><td class="border px-4 py-2">${escape_html(courier.status)}</td><td class="border px-4 py-2">${escape_html(courier.current_order_id || "Нет")}</td></tr>`);
    }
    $$renderer2.push(`<!--]--></tbody></table>`);
  });
}
export {
  _page as default
};
