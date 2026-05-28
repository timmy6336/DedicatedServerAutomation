import { ipcMain, BrowserWindow, app } from 'electron'
import { spawnSync, spawn, ChildProcess } from 'child_process'
import { existsSync, mkdirSync, createWriteStream, writeFileSync } from 'fs'
import { join } from 'path'
import { get as httpGet } from 'https'
import { readFile, writeFile } from 'fs/promises'
import * as os from 'os'

// ── active server processes keyed by game id ────────────────────────────────
const runningProcesses = new Map<string, ChildProcess>()

// ── persistent config store ─────────────────────────────────────────────────
const configPath = join(app.getPath('userData'), 'server-configs.json')

async function readConfigs(): Promise<Record<string, Record<string, unknown>>> {
  try {
    const raw = await readFile(configPath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

async function writeConfigs(data: Record<string, Record<string, unknown>>): Promise<void> {
  await writeFile(configPath, JSON.stringify(data, null, 2), 'utf-8')
}

// ── install directory ────────────────────────────────────────────────────────
function getInstallBase(): string {
  return join(app.getPath('userData'), 'servers')
}

function getSteamCmdPath(): string {
  const base = join(app.getPath('userData'), 'steamcmd')
  const exe = process.platform === 'win32' ? 'steamcmd.exe' : 'steamcmd.sh'
  return join(base, exe)
}

// ── download helper with redirect following ──────────────────────────────────
function downloadFile(url: string, dest: string, onProgress: (pct: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    const dir = join(dest, '..')
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true })

    function follow(target: string, redirects = 0) {
      if (redirects > 5) { reject(new Error('Too many redirects')); return }
      const file = createWriteStream(dest)
      httpGet(target, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.headers.location) {
          file.destroy()
          follow(res.headers.location, redirects + 1)
          return
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

// ── fetch JSON over HTTPS ─────────────────────────────────────────────────────
function fetchJson<T>(url: string): Promise<T> {
  return new Promise((resolve, reject) => {
    function follow(target: string, redirects = 0) {
      if (redirects > 5) { reject(new Error('Too many redirects')); return }
      httpGet(target, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.headers.location) {
          follow(res.headers.location, redirects + 1)
          return
        }
        let body = ''
        res.on('data', (c: Buffer) => { body += c.toString() })
        res.on('end', () => {
          try { resolve(JSON.parse(body)) }
          catch (e) { reject(e) }
        })
        res.on('error', reject)
      }).on('error', reject)
    }
    follow(url)
  })
}

// ── broadcast to all renderer windows ───────────────────────────────────────
function broadcast(channel: string, ...args: unknown[]): void {
  BrowserWindow.getAllWindows().forEach(w => w.webContents.send(channel, ...args))
}

// ── Minecraft install via Mojang API ─────────────────────────────────────────
async function installMinecraft(installDir: string): Promise<boolean> {
  // Step 0: Check Java + fetch version manifest
  broadcast('install:step', { step: 0, label: 'Checking Java & fetching version info…', progress: 0 })

  const javaCheck = spawnSync('java', ['-version'], { encoding: 'utf-8', stdio: 'pipe' })
  if (javaCheck.status !== 0 && javaCheck.error) {
    broadcast('install:error', 'Java is not installed. Please install Java 21+ from https://adoptium.net and try again.')
    return false
  }
  broadcast('install:log', `Java found: ${(javaCheck.stderr || javaCheck.stdout || '').trim().split('\n')[0]}`)
  broadcast('install:step', { step: 0, label: 'Fetching latest Minecraft version…', progress: 40 })

  interface VersionManifest {
    latest: { release: string }
    versions: Array<{ id: string; type: string; url: string }>
  }
  interface VersionMeta {
    downloads: { server: { url: string; sha1: string; size: number } }
  }

  let manifest: VersionManifest
  try {
    manifest = await fetchJson<VersionManifest>(
      'https://launchermeta.mojang.com/mc/game/version_manifest_v2.json'
    )
  } catch (e) {
    broadcast('install:error', `Failed to fetch version manifest: ${e}`)
    return false
  }

  const latestId = manifest.latest.release
  const versionEntry = manifest.versions.find(v => v.id === latestId && v.type === 'release')
  if (!versionEntry) {
    broadcast('install:error', 'Could not find latest release in version manifest.')
    return false
  }

  broadcast('install:log', `Latest release: ${latestId}`)
  broadcast('install:step', { step: 0, label: `Found Minecraft ${latestId}`, progress: 80 })

  const versionMeta = await fetchJson<VersionMeta>(versionEntry.url)
  const serverUrl = versionMeta.downloads.server.url
  const serverSize = versionMeta.downloads.server.size
  broadcast('install:step', { step: 0, label: `Found Minecraft ${latestId}`, progress: 100 })
  broadcast('install:log', `Server JAR: ${serverUrl}`)
  broadcast('install:log', `Size: ${(serverSize / 1024 / 1024).toFixed(1)} MB`)

  // Step 1: Download server.jar
  broadcast('install:step', { step: 1, label: 'Downloading server.jar…', progress: 0 })
  const jarPath = join(installDir, 'server.jar')
  try {
    await downloadFile(serverUrl, jarPath, (pct) => {
      broadcast('install:step', { step: 1, label: 'Downloading server.jar…', progress: pct })
    })
  } catch (e) {
    broadcast('install:error', `Download failed: ${e}`)
    return false
  }
  broadcast('install:log', `Downloaded server.jar to ${jarPath}`)

  // Step 2: Accept EULA + write server.properties stub
  broadcast('install:step', { step: 2, label: 'Writing config files…', progress: 30 })
  writeFileSync(join(installDir, 'eula.txt'), '#By setting eula=true you agree to the Minecraft EULA\neula=true\n', 'utf-8')
  broadcast('install:log', 'eula.txt: accepted')

  // Minimal server.properties — full values written at launch from saved config
  const props = [
    'server-port=25565',
    'max-players=20',
    'online-mode=true',
    'difficulty=normal',
    'gamemode=survival',
    'white-list=false',
    'pvp=true',
    'motd=A Minecraft Server',
    'enable-rcon=false',
  ].join('\n')
  writeFileSync(join(installDir, 'server.properties'), props + '\n', 'utf-8')
  broadcast('install:log', 'server.properties written')
  broadcast('install:step', { step: 2, label: 'Setup complete!', progress: 100 })

  return true
}

// ── SteamCMD install ─────────────────────────────────────────────────────────
async function installViaSteam(installDir: string, steamAppId: string): Promise<boolean> {
  const steamCmdPath = getSteamCmdPath()
  const steamCmdDir = join(steamCmdPath, '..')
  if (!existsSync(steamCmdDir)) mkdirSync(steamCmdDir, { recursive: true })

  // Step 0: Download SteamCMD if needed
  if (!existsSync(steamCmdPath)) {
    broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: 0 })
    const isWin = process.platform === 'win32'
    const url = isWin
      ? 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
      : 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz'
    const ext = isWin ? '.zip' : '.tar.gz'
    const archive = steamCmdPath.replace(/\.(exe|sh)$/, ext)
    try {
      await downloadFile(url, archive, (pct) => {
        broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: pct })
      })
      broadcast('install:step', { step: 0, label: 'Extracting SteamCMD…', progress: 100 })
      if (isWin) {
        spawnSync('powershell', ['-Command', `Expand-Archive -Path "${archive}" -DestinationPath "${steamCmdDir}" -Force`])
      } else {
        spawnSync('tar', ['-xzf', archive, '-C', steamCmdDir])
        spawnSync('chmod', ['+x', steamCmdPath])
      }
      broadcast('install:log', 'SteamCMD ready')
    } catch (e) {
      broadcast('install:error', String(e))
      return false
    }
  } else {
    broadcast('install:step', { step: 0, label: 'SteamCMD already installed', progress: 100 })
  }

  // Step 1: Install game via SteamCMD
  broadcast('install:step', { step: 1, label: 'Installing server files…', progress: 0 })
  return new Promise<boolean>((resolve) => {
    const args = ['+force_install_dir', installDir, '+login', 'anonymous', '+app_update', steamAppId, 'validate', '+quit']
    const proc = spawn(steamCmdPath, args)
    let buf = ''

    proc.stdout?.on('data', (chunk: Buffer) => {
      buf += chunk.toString()
      const lines = buf.split('\n')
      buf = lines.pop() ?? ''
      for (const line of lines) {
        broadcast('install:log', line)
        const m = line.match(/progress:\s*([\d.]+)/)
        if (m) broadcast('install:step', { step: 1, label: 'Installing server files…', progress: Math.round(parseFloat(m[1])) })
      }
    })
    proc.stderr?.on('data', (c: Buffer) => broadcast('install:log', c.toString()))
    proc.on('close', (code) => {
      broadcast('install:step', { step: 1, label: 'Installation complete', progress: 100 })
      broadcast('install:done', code === 0)
      resolve(code === 0)
    })
  })
}

