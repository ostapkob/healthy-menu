import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import OrderCard from './OrderCard.svelte';
import { courierId } from '../stores/courier.js';
import { tick } from 'svelte';

describe('OrderCard', () => {
  const mockOrder = {
    id: 123,
    total_price: 1500,
    status: 'pending'
  };

  beforeEach(() => {
    courierId.set(1);
    global.fetch.mockClear();
  });

  it('renders order information correctly', () => {
    render(OrderCard, { order: mockOrder });

    expect(screen.getByText(/Заказ #123/i)).toBeInTheDocument();
    expect(screen.getByText(/Цена: 1500 ₽/i)).toBeInTheDocument();
    expect(screen.getByText(/Статус: pending/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Принять заказ/i })).toBeInTheDocument();
  });

  it('shows loading state when accepting order', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({})
    });

    render(OrderCard, { order: mockOrder });
    const button = screen.getByRole('button', { name: /Принять заказ/i });

    await fireEvent.click(button);

    expect(button).toBeDisabled();
    expect(screen.getByText(/Принимаю.../i)).toBeInTheDocument();
  });

  it('calls API with correct data when accepting order', async () => {
    const mockResponse = { ok: true };
    global.fetch.mockResolvedValueOnce(mockResponse);

    render(OrderCard, { order: mockOrder });
    const button = screen.getByRole('button', { name: /Принять заказ/i });

    await fireEvent.click(button);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/assign-delivery/'),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            courier_id: 1,
            order_id: 123
          })
        }
      );
    });
  });

  it('shows error message when API fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false
    });
    window.alert = vi.fn();

    render(OrderCard, { order: mockOrder });
    const button = screen.getByRole('button', { name: /Принять заказ/i });

    await fireEvent.click(button);
    await tick();

    expect(window.alert).toHaveBeenCalledWith('Ошибка при принятии заказа');
  });

  it('shows network error on fetch failure', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    window.alert = vi.fn();

    render(OrderCard, { order: mockOrder });
    const button = screen.getByRole('button', { name: /Принять заказ/i });

    await fireEvent.click(button);
    await tick();

    expect(window.alert).toHaveBeenCalledWith('Ошибка сети');
  });
});
