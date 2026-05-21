import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import HomePage from './components/HomePage'
import ChatWindow from './components/ChatWindow'

const API_BASE = '/api'

export default function App() {
  const [conversations, setConversations] = useState([])
  const [activeConvId, setActiveConvId] = useState(null)
  const [view, setView] = useState('home')
  const [autoMessage, setAutoMessage] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/conversations`)
      const data = await res.json()
      setConversations(data)
    } catch {
      // Backend henüz başlamadıysa sessizce geç
    }
  }, [])

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  const createConversation = async (title = null) => {
    const res = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    })
    const conv = await res.json()
    setConversations(prev => [conv, ...prev])
    return conv
  }

  const handleNewChat = async () => {
    const conv = await createConversation('Yeni Sohbet')
    setAutoMessage(null)
    setActiveConvId(conv.id)
    setView('chat')
  }

  const handlePresetQuestion = async (question) => {
    const conv = await createConversation(question)
    setAutoMessage(question)
    setActiveConvId(conv.id)
    setView('chat')
  }

  const handleSelectConversation = (id) => {
    setAutoMessage(null)
    setActiveConvId(id)
    setView('chat')
  }

  const handleDeleteConversation = async (id) => {
    try {
      await fetch(`${API_BASE}/conversations/${id}`, { method: 'DELETE' })
      setConversations(prev => prev.filter(c => c.id !== id))
      if (activeConvId === id) {
        setActiveConvId(null)
        setView('home')
      }
    } catch {
      /* ignore */
    }
  }

  const handleGoHome = () => {
    setActiveConvId(null)
    setAutoMessage(null)
    setView('home')
  }

  const handleConversationUpdate = (updatedConv) => {
    setConversations(prev =>
      [...prev.map(c => (c.id === updatedConv.id ? updatedConv : c))].sort(
        (a, b) => new Date(b.updated_at) - new Date(a.updated_at),
      ),
    )
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      <Sidebar
        conversations={conversations}
        activeConvId={activeConvId}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(o => !o)}
        onSelect={handleSelectConversation}
        onDelete={handleDeleteConversation}
        onNewChat={handleNewChat}
        onGoHome={handleGoHome}
      />

      <main className="flex-1 min-w-0 overflow-hidden">
        {view === 'home' ? (
          <HomePage
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(o => !o)}
            onNewChat={handleNewChat}
            onPresetQuestion={handlePresetQuestion}
          />
        ) : (
          <ChatWindow
            key={activeConvId}
            conversationId={activeConvId}
            autoMessage={autoMessage}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(o => !o)}
            onGoHome={handleGoHome}
            onConversationUpdate={handleConversationUpdate}
          />
        )}
      </main>
    </div>
  )
}
