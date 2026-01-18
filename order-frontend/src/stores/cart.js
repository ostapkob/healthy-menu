import { writable } from 'svelte/store';

export const cart = writable([]);

export const addToCart = (dish) => {
    cart.update(items => {
        const existing = items.find(item => item.id === dish.id);
        if (existing) {
            return items.map(item =>
                item.id === dish.id ? { ...item, quantity: item.quantity + 1 } : item
            );
        } else {
            return [...items, { ...dish, quantity: 1 }];
        }
    });
};

export const removeFromCart = (dishId) => {
    cart.update(items => items.filter(item => item.id !== dishId));
};

export const clearCart = () => {
    cart.set([]);
};
