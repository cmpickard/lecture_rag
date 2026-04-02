import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchConversations, postQuery, deleteConversation } from '../../api/conversationApi';

function mockFetch(body: unknown, ok = true, status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
    ok,
    status,
    json: () => Promise.resolve(body),
  } as Response);
}

beforeEach(() => {
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------
// fetchConversations
// ---------------------------------------------------------------------------
describe('fetchConversations', () => {
  it('returns parsed conversations on success', async () => {
    const data = {
      'id-1': { history: [{ role: 'user', content: 'Hi' }], summary: null },
    };
    mockFetch(data);

    const result = await fetchConversations(['id-1']);
    expect(result).toEqual(data);
  });

  it('sends all IDs as repeated query params', async () => {
    mockFetch({});
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    } as Response);

    await fetchConversations(['a', 'b', 'c']);

    const calledUrl = fetchSpy.mock.calls[0][0] as string;
    expect(calledUrl).toContain('ids=a');
    expect(calledUrl).toContain('ids=b');
    expect(calledUrl).toContain('ids=c');
  });

  it('throws when the response is not ok', async () => {
    mockFetch(null, false, 500);

    await expect(fetchConversations(['id-1'])).rejects.toThrow('Failed to fetch conversations: 500');
  });
});

// ---------------------------------------------------------------------------
// postQuery
// ---------------------------------------------------------------------------
describe('postQuery', () => {
  const validQuery = {
    role: 'user' as const,
    content: 'What is consciousness?',
    conversation_id: '',
    dialogue_mode: false,
  };

  const validResponse = {
    role: 'assistant',
    content: 'Great question.',
    conversation_id: 'new-id-42',
    summary: null,
  };

  it('returns QueryResponse on success', async () => {
    mockFetch(validResponse);

    const result = await postQuery(validQuery);
    expect(result).toEqual(validResponse);
  });

  it('sends a POST request with JSON body and correct headers', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(validResponse),
    } as Response);

    await postQuery(validQuery);

    const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe('POST');
    expect((init.headers as Record<string, string>)['Content-Type']).toBe('application/json');
    expect(JSON.parse(init.body as string)).toMatchObject({ content: 'What is consciousness?' });
  });

  it('throws when the response shape is invalid', async () => {
    mockFetch({ unexpected: true });

    await expect(postQuery(validQuery)).rejects.toThrow('Unexpected response shape from POST /');
  });

  it('throws when the response is not ok', async () => {
    mockFetch(null, false, 503);

    await expect(postQuery(validQuery)).rejects.toThrow('Query failed: 503');
  });
});

// ---------------------------------------------------------------------------
// deleteConversation
// ---------------------------------------------------------------------------
describe('deleteConversation', () => {
  it('resolves without a value on success', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      status: 204,
    } as Response);

    await expect(deleteConversation('conv-99')).resolves.toBeUndefined();
  });

  it('sends a DELETE request to the correct URL', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      status: 204,
    } as Response);

    await deleteConversation('conv-99');

    expect(fetchSpy.mock.calls[0][0]).toContain('/api/delete/conv-99');
    expect((fetchSpy.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
  });

  it('throws when the response is not ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 404,
    } as Response);

    await expect(deleteConversation('conv-99')).rejects.toThrow('Failed to delete conversation: 404');
  });
});
