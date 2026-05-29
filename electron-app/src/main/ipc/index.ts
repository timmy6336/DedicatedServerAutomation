import { ipcMain, BrowserWindow, app, dialog } from 'electron'
import { spawnSync, spawn, ChildProcess } from 'child_process'
import {
  existsSync, mkdirSync, createWriteStream, writeFileSync, readFileSync,
  copyFileSync, readdirSync, unlinkSync, statSync, rmSync
} from 'fs'
import { join, basename } from 'path'
import { get as httpGet, request as httpRequest } from 'https'
import { readFile, writeFile } from 'fs/promises'
import * as os from 'os'

// ── types (mirrored from renderer for main-process use) ──────────────────────
interface ServerInstance {
  id: string
  gameId: string
  name: string
  config: Record<string, unknown>
  enabledMods: string[]
  createdAt: number
}
interface ModEntry {
  filename: string
  name: string
  gameId: string
  size: number
  addedAt: number
}
interface BackupEntry {
  id: string
  label: string
  sizeBytes: number
}

// ── running processes keyed by instanceId ─────────────────────────────────────
const runningProcesses = new Map<string, ChildProcess>()

// ── active install process (for cancellation) ────────────────────────────────
let activeInstallProc: ChildProcess | null = null
let installCancelled = false

// ── storage helpers ───────────────────────────────────────────────────────────
const userData = () => app.getPath('userData')
const instancesPath = () => join(userData(), 'instances.json')
const modsRegistryPath = () => join(userData(), 'mods-registry.json')
const instanceDir = (gameId: string, instanceId: string) =>
  join(userData(), 'servers', gameId, instanceId)
// Shared game binary dir — one install per game, shared across all instances
const gameBinaryDir = (gameId: string) =>
  join(userData(), 'game-installs', gameId)
const modLibDir = (gameId: string) =>
  join(userData(), 'mod-library', gameId)
const backupBase = (gameId: string, instanceId: string) =>
  join(userData(), 'backups', gameId, instanceId)
const pidFile = (instanceId: string) =>
  join(userData(), 'server-pids', `${instanceId}.pid`)

async function readJson<T>(path: string, fallback: T): Promise<T> {
  try { return JSON.parse(await readFile(path, 'utf-8')) }
  catch { return fallback }
}
async function writeJson(path: string, data: unknown): Promise<void> {
  const dir = join(path, '..')
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
  await writeFile(path, JSON.stringify(data, null, 2), 'utf-8')
}

async function readInstances(): Promise<ServerInstance[]> {
  return readJson<ServerInstance[]>(instancesPath(), [])
}
async function writeInstances(list: ServerInstance[]): Promise<void> {
  await writeJson(instancesPath(), list)
}
async function readModsRegistry(): Promise<ModEntry[]> {
  return readJson<ModEntry[]>(modsRegistryPath(), [])
}
async function writeModsRegistry(list: ModEntry[]): Promise<void> {
  await writeJson(modsRegistryPath(), list)
}

// ── download with redirect following ─────────────────────────────────────────
function downloadFile(url: string, dest: string, onProgress: (pct: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    const dir = join(dest, '..')
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
    function follow(target: string, hops = 0) {
      if (hops > 5) { reject(new Error('Too many redirects')); return }
      const file = createWriteStream(dest)
      httpGet(target, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.headers.location) {
          file.destroy(); follow(res.headers.location, hops + 1); return
        }
        if (res.statusCode && res.statusCode >= 400) {
          file.destroy(); reject(new Error(`HTTP ${res.statusCode} ${res.statusMessage}`)); return
        }
        const total = parseInt(res.headers['content-length'] || '0', 10)
        let received = 0
        res.on('data', (chunk: Buffer) => {
          received += chunk.length
          if (total > 0) onProgress(Math.round((received / total) * 100))
          file.write(chunk)
        })
        res.on('end', () => { file.end(); resolve() })
        res.on('error', (e) => { file.destroy(); reject(e) })
      }).on('error', reject)
    }
    follow(url)
  })
}

