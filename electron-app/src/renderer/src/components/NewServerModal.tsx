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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="w-96 bg-[#111113] border border-[#27272a] rounded-2xl shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#27272a]">
          <div>
            <h2 className="text-base font-semibold">New {game.name} Server</h2>
            <p className="text-xs text-[#71717a] mt-0.5">Creates a separate install directory</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[#71717a] hover:text-white hover:bg-[#27272a] transition-colors"
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-6 py-5">
          <label className="block text-sm font-medium text-[#e4e4e7] mb-2">
            Server name
          </label>
          <input
            autoFocus
            type="text"
            className="w-full px-3 py-2 rounded-lg bg-[#18181b] border border-[#27272a] text-sm text-white placeholder-[#52525b] focus:outline-none focus:border-[#3f3f46] transition-colors"
            placeholder={`My ${game.name} Server`}
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleCreate() }}
          />
        </div>

        <div className="px-6 py-4 border-t border-[#27272a] flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-[#a1a1aa] hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={!name.trim() || creating}
            className="px-5 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition-opacity hover:opacity-90"
            style={{ backgroundColor: game.accentColor }}
          >
            {creating ? 'Creating…' : 'Create Server'}
          </button>
        </div>
      </div>
    </div>
  )
}
