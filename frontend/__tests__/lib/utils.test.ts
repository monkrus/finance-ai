import { cn } from '@/lib/utils';

describe('Utils', () => {
  describe('cn()', () => {
    it('merges tailwind classes properly', () => {
      expect(cn('bg-red-500', 'text-white')).toBe('bg-red-500 text-white');
    });

    it('handles conditional classes', () => {
      expect(cn('px-2', true && 'py-2', false && 'm-4')).toBe('px-2 py-2');
    });

    it('resolves tailwind conflicts', () => {
      expect(cn('px-2 py-1 bg-red-500', 'bg-blue-500')).toBe('px-2 py-1 bg-blue-500');
    });
  });
});