function fetchJson<T>(url: string): Promise<T> {
  return new Promise((resolve, reject) => {
    function follow(target: string, hops = 0) {
      if (hops > 5) { reject(new Error('Too many redirects')); return }
      httpGet(target, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.headers.location) {
          follow(res.headers.location, hops + 1); return
        }
        let body = ''
        res.on('data', (c: Buffer) => { body += c.toString() })
        res.on('end', () => { try { resolve(JSON.parse(body)) } catch (e) { reject(e) } })
        res.on('error', reject)
      }).on('error', reject)
    }
    follow(url)
  })
}

function broadcast(channel: string, ...args: unknown[]): void {
  BrowserWindow.getAllWindows().forEach(w => w.webContents.send(channel, ...args))
}

// ── PID tracking helpers ──────────────────────────────────────────────────────
function writePid(instanceId: string, pid: number): void {
  const dir = join(userData(), 'server-pids')
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
  writeFileSync(pidFile(instanceId), String(pid), 'utf-8')
}

function readPid(instanceId: string): number | null {
  try {
    const n = parseInt(readFileSync(pidFile(instanceId), 'utf-8').trim(), 10)
    return isNaN(n) ? null : n
  } catch { return null }
}

function isPidAlive(pid: number): boolean {
  try {
    if (process.platform === 'win32') {
      const r = spawnSync('tasklist', ['/FI', `PID eq ${pid}`, '/FO', 'CSV', '/NH'], { encoding: 'utf-8' })
      return (r.stdout || '').includes(`"${pid}"`)
    } else {
      process.kill(pid, 0)
      return true
    }
  } catch { return false }
}

function clearPid(instanceId: string): void {
  try { unlinkSync(pidFile(instanceId)) } catch { /* already gone */ }
}

// ── Discord webhook ───────────────────────────────────────────────────────────
function fireDiscordWebhook(url: string, content: string): void {
  if (!url?.startsWith('https://')) return
  try {
    const body = JSON.stringify({ content, username: 'Server Manager' })
    const urlObj = new URL(url)
    const req = httpRequest({
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    })
    req.write(body)
    req.end()
    req.on('error', () => { /* silently ignore */ })
  } catch { /* ignore */ }
}

// ── directory helpers ─────────────────────────────────────────────────────────
function copyDirSync(src: string, dest: string): void {
  if (!existsSync(dest)) mkdirSync(dest, { recursive: true })
  for (const entry of readdirSync(src, { withFileTypes: true })) {
    const srcPath = join(src, entry.name)
    const destPath = join(dest, entry.name)
    if (entry.isDirectory()) copyDirSync(srcPath, destPath)
    else copyFileSync(srcPath, destPath)
  }
}

function getDirSize(dir: string): number {
  if (!existsSync(dir)) return 0
  let size = 0
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name)
    try {
      if (entry.isDirectory()) size += getDirSize(full)
      else size += statSync(full).size
    } catch { /* skip unreadable files */ }
  }
  return size
}

// ── per-game mod configuration (mirrors games.ts modsSubdir/modExtensions) ────
const MODS_CONFIG: Record<string, { subdir: string; extensions: string[] }> = {
  minecraft:  { subdir: 'mods',             extensions: ['jar'] },
  palworld:   { subdir: 'Pal/Content/Paks', extensions: ['pak'] },
  valheim:    { subdir: 'BepInEx/plugins',  extensions: ['dll', 'zip'] },
  rust:       { subdir: 'oxide/plugins',    extensions: ['dll', 'cs'] },
  sevendays:  { subdir: 'Mods',             extensions: ['dll', 'zip'] },
  zomboid:    { subdir: 'Mods',             extensions: ['zip'] },
  vrising:    { subdir: 'BepInEx/plugins',  extensions: ['dll', 'zip'] },
}

// ── copy enabled mods into the game's correct mod directory ──────────────────
// binaryBase: gameBinaryDir for steam games, instanceDir for mojang (Minecraft)
function applyMods(gameId: string, instanceId: string, enabledMods: string[], binaryBase: string): void {
  const modsSubdir = MODS_CONFIG[gameId]?.subdir ?? 'mods'
  const modsDir = join(binaryBase, modsSubdir)
  const libDir = modLibDir(gameId)

  if (!existsSync(modsDir)) mkdirSync(modsDir, { recursive: true })

  if (existsSync(modsDir)) {
    for (const f of readdirSync(modsDir)) {
      if (!enabledMods.includes(f)) {
        try { unlinkSync(join(modsDir, f)) } catch { /* ignore */ }
      }
    }
  }

  for (const filename of enabledMods) {
    const src = join(libDir, filename)
    const dest = join(modsDir, filename)
    if (existsSync(src) && !existsSync(dest)) {
      copyFileSync(src, dest)
    }
  }
}

