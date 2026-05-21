import React, { useState } from 'react'

function timeAgo(isoString) {
  const diff = Date.now() - new Date(isoString).getTime()
  if (diff < 60_000) return 'Az önce'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}dk önce`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}sa önce`
  return new Date(isoString).toLocaleDateString('tr-TR')
}

function ConvItem({ conv, isActive, onSelect, onDelete }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onSelect(conv.id)}
      onClick={() => onSelect(conv.id)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={`
        relative flex items-center gap-2 px-3 py-2.5 mx-2 rounded-lg cursor-pointer
        transition-all duration-150 group
        ${isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}
      `}
    >
      {/* Message icon */}
      <svg
        className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-200' : 'text-slate-500'}`}
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate leading-tight">{conv.title}</p>
        <p className={`text-xs mt-0.5 ${isActive ? 'text-blue-200' : 'text-slate-500'}`}>
          {timeAgo(conv.updated_at)}
        </p>
      </div>

      {/* Delete button — görünür sadece hover'da */}
      {hovered && (
        <button
          onClick={e => { e.stopPropagation(); onDelete(conv.id) }}
          className={`
            shrink-0 p-1 rounded-md transition-colors
            ${isActive
              ? 'text-blue-200 hover:bg-blue-700 hover:text-white'
              : 'text-slate-500 hover:bg-slate-700 hover:text-slate-200'}
          `}
          title="Sohbeti sil"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      )}
    </div>
  )
}

export default function Sidebar({
  conversations,
  activeConvId,
  isOpen,
  onSelect,
  onDelete,
  onNewChat,
  onGoHome,
}) {
  return (
    <aside
      className={`
        h-screen bg-slate-900 flex flex-col shrink-0 transition-all duration-300
        ${isOpen ? 'w-64' : 'w-0 overflow-hidden'}
      `}
    >
      {/* Logo / Marka */}
      <button
        onClick={onGoHome}
        className="flex items-center gap-3 px-4 py-4 hover:bg-slate-800 transition-colors text-left w-full"
      >
        <img src="/logo.png" alt="PAU Logo" className="w-12 h-12 rounded-xl object-contain shrink-0" />
        <div className="min-w-0">
          <p className="text-white font-semibold text-sm leading-tight truncate">PAU Asistan</p>
          <p className="text-slate-400 text-xs truncate">Öğrenci İşleri</p>
        </div>
      </button>

      {/* Yeni Sohbet */}
      <div className="px-3 pb-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-medium transition-colors shadow-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Yeni Sohbet
        </button>
      </div>

      {/* Ayraç */}
      <div className="mx-3 mb-2 border-t border-slate-700/60" />

      {/* Sohbet Listesi */}
      <div className="flex-1 overflow-y-auto sidebar-scroll">
        {conversations.length === 0 ? (
          <p className="text-slate-500 text-xs text-center px-4 py-6 leading-relaxed">
            Henüz sohbet yok.
            <br />Yeni bir sohbet başlatın.
          </p>
        ) : (
          <div className="space-y-0.5 py-1">
            {conversations.map(conv => (
              <ConvItem
                key={conv.id}
                conv={conv}
                isActive={conv.id === activeConvId}
                onSelect={onSelect}
                onDelete={onDelete}
              />
            ))}
          </div>
        )}
      </div>

    </aside>
  )
}
