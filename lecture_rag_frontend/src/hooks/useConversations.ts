import { useEffect, useState } from 'react'
import type { Conversation, Conversations } from '../types/conversation'
import { fetchConversations } from '../api/conversationApi'

const STORAGE_KEY = 'conversation_ids';

export function useConversations() {
  const [currConversationId, setCurrConversationId] = useState('');
  const [currConversation, setCurrConversation] = useState<Conversation>({ history: [], summary: null });
  const [conversations, setConversations] = useState<Conversations>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const rawIds = localStorage.getItem(STORAGE_KEY);
    if (rawIds === null) return;
    const ids: Array<string> = JSON.parse(rawIds);
    if (ids.length === 0) return;

    fetchConversations(ids)
      .then(data => setConversations(data))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : 'Failed to load conversations'));
  }, []);

  function addIdToStorage(id: string): void {
    const rawIds = localStorage.getItem(STORAGE_KEY);
    const ids: Array<string> = rawIds ? JSON.parse(rawIds) : [];
    ids.push(id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
  }

  function removeIdFromStorage(id: string): void {
    const rawIds = localStorage.getItem(STORAGE_KEY);
    const ids: Array<string> = rawIds ? JSON.parse(rawIds) : [];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids.filter(i => i !== id)));
  }

  return {
    currConversationId,
    setCurrConversationId,
    currConversation,
    setCurrConversation,
    conversations,
    setConversations,
    error,
    addIdToStorage,
    removeIdFromStorage,
  };
}
