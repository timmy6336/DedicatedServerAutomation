import { Minus, Square, X, Cpu } from 'lucide-react'

export default function TitleBar() {
  return (
    <div
      className="relative flex items-center justify-between h-11 px-3 bg-[#0c0c0c] border-b-2 border-[#2e2e2e] shrink-0 select-none z-10"
      style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
    >
      <div className="flex items-center gap-2.5">
        <div className="w-6 h-6 bg-[#1c1c1c] border-2 border-[#333] flex items-center justify-center">
          <Cpu size={12} className="text-[#888888]" />
        </div>
        <span className="text-[11px] font-black tracking-[0.25em] uppercase text-[#444444]">
          Server Manager
        </span>
      </div>

      <div
        className="flex items-center gap-0.5"
        style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
      >
        {([
          { icon: Minus, action: 'minimize', hoverCls: 'hover:bg-[#1c1c1c] hover:border-[#404040]' },
          { icon: Square, action: 'maximize', hoverCls: 'hover:bg-[#1c1c1c] hover:border-[#404040]' },
          { icon: X,     action: 'close',    hoverCls: 'hover:bg-red-900/60 hover:border-red-800' }
        ] as const).map(({ icon: Icon, action, hoverCls }) => (
          <button
            key={action}
            onClick={() => (window.api as Record<string, () => void>)[action]?.()}
            className={`w-8 h-7 flex items-center justify-center border border-transparent text-[#555555] hover:text-[#f0f0f0] transition-all ${hoverCls}`}
          >
            <Icon size={12} />
          </button>
        ))}
      </div>
    </div>
  )
}
