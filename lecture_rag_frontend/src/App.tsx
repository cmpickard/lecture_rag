import { useEffect, useState } from 'react'
import './App.css'
import { type Conversations, type Conversation } from './models/conversations.ts'
import Header from './components/Header.tsx'
import DialogBox from './components/DialogBox.tsx'
import QueryForm from './components/QueryForm.tsx'
import ConversationList from './components/ConversationList.tsx'

// const dummyConversation: Array<Message> = [
//   {role: 'user', content: 'Tell me about Aristotle.'},
//   {role: 'assistant', content: 'Aristotle was a philosopher'},
//   {role: 'user', content: 'Did he write about metaphysics?'},
//   {role: 'assistant', content: 'He is actually responsible for naming metaphysics!'}
// ];
/*

*/
function App() {
  const [currConversationId, setCurrConversationId] = useState('');
  const [currConversation, setCurrConversation] = useState<Conversation>({ history: [], summary: ''})
  const [conversations, setConversations] = useState<Conversations>({});

  function getConversations() {
    let rawIdString = localStorage.getItem('conversation_ids');
    if (rawIdString === null) return;

    let conversation_ids: Array<string> = JSON.parse(rawIdString);
    let params = new URLSearchParams(conversation_ids.map(id => ["ids", id]));
    let queryString = params.toString();

    (async () => {
      try {
        let response = await fetch(`http://localhost:3000/api/conversations?${queryString}`);
        if (response.ok) {
          let data = await response.json();
          setConversations(data);
        } else {
          console.error(response.status)
        }
      } catch (err: Error | unknown) {
        console.error(err)
      }
    })();
  }

  useEffect(getConversations, []);

  return (
    <>
      <Header/>
      <DialogBox currConversation={currConversation}/>
      <QueryForm currConversation={currConversation}
                 setCurrConversation={setCurrConversation}
                 setConversations={setConversations}
                 currConversationId={currConversationId}
                 setCurrConversationId={setCurrConversationId}/>
      <ConversationList conversations={conversations}
                        currConversationId={currConversationId}
                        setCurrConversationId={setCurrConversationId}
                        setCurrConversation={setCurrConversation}/>
    </>
  )
}

export default App