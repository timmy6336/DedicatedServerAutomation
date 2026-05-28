import { useState } from 'react'
import { GAMES, type Game } from './lib/games'
import TitleBar from './components/TitleBar'
import Sidebar from './components/Sidebar'
import ServerPanel from './components/ServerPanel'

export default function App() {
  const [selected, setSelected] = useState<Game>(GAMES[0])

  return (
    <div className="flex flex-col h-screen bg-[#09090b] text-[#fafafa]">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar games={GAMES} selected={selected} onSelect={setSelected} />
        <main className="flex-1 overflow-hidden">
          <ServerPanel key={selected.id} game={selected} />
        </main>
      </div>
    </div>
  )
}
