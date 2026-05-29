import { useState, useEffect, useRef } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance, type ModEntry } from '../lib/instances'
import { Plus, Trash2, Package, FolderOpen, Archive, CheckCircle2, AlertCircle } from 'lucide-react'
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
  const [exportState, setExportState] = useState<{ path?: string; error?: string } | null>(null)
  const [exporting, setExporting] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadLibrary()
  }, [game.id])

  async function loadLibrary() {
    const mods = await window.api.listMods(game.id) as ModEntry[]
    setLibrary(mods)
  }

  async function handleExportBepInEx() {
    setExporting(true)
    setExportState(null)
    const result = await window.api.exportBepInEx(game.id, instance.id, instance.name) as
      { path?: string; error?: string; canceled?: boolean }
    setExporting(false)
    if (!result.canceled) setExportState(result)
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
          <h2 className="text-base font-black uppercase tracking-tight text-[#f0f0f0]">Mod Library</h2>
          <p className="text-xs text-[#555555] mt-0.5 font-bold">
            {library.length} mod{library.length !== 1 ? 's' : ''} installed ·{' '}
            {instance.enabledMods.length} enabled on <span className="text-[#888888]">{instance.name}</span>
          </p>
          {game.modsNote && (
            <p className="text-xs text-yellow-500/70 mt-1 font-bold">{game.modsNote}</p>
          )}
        </div>
        <button
          onClick={handleBrowse}
          className="flex items-center gap-2 px-3.5 py-2 bg-[#1c1c1c] border-2 border-[#2e2e2e] text-sm font-bold text-[#888888] hover:text-white hover:border-[#555555] shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px transition-all rounded-lg"
        >
          <FolderOpen size={13} />
          Browse
        </button>
      </div>

      {/* BepInEx export card */}
      {game.modsSubdir === 'BepInEx/plugins' && (
        <div className="px-8 pb-3 shrink-0">
          <div className="bg-[#151515] border-2 border-[#2e2e2e] px-4 py-3.5 flex items-start justify-between gap-4 shadow-[3px_3px_0_#1a1a1a] rounded-xl">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Archive size={13} className="text-[#555555] shrink-0" />
                <p className="text-sm font-black uppercase tracking-wide text-[#f0f0f0]">Share Mod Pack</p>
              </div>
              <p className="text-xs text-[#555555] leading-relaxed font-medium">
                Zip the BepInEx folder so players can install the same mods on their own client.
                They extract the zip directly into their {game.name} game directory.
              </p>
              {exportState?.path && (
                <div className="mt-2.5 flex items-start gap-2 text-xs text-emerald-400">
                  <CheckCircle2 size={12} className="mt-0.5 shrink-0" />
                  <span>
                    Saved to <span className="font-mono break-all">{exportState.path}</span>
                    <br />
                    <span className="text-[#555555] font-medium">
                      Players: extract the zip into their{' '}
                      {game.clientGamePath
                        ? <span className="font-mono">…\{game.clientGamePath}\</span>
                        : `${game.name} game folder`}{' '}
                      (right-click → Extract Here).
                    </span>
                  </span>
                </div>
              )}
              {exportState?.error && (
                <div className="mt-2.5 flex items-center gap-2 text-xs text-red-400">
                  <AlertCircle size={12} className="shrink-0" />
                  {exportState.error}
                </div>
              )}
            </div>
            <button
              onClick={handleExportBepInEx}
              disabled={exporting}
              className="shrink-0 flex items-center gap-2 px-3.5 py-2 bg-[#1c1c1c] border-2 border-[#2e2e2e] text-sm font-bold text-[#888888] hover:text-white hover:border-[#555555] shadow-[2px_2px_0_#000] disabled:opacity-50 disabled:cursor-not-allowed transition-all rounded-lg"
            >
              <Archive size={13} />
              {exporting ? 'Zipping…' : 'Export .zip'}
            </button>
          </div>
        </div>
      )}

      {/* Drop zone + mod list */}
      <div className="flex-1 overflow-hidden flex flex-col px-8 pb-6 gap-3">
        {/* Drop target */}
        <div
          ref={dropRef}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          className={cn(
            'border-2 border-dashed px-6 py-4 text-center transition-all shrink-0',
            draggingOver
              ? 'border-indigo-500 bg-indigo-950/20 text-indigo-300'
              : 'border-[#2e2e2e] text-[#404040] hover:border-[#444444] hover:text-[#555555]'
          )}
        >
          <Plus size={15} className="mx-auto mb-1 opacity-50" />
          <p className="text-xs font-bold">
            Drop {displayExtensions.join(', ')} files here to add to library
          </p>
        </div>

        {/* Mod list */}
        <div className="flex-1 overflow-y-auto space-y-1">
          {loading && (
            <div className="text-center py-8 text-[#404040] text-sm font-bold uppercase tracking-wider">Adding mods…</div>
          )}

          {!loading && library.length === 0 && (
            <div className="flex flex-col items-center justify-center py-14 text-center">
              <div className="w-12 h-12 bg-[#151515] border-2 border-[#2e2e2e] flex items-center justify-center mb-3 shadow-[4px_4px_0_#1a1a1a]">
                <Package size={20} className="text-[#2e2e2e]" />
              </div>
              <p className="text-sm text-[#555555] font-black uppercase tracking-wider">No mods in library yet</p>
              <p className="text-xs text-[#404040] mt-1 font-bold">
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
                  'flex items-center gap-3 px-4 py-3 border-2 transition-all group rounded-xl',
                  isEnabled
                    ? 'bg-[#151515] border-[#2e2e2e] shadow-[3px_3px_0_#1a1a1a]'
                    : 'bg-[#0c0c0c] border-transparent hover:border-[#2e2e2e]'
                )}
              >
                {/* Toggle */}
                <button
                  onClick={() => toggleMod(mod.filename, !isEnabled)}
                  className={cn(
                    'relative w-9 h-5 rounded-full transition-colors shrink-0 border-2 border-[#2e2e2e]',
                    isEnabled ? '' : 'bg-[#1c1c1c]'
                  )}
                  style={isEnabled ? { backgroundColor: game.accentColor } : undefined}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-150',
                      isEnabled ? 'left-[18px]' : 'left-0.5'
                    )}
                  />
                </button>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className={cn('text-sm font-bold truncate', isEnabled ? 'text-[#f0f0f0]' : 'text-[#888888]')}>
                    {mod.name}
                  </p>
                  <p className="text-xs text-[#404040] mt-0.5 font-mono">
                    {mod.filename} · {(mod.size / 1024).toFixed(0)} KB
                  </p>
                </div>

                {/* Enabled badge */}
                {isEnabled && (
                  <span
                    className="text-[10px] font-black px-2 py-0.5 border-2 shrink-0 uppercase tracking-wider"
                    style={{ borderColor: game.accentColor, color: game.accentColor }}
                  >
                    Enabled
                  </span>
                )}

                {/* Remove */}
                <button
                  onClick={() => handleRemoveMod(mod.filename)}
                  className="w-7 h-7 flex items-center justify-center border-2 border-transparent text-[#404040] hover:text-red-400 hover:bg-[#1c0808] hover:border-red-900 transition-all opacity-0 group-hover:opacity-100"
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
