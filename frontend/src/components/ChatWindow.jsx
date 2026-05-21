import React, { useState, useEffect, useRef, useCallback } from 'react'

const API_BASE = '/api'

const PRESET_QUESTIONS = [
  'Çift anadal için ortalamam kaç olmalı?',
  'Kayıt yenileme (ders kayıt) işlemleri hangi tarihlerde yapılıyor?',
  'KYK Bursu almak istiyorum. Ne yapmam gerekiyor?',
  'Akademik takvime nereden ulaşabilirim?',
  'Üniversitenize nasıl dikey geçiş yapabilirim?',
  'Değişim programları hakkında nereden bilgi alabiliriz?',
  'En fazla kaç kredilik ders alabilirim?',
  'Ara sınav programı ne zaman duyurulur?',
  'Üniversitede azami öğrenim süresi ne kadardır?',
  'Yaz okulunda kaç kredilik ders alabilirim?',
]

function UserMessage({ content }) {
  return (
    <div className="flex justify-end mb-5 animate-fade-in">
      <div className="max-w-[76%] px-4 py-3 bg-blue-600 text-white rounded-2xl rounded-tr-sm shadow-sm">
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}

function AssistantMessage({ content }) {
  return (
    <div className="flex justify-start mb-5 gap-3 animate-fade-in">
      <img src="/logo.png" alt="PAU" className="w-8 h-8 rounded-xl object-contain shrink-0 mt-0.5 shadow-sm bg-white border border-gray-100" />
      <div className="max-w-[76%]">
        <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm">
          <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-5 gap-3 animate-fade-in">
      <img src="/logo.png" alt="PAU" className="w-8 h-8 rounded-xl object-contain shrink-0 mt-0.5 shadow-sm bg-white border border-gray-100" />
      <div className="px-5 py-4 bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm">
        <div className="flex items-center gap-1.5">
          {[0, 150, 300].map(delay => (
            <div
              key={delay}
              className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default function ChatWindow({
  conversationId,
  autoMessage,
  sidebarOpen,
  onToggleSidebar,
  onGoHome,
  onConversationUpdate,
}) {
  const [conversation, setConversation] = useState(null)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [fetching, setFetching] = useState(true)

  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const autoSentRef = useRef(false)

  const scrollToBottom = () =>
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })

  const fetchConversation = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}`)
      const data = await res.json()
      setConversation(data)
    } finally {
      setFetching(false)
    }
  }, [conversationId])

  useEffect(() => { fetchConversation() }, [fetchConversation])

  useEffect(() => { scrollToBottom() }, [conversation?.messages, sending])

  // Auto-send the preset question passed from the home page
  useEffect(() => {
    if (!fetching && autoMessage && !autoSentRef.current) {
      autoSentRef.current = true
      sendMessage(autoMessage)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetching])

  const adjustTextarea = () => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 128)}px`
  }

  const sendMessage = async (text) => {
    const trimmed = (text ?? input).trim()
    if (!trimmed || sending) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    setSending(true)

    // Kullanıcı mesajını anlık ekle
    setConversation(prev => ({
      ...prev,
      messages: [
        ...(prev?.messages ?? []),
        { id: `tmp-${Date.now()}`, role: 'user', content: trimmed, timestamp: new Date().toISOString() },
      ],
    }))

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId, message: trimmed }),
      })

      if (!res.ok) throw new Error('Sunucu hatası')

      // Sunucudan güncel sohbeti al
      const convRes = await fetch(`${API_BASE}/conversations/${conversationId}`)
      const updatedConv = await convRes.json()
      setConversation(updatedConv)
      onConversationUpdate(updatedConv)
    } catch {
      setConversation(prev => ({
        ...prev,
        messages: [
          ...(prev?.messages ?? []),
          {
            id: `err-${Date.now()}`,
            role: 'assistant',
            content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
            timestamp: new Date().toISOString(),
          },
        ],
      }))
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const messages = conversation?.messages ?? []
  const isEmpty = !fetching && messages.length === 0 && !sending

  if (fetching) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          Yükleniyor…
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Başlık çubuğu */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-2 shrink-0">
        {/* Kenar çubuğu aç/kapat */}
        {!sidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg text-slate-500 hover:text-slate-700 transition-colors"
            title="Kenar çubuğunu aç"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}

        {/* Ana Sayfa */}
        <button
          onClick={onGoHome}
          className="p-2 hover:bg-gray-100 rounded-lg text-slate-500 hover:text-slate-700 transition-colors"
          title="Ana Sayfa"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
        </button>

        {/* Ayraç */}
        <div className="w-px h-5 bg-gray-200 mx-1" />

        {/* Sohbet başlığı */}
        <h1 className="flex-1 text-sm font-semibold text-slate-700 truncate">
          {conversation?.title || 'Sohbet'}
        </h1>
      </header>

      {/* Mesaj alanı */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto">
          {isEmpty ? (
            /* Boş durum — hazır sorular */
            <div className="text-center py-6 animate-fade-in">
              <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-slate-700 mb-1">Nasıl yardımcı olabilirim?</h2>
              <p className="text-slate-400 text-sm mb-6">
                Sorunuzu yazın ya da aşağıdaki önerilerden birini seçin
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                {PRESET_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(q)}
                    className="px-4 py-3 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-xl text-left text-sm text-slate-600 hover:text-blue-700 transition-all duration-200 shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map(msg =>
                msg.role === 'user' ? (
                  <UserMessage key={msg.id} content={msg.content} />
                ) : (
                  <AssistantMessage
                    key={msg.id}
                    content={msg.content}
                  />
                ),
              )}
              {sending && <TypingIndicator />}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Giriş alanı */}
      <div className="bg-white border-t border-gray-200 px-4 py-4 shrink-0">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-end gap-3 bg-gray-50 border border-gray-300 rounded-2xl px-4 py-3 transition-all focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => { setInput(e.target.value); adjustTextarea() }}
              onKeyDown={handleKeyDown}
              placeholder="Sorunuzu yazın…"
              disabled={sending}
              rows={1}
              className="flex-1 bg-transparent resize-none outline-none text-sm text-slate-800 placeholder-slate-400 overflow-hidden disabled:opacity-60 leading-relaxed"
              style={{ minHeight: '24px', maxHeight: '128px' }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || sending}
              className="w-9 h-9 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-gray-300 text-white rounded-xl flex items-center justify-center transition-colors shrink-0 shadow-sm"
              title="Gönder"
            >
              {sending ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              )}
            </button>
          </div>
          <p className="text-xs text-slate-400 text-center mt-2">
            Enter ile gönder · Shift+Enter yeni satır
          </p>
        </div>
      </div>
    </div>
  )
}
