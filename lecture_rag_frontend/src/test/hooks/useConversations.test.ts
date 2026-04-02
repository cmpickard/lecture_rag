import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useConversations } from '../../hooks/useConversations';

vi.mock('../../api/conversationApi', () => ({
  fetchConversations: vi.fn(),
}));

import { fetchConversations } from '../../api/conversationApi';
const mockFetch = vi.mocked(fetchConversations);

const STORAGE_KEY = 'conversation_ids';

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------
describe('initial state', () => {
  it('starts with an empty current conversation ID', () => {
    const { result } = renderHook(() => useConversations());
    expect(result.current.currConversationId).toBe('');
  });

  it('starts with an empty history and null summary', () => {
    const { result } = renderHook(() => useConversations());
    expect(result.current.currConversation).toEqual({ history: [], summary: null });
  });

  it('starts with an empty conversations map', () => {
    const { result } = renderHook(() => useConversations());
    expect(result.current.conversations).toEqual({});
  });

  it('starts with no error', () => {
    const { result } = renderHook(() => useConversations());
    expect(result.current.error).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Mount effect — loading from localStorage
// ---------------------------------------------------------------------------
describe('on mount', () => {
  it('does not call fetchConversations when localStorage is empty', () => {
    renderHook(() => useConversations());
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('does not call fetchConversations when the stored array is empty', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
    renderHook(() => useConversations());
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('calls fetchConversations with IDs from localStorage', async () => {
    const ids = ['id-1', 'id-2'];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
    const data = {
      'id-1': { history: [], summary: null },
      'id-2': { history: [], summary: 'Summary' },
    };
    mockFetch.mockResolvedValueOnce(data);

    const { result } = renderHook(() => useConversations());

    await waitFor(() => expect(result.current.conversations).toEqual(data));
    expect(mockFetch).toHaveBeenCalledWith(ids);
  });

  it('sets an error message when fetchConversations rejects', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['id-1']));
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useConversations());

    await waitFor(() => expect(result.current.error).toBe('Network error'));
  });

  it('sets a generic error for non-Error rejections', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['id-1']));
    mockFetch.mockRejectedValueOnce('oops');

    const { result } = renderHook(() => useConversations());

    await waitFor(() => expect(result.current.error).toBe('Failed to load conversations'));
  });
});

// ---------------------------------------------------------------------------
// addIdToStorage
// ---------------------------------------------------------------------------
describe('addIdToStorage', () => {
  it('stores the first ID when localStorage is empty', () => {
    const { result } = renderHook(() => useConversations());

    act(() => result.current.addIdToStorage('new-id'));

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual(['new-id']);
  });

  it('appends to existing IDs', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['existing-id']));
    mockFetch.mockResolvedValueOnce({});
    const { result } = renderHook(() => useConversations());

    act(() => result.current.addIdToStorage('new-id'));

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual(['existing-id', 'new-id']);
  });

  it('can add multiple IDs in sequence', () => {
    const { result } = renderHook(() => useConversations());

    act(() => {
      result.current.addIdToStorage('a');
      result.current.addIdToStorage('b');
    });

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual(['a', 'b']);
  });
});

// ---------------------------------------------------------------------------
// removeIdFromStorage
// ---------------------------------------------------------------------------
describe('removeIdFromStorage', () => {
  it('removes the specified ID', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['keep', 'remove-me']));
    mockFetch.mockResolvedValueOnce({});
    const { result } = renderHook(() => useConversations());

    act(() => result.current.removeIdFromStorage('remove-me'));

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual(['keep']);
  });

  it('is a no-op when the ID is not present', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['keep']));
    mockFetch.mockResolvedValueOnce({});
    const { result } = renderHook(() => useConversations());

    act(() => result.current.removeIdFromStorage('does-not-exist'));

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual(['keep']);
  });

  it('handles an empty localStorage gracefully', () => {
    const { result } = renderHook(() => useConversations());

    expect(() => act(() => result.current.removeIdFromStorage('any-id'))).not.toThrow();
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual([]);
  });
});
