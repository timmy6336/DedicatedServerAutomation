import { type Game } from '../lib/games'
import { cn } from '../lib/utils'
import { Server } from 'lucide-react'

interface Props {
  games: Game[]
  selected: Game
  onSelect: (g: Game) => void
}

export default function Sidebar({ games, selected, onSelect }: Props) {
  return (
    <aside className="w-56 shrink-0 bg-[#111113] border-r border-[#27272a] flex flex-col overflow-hidden">
      <div className="px-3 pt-4 pb-2">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-[#52525b] px-2">
          Game Servers
        </p>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-4 space-y-0.5">
        {games.map((game) => (
          <button
            key={game.id}
            onClick={() => onSelect(game)}
            className={cn(
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all group',
              selected.id === game.id
                ? 'bg-[#18181b] text-[#fafafa]'
                : 'text-[#a1a1aa] hover:bg-[#18181b] hover:text-[#fafafa]'
            )}
          >
            <div
              className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
              style={{ backgroundColor: game.accentColor + '22', color: game.accentColor }}
            >
              <Server size={14} />
            </div>
            <span className="text-sm font-medium truncate">{game.name}</span>
          </button>
        ))}
      </nav>

      <div className="border-t border-[#27272a] px-4 py-3">
        <p className="text-[11px] text-[#52525b]">v2.0.0</p>
      </div>
    </aside>
  )
}
