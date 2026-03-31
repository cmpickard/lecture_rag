import type { Message } from './message'

export interface Query extends Message {
  conversation_id: string,
  summary?: string | null,
  dialogue_mode: boolean
}

export interface QueryResponse {
  role: 'user' | 'assistant',
  content: string,
  conversation_id: string,
  summary?: string | null
}

export function isQueryResponse(data: unknown): data is QueryResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'role' in data &&
    'content' in data &&
    'conversation_id' in data &&
    typeof (data as QueryResponse).role === 'string' &&
    typeof (data as QueryResponse).content === 'string' &&
    typeof (data as QueryResponse).conversation_id === 'string'
  );
}