// ── Minecraft install ─────────────────────────────────────────────────────────
async function installMinecraft(instDir: string): Promise<boolean> {
  broadcast('install:step', { step: 0, label: 'Checking Java & fetching version info…', progress: 0 })

  const javaCheck = spawnSync('java', ['-version'], { encoding: 'utf-8', stdio: 'pipe' })
  if (javaCheck.error) {
    broadcast('install:error', 'Java is not installed. Please install Java 21+ from https://adoptium.net and try again.')
    return false
  }
  broadcast('install:log', `Java: ${(javaCheck.stderr || javaCheck.stdout || '').trim().split('\n')[0]}`)
  broadcast('install:step', { step: 0, label: 'Fetching latest Minecraft version…', progress: 50 })

  interface Manifest { latest: { release: string }; versions: Array<{ id: string; type: string; url: string }> }
  interface VersionMeta { downloads: { server: { url: string; size: number } } }

  let manifest: Manifest
  try { manifest = await fetchJson<Manifest>('https://launchermeta.mojang.com/mc/game/version_manifest_v2.json') }
  catch (e) { broadcast('install:error', `Failed to fetch manifest: ${e}`); return false }

  const latestId = manifest.latest.release
  const entry = manifest.versions.find(v => v.id === latestId && v.type === 'release')
  if (!entry) { broadcast('install:error', 'Could not find latest release.'); return false }

  const meta = await fetchJson<VersionMeta>(entry.url)
  const { url: jarUrl, size: jarSize } = meta.downloads.server

  broadcast('install:log', `Minecraft ${latestId} — ${(jarSize / 1024 / 1024).toFixed(1)} MB`)
  broadcast('install:step', { step: 0, label: `Found Minecraft ${latestId}`, progress: 100 })

  broadcast('install:step', { step: 1, label: 'Downloading server.jar…', progress: 0 })
  const jarPath = join(instDir, 'server.jar')
  try {
    await downloadFile(jarUrl, jarPath, (pct) =>
      broadcast('install:step', { step: 1, label: 'Downloading server.jar…', progress: pct })
    )
  } catch (e) { broadcast('install:error', `Download failed: ${e}`); return false }

  broadcast('install:step', { step: 2, label: 'Writing config files…', progress: 50 })
  writeFileSync(join(instDir, 'eula.txt'), '#Minecraft EULA accepted by Dedicated Server Automation\neula=true\n', 'utf-8')
  writeFileSync(join(instDir, 'server.properties'), [
    'server-port=25565', 'max-players=20', 'online-mode=true',
    'difficulty=normal', 'gamemode=survival', 'white-list=false',
    'pvp=true', 'motd=A Minecraft Server', 'enable-rcon=false',
  ].join('\n') + '\n', 'utf-8')
  broadcast('install:log', 'eula.txt + server.properties written')
  broadcast('install:step', { step: 2, label: 'Setup complete!', progress: 100 })
  return true
}

