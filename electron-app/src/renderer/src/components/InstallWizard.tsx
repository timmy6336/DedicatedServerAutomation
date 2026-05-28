import { useState, useEffect, useRef } from 'react'
import { type Game } from '../lib/games'
import { cn } from '../lib/utils'
import { Check, X, Download, HardDrive, Rocket } from 'lucide-react'

interface StepState {
  label: string
  progress: number   // 0–100
  status: 'waiting' | 'active' | 'done' | 'error'
}

const DEFAULT_STEP_LABELS = ['Download SteamCMD', 'Install server files', 'Complete']
const STEP_ICONS = [Download, HardDrive, Rocket]

function makeInitialSteps(labels: string[]): StepState[] {
  return labels.map(label => ({ label, progress: 0, status: 'waiting' as const }))
}

interface Props {
  game: Game
  onClose: () => void
}

export default function InstallWizard({ game, onClose }: Props) {
  const [steps, setSteps] = useState<StepState[]>(() =>
    makeInitialSteps(game.installSteps ?? DEFAULT_STEP_LABELS)
  )
  const [logs, setLogs] = useState<string[]>([])
  const [started, setStarted] = useState(false)
  const [finished, setFinished] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Subscribe to install events from main process
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

    return () => {
      unsubStep(); unsubLog(); unsubDone(); unsubError()
    }
  }, [])

  // Auto-scroll log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [logs])

  async function startInstall() {
    setStarted(true)
    setSteps(prev => [{ ...prev[0], status: 'active' }, ...prev.slice(1)])
    await window.api.startInstall(game.id, game.steamAppId, game.installMode)
  }

  const activeStep = steps.findIndex(s => s.status === 'active')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="w-[620px] bg-[#111113] border border-[#27272a] rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#27272a]">
          <div>
            <h2 className="text-base font-semibold">Install {game.name} Server</h2>
            <p className="text-xs text-[#71717a] mt-0.5">Steam App ID: {game.steamAppId}</p>
          </div>
          {!started && (
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center rounded-lg text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Steps */}
        <div className="px-6 py-5 space-y-4">
          {steps.map((step, i) => {
            const Icon = STEP_ICONS[i]
            return (
              <div key={i} className="space-y-2">
                <div className="flex items-center gap-3">
                  <StepIcon status={step.status} icon={<Icon size={13} />} accentColor={game.accentColor} />
                  <span className={cn(
                    'text-sm font-medium flex-1',
                    step.status === 'waiting' ? 'text-[#52525b]' : 'text-[#fafafa]'
                  )}>
                    {step.label}
                  </span>
                  {step.status === 'active' && (
                    <span className="text-xs tabular-nums" style={{ color: game.accentColor }}>
                      {step.progress}%
                    </span>
                  )}
                  {step.status === 'done' && (
                    <span className="text-xs text-emerald-400">Done</span>
                  )}
                </div>

                {(step.status === 'active' || step.status === 'done') && (
                  <div className="ml-9 h-1.5 rounded-full bg-[#27272a] overflow-hidden">
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
          <div className="px-6 pb-4">
            <div
              ref={logRef}
              className="h-36 rounded-lg bg-[#09090b] border border-[#27272a] p-3 overflow-y-auto font-mono text-[11px] text-[#71717a] space-y-0.5"
            >
              {logs.length === 0
                ? <span className="text-[#3f3f46]">Waiting for output…</span>
                : logs.map((line, i) => <div key={i}>{line}</div>)
              }
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mx-6 mb-4 px-4 py-3 rounded-lg bg-red-950/30 border border-red-900/50 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#27272a] flex justify-end gap-3">
          {!started && (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm text-[#a1a1aa] hover:text-[#fafafa] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={startInstall}
                className="px-5 py-2 rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-90"
                style={{ backgroundColor: game.accentColor }}
              >
                Start Installation
              </button>
            </>
          )}
          {finished && (
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
            >
              Done
            </button>
          )}
          {started && !finished && !error && (
            <p className="text-xs text-[#52525b] self-center">
              This may take a while depending on your connection…
            </p>
          )}
          {error && (
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-[#a1a1aa] hover:text-[#fafafa] transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function StepIcon({ status, icon, accentColor }: { status: StepState['status']; icon: React.ReactNode; accentColor: string }) {
  if (status === 'done') {
    return (
      <div className="w-7 h-7 rounded-full bg-emerald-900/40 border border-emerald-700/50 flex items-center justify-center text-emerald-400 shrink-0">
        <Check size={13} />
      </div>
    )
  }
  if (status === 'active') {
    return (
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 border"
        style={{ backgroundColor: accentColor + '22', borderColor: accentColor + '55', color: accentColor }}
      >
        {icon}
      </div>
    )
  }
  if (status === 'error') {
    return (
      <div className="w-7 h-7 rounded-full bg-red-950/40 border border-red-800/50 flex items-center justify-center text-red-400 shrink-0">
        <X size={13} />
      </div>
    )
  }
  return (
    <div className="w-7 h-7 rounded-full bg-[#18181b] border border-[#27272a] flex items-center justify-center text-[#52525b] shrink-0">
      {icon}
    </div>
  )
}
