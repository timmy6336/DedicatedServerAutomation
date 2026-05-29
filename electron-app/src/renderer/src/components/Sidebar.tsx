import { useState, useEffect } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { cn } from '../lib/utils'
import { ChevronRight, Plus, Server } from 'lucide-react'
import NewServerModal from './NewServerModal'

interface Props {
  games: Game[]
  selectedInstance: ServerInstance | null
  onSelectInstance: (instance: ServerInstance, game: Game) => void
}

export default function Sidebar({ games, selectedInstance, onSelectInstance }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set([games[0]?.id]))
  const [instances, setInstances] = useState<Record<string, ServerInstance[]>>({})
  const [creating, setCreating] = useState<Game | null>(null)

  useEffect(() => {
    loadAll()
  }, [games])

  async function loadAll() {
    const results: Record<string, ServerInstance[]> = {}
    await Promise.all(games.map(async g => {
      results[g.id] = await window.api.listInstances(g.id) as ServerInstance[]
    }))
    setInstances(results)

    if (!selectedInstance) {
      for (const g of games) {
        if (results[g.id]?.length) {
          onSelectInstance(results[g.id][0], g)
          break
        }
      }
    }
  }

  function toggle(gameId: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(gameId) ? next.delete(gameId) : next.add(gameId)
      return next
    })
  }

  function handleCreated(inst: ServerInstance, game: Game) {
    setInstances(prev => ({
      ...prev,
      [game.id]: [...(prev[game.id] ?? []), inst]
    }))
    setCreating(null)
    onSelectInstance(inst, game)
  }

  return (
    <>
      <aside className="w-64 shrink-0 bg-[#0c0c0c] border-r-2 border-[#2e2e2e] flex flex-col overflow-hidden">
        <div className="px-4 pt-5 pb-2.5">
          <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#333333] px-2">
            Servers
          </p>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 pb-4 space-y-px">
          {games.map(game => {
            const isOpen = expanded.has(game.id)
            const gameInstances = instances[game.id] ?? []

            return (
              <div key={game.id}>
                <button
                  onClick={() => toggle(game.id)}
                  className="w-full flex items-center gap-2 px-2.5 py-2 text-left group hover:bg-[#151515] transition-all"
                >
                  <ChevronRight
                    size={11}
                    className={cn(
                      'shrink-0 text-[#404040] transition-transform duration-200',
                      isOpen && 'rotate-90'
                    )}
                  />
                  <div
                    className="w-5 h-5 flex items-center justify-center shrink-0 border border-[#2e2e2e]"
                    style={{ color: game.accentColor }}
                  >
                    <Server size={10} />
                  </div>
                  <span className="text-xs font-black uppercase tracking-wider text-[#555555] group-hover:text-[#888888] flex-1 truncate transition-colors">
                    {game.name}
                  </span>
                  {gameInstances.length > 0 && (
                    <span className="text-[10px] text-[#404040] font-bold tabular-nums">
                      {gameInstances.length}
                    </span>
                  )}
                </button>

                {isOpen && (
                  <div className="pl-6 mt-0.5 mb-0.5 space-y-px">
                    {gameInstances.map(inst => {
                      const isSelected = selectedInstance?.id === inst.id
                      return (
                        <button
                          key={inst.id}
                          onClick={() => onSelectInstance(inst, game)}
                          className={cn(
                            'w-full flex items-center gap-2 px-3 py-2 text-left transition-all',
                            isSelected
                              ? 'bg-[#1c1c1c] text-[#f0f0f0] border-l-[3px]'
                              : 'text-[#555555] hover:bg-[#151515] hover:text-[#888888] border-l-[3px] border-transparent'
                          )}
                          style={isSelected ? { borderLeftColor: game.accentColor } : undefined}
                        >
                          <span className="truncate flex-1 text-xs font-bold">{inst.name}</span>
                        </button>
                      )
                    })}

                    <button
                      onClick={() => { setCreating(game); setExpanded(prev => new Set([...prev, game.id])) }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-left text-xs font-bold uppercase text-[#555555] hover:text-[#888888] hover:bg-[#151515] transition-all"
                    >
                      <Plus size={11} />
                      New server
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        <div className="border-t-2 border-[#2e2e2e] px-5 py-3">
          <p className="text-[10px] text-[#333333] font-black uppercase tracking-widest">v2.0.0</p>
        </div>
      </aside>

      {creating && (
        <NewServerModal
          game={creating}
          onCreated={inst => handleCreated(inst, creating)}
          onClose={() => setCreating(null)}
        />
      )}
    </>
  )
}
