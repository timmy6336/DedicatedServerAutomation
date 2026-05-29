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
          <h2 className="text-base font-semibold text-[#e8e8ff]">Backups</h2>
          <p className="text-xs text-[#7070a0] mt-0.5">
            {backups.length} backup{backups.length !== 1 ? 's' : ''} · <span className="text-[#e8e8ff]">{instance.name}</span>
          </p>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating || blocked}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 active:scale-[0.98]"
          style={{ backgroundColor: game.accentColor }}
        >
          <Plus size={14} />
          {creating ? 'Creating…' : 'Create Backup'}
        </button>
      </div>

      {/* Warning */}
      {blocked && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-yellow-950/20 border border-yellow-900/40 text-sm text-yellow-400/90 shrink-0">
          <AlertTriangle size={14} className="shrink-0" />
          Stop the server before creating or restoring a backup.
        </div>
      )}

      {/* Backup list */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {backups.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-14 text-center">
            <div className="w-12 h-12 rounded-xl bg-[#18182a] border border-[#22223a] flex items-center justify-center mb-3">
              <HardDrive size={20} className="text-[#2a2a45]" />
            </div>
            <p className="text-sm text-[#7070a0]">No backups yet</p>
            <p className="text-xs text-[#404065] mt-1 max-w-xs leading-relaxed">
              Create a backup before installing updates or making major changes
            </p>
          </div>
        ) : (
          backups.map(b => (
            <div
              key={b.id}
              className="flex items-center gap-4 px-5 py-4 rounded-xl bg-[#12121a] border border-[#22223a] hover:border-[#34345a] transition-colors"
            >
              <div className="w-9 h-9 rounded-lg bg-[#18182a] border border-[#22223a] flex items-center justify-center shrink-0">
                <HardDrive size={15} className="text-[#7070a0]" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[#e8e8ff] truncate">{b.label}</p>
                <p className="text-xs text-[#404065] mt-0.5 font-mono tabular-nums">{formatBytes(b.sizeBytes)}</p>
              </div>

              {confirmRestore === b.id ? (
                <div className="flex items-center gap-2.5 shrink-0">
                  <span className="text-xs text-yellow-400">Overwrite current files?</span>
                  <button
                    onClick={() => handleRestore(b.id)}
                    disabled={!!restoring || blocked}
                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-yellow-700/80 hover:bg-yellow-600 text-white disabled:opacity-50 transition-colors"
                  >
                    {restoring === b.id ? 'Restoring…' : 'Yes, restore'}
                  </button>
                  <button
                    onClick={() => setConfirmRestore(null)}
                    className="px-3 py-1.5 rounded-xl text-xs text-[#7070a0] hover:text-[#e8e8ff] hover:bg-[#18182a] transition-all"
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
                      'flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold',
                      'bg-[#18182a] border border-[#22223a] text-[#7070a0]',
                      'hover:text-[#e8e8ff] hover:border-[#34345a]',
                      'disabled:opacity-40 disabled:cursor-not-allowed transition-all'
                    )}
                  >
                    <RotateCcw size={12} />
                    Restore
                  </button>
                  <button
                    onClick={() => handleDelete(b.id)}
                    disabled={!!restoring}
                    className="w-8 h-8 flex items-center justify-center rounded-lg text-[#404065] hover:text-red-400 hover:bg-red-950/30 disabled:opacity-40 transition-all"
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
