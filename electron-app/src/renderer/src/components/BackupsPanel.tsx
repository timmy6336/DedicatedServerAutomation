import { useState, useEffect } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { HardDrive, Plus, RotateCcw, Trash2, AlertTriangle } from 'lucide-react'
import { cn } from '../lib/utils'

interface BackupEntry {
  id: string
  label: string
  sizeBytes: number
}

interface Props {
  game: Game
  instance: ServerInstance
  serverRunning: boolean
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
}

export default function BackupsPanel({ game, instance, serverRunning }: Props) {
  const [backups, setBackups] = useState<BackupEntry[]>([])
  const [creating, setCreating] = useState(false)
  const [restoring, setRestoring] = useState<string | null>(null)
  const [confirmRestore, setConfirmRestore] = useState<string | null>(null)

  useEffect(() => {
    loadBackups()
  }, [game.id, instance.id])

  async function loadBackups() {
    const list = await window.api.listBackups(game.id, instance.id) as BackupEntry[]
    setBackups(list)
  }

  async function handleCreate() {
    setCreating(true)
    await window.api.createBackup(game.id, instance.id)
    await loadBackups()
    setCreating(false)
  }

  async function handleRestore(id: string) {
    setRestoring(id)
    setConfirmRestore(null)
    await window.api.restoreBackup(game.id, instance.id, id)
    setRestoring(null)
    await loadBackups()
  }

  async function handleDelete(id: string) {
    await window.api.deleteBackup(game.id, instance.id, id)
    await loadBackups()
  }

  const blocked = serverRunning

  return (
    <div className="h-full flex flex-col px-8 py-6 gap-4 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-base font-black uppercase tracking-tight text-[#f0f0f0]">Backups</h2>
          <p className="text-xs text-[#555555] mt-0.5 font-bold">
            {backups.length} backup{backups.length !== 1 ? 's' : ''} · <span className="text-[#888888]">{instance.name}</span>
          </p>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating || blocked}
          className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white border-2 border-black shadow-[3px_3px_0_black] hover:shadow-[4px_4px_0_black] hover:-translate-x-px hover:-translate-y-px transition-all disabled:opacity-50 disabled:cursor-not-allowed rounded-lg uppercase tracking-wider"
          style={{ backgroundColor: game.accentColor }}
        >
          <Plus size={14} />
          {creating ? 'Creating…' : 'Create Backup'}
        </button>
      </div>

      {/* Warning */}
      {blocked && (
        <div className="flex items-center gap-3 px-4 py-3 bg-[#1a1200] border-2 border-yellow-900 text-sm text-yellow-400 font-bold shrink-0 shadow-[2px_2px_0_#000]">
          <AlertTriangle size={14} className="shrink-0" />
          Stop the server before creating or restoring a backup.
        </div>
      )}

      {/* Backup list */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {backups.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-14 text-center">
            <div className="w-12 h-12 bg-[#151515] border-2 border-[#2e2e2e] flex items-center justify-center mb-3 shadow-[4px_4px_0_#1a1a1a]">
              <HardDrive size={20} className="text-[#2e2e2e]" />
            </div>
            <p className="text-sm text-[#555555] font-black uppercase tracking-wider">No backups yet</p>
            <p className="text-xs text-[#404040] mt-1 max-w-xs leading-relaxed font-bold">
              Create a backup before installing updates or making major changes
            </p>
          </div>
        ) : (
          backups.map(b => (
            <div
              key={b.id}
              className="flex items-center gap-4 px-5 py-4 bg-[#151515] border-2 border-[#2e2e2e] hover:border-[#444444] shadow-[3px_3px_0_#1a1a1a] hover:shadow-[4px_4px_0_#222222] transition-all rounded-xl"
            >
              <div className="w-9 h-9 bg-[#1c1c1c] border-2 border-[#2e2e2e] flex items-center justify-center shrink-0">
                <HardDrive size={15} className="text-[#555555]" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-[#f0f0f0] truncate">{b.label}</p>
                <p className="text-xs text-[#404040] mt-0.5 font-mono tabular-nums">{formatBytes(b.sizeBytes)}</p>
              </div>

              {confirmRestore === b.id ? (
                <div className="flex items-center gap-2.5 shrink-0">
                  <span className="text-xs text-yellow-400 font-black uppercase tracking-wider">Overwrite current files?</span>
                  <button
                    onClick={() => handleRestore(b.id)}
                    disabled={!!restoring || blocked}
                    className="px-3 py-1.5 text-xs font-bold bg-[#1a1200] border-2 border-yellow-800 text-yellow-400 hover:border-yellow-600 shadow-[2px_2px_0_#000] disabled:opacity-50 transition-all rounded-lg"
                  >
                    {restoring === b.id ? 'Restoring…' : 'Yes, restore'}
                  </button>
                  <button
                    onClick={() => setConfirmRestore(null)}
                    className="px-3 py-1.5 text-xs font-bold bg-[#1c1c1c] border-2 border-[#2e2e2e] text-[#555555] hover:text-[#f0f0f0] hover:border-[#555555] shadow-[2px_2px_0_#000] transition-all rounded-lg"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => setConfirmRestore(b.id)}
                    disabled={!!restoring || blocked}
                    className={cn(
                      'flex items-center gap-2 px-3.5 py-2 text-xs font-bold',
                      'bg-[#1c1c1c] border-2 border-[#2e2e2e] text-[#888888]',
                      'hover:text-white hover:border-[#555555]',
                      'shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px',
                      'disabled:opacity-40 disabled:cursor-not-allowed transition-all rounded-lg'
                    )}
                  >
                    <RotateCcw size={12} />
                    Restore
                  </button>
                  <button
                    onClick={() => handleDelete(b.id)}
                    disabled={!!restoring}
                    className="w-8 h-8 flex items-center justify-center border-2 border-transparent text-[#404040] hover:text-red-400 hover:bg-[#1c0808] hover:border-red-900 disabled:opacity-40 transition-all"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
