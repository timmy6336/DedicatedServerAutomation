import { useState, useEffect, useCallback } from 'react'
import { type Game } from '../lib/games'
import { Play, Square, Settings, Download, Wifi, WifiOff, Globe, Monitor } from 'lucide-react'
import { cn } from '../lib/utils'
import InstallWizard from './InstallWizard'
import ConfigModal from './ConfigModal'

interface Props {
  game: Game
}

type ServerState = 'checking' | 'not_installed' | 'stopped' | 'running'

export default function ServerPanel({ game }: Props) {
  const [state, setState] = useState<ServerState>('checking')
  const [localIp, setLocalIp] = useState<string>('—')
  const [showInstall, setShowInstall] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const [actionPending, setActionPending] = useState(false)

  const refresh = useCallback(async () => {
    const installed = await window.api.isInstalled(game.id, game.executableSubdir, game.executable)
    if (!installed) { setState('not_installed'); return }
    const running = await window.api.isRunning(game.processNames)
    setState(running ? 'running' : 'stopped')
    if (running) {
      const ip = await window.api.getLocalIp()
      setLocalIp(ip)
    }
  }, [game])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 10_000)
    return () => clearInterval(id)
  }, [refresh])

  async function handleStart() {
    setActionPending(true)
    const config = (await window.api.loadConfig(game.id)) ?? {}
    const formatted = game.launchArgs.replace(/\{(\w+)\}/g, (_, k) =>
      String(config[k] ?? '')
    )
    const args = formatted.trim() ? formatted.trim().split(/\s+/) : []
    const base = await window.api.getLocalIp() // just to trigger IPC warm-up
    void base
    await window.api.startServer(game.id, game.executable, args)
    setTimeout(() => { refresh(); setActionPending(false) }, 2000)
  }

  async function handleStop() {
    setActionPending(true)
    await window.api.stopServer(game.id, game.processNames)
    setTimeout(() => { refresh(); setActionPending(false) }, 1500)
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Hero header */}
      <div className={cn('relative px-8 pt-8 pb-6 bg-gradient-to-br shrink-0', game.bannerColor)}>
        <div className="absolute inset-0 bg-[#09090b]/60" />
        <div className="relative z-10">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest mb-1"
                 style={{ color: game.accentColor }}>
                {game.genre}
              </p>
              <h1 className="text-3xl font-bold text-white mb-1">{game.name}</h1>
              <p className="text-sm text-[#a1a1aa] max-w-lg">{game.description}</p>
            </div>
            <StatusBadge state={state} />
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">

        {/* Action buttons */}
        <div className="flex gap-3">
          {state === 'not_installed' && (
            <Button
              variant="primary"
              icon={<Download size={15} />}
              onClick={() => setShowInstall(true)}
              style={{ backgroundColor: game.accentColor }}
            >
              Install Server
            </Button>
          )}
          {state === 'stopped' && (
            <>
              <Button
                variant="primary"
                icon={<Play size={15} />}
                onClick={handleStart}
                loading={actionPending}
                style={{ backgroundColor: game.accentColor }}
              >
                Start Server
              </Button>
              <Button variant="secondary" icon={<Settings size={15} />} onClick={() => setShowConfig(true)}>
                Configure
              </Button>
            </>
          )}
          {state === 'running' && (
            <>
              <Button variant="danger" icon={<Square size={15} />} onClick={handleStop} loading={actionPending}>
                Stop Server
              </Button>
              <Button variant="secondary" icon={<Settings size={15} />} onClick={() => setShowConfig(true)}>
                Configure
              </Button>
            </>
          )}
          {state === 'checking' && (
            <div className="h-9 w-32 rounded-lg bg-[#18181b] animate-pulse" />
          )}
        </div>

        {/* Connection info */}
        {state === 'running' && (
          <div className="grid grid-cols-2 gap-4 max-w-lg">
            <InfoCard icon={<Monitor size={14} />} label="Local IP" value={`${localIp}:${game.defaultPort}`} />
            <InfoCard icon={<Globe size={14} />} label="Default Port" value={String(game.defaultPort)} />
          </div>
        )}

        {/* Port info */}
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-[#52525b] mb-3">
            Required Ports
          </h3>
          <div className="flex flex-wrap gap-2">
            {game.ports.map((p) => (
              <div
                key={`${p.port}-${p.protocol}`}
                className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#18181b] border border-[#27272a] text-sm"
              >
                <span className="font-mono font-medium">{p.port}</span>
                <span className="text-[#71717a]">{p.protocol}</span>
                {p.description && <span className="text-[#52525b] text-xs">{p.description}</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Platform badges */}
        <div className="flex gap-2">
          {game.platforms.map((p) => (
            <span key={p} className="px-2 py-1 text-xs rounded bg-[#18181b] border border-[#27272a] text-[#a1a1aa]">
              {p}
            </span>
          ))}
        </div>
      </div>

      {showInstall && (
        <InstallWizard
          game={game}
          onClose={() => { setShowInstall(false); refresh() }}
        />
      )}
      {showConfig && (
        <ConfigModal
          game={game}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  )
}

// ── sub-components ───────────────────────────────────────────────────────────

function StatusBadge({ state }: { state: ServerState }) {
  const configs = {
    checking:      { label: 'Checking…',     color: 'bg-[#3f3f46] text-[#a1a1aa]', dot: 'bg-[#71717a]' },
    not_installed: { label: 'Not Installed',  color: 'bg-[#27272a] text-[#71717a]', dot: 'bg-[#3f3f46]' },
    stopped:       { label: 'Offline',        color: 'bg-red-950/60 text-red-400',   dot: 'bg-red-500' },
    running:       { label: 'Online',         color: 'bg-emerald-950/60 text-emerald-400', dot: 'bg-emerald-500 animate-pulse' }
  }
  const { label, color, dot } = configs[state]
  return (
    <div className={cn('flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium', color)}>
      <span className={cn('w-1.5 h-1.5 rounded-full', dot)} />
      {label}
    </div>
  )
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-[#111113] border border-[#27272a] rounded-lg px-4 py-3">
      <div className="flex items-center gap-1.5 text-[#71717a] text-xs mb-1">
        {icon}
        <span>{label}</span>
      </div>
      <p className="font-mono text-sm text-[#fafafa]">{value}</p>
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
  const base = 'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50'
  const variants = {
    primary:   'text-white',
    secondary: 'bg-[#18181b] border border-[#27272a] text-[#a1a1aa] hover:text-[#fafafa] hover:border-[#3f3f46]',
    danger:    'bg-red-950/40 border border-red-900/50 text-red-400 hover:bg-red-950/60'
  }
  return (
    <button
      className={cn(base, variants[variant])}
      onClick={onClick}
      disabled={loading}
      style={variant === 'primary' ? style : undefined}
    >
      {loading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : icon}
      {children}
    </button>
  )
}
