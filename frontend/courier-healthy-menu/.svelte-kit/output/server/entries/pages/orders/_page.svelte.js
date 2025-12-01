import { y as bind_props, x as ensure_array_like } from "../../../chunks/index.js";
import { a as ssr_context, e as escape_html } from "../../../chunks/context.js";
import "clsx";
function onDestroy(fn) {
  /** @type {SSRContext} */
  ssr_context.r.on_destroy(fn);
}
function OrderCard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let order = $$props["order"];
    $$renderer2.push(`<div class="border p-4 mb-2 rounded"><p>Заказ #${escape_html(order.id)}</p> <p>Цена: ${escape_html(order.total_price)} ₽</p> <p>Статус: ${escape_html(order.status)}</p> <button class="bg-green-500 text-white px-2 py-1">Принять</button></div>`);
    bind_props($$props, { order });
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let orders = [];
    onDestroy(() => {
    });
    $$renderer2.push(`<h2 class="text-xl font-bold mb-4">Доступные заказы</h2> `);
    if (orders.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(orders);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let order = each_array[$$index];
        OrderCard($$renderer2, { order });
      }
      $$renderer2.push(`<!--]-->`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<p>Нет доступных заказов</p>`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};
