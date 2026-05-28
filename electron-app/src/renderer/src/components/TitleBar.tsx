import { Minus, Square, X, Server } from 'lucide-react'

export default function TitleBar() {
  return (
    <div
      className="flex items-center justify-between h-11 px-4 bg-[#09090b] border-b border-[#27272a] shrink-0 select-none"
      style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
    >
      <div className="flex items-center gap-2">
        <Server size={14} className="text-indigo-400" />
        <span className="text-xs font-medium text-[#a1a1aa] tracking-wide uppercase">
          Dedicated Server Automation
        </span>
      </div>

      <div
        className="flex items-center gap-0.5"
        style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
      >
        {[
          { icon: Minus, action: 'minimize', hover: 'hover:bg-[#27272a]' },
          { icon: Square, action: 'maximize', hover: 'hover:bg-[#27272a]' },
          { icon: X, action: 'close', hover: 'hover:bg-red-500/80' }
        ].map(({ icon: Icon, action, hover }) => (
          <button
            key={action}
            onClick={() => (window.api as Record<string, () => void>)[action]?.()}
            className={`w-8 h-8 flex items-center justify-center rounded ${hover} text-[#71717a] hover:text-[#fafafa] transition-colors`}
          >
            <Icon size={13} />
          </button>
        ))}
      </div>
    </div>
  )
}
