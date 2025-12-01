import { x as ensure_array_like } from "../../../chunks/index.js";
import { e as escape_html } from "../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let deliveries = [];
    $$renderer2.push(`<h2 class="text-xl font-bold mb-4">Мои доставки</h2> `);
    if (deliveries.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<table class="min-w-full border"><thead><tr><th class="border px-4 py-2">ID доставки</th><th class="border px-4 py-2">ID заказа</th><th class="border px-4 py-2">Статус</th><th class="border px-4 py-2">Действия</th></tr></thead><tbody><!--[-->`);
      const each_array = ensure_array_like(deliveries);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let delivery = each_array[$$index];
        $$renderer2.push(`<tr><td class="border px-4 py-2">${escape_html(delivery.id)}</td><td class="border px-4 py-2">${escape_html(delivery.order_id)}</td><td class="border px-4 py-2">${escape_html(delivery.status)}</td><td class="border px-4 py-2">`);
        if (delivery.status === "assigned") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="bg-blue-500 text-white px-2 py-1">Забрал</button>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (delivery.status === "picked_up") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="bg-green-500 text-white px-2 py-1">Доставлен</button>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]--></td></tr>`);
      }
      $$renderer2.push(`<!--]--></tbody></table>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<p>У вас нет активных доставок</p>`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};
