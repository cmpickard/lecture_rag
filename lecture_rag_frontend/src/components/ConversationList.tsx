import type { SyntheticEvent } from 'react';
import { type Conversations, type Conversation } from '../models/conversations.ts'

export default function ConversationList({setCurrConversation, currConversationId, setCurrConversationId, conversations, setConversations}:
    { 
      setCurrConversation: React.Dispatch<React.SetStateAction<Conversation>>,
      currConversationId: string,
      setCurrConversationId: React.Dispatch<React.SetStateAction<string>>,
      conversations: Conversations,
      setConversations: React.Dispatch<React.SetStateAction<Conversations>>
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

  async function handleDeleteConvo(event: SyntheticEvent) {
    event.preventDefault();
    let target = event.currentTarget as HTMLFormElement;
    let resource_id = target.dataset.id;
    if (resource_id === undefined) return;

    let options = {
      method: 'DELETE'
    }

    try {
      let response = await fetch(`http://localhost:3000/api/delete/${resource_id}`, options);
      if (response.ok) {
        // delete resource_id from localstorage
        let rawIds = localStorage.getItem("conversation_ids");
        let ids: Array<string> = rawIds ? JSON.parse(rawIds) : [];
        let filtered_ids = ids.filter(id => id !== resource_id);
        localStorage.setItem("conversation_ids", JSON.stringify(filtered_ids));
        // delete conversation from conversations state to trigger refresh
        let convo_copy = Object.assign({}, conversations);
        delete convo_copy[resource_id];
        setConversations(convo_copy);
        // set current conversation to new convo if user was looking at deleted convo
        if (resource_id === currConversationId) {
          setCurrConversationId('');
          setCurrConversation({history: [], summary: ''});
        }
      } else {
        console.log(response.statusText);
      }
    } catch(err: Error | unknown) {
      console.error(err);
    }
  }

  let ids = Object.keys(conversations);

  return(
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
    </ul>)
}