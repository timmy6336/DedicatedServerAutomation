import { useState, useEffect, useRef } from 'react'
import { type Game } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { cn } from '../lib/utils'
import { Check, X, Download, HardDrive, Rocket, Ban } from 'lucide-react'

interface StepState {
  label: string
  progress: number
  status: 'waiting' | 'active' | 'done' | 'error'
}

const DEFAULT_STEP_LABELS = ['Download SteamCMD', 'Install server files', 'Complete']
const STEP_ICONS = [Download, HardDrive, Rocket]

function makeInitialSteps(labels: string[]): StepState[] {
  return labels.map(label => ({ label, progress: 0, status: 'waiting' as const }))
}

interface Props {
  game: Game
  instance: ServerInstance
  onClose: () => void
}

export default function InstallWizard({ game, instance, onClose }: Props) {
  const [steps, setSteps] = useState<StepState[]>(() =>
    makeInitialSteps(game.installSteps ?? DEFAULT_STEP_LABELS)
  )
  const [logs, setLogs] = useState<string[]>([])
  const [started, setStarted] = useState(false)
  const [finished, setFinished] = useState(false)
  const [cancelled, setCancelled] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const unsubStep = window.api.on('install:step', (data: unknown) => {
      const { step, label, progress } = data as { step: number; label: string; progress: number }
      setSteps(prev => prev.map((s, i) => {
        if (i < step) return { ...s, status: 'done', progress: 100 }
        if (i === step) return { ...s, label, progress, status: 'active' }
        return s
      }))
    })

    const unsubLog = window.api.on('install:log', (line: unknown) => {
      setLogs(prev => [...prev.slice(-200), String(line)])
    })

    const unsubDone = window.api.on('install:done', (ok: unknown) => {
      if (ok) {
        setSteps(prev => prev.map(s => ({ ...s, status: 'done', progress: 100 })))
        setFinished(true)
      } else {
        setError('Installation failed. Check the log for details.')
      }
    })

    const unsubError = window.api.on('install:error', (msg: unknown) => {
      setError(String(msg))
    })

    const unsubCancelled = window.api.on('install:cancelled', () => {
      setCancelled(true)
      setCancelling(false)
    })

    return () => {
      unsubStep(); unsubLog(); unsubDone(); unsubError(); unsubCancelled()
    }
  }, [])

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [logs])

  async function startInstall() {
    setStarted(true)
    setSteps(prev => [{ ...prev[0], status: 'active' }, ...prev.slice(1)])
    await window.api.startInstall(game.id, instance.id, game.steamAppId, game.installMode, game.installOnce)
  }

  async function handleCancel() {
    setCancelling(true)
    await window.api.cancelInstall()
  }

  const isInProgress = started && !finished && !error && !cancelled

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6"
      style={{ background: 'rgba(0,0,0,0.80)', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
    >
      <div
        className="w-full max-w-2xl rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.6)] overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)', backdropFilter: 'blur(40px)', WebkitBackdropFilter: 'blur(40px)' }}
      >

        {/* Header */}
        <div
          className="flex items-start justify-between px-7 py-5"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}
        >
          <div>
            <h2 className="text-lg font-semibold text-white/90">Install {game.name} Server</h2>
            <p className="text-xs text-white/30 mt-1">Instance: <span className="text-white/50">{instance.name}</span></p>
          </div>
          {!started && (
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg text-white/30 hover:text-white transition-all ml-4 shrink-0"
              style={{ background: 'rgba(255,255,255,0.04)' }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.10)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
            >
              <X size={15} />
            </button>
          )}
        </div>

        {/* Steps */}
        <div className="px-7 py-6 space-y-5">
          {steps.map((step, i) => {
            const Icon = STEP_ICONS[i]
            return (
              <div key={i} className="space-y-2.5">
                <div className="flex items-center gap-3.5">
                  <StepIcon status={step.status} icon={<Icon size={15} />} accentColor={game.accentColor} />
                  <span className={cn(
                    'text-sm font-medium flex-1',
                    step.status === 'waiting' ? 'text-white/20' : 'text-white/90'
                  )}>
                    {step.label}
                  </span>
                  {step.status === 'active' && (
                    <span className="text-sm tabular-nums font-bold" style={{ color: game.accentColor }}>
                      {step.progress}%
                    </span>
                  )}
                  {step.status === 'done' && (
                    <span className="text-xs text-emerald-400 font-semibold">Done</span>
                  )}
                </div>

                {(step.status === 'active' || step.status === 'done') && (
                  <div
                    className="ml-11 h-1.5 rounded-full overflow-hidden"
                    style={{ background: 'rgba(255,255,255,0.08)' }}
                  >
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{
                        width: `${step.progress}%`,
                        backgroundColor: step.status === 'done' ? '#22c55e' : game.accentColor
                      }}
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Log output */}
        {started && (
          <div className="px-7 pb-5">
            <div
              ref={logRef}
              className="h-44 rounded-xl p-4 overflow-y-auto font-mono text-[11px] text-white/30 space-y-0.5 leading-relaxed"
              style={{ background: 'rgba(0,0,0,0.40)', border: '1px solid rgba(255,255,255,0.07)' }}
            >
              {logs.length === 0
                ? <span className="text-white/15">Waiting for output…</span>
                : logs.map((line, i) => <div key={i}>{line}</div>)
              }
            </div>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div
            className="mx-7 mb-5 px-4 py-3.5 rounded-xl text-sm text-red-300 leading-relaxed"
            style={{ background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.20)' }}
          >
            {error}
          </div>
        )}

        {/* Cancelled banner */}
        {cancelled && (
          <div
            className="mx-7 mb-5 px-4 py-3.5 rounded-xl text-sm text-white/50"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.10)' }}
          >
            Installation was cancelled.
          </div>
        )}

        {/* Footer */}
        <div
          className="px-7 py-4 flex items-center justify-between gap-4"
          style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
        >
          <div className="flex-1">
            {isInProgress && !cancelling && (
              <p className="text-xs text-white/20">This may take a while depending on your connection speed…</p>
            )}
            {cancelling && (
              <p className="text-xs text-white/30">Cancelling installation…</p>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            {!started && (
              <>
                <button
                  onClick={onClose}
                  className="px-5 py-2.5 text-sm font-medium text-white/30 hover:text-white transition-all rounded-xl"
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                >
                  Cancel
                </button>
                <button
                  onClick={startInstall}
                  className="px-7 py-2.5 rounded-xl text-sm font-semibold text-white hover:opacity-90 transition-all active:scale-[0.98] min-w-[150px]"
                  style={{ backgroundColor: game.accentColor }}
                >
                  Start Installation
                </button>
              </>
            )}

            {isInProgress && (
              <button
                onClick={handleCancel}
                disabled={cancelling}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white/50 hover:text-red-300 transition-all disabled:opacity-50"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(239,68,68,0.30)'
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(255,255,255,0.10)'
                }}
              >
                <Ban size={13} />
                {cancelling ? 'Cancelling…' : 'Cancel'}
              </button>
            )}

            {finished && (
              <button
                onClick={onClose}
                className="px-7 py-2.5 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all active:scale-[0.98] min-w-[120px]"
              >
                Done
              </button>
            )}

            {(error || cancelled) && (
              <button
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-white/50 hover:text-white transition-all"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.10)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StepIcon({ status, icon, accentColor }: { status: StepState['status']; icon: React.ReactNode; accentColor: string }) {
  if (status === 'done') {
    return (
      <div
        className="w-9 h-9 rounded-full flex items-center justify-center text-emerald-400 shrink-0"
        style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.30)' }}
      >
        <Check size={15} />
      </div>
    )
  }
  if (status === 'active') {
    return (
      <div
        className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
        style={{ backgroundColor: accentColor + '1e', border: `1px solid ${accentColor}50`, color: accentColor }}
      >
        {icon}
      </div>
    )
  }
  if (status === 'error') {
    return (
      <div
        className="w-9 h-9 rounded-full flex items-center justify-center text-red-300 shrink-0"
        style={{ background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.20)' }}
      >
        <X size={15} />
      </div>
    )
  }
  return (
    <div
      className="w-9 h-9 rounded-full flex items-center justify-center text-white/20 shrink-0"
      style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
    >
      {icon}
    </div>
  )
}
