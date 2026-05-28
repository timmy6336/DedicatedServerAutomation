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
    <div className="flex flex-col h-screen bg-[#09090b] text-[#fafafa]">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          games={GAMES}
          selectedInstance={selectedInstance}
          onSelectInstance={handleSelectInstance}
        />

        <main className="flex-1 overflow-hidden">
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
      <div className="w-14 h-14 rounded-2xl bg-[#18181b] border border-[#27272a] flex items-center justify-center mb-4">
        <Server size={22} className="text-[#52525b]" />
      </div>
      <p className="text-base font-medium text-[#a1a1aa]">No server selected</p>
      <p className="text-sm text-[#52525b] mt-1">
        Expand a game in the sidebar and create your first server
      </p>
    </div>
  )
}
