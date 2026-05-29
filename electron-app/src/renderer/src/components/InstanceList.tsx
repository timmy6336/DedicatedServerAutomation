import { useState, useEffect } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { cn } from '../lib/utils'
import { Plus } from 'lucide-react'
import NewServerModal from './NewServerModal'

interface Props {
  game: Game | null
  selectedInstance: ServerInstance | null
  onSelectInstance: (instance: ServerInstance, game: Game) => void
  onInstanceCreated: (instance: ServerInstance, game: Game) => void
}

export default function InstanceList({
  game,
  selectedInstance,
  onSelectInstance,
  onInstanceCreated,
}: Props) {
  const [instances, setInstances] = useState<ServerInstance[]>([])
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    setInstances([])
    setCreating(false)
    if (!game) return

    window.api.listInstances(game.id).then((list) => {
      setInstances(list as ServerInstance[])
    })
  }, [game?.id])

  function handleCreated(inst: ServerInstance) {
    if (!game) return
    setInstances(prev => [...prev, inst])
    onInstanceCreated(inst, game)
    setCreating(false)
  }

  const count = instances.length

  return (
    <>
      <aside className="w-[220px] shrink-0 bg-[#0e0e18] border-r border-[#22223a] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-4 pt-4 pb-2 shrink-0 flex items-center justify-between">
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#404065]">
            {game ? game.name : 'Servers'}
          </p>
          {count > 0 && (
            <span className="text-[10px] text-[#404065] font-bold tabular-nums">{count}</span>
          )}
        </div>

        {/* Instance cards */}
        <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-1">
          {!game ? (
            <div className="flex flex-col items-center justify-center py-10 px-3 text-center">
              <p className="text-xs text-[#404065]">Select a game above</p>
            </div>
          ) : instances.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 px-3 text-center gap-3">
              <p className="text-xs text-[#7070a0]">
                No servers for {game.name}.
              </p>
              <button
                onClick={() => setCreating(true)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold text-white hover:opacity-90 transition-all active:scale-[0.98]"
                style={{ backgroundColor: game.accentColor }}
              >
                Create one!
              </button>
            </div>
          ) : (
            instances.map(inst => {
              const isSelected = selectedInstance?.id === inst.id
              return (
                <button
                  key={inst.id}
                  onClick={() => onSelectInstance(inst, game)}
                  className={cn(
                    'w-full text-left px-3 py-3 rounded-xl border transition-all',
                    isSelected
                      ? 'bg-[#18182a] border-[#34345a] border-l-2'
                      : 'bg-[#12121a] border-[#22223a] hover:border-[#34345a]'
                  )}
                  style={isSelected ? { borderLeftColor: game.accentColor } : undefined}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={cn(
                        'font-semibold text-sm truncate',
                        isSelected ? 'text-[#e8e8ff]' : 'text-[#7070a0]'
                      )}
                    >
                      {inst.name}
                    </span>
                    <span
                      className="w-2 h-2 rounded-full shrink-0 bg-[#404065]"
                      style={isSelected ? { backgroundColor: game.accentColor } : undefined}
                    />
                  </div>
                </button>
              )
            })
          )}
        </div>

        {/* New server button */}
        {game && instances.length > 0 && (
          <div className="shrink-0 px-2 py-2 border-t border-[#22223a]">
            <button
              onClick={() => setCreating(true)}
              className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold text-[#404065] hover:text-[#7070a0] transition-colors"
            >
              <Plus size={12} />
              New server
            </button>
          </div>
        )}
      </aside>

      {creating && game && (
        <NewServerModal
          game={game}
          onCreated={handleCreated}
          onClose={() => setCreating(false)}
        />
      )}
    </>
  )
}
