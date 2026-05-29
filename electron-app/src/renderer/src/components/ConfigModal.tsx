import { useState, useEffect } from 'react'
import { type Game, type SettingDef } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { X, ExternalLink, Check } from 'lucide-react'
import { cn } from '../lib/utils'

interface Props {
  game: Game
  instance: ServerInstance
  onClose: () => void
}

export default function ConfigModal({ game, instance, onClose }: Props) {
  const [config, setConfig] = useState<Record<string, unknown>>({})
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    window.api.loadConfig(instance.id).then((saved) => {
      const defaults: Record<string, unknown> = {}
      for (const s of game.serverSettings) defaults[s.key] = s.default
      setConfig({ ...defaults, ...(saved as Record<string, unknown> | null ?? {}) })
    })
  }, [game, instance.id])

  function set(key: string, value: unknown) {
    setConfig(prev => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  async function save() {
    setSaving(true)
    await window.api.saveConfig(instance.id, config)
    setSaving(false)
    setSaved(true)
    setTimeout(onClose, 700)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6"
      style={{ background: 'rgba(0,0,0,0.80)', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
    >
      <div
        className="w-full max-w-2xl max-h-[88vh] rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)', backdropFilter: 'blur(40px)', WebkitBackdropFilter: 'blur(40px)' }}
      >

        {/* Header */}
        <div
          className="flex items-start justify-between px-7 py-5 shrink-0"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}
        >
          <div>
            <h2 className="text-lg font-semibold text-white/90">{game.name} Configuration</h2>
            <p className="text-xs text-white/30 mt-1">Settings saved locally for <span className="text-white/50">{instance.name}</span></p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-white/30 hover:text-white transition-all ml-4 shrink-0"
            style={{ background: 'rgba(255,255,255,0.04)' }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.10)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
          >
            <X size={15} />
          </button>
        </div>

        {/* Fields */}
        <div className="flex-1 overflow-y-auto px-7 py-6 space-y-6">
          {game.serverSettings.map((setting) => (
            <Field
              key={setting.key}
              setting={setting}
              value={config[setting.key]}
              onChange={(v) => set(setting.key, v)}
              accentColor={game.accentColor}
            />
          ))}
        </div>

        {/* Footer */}
        <div
          className="px-7 py-4 flex items-center justify-between gap-4 shrink-0"
          style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
        >
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-medium text-white/30 hover:text-white rounded-lg transition-all"
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="flex items-center gap-2 px-7 py-2.5 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-50 min-w-[130px] justify-center"
            style={!saved ? { backgroundColor: game.accentColor } : { backgroundColor: '#16a34a' }}
          >
            {saving ? (
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : saved ? (
              <><Check size={14} /> Saved</>
            ) : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Field({
  setting,
  value,
  onChange,
  accentColor
}: {
  setting: SettingDef
  value: unknown
  onChange: (v: unknown) => void
  accentColor: string
}) {
  const inputStyle = {
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.10)',
    backdropFilter: 'blur(8px)'
  }

  const inputClass = cn(
    'w-full px-4 py-2.5 rounded-xl',
    'text-sm text-white placeholder-white/20',
    'focus:outline-none transition-all'
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-semibold text-white/70">
          {setting.label}
          {setting.required && <span className="text-red-400 ml-1">*</span>}
        </label>
        {setting.helpUrl && (
          <a
            href={setting.helpUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-xs font-medium hover:underline"
            style={{ color: accentColor }}
          >
            Get token <ExternalLink size={10} />
          </a>
        )}
      </div>

      {setting.tooltip && (
        <p className="text-xs text-white/30 mb-2 leading-relaxed">{setting.tooltip}</p>
      )}

      {setting.type === 'string' && (
        <input
          type="text"
          className={inputClass}
          style={inputStyle}
          value={String(value ?? '')}
          placeholder={setting.placeholder}
          onChange={(e) => onChange(e.target.value)}
          onFocus={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.30)'
            e.currentTarget.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.15)'
          }}
          onBlur={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.10)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        />
      )}

      {setting.type === 'password' && (
        <input
          type="password"
          className={inputClass}
          style={inputStyle}
          value={String(value ?? '')}
          placeholder={setting.placeholder ?? '••••••••'}
          onChange={(e) => onChange(e.target.value)}
          onFocus={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.30)'
            e.currentTarget.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.15)'
          }}
          onBlur={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.10)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        />
      )}

      {setting.type === 'int' && (
        <input
          type="number"
          className={inputClass}
          style={inputStyle}
          value={Number(value ?? setting.default)}
          min={setting.min}
          max={setting.max}
          onChange={(e) => onChange(parseInt(e.target.value, 10))}
          onFocus={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.30)'
            e.currentTarget.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.15)'
          }}
          onBlur={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.10)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        />
      )}

      {setting.type === 'bool' && (
        <button
          onClick={() => onChange(!value)}
          className={cn(
            'relative inline-flex h-7 w-12 rounded-full transition-colors focus:outline-none',
            value ? 'bg-emerald-600' : ''
          )}
          style={!value ? { background: 'rgba(255,255,255,0.12)' } : undefined}
        >
          <span
            className={cn(
              'absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-md transition-transform duration-200',
              value ? 'left-[22px]' : 'left-0.5'
            )}
          />
        </button>
      )}

      {setting.type === 'choice' && (
        <select
          className={cn(inputClass, 'cursor-pointer')}
          style={{ ...inputStyle, color: 'white' }}
          value={String(value ?? setting.default)}
          onChange={(e) => onChange(e.target.value)}
          onFocus={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.30)'
            e.currentTarget.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.15)'
          }}
          onBlur={e => {
            e.currentTarget.style.border = '1px solid rgba(255,255,255,0.10)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          {setting.options?.map(opt => (
            <option key={opt} value={opt} style={{ background: '#0f0f18' }}>{opt}</option>
          ))}
        </select>
      )}
    </div>
  )
}
