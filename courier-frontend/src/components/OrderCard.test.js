import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import OrderCard from './OrderCard.svelte';

describe('OrderCard', () => {
  it('renders order data', () => {
    const order = { id: 1, totalprice: 100, status: 'new' };
    const { getByText } = render(OrderCard, { props: { order } });

    // Проверяем по реальному тексту
    expect(getByText('Заказ #1')).toBeInTheDocument();
    expect(getByText(/Цена:/)).toBeInTheDocument();
    expect(getByText('Статус: new')).toBeInTheDocument();
    expect(getByText('Принять')).toBeInTheDocument();
  });
});

