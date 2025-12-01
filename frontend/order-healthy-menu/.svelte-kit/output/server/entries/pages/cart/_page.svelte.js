import "clsx";
import { V as bind_props, X as store_get, W as ensure_array_like, Y as unsubscribe_stores } from "../../../chunks/index2.js";
import { w as writable } from "../../../chunks/index.js";
import { e as escape_html } from "../../../chunks/context.js";
const cart = writable([]);
function CartItem($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let item = $$props["item"];
    $$renderer2.push(`<div class="cart-item svelte-1hsbdxb"><span>${escape_html(item.name)} x ${escape_html(item.quantity)} = ${escape_html((item.price * item.quantity).toFixed(2))} ₽</span> <button>Удалить</button></div>`);
    bind_props($$props, { item });
  });
}
function Cart($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let total = 0;
    total = store_get($$store_subs ??= {}, "$cart", cart).reduce((sum, item) => sum + item.price * item.quantity, 0);
    $$renderer2.push(`<h1>Корзина</h1> `);
    if (store_get($$store_subs ??= {}, "$cart", cart).length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p>Корзина пуста</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$cart", cart));
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let item = each_array[$$index];
        CartItem($$renderer2, { item });
      }
      $$renderer2.push(`<!--]--> <h3>Итого: ${escape_html(total.toFixed(2))} ₽</h3> <button>Оформить заказ</button>`);
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _page($$renderer) {
  Cart($$renderer);
}
export {
  _page as default
};