// ── SteamCMD install ──────────────────────────────────────────────────────────
async function installViaSteam(binaryDir: string, steamAppId: string): Promise<boolean> {
  const steamCmdDir = join(userData(), 'steamcmd')
  const exe = process.platform === 'win32' ? 'steamcmd.exe' : 'steamcmd.sh'
  const steamCmdPath = join(steamCmdDir, exe)

  if (!existsSync(steamCmdDir)) mkdirSync(steamCmdDir, { recursive: true })

  if (!existsSync(steamCmdPath)) {
    broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: 0 })
    const isWin = process.platform === 'win32'
    const url = isWin
      ? 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
      : 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz'
    const archive = join(steamCmdDir, isWin ? 'steamcmd.zip' : 'steamcmd.tar.gz')
    try {
      await downloadFile(url, archive, (pct) =>
        broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: pct })
      )
      broadcast('install:step', { step: 0, label: 'Extracting SteamCMD…', progress: 100 })
      if (isWin) {
        const r = spawnSync('powershell', ['-Command', `Expand-Archive -Path "${archive}" -DestinationPath "${steamCmdDir}" -Force`], { encoding: 'utf-8' })
        if (r.error) throw r.error
      } else {
        spawnSync('tar', ['-xzf', archive, '-C', steamCmdDir])
        spawnSync('chmod', ['+x', steamCmdPath])
      }
      if (!existsSync(steamCmdPath)) {
        broadcast('install:error', `SteamCMD extraction failed — ${exe} not found after extraction. Check that PowerShell can run Expand-Archive.`)
        return false
      }
    } catch (e) { broadcast('install:error', String(e)); return false }
  } else {
    broadcast('install:step', { step: 0, label: 'SteamCMD already installed', progress: 100 })
  }

  broadcast('install:step', { step: 1, label: 'Installing server files…', progress: 0 })
  installCancelled = false
  return new Promise<boolean>((resolve) => {
    const proc = spawn(steamCmdPath, [
      '+force_install_dir', binaryDir, '+login', 'anonymous',
      '+app_update', steamAppId, 'validate', '+quit'
    ])
    activeInstallProc = proc
    let buf = ''
    proc.stdout?.on('data', (c: Buffer) => {
      buf += c.toString()
      const lines = buf.split('\n'); buf = lines.pop() ?? ''
      for (const line of lines) {
        broadcast('install:log', line)
        const m = line.match(/progress:\s*([\d.]+)/)
        if (m) broadcast('install:step', { step: 1, label: 'Installing server files…', progress: Math.round(parseFloat(m[1])) })
      }
    })
    proc.stderr?.on('data', (c: Buffer) => broadcast('install:log', c.toString()))
    proc.on('close', (code) => {
      activeInstallProc = null
      if (installCancelled) {
        broadcast('install:cancelled')
        resolve(false)
      } else {
        broadcast('install:step', { step: 1, label: 'Installation complete', progress: 100 })
        broadcast('install:done', code === 0)
        resolve(code === 0)
      }
      installCancelled = false
    })
  })
}

