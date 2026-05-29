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
    <div className="flex flex-col h-screen text-white" style={{ background: '#00010a' }}>
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          games={GAMES}
          selectedInstance={selectedInstance}
          onSelectInstance={handleSelectInstance}
        />

        <main className="flex-1 overflow-hidden" style={{ background: '#00010a' }}>
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
    <div className="h-full flex flex-col items-center justify-center text-center px-8 relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute w-96 h-96 rounded-full pointer-events-none" style={{ background: 'rgba(99,102,241,0.10)', filter: 'blur(120px)', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />

      <div className="relative mb-5">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(24px)' }}>
          <Server size={24} className="text-white/20" />
        </div>
      </div>
      <p className="text-base font-semibold text-white/30">No server selected</p>
      <p className="text-sm text-white/20 mt-1.5 max-w-xs leading-relaxed">
        Expand a game in the sidebar and create your first server instance
      </p>
    </div>
  )
}
