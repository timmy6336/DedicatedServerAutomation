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
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.80)', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
    >
      <div
        className="w-[420px] rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.6)] overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)', backdropFilter: 'blur(40px)', WebkitBackdropFilter: 'blur(40px)' }}
      >

        <div
          className="flex items-center justify-between px-6 py-5"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}
        >
          <div>
            <h2 className="text-base font-semibold text-white/90">New {game.name} Server</h2>
            <p className="text-xs text-white/30 mt-0.5">Creates a separate install directory</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-white/30 hover:text-white transition-all"
            style={{ background: 'rgba(255,255,255,0.04)' }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.10)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-6 py-5">
          <label className="block text-xs font-semibold text-white/40 uppercase tracking-wider mb-2">
            Server name
          </label>
          <input
            autoFocus
            type="text"
            className="w-full px-4 py-2.5 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none transition-all"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.10)', backdropFilter: 'blur(8px)' }}
            placeholder={`My ${game.name} Server`}
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleCreate() }}
            onFocus={e => {
              e.currentTarget.style.border = '1px solid rgba(255,255,255,0.30)'
              e.currentTarget.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.15)'
            }}
            onBlur={e => {
              e.currentTarget.style.border = '1px solid rgba(255,255,255,0.10)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          />
        </div>

        <div
          className="px-6 py-4 flex justify-end gap-2.5"
          style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
        >
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-white/30 hover:text-white rounded-lg transition-all"
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
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
