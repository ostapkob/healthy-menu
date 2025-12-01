import "clsx";
import { W as ensure_array_like } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/context.js";
function Orders($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let orders = [];
    $$renderer2.push(`<h1>Мои заказы</h1> `);
    if (orders.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p>У вас нет заказов</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(orders);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let order = each_array[$$index];
        $$renderer2.push(`<div class="order svelte-bj60gn"><p>Заказ #${escape_html(order.id)}, статус: ${escape_html(order.status)}</p> <p>Цена: ${escape_html(order.total_price)} ₽</p> <p>Создан: ${escape_html(order.created_at)}</p></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _page($$renderer) {
  Orders($$renderer);
}
export {
  _page as default
};
