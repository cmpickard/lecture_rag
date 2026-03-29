import { type Conversation } from '../models/conversations.ts'

export default function DialogBox({currConversation}:
    {currConversation: Conversation})
  {
  
  let nextKey = 0;

  return (<ul id="dialog-box">
    {
      !currConversation || currConversation.history.length === 0 ? '' :
      currConversation.history.map(message => {
        return <li key={nextKey++} className="message" data-role={message.role}>{message.content}</li>
      })
    }
  </ul>)
}