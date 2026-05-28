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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="w-[520px] max-h-[80vh] bg-[#111113] border border-[#27272a] rounded-2xl shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#27272a] shrink-0">
          <div>
            <h2 className="text-base font-semibold">{game.name} Configuration</h2>
            <p className="text-xs text-[#71717a] mt-0.5">Settings saved locally</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
          >
            <X size={14} />
          </button>
        </div>

        {/* Fields */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
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
        <div className="px-6 py-4 border-t border-[#27272a] flex items-center justify-between shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-[#a1a1aa] hover:text-[#fafafa] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className={cn(
              'px-5 py-2 rounded-lg text-sm font-medium text-white transition-all',
              saved ? 'bg-emerald-600' : ''
            )}
            style={!saved ? { backgroundColor: game.accentColor } : undefined}
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
    'w-full px-3 py-2 rounded-lg bg-[#18181b] border border-[#27272a]',
    'text-sm text-[#fafafa] placeholder-[#52525b]',
    'focus:outline-none focus:border-[#3f3f46] transition-colors'
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-sm font-medium text-[#e4e4e7]">
          {setting.label}
          {setting.required && <span className="text-red-400 ml-1">*</span>}
        </label>
        {setting.helpUrl && (
          <a
            href={setting.helpUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-xs hover:underline"
            style={{ color: accentColor }}
          >
            Get token <ExternalLink size={10} />
          </a>
        )}
      </div>

      {setting.tooltip && (
        <p className="text-xs text-[#71717a] mb-1.5">{setting.tooltip}</p>
      )}

      {(setting.type === 'string') && (
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
            'relative inline-flex h-6 w-11 rounded-full transition-colors',
            value ? 'bg-emerald-600' : 'bg-[#3f3f46]'
          )}
        >
          <span
            className={cn(
              'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform',
              value ? 'translate-x-5' : 'translate-x-0'
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
