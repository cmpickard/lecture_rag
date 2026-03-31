import { type Conversation } from '../types/conversation'
import ReactMarkdown from 'react-markdown';

export default function DialogBox({currConversation}:
    {currConversation: Conversation})
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
  </ul>)
}