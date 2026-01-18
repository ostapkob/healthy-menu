import { writable } from 'svelte/store';

export const courierId = writable(1); // можно заменить на логин
export const wsConnection = writable(null);
export const availableOrders = writable([]);
export const currentDelivery = writable(null);
