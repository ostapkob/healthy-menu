// src/stores/courier.test.js
import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import {
  courierId,
  wsConnection,
  availableOrders,
  currentDelivery,
} from './courier.js';

describe('courier store', () => {
  it('has correct default values', () => {
    expect(get(courierId)).toBe(1);
    expect(get(wsConnection)).toBeNull();
    expect(get(availableOrders)).toEqual([]);
    expect(get(currentDelivery)).toBeNull();
  });

  it('updates courierId', () => {
    courierId.set(5);
    expect(get(courierId)).toBe(5);
  });

  it('updates wsConnection', () => {
    const ws = { readyState: 1 };
    wsConnection.set(ws);
    expect(get(wsConnection)).toBe(ws);
  });

  it('updates availableOrders', () => {
    const orders = [{ id: 1 }, { id: 2 }];
    availableOrders.set(orders);
    expect(get(availableOrders)).toEqual(orders);
  });

  it('updates currentDelivery', () => {
    const delivery = { id: 10, status: 'assigned' };
    currentDelivery.set(delivery);
    expect(get(currentDelivery)).toEqual(delivery);
  });
});
