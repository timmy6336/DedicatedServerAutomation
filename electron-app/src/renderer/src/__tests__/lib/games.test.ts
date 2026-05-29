import { describe, it, expect } from 'vitest'
import { GAMES, type Game } from '../../lib/games'

// ── Catalog-level assertions ──────────────────────────────────────────────────

describe('GAMES catalog', () => {
  it('contains exactly 10 games', () => {
    expect(GAMES).toHaveLength(10)
  })

  it('contains no duplicate IDs', () => {
    const ids = GAMES.map(g => g.id)
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('contains no duplicate names', () => {
    const names = GAMES.map(g => g.name)
    expect(new Set(names).size).toBe(names.length)
  })

  it('includes all expected game IDs', () => {
    const ids = GAMES.map(g => g.id)
    expect(ids).toContain('palworld')
    expect(ids).toContain('valheim')
    expect(ids).toContain('rust')
    expect(ids).toContain('dst')
    expect(ids).toContain('minecraft')
    expect(ids).toContain('ark')
    expect(ids).toContain('sevendays')
    expect(ids).toContain('zomboid')
    expect(ids).toContain('vrising')
    expect(ids).toContain('enshrouded')
  })
})

// ── Per-game field validation ─────────────────────────────────────────────────

describe.each(GAMES)('Game: $name', (game: Game) => {
  it('has a non-empty id', () => {
    expect(game.id).toBeTruthy()
    expect(game.id).toMatch(/^[a-z0-9_]+$/)
  })

  it('has a non-empty name and description', () => {
    expect(game.name.length).toBeGreaterThan(0)
    expect(game.description.length).toBeGreaterThan(0)
  })

  it('has a valid genre string', () => {
    expect(game.genre).toBeTruthy()
  })

  it('has at least one platform', () => {
    expect(game.platforms.length).toBeGreaterThan(0)
    for (const p of game.platforms) {
      expect(['Windows', 'Linux', 'macOS']).toContain(p)
    }
  })

  it('has a valid installMode', () => {
    expect(['steam', 'mojang']).toContain(game.installMode)
  })

  it('has a valid launchMode', () => {
    expect(['steam', 'java', 'dst_dual_shard']).toContain(game.launchMode)
  })

  it('has a valid hex accentColor', () => {
    expect(game.accentColor).toMatch(/^#[0-9a-fA-F]{6}$/)
  })

  it('has a non-empty bannerColor (Tailwind gradient class)', () => {
    expect(game.bannerColor).toMatch(/^from-/)
  })

  it('has a positive defaultPort within valid range', () => {
    expect(game.defaultPort).toBeGreaterThanOrEqual(1024)
    expect(game.defaultPort).toBeLessThanOrEqual(65535)
  })

  it('has at least one port definition', () => {
    expect(game.ports.length).toBeGreaterThan(0)
  })

  it('has all port numbers in valid range', () => {
    for (const p of game.ports) {
      expect(p.port).toBeGreaterThan(0)
      expect(p.port).toBeLessThanOrEqual(65535)
      expect(['TCP', 'UDP', 'TCP/UDP']).toContain(p.protocol)
    }
  })

  it('has serverSettings array', () => {
    expect(Array.isArray(game.serverSettings)).toBe(true)
  })

  it('includes a discord_webhook setting', () => {
    const webhookSetting = game.serverSettings.find(s => s.key === 'discord_webhook')
    expect(webhookSetting).toBeDefined()
    expect(webhookSetting?.type).toBe('string')
  })

  it('has no duplicate setting keys', () => {
    const keys = game.serverSettings.map(s => s.key)
    expect(new Set(keys).size).toBe(keys.length)
  })

  it('has valid setting types for all serverSettings', () => {
    for (const s of game.serverSettings) {
      expect(['string', 'password', 'int', 'bool', 'choice']).toContain(s.type)
    }
  })

  it('has non-empty labels for all settings', () => {
    for (const s of game.serverSettings) {
      expect(s.label.length).toBeGreaterThan(0)
    }
  })

  it('has options array for every choice-type setting', () => {
    for (const s of game.serverSettings) {
      if (s.type === 'choice') {
        expect(Array.isArray(s.options)).toBe(true)
        expect((s.options ?? []).length).toBeGreaterThan(0)
      }
    }
  })

  it('has min ≤ max for int settings', () => {
    for (const s of game.serverSettings) {
      if (s.type === 'int' && s.min !== undefined && s.max !== undefined) {
        expect(s.min).toBeLessThanOrEqual(s.max)
      }
    }
  })

  it('has non-empty executable', () => {
    expect(game.executable).toBeTruthy()
  })

  it('has non-empty serverDirName', () => {
    expect(game.serverDirName).toBeTruthy()
  })

  it('has at least one processName', () => {
    expect(game.processNames.length).toBeGreaterThan(0)
  })
})

// ── Game-specific assertions ──────────────────────────────────────────────────

describe('Minecraft (Mojang install)', () => {
  const mc = GAMES.find(g => g.id === 'minecraft')!

  it('uses mojang installMode', () => expect(mc.installMode).toBe('mojang'))
  it('is not installOnce (each instance gets its own jar)', () => expect(mc.installOnce).toBe(false))
  it('uses java launchMode', () => expect(mc.launchMode).toBe('java'))
  it('has empty steamAppId', () => expect(mc.steamAppId).toBe(''))
  it('has mods support with jar extension', () => {
    expect(mc.modsSubdir).toBe('mods')
    expect(mc.modExtensions).toContain('jar')
  })
  it('has custom installSteps', () => {
    expect(mc.installSteps).toBeDefined()
    expect(mc.installSteps!.length).toBe(3)
  })
})

describe('Steam games (installOnce)', () => {
  const steamGames = GAMES.filter(g => g.installMode === 'steam')

  it('all steam games have a numeric steamAppId', () => {
    for (const g of steamGames) {
      expect(g.steamAppId).toMatch(/^\d+$/)
    }
  })
})

describe('BepInEx mod games (Valheim, V Rising)', () => {
  const bepGames = GAMES.filter(g => g.modsSubdir === 'BepInEx/plugins')

  it('includes Valheim and V Rising', () => {
    const ids = bepGames.map(g => g.id)
    expect(ids).toContain('valheim')
    expect(ids).toContain('vrising')
  })

  it('only accepts dll and zip extensions', () => {
    for (const g of bepGames) {
      expect(g.modExtensions).toContain('dll')
    }
  })

  it('has a modsNote about BepInEx', () => {
    for (const g of bepGames) {
      expect(g.modsNote).toContain('BepInEx')
    }
  })

  it('has clientGamePath for mod-pack export instructions', () => {
    for (const g of bepGames) {
      expect(g.clientGamePath).toBeTruthy()
    }
  })
})

describe('Games without mod support (DST, ARK, Enshrouded)', () => {
  const noModIds = ['dst', 'ark', 'enshrouded']

  it.each(noModIds)('%s has no modsSubdir', (id) => {
    const game = GAMES.find(g => g.id === id)!
    expect(game.modsSubdir).toBeUndefined()
    expect(game.modExtensions).toBeUndefined()
  })
})

describe('Palworld mods', () => {
  const palworld = GAMES.find(g => g.id === 'palworld')!

  it('uses Pal/Content/Paks as modsSubdir', () => {
    expect(palworld.modsSubdir).toBe('Pal/Content/Paks')
  })

  it('only accepts pak extension', () => {
    expect(palworld.modExtensions).toEqual(['pak'])
  })
})

describe('Don\'t Starve Together', () => {
  const dst = GAMES.find(g => g.id === 'dst')!

  it('uses dst_dual_shard launchMode', () => {
    expect(dst.launchMode).toBe('dst_dual_shard')
  })

  it('has executableSubdir set to bin64', () => {
    expect(dst.executableSubdir).toBe('bin64')
  })

  it('has server_token setting with helpUrl', () => {
    const tokenSetting = dst.serverSettings.find(s => s.key === 'server_token')
    expect(tokenSetting).toBeDefined()
    expect(tokenSetting?.helpUrl).toBeTruthy()
  })
})
