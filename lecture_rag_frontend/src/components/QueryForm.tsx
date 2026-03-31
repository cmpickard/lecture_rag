import type { SyntheticEvent } from "react";
import { useState, useRef, useEffect } from "react";
import type { Message } from '../types/message';
import type { Query } from '../types/query'
import { type Conversations, type Conversation } from '../types/conversation'
import { postQuery } from '../api/conversationApi'

export default function QueryForm({ currConversation, setCurrConversation,
                                    setConversations,
                                    currConversationId, setCurrConversationId,
                                    addIdToStorage }:
  {
    currConversation: Conversation,
    setCurrConversation: React.Dispatch<React.SetStateAction<Conversation>>,
    setConversations: React.Dispatch<React.SetStateAction<Conversations>>,
    currConversationId: string,
    setCurrConversationId: React.Dispatch<React.SetStateAction<string>>,
    addIdToStorage: (id: string) => void,
  }) {

  const [query, setQuery] = useState('');
  const [isDialogue, setIsDialogue] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = el.scrollHeight + 'px';
    }
  }, [query]);

  async function handleSubmitQuery(event: SyntheticEvent) {
    event.preventDefault();
    const new_msg: Message = { role: 'user', content: query };
    const new_history = [...currConversation.history, new_msg];
    setCurrConversation({ history: new_history, summary: currConversation.summary });
    setQuery('');

    const new_query: Query = { ...new_msg, conversation_id: currConversationId, dialogue_mode: isDialogue };

    setIsSubmitting(true);
    try {
      const message = await postQuery(new_query);

      if (currConversationId === '') {
        addIdToStorage(message.conversation_id);
        setCurrConversationId(message.conversation_id);
        setConversations(prev => ({
          ...prev,
          [message.conversation_id]: {
            history: [...new_history, { role: message.role, content: message.content }],
            summary: message.summary ?? null,
          }
        }));
      }

      setCurrConversation(prev => ({
        history: [...prev.history, { role: message.role, content: message.content }],
        summary: prev.summary,
      }));
    } catch (error: unknown) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleTyping(event: SyntheticEvent) {
    const target = event.target as HTMLTextAreaElement;
    setQuery(target.value);
  }

  return (
  <form id="query-form" onSubmit={handleSubmitQuery}>
    <div id="query-row">
      <textarea id="query-input" ref={textareaRef} onChange={handleTyping} value={query} placeholder="Ask a question..."></textarea>
      <button id="submit-btn" disabled={isSubmitting}>{isSubmitting ? '...' : 'Submit'}</button>
    </div>
    <div id="mode-row">
      <div className="switch-wrapper">
        <span className={`switch-label${!isDialogue ? ' active-mode' : ''}`}>Instruction</span>
        <label className="switch" htmlFor="toggle-option">
          <input type="checkbox" id="toggle-option" onChange={e => setIsDialogue(e.target.checked)} />
          <span className="slider"></span>
        </label>
        <span className={`switch-label${isDialogue ? ' active-mode' : ''}`}>Dialogue</span>
        <span className="tooltip-anchor">?
          <span className="tooltip-text">Use <strong>Instruction Mode</strong> for quick, direct explanations. Use <strong>Dialogue Mode</strong> for deeper investigation.</span>
        </span>
      </div>
    </div>
  </form>
  )
}
