import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { theme, setTheme } from './theme.js';

describe('theme', () => {
  it('sets theme correctly', () => {
    setTheme('dark');
    expect(get(theme)).toBe('dark');
  });
});