// ── IPC registration ──────────────────────────────────────────────────────────
export function registerIpcHandlers(): void {

  // Window controls
  ipcMain.on('window:minimize', () => BrowserWindow.getFocusedWindow()?.minimize())
  ipcMain.on('window:maximize', () => {
    const win = BrowserWindow.getFocusedWindow()
    win?.isMaximized() ? win.unmaximize() : win?.maximize()
  })
  ipcMain.on('window:close', () => BrowserWindow.getFocusedWindow()?.close())

  // ── Instance management ──────────────────────────────────────────────────

  ipcMain.handle('instance:list', async (_, gameId: string) => {
    const all = await readInstances()
    return all.filter(i => i.gameId === gameId)
  })

  ipcMain.handle('instance:create', async (_, gameId: string, name: string) => {
    const all = await readInstances()
    const id = `${gameId}-${Date.now().toString(36)}`
    const inst: ServerInstance = { id, gameId, name, config: {}, enabledMods: [], createdAt: Date.now() }
    all.push(inst)
    await writeInstances(all)
    mkdirSync(instanceDir(gameId, id), { recursive: true })
    return inst
  })

  ipcMain.handle('instance:delete', async (_, instanceId: string, gameId: string) => {
    const all = await readInstances()
    const updated = all.filter(i => i.id !== instanceId)
    await writeInstances(updated)
    const dir = instanceDir(gameId, instanceId)
    if (existsSync(dir)) rmSync(dir, { recursive: true, force: true })
    return true
  })

  ipcMain.handle('instance:rename', async (_, instanceId: string, name: string) => {
    const all = await readInstances()
    const inst = all.find(i => i.id === instanceId)
    if (!inst) return false
    inst.name = name
    await writeInstances(all)
    return true
  })

  ipcMain.handle('instance:saveConfig', async (_, instanceId: string, config: Record<string, unknown>) => {
    const all = await readInstances()
    const inst = all.find(i => i.id === instanceId)
    if (!inst) return false
    inst.config = config
    await writeInstances(all)
    return true
  })

  ipcMain.handle('instance:loadConfig', async (_, instanceId: string) => {
    const all = await readInstances()
    return all.find(i => i.id === instanceId)?.config ?? null
  })

  ipcMain.handle('instance:setEnabledMods', async (_, instanceId: string, gameId: string, enabledMods: string[]) => {
    const all = await readInstances()
    const inst = all.find(i => i.id === instanceId)
    if (!inst) return false
    inst.enabledMods = enabledMods
    await writeInstances(all)
    // We don't know launchMode here, so just stage mods into the right dir
    const binaryBase = existsSync(gameBinaryDir(gameId)) ? gameBinaryDir(gameId) : instanceDir(gameId, instanceId)
    applyMods(gameId, instanceId, enabledMods, binaryBase)
    return true
  })

  // ── Server state ─────────────────────────────────────────────────────────

  ipcMain.handle('server:isInstalled', (_, gameId: string, instanceId: string, installOnce: boolean, executableSubdir: string, executable: string) => {
    const base = installOnce ? gameBinaryDir(gameId) : instanceDir(gameId, instanceId)
    const exePath = executableSubdir ? join(base, executableSubdir, executable) : join(base, executable)
    return existsSync(exePath)
  })

  ipcMain.handle('server:isRunning', (_, instanceId: string, _processNames: string[]) => {
    const proc = runningProcesses.get(instanceId)
    if (proc && !proc.killed) return true
    // Fall back to PID file — avoids false positives from generic process names like 'java'
    const pid = readPid(instanceId)
    if (pid !== null) {
      if (isPidAlive(pid)) return true
      clearPid(instanceId) // stale PID file
    }
    return false
  })

  ipcMain.handle('server:localIp', () => {
    const nets = os.networkInterfaces()
    for (const iface of Object.values(nets))
      for (const addr of iface ?? [])
        if (addr.family === 'IPv4' && !addr.internal) return addr.address
    return '127.0.0.1'
  })

  ipcMain.handle('server:checkJava', () => {
    const r = spawnSync('java', ['-version'], { encoding: 'utf-8', stdio: 'pipe' })
    if (r.error) return null
    return (r.stderr || r.stdout || '').trim().split('\n')[0] || null
  })

  // ── Install ───────────────────────────────────────────────────────────────

  ipcMain.handle('server:uninstall', (_, gameId: string, instanceId: string, installOnce: boolean) => {
    const dir = installOnce ? gameBinaryDir(gameId) : instanceDir(gameId, instanceId)
    try {
      if (existsSync(dir)) rmSync(dir, { recursive: true, force: true })
      return true
    } catch (e) {
      broadcast('server:error', `Uninstall failed: ${e}`)
      return false
    }
  })

  ipcMain.handle('install:cancel', () => {
    if (activeInstallProc && !activeInstallProc.killed) {
      installCancelled = true
      activeInstallProc.kill()
      return true
    }
    return false
  })

  ipcMain.handle('install:start', async (_, gameId: string, instanceId: string, steamAppId: string, installMode: string, installOnce: boolean) => {
    // Always create the instance dir — config, backups, and per-instance save data live here
    const instDir = instanceDir(gameId, instanceId)
    if (!existsSync(instDir)) mkdirSync(instDir, { recursive: true })

    if (installMode === 'mojang') {
      // Minecraft: each instance owns its own server.jar + world directory
      const ok = await installMinecraft(instDir)
      broadcast('install:done', ok)
      return ok
    }

    if (installOnce) {
      // Shared binary: install once, all instances share the same game files
      const binaryDir = gameBinaryDir(gameId)
      if (!existsSync(binaryDir)) mkdirSync(binaryDir, { recursive: true })
      return installViaSteam(binaryDir, steamAppId)
    } else {
      // Per-instance: each instance gets its own full game installation
      return installViaSteam(instDir, steamAppId)
    }
  })

  // ── Start / Stop ──────────────────────────────────────────────────────────

  ipcMain.handle('server:start', async (_, instanceId: string, gameId: string, launchMode: string, exeRelPath: string, args: string[], installOnce: boolean) => {
    const existing = runningProcesses.get(instanceId)
    if (existing && !existing.killed) return true

    const instDir = instanceDir(gameId, instanceId)
    const binaryBase = installOnce ? gameBinaryDir(gameId) : instDir

    // Apply this instance's mods into the binary dir before launch
    const allInst = await readInstances()
    const inst = allInst.find(i => i.id === instanceId)
    if (inst?.enabledMods.length) applyMods(gameId, instanceId, inst.enabledMods, binaryBase)

    try {
      let cmd: string, cmdArgs: string[], cwd: string
      if (launchMode === 'java') {
        cmd = 'java'; cmdArgs = args; cwd = binaryBase
      } else {
        const exePath = join(binaryBase, exeRelPath)
        cmd = exePath; cmdArgs = args; cwd = binaryBase
      }

      const proc = spawn(cmd, cmdArgs, {
        cwd,
        detached: true,
        windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe']
      })

      let lineBuf = ''
      function emitLines(chunk: Buffer) {
        lineBuf += chunk.toString()
        const parts = lineBuf.split('\n')
        lineBuf = parts.pop() ?? ''
        for (const line of parts) {
          if (line.trim()) broadcast('server:log', { instanceId, line })
        }
      }

      proc.stdout?.on('data', emitLines)
      proc.stderr?.on('data', emitLines)
      proc.on('exit', (code) => {
        broadcast('server:exit', { instanceId, code })
        runningProcesses.delete(instanceId)
        clearPid(instanceId)
        const webhookUrl = inst?.config?.discord_webhook as string
        if (webhookUrl && code !== 0) {
          fireDiscordWebhook(webhookUrl, `⚠️ **${inst?.name}** crashed (exit code ${code}).`)
        }
      })

      proc.unref()
      runningProcesses.set(instanceId, proc)
      if (proc.pid) writePid(instanceId, proc.pid)

      // Fire start webhook
      const webhookUrl = inst?.config?.discord_webhook as string
      if (webhookUrl) {
        fireDiscordWebhook(webhookUrl, `🟢 **${inst?.name}** is now **Online**!`)
      }

      return true
    } catch (e) {
      broadcast('server:error', String(e))
      return false
    }
  })

  ipcMain.handle('server:stop', async (_, instanceId: string, _processNames: string[]) => {
    const proc = runningProcesses.get(instanceId)
    if (proc && !proc.killed) {
      proc.kill()
      runningProcesses.delete(instanceId)
    } else {
      // Fall back to PID file — avoids killing unrelated processes with the same name
      const pid = readPid(instanceId)
      if (pid !== null) {
        try {
          if (process.platform === 'win32') spawnSync('taskkill', ['/F', '/PID', String(pid)])
          else process.kill(pid, 'SIGTERM')
        } catch { /* process may have already exited */ }
      }
    }
    clearPid(instanceId)

    // Fire stop webhook
    const allInst = await readInstances()
    const inst = allInst.find(i => i.id === instanceId)
    const webhookUrl = inst?.config?.discord_webhook as string
    if (webhookUrl) {
      fireDiscordWebhook(webhookUrl, `🔴 **${inst?.name}** is now **Offline**.`)
    }

    return true
  })

  // ── Mod library ───────────────────────────────────────────────────────────

  ipcMain.handle('mods:list', async (_, gameId: string) => {
    const all = await readModsRegistry()
    return all.filter(m => m.gameId === gameId)
  })

  ipcMain.handle('mods:add', async (_, gameId: string, sourcePaths: string[]) => {
    const libDir = modLibDir(gameId)
    if (!existsSync(libDir)) mkdirSync(libDir, { recursive: true })

    const registry = await readModsRegistry()
    const added: ModEntry[] = []

    for (const src of sourcePaths) {
      if (!existsSync(src)) continue
      const filename = basename(src)
      const dest = join(libDir, filename)
      copyFileSync(src, dest)
      const size = statSync(dest).size
      const existing = registry.findIndex(m => m.gameId === gameId && m.filename === filename)
      const entry: ModEntry = {
        filename,
        name: filename.replace(/\.(jar|zip|dll)$/i, ''),
        gameId,
        size,
        addedAt: Date.now()
      }
      if (existing >= 0) registry[existing] = entry
      else registry.push(entry)
      added.push(entry)
    }
    await writeModsRegistry(registry)
    return added
  })

  ipcMain.handle('mods:remove', async (_, gameId: string, filename: string) => {
    const libDir = modLibDir(gameId)
    const filePath = join(libDir, filename)
    if (existsSync(filePath)) unlinkSync(filePath)

    const registry = await readModsRegistry()
    const updated = registry.filter(m => !(m.gameId === gameId && m.filename === filename))
    await writeModsRegistry(updated)

    const instances = await readInstances()
    let changed = false
    for (const inst of instances) {
      if (inst.gameId !== gameId) continue
      const before = inst.enabledMods.length
      inst.enabledMods = inst.enabledMods.filter(f => f !== filename)
      if (inst.enabledMods.length !== before) changed = true
    }
    if (changed) await writeInstances(instances)
    return true
  })

  ipcMain.handle('mods:exportBepInEx', async (_, gameId: string, instanceId: string, instanceName: string) => {
    const instDir = instanceDir(gameId, instanceId)
    const bepInExDir = join(instDir, 'BepInEx')
    if (!existsSync(bepInExDir)) {
      return { error: 'BepInEx folder not found in the server directory. Add mods first.' }
    }

    const safeName = instanceName.replace(/[^a-zA-Z0-9_-]/g, '_')
    const result = await dialog.showSaveDialog({
      title: 'Save BepInEx Mod Pack',
      defaultPath: `${safeName}_BepInEx_Pack.zip`,
      filters: [{ name: 'ZIP Archive', extensions: ['zip'] }]
    })
    if (result.canceled || !result.filePath) return { canceled: true }

    const dest = result.filePath
    try {
      if (process.platform === 'win32') {
        spawnSync('powershell', [
          '-Command',
          `Compress-Archive -LiteralPath "${bepInExDir}" -DestinationPath "${dest}" -Force`
        ], { encoding: 'utf-8' })
      } else {
        spawnSync('zip', ['-r', dest, 'BepInEx'], { cwd: instDir, encoding: 'utf-8' })
      }
      return { path: dest }
    } catch (e) {
      return { error: String(e) }
    }
  })

  ipcMain.handle('mods:openPicker', async (_, gameId: string) => {
    const extensions = MODS_CONFIG[gameId]?.extensions ?? ['zip', 'dll', 'jar']
    const result = await dialog.showOpenDialog({
      title: 'Select Mod Files',
      filters: [{ name: 'Mod files', extensions }],
      properties: ['openFile', 'multiSelections']
    })
    return result.canceled ? [] : result.filePaths
  })

  // ── Backups ───────────────────────────────────────────────────────────────

  ipcMain.handle('backup:create', (_, gameId: string, instanceId: string) => {
    const instDir = instanceDir(gameId, instanceId)
    if (!existsSync(instDir)) return false
    const bkpId = Date.now().toString()
    const dest = join(backupBase(gameId, instanceId), bkpId)
    try {
      copyDirSync(instDir, dest)
      return bkpId
    } catch (e) {
      broadcast('server:error', `Backup failed: ${e}`)
      return false
    }
  })

  ipcMain.handle('backup:list', (_, gameId: string, instanceId: string): BackupEntry[] => {
    const bkpDir = backupBase(gameId, instanceId)
    if (!existsSync(bkpDir)) return []
    return readdirSync(bkpDir, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .sort((a, b) => Number(b.name) - Number(a.name))
      .map(e => {
        const id = e.name
        const ts = Number(id)
        const sizeBytes = getDirSize(join(bkpDir, id))
        const label = isNaN(ts) ? id : new Date(ts).toLocaleString()
        return { id, label, sizeBytes }
      })
  })

  ipcMain.handle('backup:restore', (_, gameId: string, instanceId: string, bkpId: string) => {
    const instDir = instanceDir(gameId, instanceId)
    const bkpPath = join(backupBase(gameId, instanceId), bkpId)
    if (!existsSync(bkpPath)) return false
    try {
      if (existsSync(instDir)) rmSync(instDir, { recursive: true, force: true })
      copyDirSync(bkpPath, instDir)
      return true
    } catch (e) {
      broadcast('server:error', `Restore failed: ${e}`)
      return false
    }
  })

  ipcMain.handle('backup:delete', (_, gameId: string, instanceId: string, bkpId: string) => {
    const bkpPath = join(backupBase(gameId, instanceId), bkpId)
    if (!existsSync(bkpPath)) return false
    try { rmSync(bkpPath, { recursive: true, force: true }); return true }
    catch { return false }
  })
}
