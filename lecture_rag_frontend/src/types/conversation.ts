import type { Message } from './message'

export interface Conversations {
  [key: string]: Conversation
}

export interface Conversation {
  history: Array<Message>,
  summary: string | null
}
