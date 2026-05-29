import { useState, useEffect } from 'react'
import { GAMES, type Game } from './lib/games'
import { type ServerInstance } from './lib/instances'
import TitleBar from './components/TitleBar'
import GameBar from './components/GameBar'
import InstanceList from './components/InstanceList'
import ServerPanel from './components/ServerPanel'
import { Server } from 'lucide-react'

export default function App() {
  const [selectedGame, setSelectedGame] = useState<Game | null>(null)
  const [selectedInstance, setSelectedInstance] = useState<ServerInstance | null>(null)

  // Auto-select first game on mount
  useEffect(() => {
    if (GAMES.length > 0) {
      setSelectedGame(GAMES[0])
    }
  }, [])

  function handleSelectGame(game: Game) {
    setSelectedGame(game)
    // No auto-select of instance on game switch — user must click a card
    setSelectedInstance(null)
  }

  function handleSelectInstance(instance: ServerInstance, game: Game) {
    setSelectedInstance(instance)
    setSelectedGame(game)
  }

  function handleInstanceCreated(instance: ServerInstance, game: Game) {
    setSelectedInstance(instance)
    setSelectedGame(game)
  }

  function handleInstanceUpdated(updated: ServerInstance) {
    setSelectedInstance(updated)
  }

  return (
    <div className="flex flex-col h-screen bg-[#0d0d14] text-[#e8e8ff]">
      <TitleBar />
      <GameBar
        games={GAMES}
        selectedGame={selectedGame}
        onSelectGame={handleSelectGame}
      />
      <div className="flex flex-1 overflow-hidden">
        <InstanceList
          game={selectedGame}
          selectedInstance={selectedInstance}
          onSelectInstance={handleSelectInstance}
          onInstanceCreated={handleInstanceCreated}
        />

        <main className="flex-1 overflow-hidden bg-[#0d0d14]">
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
        <div className="relative w-16 h-16 rounded-2xl bg-[#12121a] border border-[#22223a] flex items-center justify-center">
          <Server size={24} className="text-[#404065]" />
        </div>
      </div>
      <p className="text-base font-semibold text-[#404065]">No server selected</p>
      <p className="text-sm text-[#404065] mt-1.5 max-w-xs leading-relaxed">
        Select a game above, then pick a server from the list or create a new one
      </p>
    </div>
  )
}
