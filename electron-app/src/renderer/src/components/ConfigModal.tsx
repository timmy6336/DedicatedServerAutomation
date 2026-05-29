import { useState, useEffect } from 'react'
import { type Game, type SettingDef } from '../lib/games'
import { type ServerInstance } from '../lib/instances'
import { X, ExternalLink } from 'lucide-react'
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
    setTimeout(onClose, 800)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-6">
      <div className="w-full max-w-2xl max-h-[90vh] bg-[#111113] border border-[#27272a] rounded-2xl shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-start justify-between px-8 py-6 border-b border-[#27272a] shrink-0">
          <div>
            <h2 className="text-xl font-semibold text-white">{game.name} Configuration</h2>
            <p className="text-sm text-[#71717a] mt-1">Settings saved locally for {instance.name}</p>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center rounded-lg text-[#71717a] hover:text-white hover:bg-[#27272a] transition-colors ml-4 shrink-0"
          >
            <X size={16} />
          </button>
        </div>

        {/* Fields */}
        <div className="flex-1 overflow-y-auto px-8 py-7 space-y-7">
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
        <div className="px-8 py-5 border-t border-[#27272a] flex items-center justify-between gap-4 shrink-0">
          <button
            onClick={onClose}
            className="px-6 py-3 text-sm font-medium text-[#a1a1aa] hover:text-white rounded-lg hover:bg-[#18181b] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="px-8 py-3 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-50 min-w-[140px]"
            style={!saved ? { backgroundColor: game.accentColor } : { backgroundColor: '#16a34a' }}
          >
            {saving ? 'Saving…' : saved ? 'Saved ✓' : 'Save Changes'}
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
    'w-full px-4 py-3 rounded-xl bg-[#18181b] border border-[#27272a]',
    'text-sm text-white placeholder-[#52525b]',
    'focus:outline-none focus:border-[#52525b] transition-colors'
  )

  return (
    <div>
      {/* Label row */}
      <div className="flex items-center justify-between mb-2.5">
        <label className="text-sm font-semibold text-[#e4e4e7]">
          {setting.label}
          {setting.required && <span className="text-red-400 ml-1">*</span>}
        </label>
        {setting.helpUrl && (
          <a
            href={setting.helpUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-xs font-medium hover:underline"
            style={{ color: accentColor }}
          >
            Get token <ExternalLink size={11} />
          </a>
        )}
      </div>

      {setting.tooltip && (
        <p className="text-sm text-[#71717a] mb-2.5 leading-relaxed">{setting.tooltip}</p>
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
            'relative inline-flex h-8 w-14 rounded-full transition-colors focus:outline-none',
            value ? 'bg-emerald-600' : 'bg-[#3f3f46]'
          )}
        >
          <span
            className={cn(
              'absolute top-1 left-1 w-6 h-6 rounded-full bg-white shadow-md transition-transform',
              value ? 'translate-x-6' : 'translate-x-0'
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
            <option key={opt} value={opt} className="bg-[#18181b]">{opt}</option>
          ))}
        </select>
      )}
    </div>
  )
}
