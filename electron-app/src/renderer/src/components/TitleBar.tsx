import { Minus, Square, X, Cpu } from 'lucide-react'

export default function TitleBar() {
  return (
    <div
      className="relative flex items-center justify-between h-11 px-3 bg-[#09090e] shrink-0 select-none z-10"
      style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
    >
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />

      <div className="flex items-center gap-2.5">
        <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center shadow-[0_0_12px_rgba(99,102,241,0.4)]">
          <Cpu size={12} className="text-white" />
        </div>
        <span className="text-[11px] font-semibold tracking-[0.1em] uppercase text-[#383854]">
          Server Manager
        </span>
      </div>

      <div
        className="flex items-center gap-0.5"
        style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
      >
        {([
          { icon: Minus, action: 'minimize', hoverBg: 'hover:bg-[#1c1c2e]' },
          { icon: Square, action: 'maximize', hoverBg: 'hover:bg-[#1c1c2e]' },
          { icon: X,     action: 'close',    hoverBg: 'hover:bg-red-500/70' }
        ] as const).map(({ icon: Icon, action, hoverBg }) => (
          <button
            key={action}
            onClick={() => (window.api as Record<string, () => void>)[action]?.()}
            className={`w-8 h-7 flex items-center justify-center rounded text-[#575770] hover:text-[#e2e2ef] transition-all ${hoverBg}`}
          >
            <Icon size={12} />
          </button>
        ))}
      </div>
    </div>
  )
}
