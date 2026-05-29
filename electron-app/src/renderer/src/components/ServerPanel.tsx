import { useState, useEffect, useCallback } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { Play, Square, Settings, Download, Globe, Monitor, Package, ScrollText, HardDrive, Trash2 } from 'lucide-react'
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
  const [confirmUninstall, setConfirmUninstall] = useState(false)

  const refresh = useCallback(async () => {
    const installed = await window.api.isInstalled(
      game.id, instance.id, game.installOnce, game.executableSubdir, game.executable
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
    setConfirmUninstall(false)
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
    await window.api.startServer(instance.id, game.id, game.launchMode, exeRelPath, args, game.installOnce)
    setTimeout(() => { refresh(); setActionPending(false) }, 2000)
  }

  async function handleStop() {
    setActionPending(true)
    await window.api.stopServer(instance.id, game.processNames)
    setTimeout(() => { refresh(); setActionPending(false) }, 1500)
  }

  async function handleUninstall() {
    setConfirmUninstall(false)
    setActionPending(true)
    await window.api.uninstallServer(game.id, instance.id, game.installOnce)
    refresh()
    setActionPending(false)
  }

  const hasMods = GAMES_WITH_MODS.includes(game.id)

  const tabs: { id: Tab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'overview', label: 'Overview', icon: <Monitor size={15} /> },
    ...(hasMods ? [{ id: 'mods' as Tab, label: 'Mods', icon: <Package size={15} />, badge: instance.enabledMods.length || undefined }] : []),
    { id: 'logs', label: 'Logs', icon: <ScrollText size={15} /> },
    { id: 'backups', label: 'Backups', icon: <HardDrive size={15} /> },
  ]

  return (
    <div className="h-full flex flex-col overflow-hidden">

      {/* Hero header */}
      <div className={cn('relative px-10 pt-12 pb-10 bg-gradient-to-br shrink-0', game.bannerColor)}>
        <div className="absolute inset-0 bg-[#09090b]/65" />
        <div className="relative z-10 flex items-start justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest mb-2.5"
               style={{ color: game.accentColor }}>
              {game.genre}
            </p>
            <h1 className="text-4xl font-bold text-white leading-tight">{instance.name}</h1>
            <p className="text-base text-[#a1a1aa] mt-2">{game.name}</p>
          </div>
          <StatusBadge state={state} />
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-1 px-8 border-b border-[#27272a] bg-[#09090b] shrink-0">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-4 text-sm border-b-2 -mb-px transition-colors',
              tab === t.id
                ? 'border-current font-medium'
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

      {/* Overview tab */}
      {tab === 'overview' && (
        <div className="flex-1 overflow-y-auto px-10 py-10 space-y-10">

          {/* Actions row */}
          <div className="flex items-center gap-3 flex-wrap">
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
                <div className="flex-1" />
                {confirmUninstall ? (
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-red-400">
                      {game.installOnce
                        ? 'Remove shared game files for all instances?'
                        : 'Remove all server files for this instance?'}
                    </span>
                    <button
                      onClick={handleUninstall}
                      className="px-4 py-2.5 rounded-lg text-sm font-medium bg-red-700 hover:bg-red-600 text-white transition-colors"
                    >
                      Yes, uninstall
                    </button>
                    <button
                      onClick={() => setConfirmUninstall(false)}
                      className="px-4 py-2.5 rounded-lg text-sm text-[#71717a] hover:text-white hover:bg-[#18181b] transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <Button variant="danger" icon={<Trash2 size={16} />}
                    onClick={() => setConfirmUninstall(true)} loading={actionPending}>
                    Uninstall
                  </Button>
                )}
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
              <div className="h-11 w-40 rounded-lg bg-[#18181b] animate-pulse" />
            )}
          </div>

          {/* Connection info — only when running */}
          {state === 'running' && (
            <div className="grid grid-cols-2 gap-4">
              <InfoCard icon={<Monitor size={16} />} label="Local IP"
                value={`${localIp}:${game.defaultPort}`} />
              <InfoCard icon={<Globe size={16} />} label="Game Port"
                value={String(game.defaultPort)} />
            </div>
          )}

          {/* About */}
          <div>
            <SectionLabel>About</SectionLabel>
            <p className="mt-4 text-base text-[#a1a1aa] leading-relaxed">{game.description}</p>
          </div>

          {/* Required Ports */}
          <div>
            <SectionLabel>Required Ports</SectionLabel>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {game.ports.map(p => (
                <div key={`${p.port}-${p.protocol}`}
                  className="px-6 py-5 rounded-xl bg-[#111113] border border-[#27272a] hover:border-[#3f3f46] transition-colors">
                  <span className="font-mono font-bold text-2xl text-white">{p.port}</span>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-sm font-medium text-[#71717a]">{p.protocol}</span>
                    {p.description && (
                      <span className="text-sm text-[#52525b]">· {p.description}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platforms */}
          <div>
            <SectionLabel>Platforms</SectionLabel>
            <div className="mt-4 flex gap-3 flex-wrap">
              {game.platforms.map(p => (
                <span key={p}
                  className="px-5 py-2.5 text-sm font-medium rounded-xl bg-[#111113] border border-[#27272a] text-[#a1a1aa]">
                  {p}
                </span>
              ))}
            </div>
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

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-bold uppercase tracking-widest text-[#52525b]">{children}</h3>
  )
}

function StatusBadge({ state }: { state: ServerState }) {
  const cfg = {
    checking:      { label: 'Checking…',    cls: 'bg-[#3f3f46] text-[#a1a1aa]',       dot: 'bg-[#71717a]' },
    not_installed: { label: 'Not Installed', cls: 'bg-[#27272a] text-[#71717a]',       dot: 'bg-[#3f3f46]' },
    stopped:       { label: 'Offline',       cls: 'bg-red-950/60 text-red-400',         dot: 'bg-red-500' },
    running:       { label: 'Online',        cls: 'bg-emerald-950/60 text-emerald-400', dot: 'bg-emerald-500 animate-pulse' }
  }
  const { label, cls, dot } = cfg[state]
  return (
    <div className={cn('flex items-center gap-2.5 px-5 py-2.5 rounded-full text-sm font-semibold', cls)}>
      <span className={cn('w-2.5 h-2.5 rounded-full shrink-0', dot)} />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-[#111113] border border-[#27272a] rounded-xl px-6 py-5">
      <div className="flex items-center gap-2 text-[#71717a] text-sm mb-2">{icon}<span>{label}</span></div>
      <p className="font-mono text-xl text-white font-semibold">{value}</p>
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
  const base = 'flex items-center gap-2.5 px-6 py-3 rounded-lg text-sm font-medium transition-all disabled:opacity-50'
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
