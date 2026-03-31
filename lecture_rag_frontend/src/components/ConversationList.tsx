import type { SyntheticEvent } from 'react';
import { type Conversations, type Conversation } from '../types/conversation'
import { deleteConversation } from '../api/conversationApi'

export default function ConversationList({ setCurrConversation, currConversationId, setCurrConversationId, conversations, setConversations, removeIdFromStorage }:
    {
      setCurrConversation: React.Dispatch<React.SetStateAction<Conversation>>,
      currConversationId: string,
      setCurrConversationId: React.Dispatch<React.SetStateAction<string>>,
      conversations: Conversations,
      setConversations: React.Dispatch<React.SetStateAction<Conversations>>,
      removeIdFromStorage: (id: string) => void,
    }) {

  function handleSwitchConvo(event: SyntheticEvent) {
    event.preventDefault();
    const target = event.target as HTMLAnchorElement;
    const conversation_id = target.id;
    if (conversation_id === currConversationId) {
      return;
    } else if (conversation_id === "") {
      setCurrConversationId('');
      setCurrConversation({ history: [], summary: null });
    } else {
      setCurrConversationId(conversation_id);
      setCurrConversation(conversations[conversation_id]);
    }
  }

  async function handleDeleteConvo(event: SyntheticEvent) {
    event.preventDefault();
    const target = event.currentTarget as HTMLFormElement;
    const resource_id = target.dataset.id;
    if (resource_id === undefined) return;

    try {
      await deleteConversation(resource_id);
      removeIdFromStorage(resource_id);
      const convo_copy = Object.assign({}, conversations);
      delete convo_copy[resource_id];
      setConversations(convo_copy);
      if (resource_id === currConversationId) {
        setCurrConversationId('');
        setCurrConversation({ history: [], summary: null });
      }
    } catch (err: unknown) {
      console.error(err);
    }
  }

  const ids = Object.keys(conversations);

  return (
    <ul id="conversation-list">
      {ids.map(id => {
        return (
          <li key={id} className="convo-item">
            <a id={id} href="#" onClick={handleSwitchConvo}
               className={`convo-link${id === currConversationId ? ' active' : ''}`}>
              {conversations[id].summary ?? id}
            </a>
            <form onSubmit={handleDeleteConvo} data-id={id}><button className="delete-btn" title="Delete conversation">×</button></form>
          </li>
        )
      })}
      <li key="new-convo" className="convo-item new-convo-item">
        <a id="" href="#" onClick={handleSwitchConvo} className="convo-link">
          + New conversation
        </a>
      </li>
    </ul>
  )
}
