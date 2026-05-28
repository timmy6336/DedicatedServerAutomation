import { useState, useEffect } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { cn } from '../lib/utils'
import { ChevronDown, ChevronRight, Plus, Server } from 'lucide-react'
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
      <aside className="w-64 shrink-0 bg-[#111113] border-r border-[#27272a] flex flex-col overflow-hidden">
        <div className="px-4 pt-5 pb-3">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-[#52525b] px-2">
            Servers
          </p>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
          {games.map(game => {
            const isOpen = expanded.has(game.id)
            const gameInstances = instances[game.id] ?? []

            return (
              <div key={game.id}>
                {/* Game row */}
                <button
                  onClick={() => toggle(game.id)}
                  className="w-full flex items-center gap-2.5 px-2.5 py-2.5 rounded-lg text-left text-[#71717a] hover:text-[#a1a1aa] hover:bg-[#18181b] transition-all group"
                >
                  {isOpen
                    ? <ChevronDown size={13} className="shrink-0" />
                    : <ChevronRight size={13} className="shrink-0" />
                  }
                  <div
                    className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                    style={{ backgroundColor: game.accentColor + '22', color: game.accentColor }}
                  >
                    <Server size={13} />
                  </div>
                  <span className="text-xs font-semibold tracking-wide uppercase flex-1 truncate">
                    {game.name}
                  </span>
                  <span className="text-xs text-[#3f3f46] tabular-nums">{gameInstances.length}</span>
                </button>

                {/* Instances */}
                {isOpen && (
                  <div className="pl-6 space-y-0.5 mt-1 mb-1">
                    {gameInstances.map(inst => (
                      <button
                        key={inst.id}
                        onClick={() => onSelectInstance(inst, game)}
                        className={cn(
                          'w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left transition-all',
                          selectedInstance?.id === inst.id
                            ? 'bg-[#18181b] text-white'
                            : 'text-[#a1a1aa] hover:bg-[#18181b] hover:text-white'
                        )}
                      >
                        <span
                          className="w-2 h-2 rounded-full shrink-0"
                          style={{ backgroundColor: selectedInstance?.id === inst.id ? game.accentColor : '#3f3f46' }}
                        />
                        <span className="truncate flex-1 text-sm">{inst.name}</span>
                      </button>
                    ))}

                    <button
                      onClick={() => { setCreating(game); setExpanded(prev => new Set([...prev, game.id])) }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left text-sm text-[#52525b] hover:text-[#a1a1aa] hover:bg-[#18181b] transition-all"
                    >
                      <Plus size={13} />
                      New server
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        <div className="border-t border-[#27272a] px-5 py-4">
          <p className="text-xs text-[#52525b]">v2.0.0</p>
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
