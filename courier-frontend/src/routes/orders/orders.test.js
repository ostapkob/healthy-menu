// src/routes/orders/orders.test.js
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import OrdersPage from './+page.svelte';

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  global.fetch = mockFetch;
});

describe('Orders +page.svelte', () => {

  it('renders empty state when no orders', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(OrdersPage);

    expect(
      await screen.findByText(/Доступные заказы/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText('Количество заказов: 0')
    ).toBeInTheDocument();

    expect(
      screen.getByText('Нет доступных заказов')
    ).toBeInTheDocument();
  });
});

