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
          <h2 className="text-base font-semibold text-white/90">Mod Library</h2>
          <p className="text-xs text-white/30 mt-0.5">
            {library.length} mod{library.length !== 1 ? 's' : ''} installed ·{' '}
            {instance.enabledMods.length} enabled on <span className="text-white/50">{instance.name}</span>
          </p>
          {game.modsNote && (
            <p className="text-xs text-yellow-400/70 mt-1">{game.modsNote}</p>
          )}
        </div>
        <button
          onClick={handleBrowse}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm text-white/50 hover:text-white transition-all"
          style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)' }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.12)'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.20)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.12)'
          }}
        >
          <FolderOpen size={13} />
          Browse
        </button>
      </div>

      {/* BepInEx export card */}
      {game.modsSubdir === 'BepInEx/plugins' && (
        <div className="px-8 pb-3 shrink-0">
          <div
            className="rounded-xl px-4 py-3.5 flex items-start justify-between gap-4"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Archive size={13} className="text-white/30 shrink-0" />
                <p className="text-sm font-semibold text-white/70">Share Mod Pack</p>
              </div>
              <p className="text-xs text-white/30 leading-relaxed">
                Zip the BepInEx folder so players can install the same mods on their own client.
                They extract the zip directly into their {game.name} game directory.
              </p>
              {exportState?.path && (
                <div className="mt-2.5 flex items-start gap-2 text-xs text-emerald-400">
                  <CheckCircle2 size={12} className="mt-0.5 shrink-0" />
                  <span>
                    Saved to <span className="font-mono break-all">{exportState.path}</span>
                    <br />
                    <span className="text-white/30">
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
                <div className="mt-2.5 flex items-center gap-2 text-xs text-red-300">
                  <AlertCircle size={12} className="shrink-0" />
                  {exportState.error}
                </div>
              )}
            </div>
            <button
              onClick={handleExportBepInEx}
              disabled={exporting}
              className="shrink-0 flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm text-white/50 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)' }}
              onMouseEnter={e => {
                if (!exporting) (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.12)'
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'
              }}
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
          className="border-2 border-dashed rounded-xl px-6 py-4 text-center transition-all shrink-0"
          style={draggingOver ? {
            borderColor: 'rgba(99,102,241,0.60)',
            background: 'rgba(99,102,241,0.08)',
            color: 'rgb(165,180,252)'
          } : {
            borderColor: 'rgba(255,255,255,0.10)',
            color: 'rgba(255,255,255,0.20)'
          }}
        >
          <Plus size={15} className="mx-auto mb-1 opacity-50" />
          <p className="text-xs">
            Drop {displayExtensions.join(', ')} files here to add to library
          </p>
        </div>

        {/* Mod list */}
        <div className="flex-1 overflow-y-auto space-y-1">
          {loading && (
            <div className="text-center py-8 text-white/20 text-sm">Adding mods…</div>
          )}

          {!loading && library.length === 0 && (
            <div className="flex flex-col items-center justify-center py-14 text-center">
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <Package size={20} className="text-white/15" />
              </div>
              <p className="text-sm text-white/30">No mods in library yet</p>
              <p className="text-xs text-white/20 mt-1">
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
                  'flex items-center gap-3 px-4 py-3 rounded-xl transition-all group'
                )}
                style={isEnabled ? {
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.10)'
                } : {
                  background: 'transparent',
                  border: '1px solid transparent'
                }}
                onMouseEnter={e => {
                  if (!isEnabled) (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.07)'
                }}
                onMouseLeave={e => {
                  if (!isEnabled) (e.currentTarget as HTMLDivElement).style.borderColor = 'transparent'
                }}
              >
                {/* Toggle */}
                <button
                  onClick={() => toggleMod(mod.filename, !isEnabled)}
                  className="relative w-9 h-5 rounded-full transition-colors shrink-0"
                  style={isEnabled ? { backgroundColor: game.accentColor } : { background: 'rgba(255,255,255,0.15)' }}
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
                  <p className={cn('text-sm font-medium truncate', isEnabled ? 'text-white/90' : 'text-white/50')}>
                    {mod.name}
                  </p>
                  <p className="text-xs text-white/20 mt-0.5 font-mono">
                    {mod.filename} · {(mod.size / 1024).toFixed(0)} KB
                  </p>
                </div>

                {/* Enabled badge */}
                {isEnabled && (
                  <span
                    className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
                    style={{ backgroundColor: game.accentColor + '1e', color: game.accentColor }}
                  >
                    Enabled
                  </span>
                )}

                {/* Remove */}
                <button
                  onClick={() => handleRemoveMod(mod.filename)}
                  className="w-7 h-7 flex items-center justify-center rounded-lg text-white/20 hover:text-red-300 transition-all opacity-0 group-hover:opacity-100"
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.15)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
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
