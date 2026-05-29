import { describe, it, expect } from 'vitest'
import { cn } from '../../lib/utils'

describe('cn()', () => {
  it('returns empty string with no arguments', () => {
    expect(cn()).toBe('')
  })

  it('returns a single class unchanged', () => {
    expect(cn('text-sm')).toBe('text-sm')
  })

  it('joins multiple classes', () => {
    expect(cn('flex', 'items-center', 'gap-2')).toBe('flex items-center gap-2')
  })

  it('filters out falsy values', () => {
    expect(cn('flex', undefined, null, false, 'gap-2')).toBe('flex gap-2')
  })

  it('handles conditional object syntax', () => {
    expect(cn({ 'text-red-500': true, 'text-green-500': false })).toBe('text-red-500')
  })

  it('merges conflicting Tailwind classes (last wins)', () => {
    // tailwind-merge resolves text-sm + text-lg → text-lg
    expect(cn('text-sm', 'text-lg')).toBe('text-lg')
  })

  it('merges conflicting background colors (last wins)', () => {
    expect(cn('bg-red-500', 'bg-blue-500')).toBe('bg-blue-500')
  })

  it('handles conditional classes mixed with static classes', () => {
    const isActive = true
    const result = cn('px-4', isActive && 'bg-indigo-600', 'rounded')
    expect(result).toBe('px-4 bg-indigo-600 rounded')
  })

  it('handles array inputs', () => {
    expect(cn(['flex', 'items-center'])).toBe('flex items-center')
  })

  it('handles deeply nested conditionals', () => {
    const result = cn('base', { active: true, disabled: false }, 'extra')
    expect(result).toBe('base active extra')
  })
})
