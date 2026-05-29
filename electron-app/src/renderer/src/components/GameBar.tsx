import { type Game } from '../lib/games'
import { Server } from 'lucide-react'

interface Props {
  games: Game[]
  selectedGame: Game | null
  onSelectGame: (game: Game) => void
}

export default function GameBar({ games, selectedGame, onSelectGame }: Props) {
  return (
    <div className="h-11 shrink-0 bg-[#0a0a12] border-b border-[#22223a] flex items-center px-3 gap-1.5 overflow-x-auto">
      {games.map(game => {
        const isSelected = selectedGame?.id === game.id
        return (
          <button
            key={game.id}
            onClick={() => onSelectGame(game)}
            className="shrink-0 flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-semibold transition-all"
            style={
              isSelected
                ? {
                    backgroundColor: game.accentColor,
                    color: '#ffffff',
                    boxShadow: `0 0 12px ${game.accentColor}4d`,
                  }
                : undefined
            }
            data-selected={isSelected}
          >
            <div
              className="w-3.5 h-3.5 flex items-center justify-center shrink-0"
              style={{ color: isSelected ? '#ffffff' : game.accentColor }}
            >
              <Server size={11} />
            </div>
            <span
              style={
                isSelected
                  ? { color: '#ffffff' }
                  : { color: '#7070a0' }
              }
              className={isSelected ? '' : 'hover:text-[#e8e8ff]'}
            >
              {game.name}
            </span>
          </button>
        )
      })}
    </div>
  )
}
