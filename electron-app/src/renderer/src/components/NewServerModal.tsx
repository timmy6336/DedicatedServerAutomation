import { useState } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { X } from 'lucide-react'

interface Props {
  game: Game
  onCreated: (instance: ServerInstance) => void
  onClose: () => void
}

export default function NewServerModal({ game, onCreated, onClose }: Props) {
  const [name, setName] = useState('')
  const [creating, setCreating] = useState(false)

  async function handleCreate() {
    const trimmed = name.trim()
    if (!trimmed) return
    setCreating(true)
    const inst = await window.api.createInstance(game.id, trimmed) as ServerInstance
    onCreated(inst)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xl">
      <div className="w-[420px] bg-[#0f0f18] border border-[#1c1c2e] rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.6)] overflow-hidden">

        <div className="flex items-center justify-between px-6 py-5 border-b border-[#1c1c2e]">
          <div>
            <h2 className="text-base font-semibold text-[#e2e2ef]">New {game.name} Server</h2>
            <p className="text-xs text-[#575770] mt-0.5">Creates a separate install directory</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[#575770] hover:text-[#e2e2ef] hover:bg-[#1c1c2e] transition-all"
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-6 py-5">
          <label className="block text-xs font-semibold text-[#8e8ea8] uppercase tracking-wider mb-2">
            Server name
          </label>
          <input
            autoFocus
            type="text"
            className="w-full px-4 py-2.5 rounded-xl bg-[#151521] border border-[#1c1c2e] text-sm text-[#e2e2ef] placeholder-[#383854] focus:outline-none focus:border-[#28283f] focus:ring-1 focus:ring-[#28283f] transition-all"
            placeholder={`My ${game.name} Server`}
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleCreate() }}
          />
        </div>

        <div className="px-6 py-4 border-t border-[#1c1c2e] flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-[#575770] hover:text-[#e2e2ef] rounded-lg hover:bg-[#151521] transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={!name.trim() || creating}
            className="px-5 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-40 hover:opacity-90 transition-all active:scale-[0.98]"
            style={{ backgroundColor: game.accentColor }}
          >
            {creating ? 'Creating…' : 'Create Server'}
          </button>
        </div>
      </div>
    </div>
  )
}
