import { U as slot } from "../../chunks/index2.js";
function _layout($$renderer, $$props) {
  $$renderer.push(`<nav><a href="/">Меню</a> <a href="/cart">Корзина</a> <a href="/orders">Заказы</a></nav> <!--[-->`);
  slot($$renderer, $$props, "default", {});
  $$renderer.push(`<!--]-->`);
}
export {
  _layout as default
};
