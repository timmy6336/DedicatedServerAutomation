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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-6">
      <div className="w-full max-w-2xl max-h-[88vh] bg-[#0c0c0c] border-2 border-[#333333] rounded-xl shadow-[6px_6px_0_#111111] flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-start justify-between px-7 py-5 border-b-2 border-[#2e2e2e] shrink-0">
          <div>
            <h2 className="text-lg font-black uppercase tracking-tight text-[#f0f0f0]">{game.name} Configuration</h2>
            <p className="text-xs text-[#555555] mt-1 font-bold">Settings saved locally for <span className="text-[#888888]">{instance.name}</span></p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center border-2 border-[#2e2e2e] text-[#555555] hover:text-[#f0f0f0] hover:border-[#555555] transition-all ml-4 shrink-0 shadow-[2px_2px_0_#000]"
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
        <div className="px-7 py-4 border-t-2 border-[#2e2e2e] flex items-center justify-between gap-4 shrink-0">
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-bold text-[#555555] hover:text-[#f0f0f0] bg-[#1c1c1c] border-2 border-[#2e2e2e] hover:border-[#555555] shadow-[2px_2px_0_#000] hover:shadow-[3px_3px_0_#000] hover:-translate-x-px hover:-translate-y-px transition-all rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="flex items-center gap-2 px-7 py-2.5 text-sm font-bold text-white border-2 border-black shadow-[3px_3px_0_black] hover:shadow-[4px_4px_0_black] hover:-translate-x-px hover:-translate-y-px transition-all disabled:opacity-50 min-w-[130px] justify-center rounded-lg"
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
    'w-full px-4 py-2.5 rounded-lg bg-[#0c0c0c] border-2 border-[#2e2e2e]',
    'text-sm text-[#f0f0f0] font-medium placeholder-[#404040]',
    'focus:outline-none focus:border-[#555555] shadow-[2px_2px_0_#000] focus:shadow-[3px_3px_0_#111111] transition-all'
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-black uppercase tracking-wider text-[#f0f0f0]">
          {setting.label}
          {setting.required && <span className="text-red-400 ml-1">*</span>}
        </label>
        {setting.helpUrl && (
          <a
            href={setting.helpUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-xs font-bold hover:underline"
            style={{ color: accentColor }}
          >
            Get token <ExternalLink size={10} />
          </a>
        )}
      </div>

      {setting.tooltip && (
        <p className="text-xs text-[#555555] mb-2 leading-relaxed font-medium">{setting.tooltip}</p>
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
            'relative inline-flex h-7 w-12 rounded-full transition-colors focus:outline-none border-2 border-[#2e2e2e]',
            value ? 'bg-emerald-600' : 'bg-[#1c1c1c]'
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
            <option key={opt} value={opt} className="bg-[#0c0c0c]">{opt}</option>
          ))}
        </select>
      )}
    </div>
  )
}
