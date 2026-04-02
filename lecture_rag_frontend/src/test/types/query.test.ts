import { describe, it, expect } from 'vitest';
import { isQueryResponse } from '../../types/query';

describe('isQueryResponse', () => {
  it('returns true for a valid QueryResponse', () => {
    expect(isQueryResponse({
      role: 'assistant',
      content: 'Hello there.',
      conversation_id: 'abc-123',
    })).toBe(true);
  });

  it('returns true when optional summary is a string', () => {
    expect(isQueryResponse({
      role: 'user',
      content: 'A question',
      conversation_id: 'uuid-1',
      summary: 'A brief summary',
    })).toBe(true);
  });

  it('returns true when optional summary is null', () => {
    expect(isQueryResponse({
      role: 'assistant',
      content: 'Answer',
      conversation_id: 'uuid-2',
      summary: null,
    })).toBe(true);
  });

  it('returns false for null', () => {
    expect(isQueryResponse(null)).toBe(false);
  });

  it('returns false for a non-object primitive', () => {
    expect(isQueryResponse('string')).toBe(false);
    expect(isQueryResponse(42)).toBe(false);
    expect(isQueryResponse(true)).toBe(false);
  });

  it('returns false when role is missing', () => {
    expect(isQueryResponse({
      content: 'Hello',
      conversation_id: 'abc-123',
    })).toBe(false);
  });

  it('returns false when content is missing', () => {
    expect(isQueryResponse({
      role: 'assistant',
      conversation_id: 'abc-123',
    })).toBe(false);
  });

  it('returns false when conversation_id is missing', () => {
    expect(isQueryResponse({
      role: 'assistant',
      content: 'Hello',
    })).toBe(false);
  });

  it('returns false when role is not a string', () => {
    expect(isQueryResponse({
      role: 123,
      content: 'Hello',
      conversation_id: 'abc-123',
    })).toBe(false);
  });

  it('returns false when content is not a string', () => {
    expect(isQueryResponse({
      role: 'assistant',
      content: { nested: true },
      conversation_id: 'abc-123',
    })).toBe(false);
  });

  it('returns false when conversation_id is not a string', () => {
    expect(isQueryResponse({
      role: 'assistant',
      content: 'Hello',
      conversation_id: 99,
    })).toBe(false);
  });

  it('returns false for an empty object', () => {
    expect(isQueryResponse({})).toBe(false);
  });
});
