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
    { id: 'overview', label: 'Overview', icon: <Monitor size={14} /> },
    ...(hasMods ? [{ id: 'mods' as Tab, label: 'Mods', icon: <Package size={14} />, badge: instance.enabledMods.length || undefined }] : []),
    { id: 'logs', label: 'Logs', icon: <ScrollText size={14} /> },
    { id: 'backups', label: 'Backups', icon: <HardDrive size={14} /> },
  ]

  return (
    <div className="h-full flex flex-col overflow-hidden">

      {/* Hero header */}
      <div
        className={cn('relative overflow-hidden px-10 pt-12 pb-9 bg-gradient-to-br shrink-0', game.bannerColor)}
      >
        <div className="absolute inset-0" style={{ background: 'rgba(0,1,10,0.30)' }} />
        {/* Ambient blobs */}
        <div
          className="absolute top-0 right-0 w-80 h-80 rounded-full pointer-events-none"
          style={{ backgroundColor: game.accentColor, filter: 'blur(100px)', opacity: 0.20 }}
        />
        <div
          className="absolute bottom-0 left-16 w-48 h-48 rounded-full pointer-events-none"
          style={{ backgroundColor: game.accentColor, filter: 'blur(80px)', opacity: 0.10 }}
        />
        <div className="relative z-10 flex items-start justify-between gap-6">
          <div>
            <div className="mb-3">
              <span
                className="inline-flex items-center text-[10px] font-bold uppercase tracking-[0.14em] px-2.5 py-1 rounded-full"
                style={{
                  background: 'rgba(255,255,255,0.08)',
                  color: game.accentColor,
                  border: `1px solid rgba(255,255,255,0.12)`,
                  backdropFilter: 'blur(8px)'
                }}
              >
                {game.genre}
              </span>
            </div>
            <h1 className="text-4xl font-bold text-white leading-tight tracking-tight">{instance.name}</h1>
            <p className="text-sm text-white/50 mt-2 font-medium">{game.name}</p>
          </div>
          <StatusBadge state={state} />
        </div>
        <div
          className="absolute bottom-0 left-0 right-0 h-px opacity-50"
          style={{ background: `linear-gradient(90deg, transparent, ${game.accentColor}80, transparent)` }}
        />
      </div>

      {/* Tab bar */}
      <div
        className="flex items-center gap-1 px-6 py-2 shrink-0"
        style={{ background: 'rgba(0,0,0,0.20)', backdropFilter: 'blur(8px)', borderBottom: '1px solid rgba(255,255,255,0.07)' }}
      >
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm transition-all',
              tab === t.id
                ? 'text-white font-medium'
                : 'text-white/40 hover:text-white/70'
            )}
            style={tab === t.id ? { background: 'rgba(255,255,255,0.08)' } : undefined}
            onMouseEnter={e => {
              if (tab !== t.id) e.currentTarget.style.background = 'rgba(255,255,255,0.04)'
            }}
            onMouseLeave={e => {
              if (tab !== t.id) e.currentTarget.style.background = 'transparent'
            }}
          >
            {t.icon}
            {t.label}
            {t.badge !== undefined && t.badge > 0 && (
              <span
                className="text-[10px] px-1.5 py-0.5 rounded-full font-medium tabular-nums"
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
        <div className="flex-1 overflow-y-auto px-10 py-8 space-y-8">

          {/* Actions row */}
          <div className="flex items-center gap-2.5 flex-wrap">
            {state === 'not_installed' && (
              <PanelButton variant="primary" icon={<Download size={15} />}
                onClick={() => setShowInstall(true)} accentColor={game.accentColor}>
                Install Server
              </PanelButton>
            )}
            {state === 'stopped' && (
              <>
                <PanelButton variant="primary" icon={<Play size={15} />}
                  onClick={handleStart} loading={actionPending} accentColor={game.accentColor}>
                  Start Server
                </PanelButton>
                <PanelButton variant="secondary" icon={<Settings size={15} />}
                  onClick={() => setShowConfig(true)}>
                  Configure
                </PanelButton>
                <div className="flex-1" />
                {confirmUninstall ? (
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-red-300/90">
                      {game.installOnce
                        ? 'Remove shared game files for all instances?'
                        : 'Remove all server files for this instance?'}
                    </span>
                    <button
                      onClick={handleUninstall}
                      className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
                      style={{ background: 'rgba(239,68,68,0.75)' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.90)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.75)')}
                    >
                      Yes, uninstall
                    </button>
                    <button
                      onClick={() => setConfirmUninstall(false)}
                      className="px-4 py-2 rounded-lg text-sm text-white/50 hover:text-white transition-colors"
                      style={{ background: 'rgba(255,255,255,0.04)' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.08)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <PanelButton variant="danger" icon={<Trash2 size={15} />}
                    onClick={() => setConfirmUninstall(true)} loading={actionPending}>
                    Uninstall
                  </PanelButton>
                )}
              </>
            )}
            {state === 'running' && (
              <>
                <PanelButton variant="danger" icon={<Square size={15} />}
                  onClick={handleStop} loading={actionPending}>
                  Stop Server
                </PanelButton>
                <PanelButton variant="secondary" icon={<Settings size={15} />}
                  onClick={() => setShowConfig(true)}>
                  Configure
                </PanelButton>
              </>
            )}
            {state === 'checking' && (
              <div className="h-10 w-36 rounded-xl animate-pulse" style={{ background: 'rgba(255,255,255,0.06)' }} />
            )}
          </div>

          {/* Connection info — only when running */}
          {state === 'running' && (
            <div className="grid grid-cols-2 gap-3">
              <InfoCard icon={<Monitor size={14} />} label="Local IP"
                value={`${localIp}:${game.defaultPort}`} />
              <InfoCard icon={<Globe size={14} />} label="Game Port"
                value={String(game.defaultPort)} />
            </div>
          )}

          {/* About */}
          <div>
            <SectionLabel>About</SectionLabel>
            <p className="mt-3.5 text-sm text-white/50 leading-relaxed">{game.description}</p>
          </div>

          {/* Required Ports */}
          <div>
            <SectionLabel>Required Ports</SectionLabel>
            <div className="mt-3.5 grid grid-cols-2 gap-2.5">
              {game.ports.map(p => (
                <div
                  key={`${p.port}-${p.protocol}`}
                  className="px-5 py-4 rounded-xl transition-all"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(24px)' }}
                  onMouseEnter={e => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.18)')}
                  onMouseLeave={e => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.07)')}
                >
                  <span className="font-mono font-bold text-2xl text-white tabular-nums">{p.port}</span>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-white/30">{p.protocol}</span>
                    {p.description && (
                      <span className="text-xs text-white/20">· {p.description}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platforms */}
          <div>
            <SectionLabel>Platforms</SectionLabel>
            <div className="mt-3.5 flex gap-2 flex-wrap">
              {game.platforms.map(p => (
                <span
                  key={p}
                  className="px-4 py-2 text-xs font-medium rounded-lg text-white/50"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}
                >
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
    <h3 className="text-[10px] font-bold uppercase tracking-[0.18em] text-white/20">{children}</h3>
  )
}

function StatusBadge({ state }: { state: ServerState }) {
  const cfg = {
    checking:      { label: 'Checking',      bg: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.40)', border: 'rgba(255,255,255,0.10)', dot: 'rgba(255,255,255,0.20)' },
    not_installed: { label: 'Not Installed', bg: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.30)', border: 'rgba(255,255,255,0.08)', dot: 'rgba(255,255,255,0.15)' },
    stopped:       { label: 'Offline',       bg: 'rgba(239,68,68,0.10)',   color: 'rgb(252,165,165)',        border: 'rgba(239,68,68,0.20)',   dot: 'rgb(248,113,113)' },
    running:       { label: 'Online',        bg: 'rgba(16,185,129,0.12)',  color: 'rgb(110,231,183)',        border: 'rgba(16,185,129,0.25)',  dot: 'rgb(52,211,153)' }
  }
  const { label, bg, color, border, dot } = cfg[state]
  return (
    <div
      className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold"
      style={{ background: bg, color, border: `1px solid ${border}`, backdropFilter: 'blur(8px)' }}
    >
      <span
        className={cn('w-2 h-2 rounded-full shrink-0', state === 'running' && 'animate-pulse')}
        style={{ backgroundColor: dot }}
      />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div
      className="rounded-xl px-5 py-4 transition-all"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(24px)' }}
      onMouseEnter={e => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.18)')}
      onMouseLeave={e => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.07)')}
    >
      <div className="flex items-center gap-2 text-white/30 text-xs mb-2.5 font-semibold uppercase tracking-wider">
        {icon}
        <span>{label}</span>
      </div>
      <p className="font-mono text-xl text-white font-bold tabular-nums">{value}</p>
    </div>
  )
}

interface PanelButtonProps {
  variant: 'primary' | 'secondary' | 'danger'
  icon?: React.ReactNode
  onClick?: () => void
  loading?: boolean
  accentColor?: string
  children: React.ReactNode
}

function PanelButton({ variant, icon, onClick, loading, accentColor, children }: PanelButtonProps) {
  const base = 'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all disabled:opacity-50 active:scale-[0.98]'

  function getStyle(hovered: boolean) {
    if (variant === 'primary') {
      return {
        backgroundColor: accentColor,
        boxShadow: hovered
          ? `0 0 30px ${accentColor}80`
          : `0 0 20px ${accentColor}66`,
        color: '#fff'
      }
    }
    if (variant === 'secondary') {
      return {
        background: hovered ? 'rgba(255,255,255,0.12)' : 'rgba(255,255,255,0.06)',
        border: `1px solid ${hovered ? 'rgba(255,255,255,0.20)' : 'rgba(255,255,255,0.12)'}`,
        color: hovered ? '#fff' : 'rgba(255,255,255,0.80)'
      }
    }
    // danger
    return {
      background: hovered ? 'rgba(239,68,68,0.20)' : 'rgba(239,68,68,0.10)',
      border: `1px solid rgba(239,68,68,0.20)`,
      color: 'rgb(252,165,165)'
    }
  }

  return (
    <button
      className={base}
      onClick={onClick}
      disabled={loading}
      style={getStyle(false)}
      onMouseEnter={e => Object.assign((e.currentTarget as HTMLButtonElement).style, getStyle(true))}
      onMouseLeave={e => Object.assign((e.currentTarget as HTMLButtonElement).style, getStyle(false))}
    >
      {loading
        ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        : icon}
      {children}
    </button>
  )
}
