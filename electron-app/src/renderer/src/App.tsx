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
    <div className="flex flex-col h-screen bg-[#0c0c0c] text-[#f0f0f0]">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          games={GAMES}
          selectedInstance={selectedInstance}
          onSelectInstance={handleSelectInstance}
        />

        <main className="flex-1 overflow-hidden bg-[#0c0c0c]">
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
      <div className="relative mb-6">
        <div className="w-16 h-16 bg-[#151515] border-2 border-[#2e2e2e] flex items-center justify-center shadow-[4px_4px_0_#1a1a1a]">
          <Server size={24} className="text-[#404040]" />
        </div>
      </div>
      <p className="text-base font-black uppercase tracking-wider text-[#555555]">No server selected</p>
      <p className="text-sm text-[#404040] mt-2 max-w-xs leading-relaxed font-bold">
        Expand a game in the sidebar and create your first server instance
      </p>
    </div>
  )
}
