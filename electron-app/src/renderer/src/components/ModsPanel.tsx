import { useState, useEffect, useRef } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance, type ModEntry } from '../lib/instances'
import { Plus, Trash2, Package, FolderOpen } from 'lucide-react'
import { cn } from '../lib/utils'

interface Props {
  game: Game
  instance: ServerInstance
  onInstanceUpdated: (updated: ServerInstance) => void
}

export default function ModsPanel({ game, instance, onInstanceUpdated }: Props) {
  const [library, setLibrary] = useState<ModEntry[]>([])
  const [draggingOver, setDraggingOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadLibrary()
  }, [game.id])

  async function loadLibrary() {
    const mods = await window.api.listMods(game.id) as ModEntry[]
    setLibrary(mods)
  }

  async function addFiles(paths: string[]) {
    if (!paths.length) return
    setLoading(true)
    await window.api.addMods(game.id, paths)
    await loadLibrary()
    setLoading(false)
  }

  async function handleBrowse() {
    const paths = await window.api.openModPicker(game.id) as string[]
    await addFiles(paths)
  }

  async function handleRemoveMod(filename: string) {
    await window.api.removeMod(game.id, filename)
    await loadLibrary()
    // Also remove from enabled list if present
    if (instance.enabledMods.includes(filename)) {
      await toggleMod(filename, false)
    }
  }

  async function toggleMod(filename: string, enabled: boolean) {
    const next = enabled
      ? [...instance.enabledMods, filename]
      : instance.enabledMods.filter(f => f !== filename)
    await window.api.setEnabledMods(instance.id, game.id, next)
    onInstanceUpdated({ ...instance, enabledMods: next })
  }

  // Drag-and-drop from OS
  function onDragOver(e: React.DragEvent) {
    e.preventDefault()
    const hasFiles = Array.from(e.dataTransfer.items).some(i => i.kind === 'file')
    if (hasFiles) setDraggingOver(true)
  }
  function onDragLeave(e: React.DragEvent) {
    if (!dropRef.current?.contains(e.relatedTarget as Node)) setDraggingOver(false)
  }
  async function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDraggingOver(false)
    const paths: string[] = []
    for (const item of Array.from(e.dataTransfer.items)) {
      if (item.kind === 'file') {
        const file = item.getAsFile()
        if (file) paths.push((file as File & { path?: string }).path ?? '')
      }
    }
    await addFiles(paths.filter(Boolean))
  }

  const displayExtensions = (game.modExtensions ?? ['jar', 'zip', 'dll']).map(e => `.${e}`)
  const enabledSet = new Set(instance.enabledMods)

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-8 pt-6 pb-4 shrink-0 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Mod Library</h2>
          <p className="text-xs text-[#71717a] mt-0.5">
            {library.length} mod{library.length !== 1 ? 's' : ''} installed ·{' '}
            {instance.enabledMods.length} enabled on <span className="text-[#a1a1aa]">{instance.name}</span>
          </p>
          {game.modsNote && (
            <p className="text-xs text-yellow-500/80 mt-1">{game.modsNote}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleBrowse}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#18181b] border border-[#27272a] text-sm text-[#a1a1aa] hover:text-white hover:border-[#3f3f46] transition-all"
          >
            <FolderOpen size={13} />
            Browse
          </button>
        </div>
      </div>

      {/* Drop zone + mod list */}
      <div className="flex-1 overflow-hidden flex flex-col px-8 pb-6 gap-4">
        {/* Drop target */}
        <div
          ref={dropRef}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          className={cn(
            'border-2 border-dashed rounded-xl px-6 py-4 text-center transition-all shrink-0',
            draggingOver
              ? 'border-indigo-500 bg-indigo-950/20 text-indigo-300'
              : 'border-[#27272a] text-[#52525b] hover:border-[#3f3f46]'
          )}
        >
          <Plus size={16} className="mx-auto mb-1 opacity-60" />
          <p className="text-xs">
            Drop {displayExtensions.join(', ')} files here to add to library
          </p>
        </div>

        {/* Mod list */}
        <div className="flex-1 overflow-y-auto space-y-1">
          {loading && (
            <div className="text-center py-8 text-[#52525b] text-sm">Adding mods…</div>
          )}

          {!loading && library.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Package size={32} className="text-[#3f3f46] mb-3" />
              <p className="text-sm text-[#71717a]">No mods in library yet</p>
              <p className="text-xs text-[#52525b] mt-1">
                Drop files above or click Browse to add mods
              </p>
            </div>
          )}

          {library.map(mod => {
            const isEnabled = enabledSet.has(mod.filename)
            return (
              <div
                key={mod.filename}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg border transition-all group',
                  isEnabled
                    ? 'bg-[#18181b] border-[#27272a]'
                    : 'bg-[#111113] border-transparent hover:border-[#27272a]'
                )}
              >
                {/* Toggle */}
                <button
                  onClick={() => toggleMod(mod.filename, !isEnabled)}
                  className={cn(
                    'relative w-9 h-5 rounded-full transition-colors shrink-0',
                    isEnabled ? '' : 'bg-[#3f3f46]'
                  )}
                  style={isEnabled ? { backgroundColor: game.accentColor } : undefined}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform',
                      isEnabled ? 'left-[18px]' : 'left-0.5'
                    )}
                  />
                </button>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className={cn('text-sm font-medium truncate', isEnabled ? 'text-white' : 'text-[#a1a1aa]')}>
                    {mod.name}
                  </p>
                  <p className="text-xs text-[#52525b] mt-0.5">
                    {mod.filename} · {(mod.size / 1024).toFixed(0)} KB
                  </p>
                </div>

                {/* Enabled badge */}
                {isEnabled && (
                  <span
                    className="text-[10px] font-medium px-2 py-0.5 rounded-full shrink-0"
                    style={{ backgroundColor: game.accentColor + '22', color: game.accentColor }}
                  >
                    Enabled
                  </span>
                )}

                {/* Remove from library */}
                <button
                  onClick={() => handleRemoveMod(mod.filename)}
                  className="w-7 h-7 flex items-center justify-center rounded-lg text-[#52525b] hover:text-red-400 hover:bg-red-950/30 transition-all opacity-0 group-hover:opacity-100"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
