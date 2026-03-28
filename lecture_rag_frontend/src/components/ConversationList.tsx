import type { SyntheticEvent } from 'react';
import { type Conversations, type Conversation } from '../models/conversations.ts'

export default function ConversationList({setCurrConversation, currConversationId, setCurrConversationId, conversations}:
    { 
      setCurrConversation: React.Dispatch<React.SetStateAction<Conversation>>,
      currConversationId: string,
      setCurrConversationId: React.Dispatch<React.SetStateAction<string>>,
      conversations: Conversations
    }) {

  function handleSwitchConvo(event: SyntheticEvent) {
    event.preventDefault();
    let target = event.target as HTMLAnchorElement;
    let conversation_id = target.id;
    if (conversation_id === currConversationId) {
      return;
    } else if (conversation_id === "") {
      setCurrConversationId('');
      setCurrConversation({history: [], summary: ''});
    } else {
      setCurrConversationId(conversation_id);
      setCurrConversation(conversations[conversation_id]);
    }
  }

  let ids = Object.keys(conversations);

  return(
    <ul>
      {ids.map(id => {
        return <li key={id}><a id={id} href="#" onClick={handleSwitchConvo}>{conversations[id].summary ?? id}</a></li>
      })}
      <li key="new-convo"><a href="#" onClick={handleSwitchConvo}>Start a new conversation</a></li>
    </ul>)
}