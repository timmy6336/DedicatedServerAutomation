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
      <div className={cn('relative overflow-hidden px-10 pt-12 pb-9 bg-gradient-to-br shrink-0', game.bannerColor)}>
        <div className="absolute inset-0 bg-[#09090e]/75" />
        <div
          className="absolute -top-20 -right-20 w-72 h-72 rounded-full blur-3xl opacity-15 pointer-events-none"
          style={{ backgroundColor: game.accentColor }}
        />
        <div className="relative z-10 flex items-start justify-between gap-6">
          <div>
            <div className="mb-3">
              <span
                className="inline-flex items-center text-[10px] font-bold uppercase tracking-[0.14em] px-2.5 py-1 rounded-full"
                style={{
                  backgroundColor: game.accentColor + '1e',
                  color: game.accentColor,
                  border: `1px solid ${game.accentColor}35`
                }}
              >
                {game.genre}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-white leading-tight tracking-tight">{instance.name}</h1>
            <p className="text-sm text-[#8e8ea8] mt-2 font-medium">{game.name}</p>
          </div>
          <StatusBadge state={state} />
        </div>
        <div
          className="absolute bottom-0 left-0 right-0 h-px opacity-50"
          style={{ background: `linear-gradient(90deg, transparent, ${game.accentColor}80, transparent)` }}
        />
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-1 px-6 py-2 bg-[#09090e] border-b border-[#1c1c2e] shrink-0">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm transition-all',
              tab === t.id
                ? 'bg-[#151521] text-[#e2e2ef] font-medium'
                : 'text-[#575770] hover:text-[#8e8ea8] hover:bg-[#111120]'
            )}
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
                    <span className="text-sm text-red-400/90">
                      {game.installOnce
                        ? 'Remove shared game files for all instances?'
                        : 'Remove all server files for this instance?'}
                    </span>
                    <button
                      onClick={handleUninstall}
                      className="px-4 py-2 rounded-lg text-sm font-medium bg-red-700/80 hover:bg-red-600 text-white transition-colors"
                    >
                      Yes, uninstall
                    </button>
                    <button
                      onClick={() => setConfirmUninstall(false)}
                      className="px-4 py-2 rounded-lg text-sm text-[#575770] hover:text-[#e2e2ef] hover:bg-[#151521] transition-colors"
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
              <div className="h-10 w-36 rounded-xl bg-[#151521] animate-pulse" />
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
            <p className="mt-3.5 text-sm text-[#8e8ea8] leading-relaxed">{game.description}</p>
          </div>

          {/* Required Ports */}
          <div>
            <SectionLabel>Required Ports</SectionLabel>
            <div className="mt-3.5 grid grid-cols-2 gap-2.5">
              {game.ports.map(p => (
                <div key={`${p.port}-${p.protocol}`}
                  className="px-5 py-4 rounded-xl bg-[#0f0f18] border border-[#1c1c2e] hover:border-[#28283f] transition-colors">
                  <span className="font-mono font-bold text-2xl text-[#e2e2ef] tabular-nums">{p.port}</span>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#575770]">{p.protocol}</span>
                    {p.description && (
                      <span className="text-xs text-[#383854]">· {p.description}</span>
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
                <span key={p}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-[#0f0f18] border border-[#1c1c2e] text-[#8e8ea8]">
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
    <h3 className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#383854]">{children}</h3>
  )
}

function StatusBadge({ state }: { state: ServerState }) {
  const cfg = {
    checking:      { label: 'Checking',      cls: 'bg-[#1c1c2e]/70 text-[#575770] border border-[#28283f]/50',             dot: 'bg-[#383854]' },
    not_installed: { label: 'Not Installed', cls: 'bg-[#1c1c2e]/70 text-[#575770] border border-[#28283f]/50',             dot: 'bg-[#28283f]' },
    stopped:       { label: 'Offline',       cls: 'bg-red-950/50 text-red-400 border border-red-900/40',                   dot: 'bg-red-500' },
    running:       { label: 'Online',        cls: 'bg-emerald-950/50 text-emerald-400 border border-emerald-900/40',       dot: 'bg-emerald-400 animate-pulse' }
  }
  const { label, cls, dot } = cfg[state]
  return (
    <div className={cn('flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold backdrop-blur-sm', cls)}>
      <span className={cn('w-2 h-2 rounded-full shrink-0', dot)} />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-[#0f0f18] border border-[#1c1c2e] rounded-xl px-5 py-4 hover:border-[#28283f] transition-colors">
      <div className="flex items-center gap-2 text-[#575770] text-xs mb-2.5 font-semibold uppercase tracking-wider">
        {icon}
        <span>{label}</span>
      </div>
      <p className="font-mono text-xl text-[#e2e2ef] font-bold tabular-nums">{value}</p>
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
  const variants = {
    primary:   'text-white hover:opacity-90',
    secondary: 'bg-[#151521] border border-[#1c1c2e] text-[#8e8ea8] hover:text-[#e2e2ef] hover:border-[#28283f]',
    danger:    'bg-red-950/30 border border-red-900/40 text-red-400 hover:bg-red-950/50 hover:border-red-800/60'
  }
  return (
    <button
      className={cn(base, variants[variant])}
      onClick={onClick}
      disabled={loading}
      style={variant === 'primary' ? { backgroundColor: accentColor } : undefined}
    >
      {loading
        ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        : icon}
      {children}
    </button>
  )
}
