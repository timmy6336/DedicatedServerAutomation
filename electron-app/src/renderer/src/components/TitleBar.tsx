import { Minus, Square, X, Cpu } from 'lucide-react'

export default function TitleBar() {
  return (
    <div
      className="relative flex items-center justify-between h-11 px-3 shrink-0 select-none z-10"
      style={{
        background: 'rgba(0,0,0,0.40)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        WebkitAppRegion: 'drag'
      } as React.CSSProperties}
    >
      <div className="absolute bottom-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.25), transparent)' }} />

      <div className="flex items-center gap-2.5">
        <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center" style={{ boxShadow: '0 0 12px rgba(99,102,241,0.45)' }}>
          <Cpu size={12} className="text-white" />
        </div>
        <span className="text-[11px] font-semibold tracking-[0.1em] uppercase text-white/25">
          Server Manager
        </span>
      </div>

      <div
        className="flex items-center gap-0.5"
        style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
      >
        {([
          { icon: Minus, action: 'minimize', hoverBg: 'rgba(255,255,255,0.07)' },
          { icon: Square, action: 'maximize', hoverBg: 'rgba(255,255,255,0.07)' },
          { icon: X,     action: 'close',    hoverBg: 'rgba(239,68,68,0.65)' }
        ] as const).map(({ icon: Icon, action, hoverBg }) => (
          <button
            key={action}
            onClick={() => (window.api as Record<string, () => void>)[action]?.()}
            className="w-8 h-7 flex items-center justify-center rounded text-white/30 hover:text-white transition-all"
            onMouseEnter={e => (e.currentTarget.style.background = hoverBg)}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <Icon size={12} />
          </button>
        ))}
      </div>
    </div>
  )
}
