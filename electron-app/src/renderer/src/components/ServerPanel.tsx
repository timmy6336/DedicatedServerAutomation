import { useState, useEffect, useCallback } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { Play, Square, Settings, Download, Globe, Monitor, Package, ScrollText, HardDrive } from 'lucide-react'
import { cn } from '../lib/utils'
import InstallWizard from './InstallWizard'
import ConfigModal from './ConfigModal'
import ModsPanel from './ModsPanel'
import LogsPanel from './LogsPanel'
import BackupsPanel from './BackupsPanel'

interface Props {
  game: Game
  instance: ServerInstance
  onInstanceUpdated: (updated: ServerInstance) => void
}

type ServerState = 'checking' | 'not_installed' | 'stopped' | 'running'
type Tab = 'overview' | 'mods' | 'logs' | 'backups'

const GAMES_WITH_MODS = ['minecraft', 'palworld', 'valheim', 'rust', 'sevendays', 'zomboid', 'vrising']

export default function ServerPanel({ game, instance, onInstanceUpdated }: Props) {
  const [state, setState] = useState<ServerState>('checking')
  const [localIp, setLocalIp] = useState<string>('—')
  const [tab, setTab] = useState<Tab>('overview')
  const [showInstall, setShowInstall] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const [actionPending, setActionPending] = useState(false)

  const refresh = useCallback(async () => {
    const installed = await window.api.isInstalled(
      game.id, instance.id, game.executableSubdir, game.executable
    )
    if (!installed) { setState('not_installed'); return }
    const running = await window.api.isRunning(instance.id, game.processNames)
    setState(running ? 'running' : 'stopped')
    if (running) {
      const ip = await window.api.getLocalIp()
      setLocalIp(ip as string)
    }
  }, [game, instance.id])

  useEffect(() => {
    setState('checking')
    setTab('overview')
    refresh()
    const id = setInterval(refresh, 10_000)
    return () => clearInterval(id)
  }, [refresh])

  useEffect(() => {
    const unsub = window.api.on('server:exit', (data: unknown) => {
      const { instanceId } = data as { instanceId: string }
      if (instanceId === instance.id) refresh()
    })
    return unsub
  }, [instance.id, refresh])

  async function handleStart() {
    setActionPending(true)
    const config = (await window.api.loadConfig(instance.id) as Record<string, unknown> | null) ?? {}
    const formatted = game.launchArgs.replace(/\{(\w+)\}/g, (_, k) => String(config[k] ?? ''))
    const args = formatted.trim() ? formatted.trim().split(/\s+/) : []
    const exeRelPath = game.executableSubdir
      ? `${game.executableSubdir}/${game.executable}`
      : game.executable
    await window.api.startServer(instance.id, game.id, game.launchMode, exeRelPath, args)
    setTimeout(() => { refresh(); setActionPending(false) }, 2000)
  }

  async function handleStop() {
    setActionPending(true)
    await window.api.stopServer(instance.id, game.processNames)
    setTimeout(() => { refresh(); setActionPending(false) }, 1500)
  }

  const hasMods = GAMES_WITH_MODS.includes(game.id)

  const tabs: { id: Tab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'overview', label: 'Overview', icon: <Monitor size={14} /> },
    ...(hasMods ? [{ id: 'mods' as Tab, label: 'Mods', icon: <Package size={14} />, badge: instance.enabledMods.length || undefined }] : []),
    { id: 'logs', label: 'Logs', icon: <ScrollText size={14} /> },
    { id: 'backups', label: 'Backups', icon: <HardDrive size={14} /> },
  ]

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Hero header */}
      <div className={cn('relative px-8 pt-8 pb-6 bg-gradient-to-br shrink-0', game.bannerColor)}>
        <div className="absolute inset-0 bg-[#09090b]/60" />
        <div className="relative z-10">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest mb-1"
                 style={{ color: game.accentColor }}>
                {game.genre}
              </p>
              <h1 className="text-3xl font-bold text-white">{instance.name}</h1>
              <p className="text-sm text-[#71717a] mt-1">{game.name}</p>
            </div>
            <StatusBadge state={state} />
          </div>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-1 px-8 border-b border-[#27272a] bg-[#09090b] shrink-0">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-3.5 text-sm border-b-2 -mb-px transition-colors',
              tab === t.id
                ? 'border-current font-medium text-white'
                : 'border-transparent text-[#71717a] hover:text-[#a1a1aa]'
            )}
            style={tab === t.id ? { borderColor: game.accentColor, color: game.accentColor } : undefined}
          >
            {t.icon}
            {t.label}
            {t.badge !== undefined && t.badge > 0 && (
              <span
                className="text-xs px-1.5 py-0.5 rounded-full font-medium"
                style={{ backgroundColor: game.accentColor + '22', color: game.accentColor }}
              >
                {t.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && (
        <div className="flex-1 overflow-y-auto px-8 py-7 space-y-8">
          {/* Actions */}
          <div className="flex gap-3">
            {state === 'not_installed' && (
              <Button variant="primary" icon={<Download size={16} />}
                onClick={() => setShowInstall(true)} style={{ backgroundColor: game.accentColor }}>
                Install Server
              </Button>
            )}
            {state === 'stopped' && (
              <>
                <Button variant="primary" icon={<Play size={16} />}
                  onClick={handleStart} loading={actionPending}
                  style={{ backgroundColor: game.accentColor }}>
                  Start Server
                </Button>
                <Button variant="secondary" icon={<Settings size={16} />}
                  onClick={() => setShowConfig(true)}>
                  Configure
                </Button>
              </>
            )}
            {state === 'running' && (
              <>
                <Button variant="danger" icon={<Square size={16} />}
                  onClick={handleStop} loading={actionPending}>
                  Stop Server
                </Button>
                <Button variant="secondary" icon={<Settings size={16} />}
                  onClick={() => setShowConfig(true)}>
                  Configure
                </Button>
              </>
            )}
            {state === 'checking' && (
              <div className="h-10 w-36 rounded-lg bg-[#18181b] animate-pulse" />
            )}
          </div>

          {/* Connection info */}
          {state === 'running' && (
            <div className="grid grid-cols-2 gap-4 max-w-lg">
              <InfoCard icon={<Monitor size={15} />} label="Local IP"
                value={`${localIp}:${game.defaultPort}`} />
              <InfoCard icon={<Globe size={15} />} label="Game Port"
                value={String(game.defaultPort)} />
            </div>
          )}

          {/* Ports */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-[#52525b] mb-4">
              Required Ports
            </h3>
            <div className="flex flex-wrap gap-2.5">
              {game.ports.map(p => (
                <div key={`${p.port}-${p.protocol}`}
                  className="flex items-center gap-2.5 px-4 py-2 rounded-lg bg-[#18181b] border border-[#27272a]">
                  <span className="font-mono font-semibold text-sm">{p.port}</span>
                  <span className="text-[#71717a] text-sm">{p.protocol}</span>
                  {p.description && <span className="text-[#52525b] text-xs">{p.description}</span>}
                </div>
              ))}
            </div>
          </div>

          {/* Platforms */}
          <div className="flex gap-2">
            {game.platforms.map(p => (
              <span key={p} className="px-3 py-1.5 text-sm rounded-lg bg-[#18181b] border border-[#27272a] text-[#a1a1aa]">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {tab === 'mods' && hasMods && (
        <div className="flex-1 overflow-hidden">
          <ModsPanel game={game} instance={instance} onInstanceUpdated={onInstanceUpdated} />
        </div>
      )}

      {tab === 'logs' && (
        <div className="flex-1 overflow-hidden">
          <LogsPanel instanceId={instance.id} serverRunning={state === 'running'} />
        </div>
      )}

      {tab === 'backups' && (
        <div className="flex-1 overflow-hidden">
          <BackupsPanel game={game} instance={instance} serverRunning={state === 'running'} />
        </div>
      )}

      {showInstall && (
        <InstallWizard
          game={game}
          instance={instance}
          onClose={() => { setShowInstall(false); refresh() }}
        />
      )}
      {showConfig && (
        <ConfigModal
          game={game}
          instance={instance}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  )
}

// ── sub-components ────────────────────────────────────────────────────────────

function StatusBadge({ state }: { state: ServerState }) {
  const cfg = {
    checking:      { label: 'Checking…',    cls: 'bg-[#3f3f46] text-[#a1a1aa]',          dot: 'bg-[#71717a]' },
    not_installed: { label: 'Not Installed', cls: 'bg-[#27272a] text-[#71717a]',          dot: 'bg-[#3f3f46]' },
    stopped:       { label: 'Offline',       cls: 'bg-red-950/60 text-red-400',            dot: 'bg-red-500' },
    running:       { label: 'Online',        cls: 'bg-emerald-950/60 text-emerald-400',    dot: 'bg-emerald-500 animate-pulse' }
  }
  const { label, cls, dot } = cfg[state]
  return (
    <div className={cn('flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium', cls)}>
      <span className={cn('w-2 h-2 rounded-full', dot)} />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-[#111113] border border-[#27272a] rounded-xl px-5 py-4">
      <div className="flex items-center gap-2 text-[#71717a] text-sm mb-1.5">{icon}<span>{label}</span></div>
      <p className="font-mono text-base text-white font-medium">{value}</p>
    </div>
  )
}

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger'
  icon?: React.ReactNode
  onClick?: () => void
  loading?: boolean
  style?: React.CSSProperties
  children: React.ReactNode
}

function Button({ variant, icon, onClick, loading, style, children }: ButtonProps) {
  const base = 'flex items-center gap-2.5 px-5 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50'
  const variants = {
    primary:   'text-white',
    secondary: 'bg-[#18181b] border border-[#27272a] text-[#a1a1aa] hover:text-white hover:border-[#3f3f46]',
    danger:    'bg-red-950/40 border border-red-900/50 text-red-400 hover:bg-red-950/60'
  }
  return (
    <button className={cn(base, variants[variant])} onClick={onClick} disabled={loading}
      style={variant === 'primary' ? style : undefined}>
      {loading
        ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        : icon}
      {children}
    </button>
  )
}
