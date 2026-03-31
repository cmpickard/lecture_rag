import type { Conversations } from '../types/conversation'
import type { Query, QueryResponse } from '../types/query'
import { isQueryResponse } from '../types/query'

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export async function fetchConversations(ids: string[]): Promise<Conversations> {
  const params = new URLSearchParams(ids.map(id => ['ids', id]));
  const response = await fetch(`${BASE_URL}/api/conversations?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch conversations: ${response.status}`);
  }
  return response.json() as Promise<Conversations>;
}

export async function postQuery(query: Query): Promise<QueryResponse> {
  const response = await fetch(BASE_URL, {
    method: 'POST',
    body: JSON.stringify(query),
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Query failed: ${response.status}`);
  }
  const data: unknown = await response.json();
  if (!isQueryResponse(data)) {
    throw new Error('Unexpected response shape from POST /');
  }
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/delete/${id}`, { method: 'DELETE' });
  if (!response.ok) {
    throw new Error(`Failed to delete conversation: ${response.status}`);
  }
}
