export interface ServerInstance {
  id: string            // unique slug, e.g. "minecraft-a1b2c3"
  gameId: string
  name: string
  config: Record<string, unknown>
  enabledMods: string[] // filenames of mods enabled for this instance
  createdAt: number
}

export interface ModEntry {
  filename: string      // unique key — the actual file name
  name: string          // display name (no extension)
  gameId: string
  size: number
  addedAt: number
}
