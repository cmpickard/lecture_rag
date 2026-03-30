import type { Message } from './message.ts'

export interface Query extends Message {
  conversation_id: string,
  summary?: string | null,
  dialogue_mode: boolean
}