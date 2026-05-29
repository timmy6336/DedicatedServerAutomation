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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xl p-6">
      <div className="w-full max-w-2xl bg-[#0d0d14] border border-[#22223a] rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-start justify-between px-7 py-5 border-b border-[#22223a]">
          <div>
            <h2 className="text-lg font-semibold text-[#e8e8ff]">Install {game.name} Server</h2>
            <p className="text-xs text-[#7070a0] mt-1">Instance: <span className="text-[#e8e8ff]">{instance.name}</span></p>
          </div>
          {!started && (
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg text-[#7070a0] hover:text-[#e8e8ff] hover:bg-[#18182a] transition-all ml-4 shrink-0"
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
                    step.status === 'waiting' ? 'text-[#404065]' : 'text-[#e8e8ff]'
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
                  <div className="ml-11 h-1.5 rounded-full bg-[#22223a] overflow-hidden">
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
              className="h-44 rounded-xl bg-[#080810] border border-[#22223a] p-4 overflow-y-auto font-mono text-[11px] text-[#7070a0] space-y-0.5 leading-relaxed"
            >
              {logs.length === 0
                ? <span className="text-[#404065]">Waiting for output…</span>
                : logs.map((line, i) => <div key={i}>{line}</div>)
              }
            </div>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="mx-7 mb-5 px-4 py-3.5 rounded-xl bg-red-950/30 border border-red-900/40 text-sm text-red-400 leading-relaxed">
            {error}
          </div>
        )}

        {/* Cancelled banner */}
        {cancelled && (
          <div className="mx-7 mb-5 px-4 py-3.5 rounded-xl bg-[#18182a] border border-[#22223a] text-sm text-[#7070a0]">
            Installation was cancelled.
          </div>
        )}

        {/* Footer */}
        <div className="px-7 py-4 border-t border-[#22223a] flex items-center justify-between gap-4">
          <div className="flex-1">
            {isInProgress && !cancelling && (
              <p className="text-xs text-[#404065]">This may take a while depending on your connection speed…</p>
            )}
            {cancelling && (
              <p className="text-xs text-[#7070a0]">Cancelling installation…</p>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            {!started && (
              <>
                <button
                  onClick={onClose}
                  className="px-5 py-2.5 text-sm font-semibold text-[#7070a0] hover:text-[#e8e8ff] transition-all rounded-xl hover:bg-[#18182a]"
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
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-[#18182a] border border-[#22223a] text-[#7070a0] hover:text-red-400 hover:border-red-900/40 transition-all disabled:opacity-50"
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
                className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-[#18182a] border border-[#22223a] text-[#7070a0] hover:text-[#e8e8ff] transition-all"
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
      <div className="w-9 h-9 rounded-full bg-emerald-900/30 border border-emerald-700/40 flex items-center justify-center text-emerald-400 shrink-0">
        <Check size={15} />
      </div>
    )
  }
  if (status === 'active') {
    return (
      <div
        className="w-9 h-9 rounded-full flex items-center justify-center shrink-0 border"
        style={{ backgroundColor: accentColor + '1e', borderColor: accentColor + '50', color: accentColor }}
      >
        {icon}
      </div>
    )
  }
  if (status === 'error') {
    return (
      <div className="w-9 h-9 rounded-full bg-red-950/30 border border-red-800/40 flex items-center justify-center text-red-400 shrink-0">
        <X size={15} />
      </div>
    )
  }
  return (
    <div className="w-9 h-9 rounded-full bg-[#18182a] border border-[#22223a] flex items-center justify-center text-[#404065] shrink-0">
      {icon}
    </div>
  )
}
