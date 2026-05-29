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
      return 'text-[#888888]'
    return 'text-[#555555]'
  }

  return (
    <div className="h-full flex flex-col px-8 py-6 gap-4">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-base font-black uppercase tracking-tight text-[#f0f0f0]">Server Log</h2>
          <p className="text-xs text-[#555555] mt-0.5 font-bold">
            {serverRunning
              ? `Live output · ${lines.length} line${lines.length !== 1 ? 's' : ''}`
              : 'Start the server to see live output'}
          </p>
        </div>
        <button
          onClick={() => setLines([])}
          disabled={lines.length === 0}
          className="flex items-center gap-2 px-3.5 py-2 bg-[#1c1c1c] border-2 border-[#2e2e2e] text-sm font-bold text-[#555555] hover:text-white hover:border-[#555555] shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px disabled:opacity-40 disabled:cursor-not-allowed transition-all rounded-lg"
        >
          <Trash2 size={13} />
          Clear
        </button>
      </div>

      {/* Terminal */}
      <div
        ref={logRef}
        onScroll={onScroll}
        className="flex-1 overflow-y-auto bg-[#080808] border-2 border-[#2e2e2e] p-5 font-mono text-[11px] leading-relaxed shadow-[3px_3px_0_#1a1a1a]"
      >
        {lines.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <p className="text-[#2e2e2e] font-bold">
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
          className="shrink-0 flex items-center justify-center gap-2 text-xs py-2.5 bg-[#1c1c1c] border-2 border-[#2e2e2e] text-[#888888] hover:text-white hover:border-[#555555] shadow-[2px_2px_0_#000] transition-all font-bold uppercase tracking-wider rounded-lg"
        >
          <ArrowDown size={12} />
          Scroll to bottom
        </button>
      )}
    </div>
  )
}
