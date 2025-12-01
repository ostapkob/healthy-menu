import "clsx";
import { V as bind_props, W as ensure_array_like } from "../../chunks/index2.js";
import { e as escape_html } from "../../chunks/context.js";
function DishCard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let dish = $$props["dish"];
    $$renderer2.push(`<div class="dish-card svelte-1fp39lq"><h3>${escape_html(dish.name)}</h3> <p>Цена: ${escape_html(dish.price)} ₽</p> <button>Добавить в корзину</button></div>`);
    bind_props($$props, { dish });
  });
}
function Menu($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let dishes = [];
    $$renderer2.push(`<h1>Меню</h1> <!--[-->`);
    const each_array = ensure_array_like(dishes);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let dish = each_array[$$index];
      DishCard($$renderer2, { dish });
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _page($$renderer) {
  Menu($$renderer);
}
export {
  _page as default
};
