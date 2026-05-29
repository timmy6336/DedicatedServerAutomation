import { useState } from 'react'
import { GAMES, type Game } from './lib/games'
import { type ServerInstance } from './lib/instances'
import TitleBar from './components/TitleBar'
import Sidebar from './components/Sidebar'
import ServerPanel from './components/ServerPanel'
import { Server } from 'lucide-react'

export default function App() {
  const [selectedGame, setSelectedGame] = useState<Game | null>(null)
  const [selectedInstance, setSelectedInstance] = useState<ServerInstance | null>(null)

  function handleSelectInstance(instance: ServerInstance, game: Game) {
    setSelectedInstance(instance)
    setSelectedGame(game)
  }

  function handleInstanceUpdated(updated: ServerInstance) {
    setSelectedInstance(updated)
  }

  return (
    <div className="flex flex-col h-screen bg-[#09090e] text-[#e2e2ef]">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          games={GAMES}
          selectedInstance={selectedInstance}
          onSelectInstance={handleSelectInstance}
        />

        <main className="flex-1 overflow-hidden bg-[#09090e]">
          {selectedInstance && selectedGame ? (
            <ServerPanel
              key={selectedInstance.id}
              game={selectedGame}
              instance={selectedInstance}
              onInstanceUpdated={handleInstanceUpdated}
            />
          ) : (
            <EmptyState />
          )}
        </main>
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-8">
      <div className="relative mb-5">
        <div className="absolute inset-0 rounded-2xl bg-indigo-500/5 blur-2xl scale-150" />
        <div className="relative w-16 h-16 rounded-2xl bg-[#151521] border border-[#1c1c2e] flex items-center justify-center">
          <Server size={24} className="text-[#383854]" />
        </div>
      </div>
      <p className="text-base font-semibold text-[#575770]">No server selected</p>
      <p className="text-sm text-[#383854] mt-1.5 max-w-xs leading-relaxed">
        Expand a game in the sidebar and create your first server instance
      </p>
    </div>
  )
}
