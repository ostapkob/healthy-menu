import '@testing-library/jest-dom';
import { vi } from 'vitest';

// matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  enumerable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  })),
});

// при необходимости — мок fetch
if (!global.fetch) {
  global.fetch = vi.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
  );
}

