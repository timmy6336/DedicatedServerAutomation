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
      <div className={cn('relative overflow-hidden shrink-0 bg-gradient-to-br', game.bannerColor)}
        style={{ borderLeft: `4px solid ${game.accentColor}` }}
      >
        <div className="absolute inset-0 bg-[#0c0c0c]/80" />
        <div className="relative z-10 px-10 pt-10 pb-8">
          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="mb-3">
                <span
                  className="inline-flex items-center text-[10px] font-black uppercase tracking-[0.25em] px-3 py-1 border-2 rounded-none"
                  style={{
                    color: game.accentColor,
                    borderColor: game.accentColor
                  }}
                >
                  {game.genre}
                </span>
              </div>
              <h1 className="text-3xl font-black uppercase tracking-tight text-white leading-tight">{instance.name}</h1>
              <p className="font-bold text-sm text-[#888888] mt-2">{game.name}</p>
            </div>
            <StatusBadge state={state} />
          </div>
        </div>
        <div
          className="absolute bottom-0 left-0 right-0 h-[3px]"
          style={{ backgroundColor: game.accentColor }}
        />
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-0 px-6 bg-[#0c0c0c] border-b-2 border-[#2e2e2e] shrink-0">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-1.5 px-4 py-3 text-xs font-bold uppercase tracking-wider transition-all',
              tab === t.id
                ? 'text-white -mb-[3px]'
                : 'text-[#555555] hover:text-[#888888]'
            )}
            style={tab === t.id ? { borderBottom: `3px solid ${game.accentColor}` } : undefined}
          >
            {t.icon}
            {t.label}
            {t.badge !== undefined && t.badge > 0 && (
              <span
                className="text-[10px] px-1.5 py-0.5 border-2 font-black tabular-nums"
                style={{ borderColor: game.accentColor + '80', color: game.accentColor }}
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
                    <span className="text-sm text-red-400 font-bold">
                      {game.installOnce
                        ? 'Remove shared game files for all instances?'
                        : 'Remove all server files for this instance?'}
                    </span>
                    <button
                      onClick={handleUninstall}
                      className="px-4 py-2 text-sm font-bold bg-[#1c0808] border-2 border-red-900 text-red-400 shadow-[2px_2px_0_#000] hover:-translate-x-px hover:-translate-y-px transition-all"
                    >
                      Yes, uninstall
                    </button>
                    <button
                      onClick={() => setConfirmUninstall(false)}
                      className="px-4 py-2 text-sm font-bold bg-[#1c1c1c] border-2 border-[#2e2e2e] text-[#888888] shadow-[2px_2px_0_#000] hover:-translate-x-px hover:-translate-y-px transition-all"
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
              <div className="h-10 w-36 bg-[#151515] border-2 border-[#2e2e2e] animate-pulse" />
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
            <p className="mt-3.5 text-sm text-[#888888] leading-relaxed font-medium">{game.description}</p>
          </div>

          {/* Required Ports */}
          <div>
            <SectionLabel>Required Ports</SectionLabel>
            <div className="mt-3.5 grid grid-cols-2 gap-2.5">
              {game.ports.map(p => (
                <div key={`${p.port}-${p.protocol}`}
                  className="px-5 py-4 bg-[#151515] border-2 border-[#2e2e2e] hover:border-[#444444] shadow-[3px_3px_0_#1a1a1a] transition-all">
                  <span className="font-mono font-black text-2xl text-[#f0f0f0] tabular-nums">{p.port}</span>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-black uppercase tracking-wider text-[#555555]">{p.protocol}</span>
                    {p.description && (
                      <span className="text-xs text-[#404040] font-bold">· {p.description}</span>
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
                  className="px-4 py-2 text-xs font-bold bg-[#151515] border-2 border-[#2e2e2e] text-[#888888] uppercase tracking-wider">
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
    <h3 className="text-[10px] font-black uppercase tracking-[0.25em] text-[#404040]">{children}</h3>
  )
}

function StatusBadge({ state }: { state: ServerState }) {
  const cfg = {
    checking:      { label: 'Checking',      cls: 'border-2 border-[#2e2e2e] text-[#555555]',                dot: 'bg-[#404040]' },
    not_installed: { label: 'Not Installed', cls: 'border-2 border-[#222222] text-[#444444]',                dot: 'bg-[#333333]' },
    stopped:       { label: 'Offline',       cls: 'border-2 border-red-900 text-red-400 bg-[#1a0808]',       dot: 'bg-red-500' },
    running:       { label: 'Online',        cls: 'border-2 border-emerald-800 text-emerald-400 bg-[#081a0d]', dot: 'bg-emerald-400 animate-pulse' }
  }
  const { label, cls, dot } = cfg[state]
  return (
    <div className={cn('flex items-center gap-2 px-3.5 py-1.5 text-xs font-black uppercase rounded-none', cls)}>
      <span className={cn('w-2 h-2 rounded-full shrink-0', dot)} />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-[#151515] border-2 border-[#2e2e2e] px-5 py-4 shadow-[3px_3px_0_#1a1a1a] hover:border-[#444444] hover:shadow-[4px_4px_0_#222222] transition-all">
      <div className="flex items-center gap-2 text-[#555555] text-xs mb-2.5 font-black uppercase tracking-wider">
        {icon}
        <span>{label}</span>
      </div>
      <p className="font-mono text-xl text-[#f0f0f0] font-black tabular-nums">{value}</p>
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
  const base = 'flex items-center gap-2 px-5 py-2.5 text-sm font-bold transition-all disabled:opacity-50 rounded-lg'
  const variants = {
    primary:   'text-white border-2 border-black shadow-[3px_3px_0_black] hover:shadow-[4px_4px_0_black] hover:-translate-x-px hover:-translate-y-px',
    secondary: 'bg-[#1c1c1c] border-2 border-[#2e2e2e] text-[#888888] hover:text-white hover:border-[#555555] shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px',
    danger:    'bg-[#1c0808] border-2 border-red-900 text-red-400 shadow-[2px_2px_0_#000] hover:-translate-x-px hover:-translate-y-px'
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
