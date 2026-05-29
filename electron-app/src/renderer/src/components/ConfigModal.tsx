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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xl p-6">
      <div className="w-full max-w-2xl max-h-[88vh] bg-[#0f0f18] border border-[#1c1c2e] rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-start justify-between px-7 py-5 border-b border-[#1c1c2e] shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e2ef]">{game.name} Configuration</h2>
            <p className="text-xs text-[#575770] mt-1">Settings saved locally for <span className="text-[#8e8ea8]">{instance.name}</span></p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-[#575770] hover:text-[#e2e2ef] hover:bg-[#1c1c2e] transition-all ml-4 shrink-0"
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
        <div className="px-7 py-4 border-t border-[#1c1c2e] flex items-center justify-between gap-4 shrink-0">
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-medium text-[#575770] hover:text-[#e2e2ef] rounded-lg hover:bg-[#151521] transition-all"
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
  const inputClass = cn(
    'w-full px-4 py-2.5 rounded-xl bg-[#151521] border border-[#1c1c2e]',
    'text-sm text-[#e2e2ef] placeholder-[#383854]',
    'focus:outline-none focus:border-[#28283f] focus:ring-1 focus:ring-[#28283f] transition-all'
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-semibold text-[#c0c0d8]">
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
        <p className="text-xs text-[#575770] mb-2 leading-relaxed">{setting.tooltip}</p>
      )}

      {setting.type === 'string' && (
        <input
          type="text"
          className={inputClass}
          value={String(value ?? '')}
          placeholder={setting.placeholder}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {setting.type === 'password' && (
        <input
          type="password"
          className={inputClass}
          value={String(value ?? '')}
          placeholder={setting.placeholder ?? '••••••••'}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {setting.type === 'int' && (
        <input
          type="number"
          className={inputClass}
          value={Number(value ?? setting.default)}
          min={setting.min}
          max={setting.max}
          onChange={(e) => onChange(parseInt(e.target.value, 10))}
        />
      )}

      {setting.type === 'bool' && (
        <button
          onClick={() => onChange(!value)}
          className={cn(
            'relative inline-flex h-7 w-12 rounded-full transition-colors focus:outline-none',
            value ? 'bg-emerald-600' : 'bg-[#28283f]'
          )}
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
          value={String(value ?? setting.default)}
          onChange={(e) => onChange(e.target.value)}
        >
          {setting.options?.map(opt => (
            <option key={opt} value={opt} className="bg-[#151521]">{opt}</option>
          ))}
        </select>
      )}
    </div>
  )
}
