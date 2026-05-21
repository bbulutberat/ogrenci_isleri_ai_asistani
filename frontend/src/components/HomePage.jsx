import React from 'react'

const PRESET_QUESTIONS = [
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
    label: 'Akademik',
    question: 'Çift anadal için ortalamam kaç olmalı?',
    color: 'bg-violet-50 text-violet-600 border-violet-100',
    iconBg: 'bg-violet-100 text-violet-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
    ),
    label: 'Kayıt',
    question: 'Kayıt yenileme (ders kayıt) işlemleri hangi tarihlerde yapılıyor?',
    color: 'bg-blue-50 text-blue-600 border-blue-100',
    iconBg: 'bg-blue-100 text-blue-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    label: 'Burs',
    question: 'KYK Bursu almak istiyorum. Ne yapmam gerekiyor?',
    color: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    iconBg: 'bg-emerald-100 text-emerald-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"
        />
      </svg>
    ),
    label: 'Genel',
    question: 'Akademik takvime nereden ulaşabilirim?',
    color: 'bg-amber-50 text-amber-600 border-amber-100',
    iconBg: 'bg-amber-100 text-amber-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M19 14l-7 7m0 0l-7-7m7 7V3"
        />
      </svg>
    ),
    label: 'Geçiş',
    question: 'Üniversitenize nasıl dikey geçiş yapabilirim?',
    color: 'bg-rose-50 text-rose-600 border-rose-100',
    iconBg: 'bg-rose-100 text-rose-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    label: 'Değişim',
    question: 'Değişim programları hakkında nereden bilgi alabiliriz?',
    color: 'bg-cyan-50 text-cyan-600 border-cyan-100',
    iconBg: 'bg-cyan-100 text-cyan-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
    ),
    label: 'Kredi',
    question: 'En fazla kaç kredilik ders alabilirim?',
    color: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    iconBg: 'bg-indigo-100 text-indigo-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
        />
      </svg>
    ),
    label: 'Sınav',
    question: 'Ara sınav programı ne zaman duyurulur?',
    color: 'bg-orange-50 text-orange-600 border-orange-100',
    iconBg: 'bg-orange-100 text-orange-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    label: 'Süre',
    question: 'Üniversitede azami öğrenim süresi ne kadardır?',
    color: 'bg-teal-50 text-teal-600 border-teal-100',
    iconBg: 'bg-teal-100 text-teal-600',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M12 3v1m0 16v1m8.66-13l-.87.5M4.21 15.5l-.87.5M19.79 15.5l.87.5M4.21 8.5l.87-.5M21 12h-1M4 12H3m15.36-5.36l-.7.7M6.34 17.66l-.7.7M17.66 17.66l.7.7M6.34 6.34l.7-.7"
        />
      </svg>
    ),
    label: 'Yaz Okulu',
    question: 'Yaz okulunda kaç kredilik ders alabilirim?',
    color: 'bg-yellow-50 text-yellow-600 border-yellow-100',
    iconBg: 'bg-yellow-100 text-yellow-600',
  },
]

export default function HomePage({ sidebarOpen, onToggleSidebar, onNewChat, onPresetQuestion }) {
  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50">

      {/* Üst bar — sadece sidebar kapalıyken hamburger göster */}
      {!sidebarOpen && (
        <header className="flex items-center px-5 py-3 bg-white/70 backdrop-blur border-b border-gray-100 shrink-0">
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg text-slate-500 hover:text-slate-700 transition-colors mr-2"
            title="Kenar çubuğunu aç"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <img src="/logo.png" alt="PAU Logo" className="h-7 w-auto" />
        </header>
      )}

      {/* Ana İçerik */}
      <div className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-6 py-10">

        {/* Hero Bölümü */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-block mb-6">
            <div className="relative">
              {/* Arka hale efekti */}
              <div className="absolute inset-0 bg-blue-200 rounded-3xl blur-2xl opacity-40 scale-110" />
              <div className="relative bg-white rounded-3xl p-5 shadow-xl border border-gray-100">
                <img
                  src="/logo.png"
                  alt="PAU Öğrenci İşleri Asistanı"
                  className="h-28 w-auto"
                />
              </div>
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-3 tracking-tight">
            Öğrenci İşleri Asistanı
          </h1>
          <p className="text-slate-500 text-base sm:text-lg max-w-lg mx-auto leading-relaxed">
            Pamukkale Üniversitesi öğrenci sorularınıza hızlı ve doğru yanıtlar alın.
          </p>
        </div>

        {/* Sık Sorulan Sorular */}
        <div className="w-full max-w-3xl animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-gray-200" />
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest px-2">
              Sık Sorulan Sorular
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {PRESET_QUESTIONS.map((item, idx) => (
              <button
                key={idx}
                onClick={() => onPresetQuestion(item.question)}
                className={`
                  flex items-start gap-3.5 p-4 rounded-2xl border text-left
                  bg-white hover:scale-[1.015] active:scale-[0.99]
                  transition-all duration-200 shadow-sm hover:shadow-md
                  group ${item.color.split(' ').slice(-1)[0]}
                  hover:border-blue-200
                `}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${item.iconBg}`}>
                  {item.icon}
                </div>
                <div>
                  <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full mb-1.5 ${item.color}`}>
                    {item.label}
                  </span>
                  <p className="text-sm text-slate-700 font-medium leading-snug group-hover:text-blue-700 transition-colors">
                    {item.question}
                  </p>
                </div>
              </button>
            ))}
          </div>

          {/* Serbest sohbet butonu */}
          <div className="mt-6 text-center">
            <button
              onClick={onNewChat}
              className="inline-flex items-center gap-2.5 px-7 py-3 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold rounded-2xl transition-all duration-200 shadow-lg shadow-blue-200 hover:shadow-blue-300"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              Farklı Bir Şey Sor
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
