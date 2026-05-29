import { useState, useEffect, useRef } from 'react'
import { Trash2, ArrowDown } from 'lucide-react'
import { cn } from '../lib/utils'

interface Props {
  instanceId: string
  serverRunning: boolean
}

interface LogLine {
  id: number
  text: string
}

let lineCounter = 0

export default function LogsPanel({ instanceId, serverRunning }: Props) {
  const [lines, setLines] = useState<LogLine[]>([])
  const logRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(true)

  useEffect(() => {
    setLines([])
    const unsub = window.api.on('server:log', (data: unknown) => {
      const { instanceId: id, line } = data as { instanceId: string; line: string }
      if (id !== instanceId) return
      setLines(prev => {
        const next = [...prev, { id: ++lineCounter, text: line }]
        return next.length > 1000 ? next.slice(-1000) : next
      })
    })
    return unsub
  }, [instanceId])

  useEffect(() => {
    if (autoScroll && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [lines, autoScroll])

  function onScroll() {
    if (!logRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = logRef.current
    setAutoScroll(scrollHeight - scrollTop - clientHeight < 40)
  }

  function lineColor(text: string) {
    const lower = text.toLowerCase()
    if (lower.includes('error') || lower.includes('exception') || lower.includes('fatal'))
      return 'text-red-400/90'
    if (lower.includes('warn'))
      return 'text-yellow-400/80'
    if (lower.includes('info') || lower.includes('[server]'))
      return 'text-white/50'
    return 'text-white/30'
  }

  return (
    <div className="h-full flex flex-col px-8 py-6 gap-4">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-base font-semibold text-white/90">Server Log</h2>
          <p className="text-xs text-white/30 mt-0.5">
            {serverRunning
              ? `Live output · ${lines.length} line${lines.length !== 1 ? 's' : ''}`
              : 'Start the server to see live output'}
          </p>
        </div>
        <button
          onClick={() => setLines([])}
          disabled={lines.length === 0}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm text-white/30 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
          onMouseEnter={e => {
            if (lines.length > 0) {
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.10)'
              ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.18)'
            }
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.10)'
          }}
        >
          <Trash2 size={13} />
          Clear
        </button>
      </div>

      {/* Terminal */}
      <div
        ref={logRef}
        onScroll={onScroll}
        className="flex-1 overflow-y-auto rounded-xl p-5 font-mono text-[11px] leading-relaxed"
        style={{ background: 'rgba(0,0,0,0.50)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(8px)' }}
      >
        {lines.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <p className="text-white/15">
              {serverRunning
                ? 'Waiting for output…'
                : 'No log output yet. Start the server to begin streaming.'}
            </p>
          </div>
        ) : (
          <div className="space-y-px">
            {lines.map(l => (
              <div key={l.id} className={cn('break-all', lineColor(l.text))}>
                {l.text}
              </div>
            ))}
          </div>
        )}
      </div>

      {!autoScroll && lines.length > 0 && (
        <button
          onClick={() => {
            setAutoScroll(true)
            if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
          }}
          className="shrink-0 flex items-center justify-center gap-2 text-xs py-2.5 rounded-xl text-white/50 hover:text-white transition-all"
          style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.10)'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.18)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.06)'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.10)'
          }}
        >
          <ArrowDown size={12} />
          Scroll to bottom
        </button>
      )}
    </div>
  )
}
