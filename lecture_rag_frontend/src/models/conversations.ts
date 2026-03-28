import type { Message } from './message'

export interface Conversations {
  [key:string]: Conversation
}

export interface Conversation {
  history: Array<Message>,
  summary: string | null
} 

// let uuid = 'j23452345n235ldsf'
// { uuid1: [ {role: 'user', content: 'something'}, {role: 'assistant', content: 'something'} ],
//   uuid2: [ {role: 'user', content: 'something'}, {role: 'assistant', content: 'something'} ]
// }