// ── IPC registration ─────────────────────────────────────────────────────────
export function registerIpcHandlers(): void {

  // Window controls
  ipcMain.on('window:minimize', () => BrowserWindow.getFocusedWindow()?.minimize())
  ipcMain.on('window:maximize', () => {
    const win = BrowserWindow.getFocusedWindow()
    if (win?.isMaximized()) win.unmaximize()
    else win?.maximize()
  })
  ipcMain.on('window:close', () => BrowserWindow.getFocusedWindow()?.close())

  // Config persistence
  ipcMain.handle('config:load', async (_, gameId: string) => {
    const all = await readConfigs()
    return all[gameId] ?? null
  })

  ipcMain.handle('config:save', async (_, gameId: string, config: Record<string, unknown>) => {
    const all = await readConfigs()
    all[gameId] = config
    await writeConfigs(all)
    return true
  })

  // Check if game server is installed
  ipcMain.handle('server:isInstalled', (_, gameId: string, executableSubdir: string, executable: string) => {
    const base = join(getInstallBase(), gameId)
    const exePath = executableSubdir ? join(base, executableSubdir, executable) : join(base, executable)
    return existsSync(exePath)
  })

  // Check if server is running
  ipcMain.handle('server:isRunning', (_, gameId: string, processNames: string[]) => {
    const proc = runningProcesses.get(gameId)
    if (proc && !proc.killed) return true
    try {
      if (process.platform === 'win32') {
        const result = spawnSync('tasklist', ['/FO', 'CSV', '/NH'], { encoding: 'utf-8' })
        const lower = (result.stdout || '').toLowerCase()
        return processNames.some(n => lower.includes(n.toLowerCase()))
      } else {
        const result = spawnSync('pgrep', ['-f', processNames[0]], { encoding: 'utf-8' })
        return result.status === 0
      }
    } catch {
      return false
    }
  })

  // Get local IP
  ipcMain.handle('server:localIp', () => {
    const nets = os.networkInterfaces()
    for (const iface of Object.values(nets)) {
      for (const addr of iface ?? []) {
        if (addr.family === 'IPv4' && !addr.internal) return addr.address
      }
    }
    return '127.0.0.1'
  })

  // Check Java
  ipcMain.handle('server:checkJava', () => {
    const result = spawnSync('java', ['-version'], { encoding: 'utf-8', stdio: 'pipe' })
    if (result.error) return null
    const output = (result.stderr || result.stdout || '').trim().split('\n')[0]
    return output || null
  })

  // Install — routes to Steam or Mojang based on installMode
  ipcMain.handle('install:start', async (_, gameId: string, steamAppId: string, installMode: string) => {
    const installDir = join(getInstallBase(), gameId)
    if (!existsSync(installDir)) mkdirSync(installDir, { recursive: true })

    if (installMode === 'mojang') {
      const ok = await installMinecraft(installDir)
      broadcast('install:done', ok)
      return ok
    } else {
      return installViaSteam(installDir, steamAppId)
    }
  })

  // Start server — handles native exe and Java JAR
  ipcMain.handle('server:start', (_, gameId: string, exePath: string, args: string[], launchMode: string) => {
    const existing = runningProcesses.get(gameId)
    if (existing && !existing.killed) return true

    try {
      let cmd: string
      let cmdArgs: string[]

      if (launchMode === 'java') {
        // exePath is the installDir; args already contain -jar server.jar etc.
        cmd = 'java'
        cmdArgs = args
      } else {
        cmd = exePath
        cmdArgs = args
      }

      const cwd = launchMode === 'java' ? exePath : join(exePath, '..')
      const proc = spawn(cmd, cmdArgs, { cwd, detached: true, stdio: 'ignore' })
      proc.unref()
      runningProcesses.set(gameId, proc)
      return true
    } catch (e) {
      broadcast('server:error', String(e))
      return false
    }
  })

  // Stop server
  ipcMain.handle('server:stop', (_, gameId: string, processNames: string[]) => {
    const proc = runningProcesses.get(gameId)
    if (proc && !proc.killed) {
      proc.kill()
      runningProcesses.delete(gameId)
      return true
    }
    try {
      if (process.platform === 'win32') {
        for (const name of processNames) spawnSync('taskkill', ['/F', '/IM', name])
      } else {
        for (const name of processNames) spawnSync('pkill', ['-f', name])
      }
      return true
    } catch {
      return false
    }
  })
}
