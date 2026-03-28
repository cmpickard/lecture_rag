import type { SyntheticEvent } from "react";
import { useState } from "react";
import type { Message } from '../models/message';
import type { Query } from '../models/query'
import { type Conversations, type Conversation } from '../models/conversations'

export default function QueryForm({ currConversation, setCurrConversation,
                                    setConversations,
                                    currConversationId, setCurrConversationId, }:
  {
    currConversation: Conversation,
    setCurrConversation: React.Dispatch<React.SetStateAction<Conversation>>,
    setConversations: React.Dispatch<React.SetStateAction<Conversations>>,
    currConversationId: string,
    setCurrConversationId: React.Dispatch<React.SetStateAction<string>>
  }) {

  const [query, setQuery] = useState('');

  async function handleSubmitQuery(event: SyntheticEvent) {
    event.preventDefault();
    // first add user query to the conversation array and reset textarea
    let new_msg: Message = { role: 'user', content: query };
    let new_history = [...currConversation.history, new_msg]
    setCurrConversation({history: new_history, summary: currConversation.summary});
    setQuery('');

    let new_query: Query = { ...new_msg, conversation_id: currConversationId };

    // submit query to backend using Query type
    let body = JSON.stringify(new_query);
    let options = {
      method: 'POST',
      body: body,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    try {
      let response = await fetch('http://localhost:3000', options);

      if (response.ok) {
        let data: unknown = await response.json();
        let message = data as Query;

        if (currConversationId === '') {
          let rawIds = localStorage.getItem("conversation_ids");
          let ids: Array<string> = rawIds ? JSON.parse(rawIds) : [];
          ids.push(message.conversation_id);
          localStorage.setItem("conversation_ids", JSON.stringify(ids));
          setCurrConversationId(message.conversation_id);
          setConversations(prev => ({
            ...prev,
            [message.conversation_id]: { history: [...new_history, { role: message.role, content: message.content }], summary: message.summary ?? null }
          }));
        }

        setCurrConversation(prev => ({
          history: [...prev.history, { role: message.role, content: message.content }],
          summary: prev.summary
        }));

      } else {
        console.error(response.status);
      }
    } catch (error: Error | unknown) {
      console.error(error);
    }
  }

  function handleTyping(event: SyntheticEvent) {
    let target = event.target as HTMLFormElement
    setQuery(target.value);
  }

  return (
  <form onSubmit={handleSubmitQuery}>
    <textarea rows={25} cols={80} onChange={handleTyping} value={query}></textarea>
    <button>Submit</button>
  </form>
  )
}