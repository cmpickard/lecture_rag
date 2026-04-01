import { type Conversation } from '../types/conversation'
import ReactMarkdown from 'react-markdown';

export default function DialogBox({ currConversation, isThinking }:
    { currConversation: Conversation, isThinking: boolean })
  {

  let nextKey = 0;

  return (<ul id="dialog-box">
    {
      !currConversation || currConversation.history.length === 0 ? '' :
      currConversation.history.map(message => {
        return  <li key={nextKey++} className="message" data-role={message.role}>
                  <span className='name-tag'>{message.role === 'assistant' ? 'Talkrates' : 'You'}</span><ReactMarkdown>{message.content}</ReactMarkdown>
                </li>
      })
    }
    {isThinking && (
      <li className="message thinking-indicator" data-role="assistant">
        <span className="name-tag">Talkrates</span>
        <span className="thinking-dots">Thinking<span>.</span><span>.</span><span>.</span></span>
      </li>
    )}
  </ul>)
}