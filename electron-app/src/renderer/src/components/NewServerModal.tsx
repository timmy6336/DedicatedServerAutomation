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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90">
      <div className="w-[420px] bg-[#0c0c0c] border-2 border-[#333333] rounded-xl shadow-[6px_6px_0_#111111] overflow-hidden">

        <div className="flex items-center justify-between px-6 py-5 border-b-2 border-[#2e2e2e]">
          <div>
            <h2 className="text-base font-black uppercase tracking-tight text-[#f0f0f0]">New {game.name} Server</h2>
            <p className="text-xs text-[#555555] mt-0.5 font-bold">Creates a separate install directory</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center border-2 border-[#2e2e2e] text-[#555555] hover:text-[#f0f0f0] hover:border-[#555555] shadow-[2px_2px_0_#000] transition-all"
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-6 py-5">
          <label className="block text-xs font-black text-[#888888] uppercase tracking-widest mb-2">
            Server name
          </label>
          <input
            autoFocus
            type="text"
            className="w-full px-4 py-2.5 rounded-lg bg-[#0c0c0c] border-2 border-[#2e2e2e] text-sm text-[#f0f0f0] font-medium placeholder-[#404040] focus:outline-none focus:border-[#555555] shadow-[2px_2px_0_#000] focus:shadow-[3px_3px_0_#111111] transition-all"
            placeholder={`My ${game.name} Server`}
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleCreate() }}
          />
        </div>

        <div className="px-6 py-4 border-t-2 border-[#2e2e2e] flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-bold text-[#555555] hover:text-[#f0f0f0] bg-[#1c1c1c] border-2 border-[#2e2e2e] hover:border-[#555555] shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px transition-all rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={!name.trim() || creating}
            className="px-5 py-2 text-sm font-bold text-white border-2 border-black shadow-[3px_3px_0_black] hover:shadow-[4px_4px_0_black] hover:-translate-x-px hover:-translate-y-px transition-all disabled:opacity-40 rounded-lg uppercase tracking-wider"
            style={{ backgroundColor: game.accentColor }}
          >
            {creating ? 'Creating…' : 'Create Server'}
          </button>
        </div>
      </div>
    </div>
  )
}
