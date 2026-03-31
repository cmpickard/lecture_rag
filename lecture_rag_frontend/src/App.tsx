import './App.css'
import Header from './components/Header.tsx'
import DialogBox from './components/DialogBox.tsx'
import QueryForm from './components/QueryForm.tsx'
import ConversationList from './components/ConversationList.tsx'
import { useConversations } from './hooks/useConversations.ts'

function App() {
  const {
    currConversationId, setCurrConversationId,
    currConversation, setCurrConversation,
    conversations, setConversations,
    error, addIdToStorage, removeIdFromStorage,
  } = useConversations();

  return (
    <div id="app">
      <Header/>
      {error && <p id="error-banner">{error}</p>}
      <div id="main-layout">
        <div id="chat-panel">
          <DialogBox currConversation={currConversation}/>
          <QueryForm
            currConversation={currConversation}
            setCurrConversation={setCurrConversation}
            setConversations={setConversations}
            currConversationId={currConversationId}
            setCurrConversationId={setCurrConversationId}
            addIdToStorage={addIdToStorage}
          />
        </div>
        <nav id="sidebar">
          <ConversationList
            conversations={conversations}
            setConversations={setConversations}
            currConversationId={currConversationId}
            setCurrConversationId={setCurrConversationId}
            setCurrConversation={setCurrConversation}
            removeIdFromStorage={removeIdFromStorage}
          />
        </nav>
      </div>
    </div>
  )
}

export default App
